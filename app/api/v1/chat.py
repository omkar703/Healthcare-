"""
Unified Chat API Router for Patient and Doctor Chatbots.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import uuid
import shutil
from pathlib import Path
import logging
from datetime import datetime

from app.database import get_db
from app.models.patient import Patient, Doctor
from app.models.conversation import PatientConversation, DoctorConversation
from app.models.document import MedicalDocument, DocumentType, ProcessingStatus
from app.models.health_score import HealthScore, RiskAssessment
from app.schemas.chat import (
    PatientChatRequest,
    PatientChatResponse,
    DoctorGeneralChatRequest,
    DoctorPatientChatRequest,
    DoctorChatResponse,
    DocumentUploadResponse,
    DocumentStatusResponse,
    ConversationHistoryResponse,
    ConversationSummary,
    ConversationDetail,
    DocumentListResponse,
    DocumentSummary,
    ChatMessage,
    MessageRole
)
from app.services.rag_service import rag_service
from app.services.aws_bedrock import bedrock_service
from app.services.ai_guardrails import ai_guardrails_service
from app.tasks.document_tasks import process_document_complete

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)


# ==================== PATIENT CHAT ENDPOINTS ====================

@router.post("/patient/{patient_uuid}", response_model=PatientChatResponse)
async def patient_chat(
    patient_uuid: uuid.UUID,
    request: PatientChatRequest,
    db: Session = Depends(get_db)
):
    """
    Patient chat with AI (with safety guardrails).
    """
    try:
        # Verify patient exists
        patient = db.query(Patient).filter(Patient.patient_uuid == patient_uuid).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Get or create conversation
        if request.conversation_id:
            conversation = db.query(PatientConversation).filter(
                PatientConversation.conversation_id == request.conversation_id,
                PatientConversation.patient_uuid == patient_uuid
            ).first()
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        else:
            conversation = PatientConversation(
                patient_uuid=patient_uuid,
                messages=[],
                rag_context_ids=[]
            )
            db.add(conversation)
            db.flush()
        
        # Get RAG context with graceful error handling
        try:
            context_data = rag_service.get_context_for_chat(
                query=request.message,
                patient_uuid=str(patient_uuid),
                db=db,
                is_doctor=False
            )
        except Exception as rag_error:
            logger.warning(f"RAG context retrieval failed for patient {patient_uuid}: {str(rag_error)}")
            context_data = {
                'context_text': "No medical records available for analysis.",
                'source_documents': [],
                'chunk_ids': []
            }
        
        # Build system prompt with patient guardrails
        system_prompt = ai_guardrails_service.build_patient_system_prompt(
            context=context_data['context_text']
        )
        
        # Generate AI response
        messages = [{"role": "user", "content": request.message}]
        
        ai_response = bedrock_service.chat_completion(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.7
        )
        
        # Extract response text
        response_text = ai_response.get('content', [{}])[0].get('text', 'I apologize, I encountered an error.')
        
        # Apply patient guardrails
        filtered_response, guardrails_metadata = ai_guardrails_service.apply_patient_guardrails(
            query=request.message,
            ai_response=response_text
        )
        
        # Add messages to conversation
        from sqlalchemy.orm.attributes import flag_modified
        new_messages = list(conversation.messages)
        new_messages.append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.utcnow().isoformat()
        })
        new_messages.append({
            "role": "assistant",
            "content": filtered_response,
            "timestamp": datetime.utcnow().isoformat(),
            "sources": list(context_data['source_documents'])
        })
        conversation.messages = new_messages
        flag_modified(conversation, "messages")
        
        # Update RAG context IDs
        if context_data['chunk_ids']:
            new_ids = [uuid.UUID(cid) for cid in context_data['chunk_ids']]
            conversation.rag_context_ids.extend(new_ids)
            flag_modified(conversation, "rag_context_ids")
        
        db.commit()
        db.refresh(conversation)
        
        return PatientChatResponse(
            conversation_id=conversation.conversation_id,
            message=filtered_response,
            sources=list(context_data['source_documents']),
            is_emergency=guardrails_metadata['is_emergency'],
            is_complex=guardrails_metadata['is_complex'],
            guardrails_applied=guardrails_metadata['guardrails_applied']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error in patient chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error in patient chat: {str(e)}")


@router.post("/patient/{patient_uuid}/upload", response_model=DocumentUploadResponse)
async def patient_upload_document(
    patient_uuid: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload medical document for patient.
    """
    try:
        patient = db.query(Patient).filter(Patient.patient_uuid == patient_uuid).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        doc_dir = Path(f"_documents/patients/{patient_uuid}")
        doc_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = doc_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        mime_type = file.content_type or "application/octet-stream"
        
        document = MedicalDocument(
            document_id=uuid.uuid4(),
            patient_uuid=patient_uuid,
            file_path=str(file_path),
            original_filename=file.filename,
            file_size_bytes=file_path.stat().st_size,
            mime_type=mime_type,
            document_type=DocumentType.OTHER,
            processing_status=ProcessingStatus.UPLOADED
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        process_document_complete.delay(
            str(document.document_id),
            str(file_path),
            mime_type
        )
        
        return DocumentUploadResponse(
            document_id=document.document_id,
            patient_uuid=patient_uuid,
            filename=file.filename,
            file_size_bytes=document.file_size_bytes,
            mime_type=mime_type,
            processing_status="UPLOADED",
            message="Document uploaded successfully. Processing started."
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error uploading document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patient/{patient_uuid}/history", response_model=ConversationHistoryResponse)
async def get_patient_conversation_history(
    patient_uuid: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get patient's conversation history"""
    try:
        conversations = db.query(PatientConversation).filter(
            PatientConversation.patient_uuid == patient_uuid
        ).order_by(PatientConversation.updated_at.desc()).all()
        
        summaries = []
        for conv in conversations:
            last_message = conv.messages[-1]['content'] if conv.messages else None
            summaries.append(ConversationSummary(
                conversation_id=conv.conversation_id,
                title=None,
                message_count=len(conv.messages),
                last_message=last_message[:100] if last_message else None,
                created_at=conv.created_at,
                updated_at=conv.updated_at
            ))
        
        return ConversationHistoryResponse(
            conversations=summaries,
            total_count=len(summaries)
        )
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patient/{patient_uuid}/documents", response_model=DocumentListResponse)
async def get_patient_documents(
    patient_uuid: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get list of patient's uploaded documents"""
    try:
        documents = db.query(MedicalDocument).filter(
            MedicalDocument.patient_uuid == patient_uuid
        ).order_by(MedicalDocument.uploaded_at.desc()).all()
        
        summaries = [
            DocumentSummary(
                document_id=doc.document_id,
                filename=doc.original_filename,
                file_size_bytes=doc.file_size_bytes,
                mime_type=doc.mime_type,
                document_type=doc.document_type.value,
                processing_status=doc.processing_status.value,
                uploaded_at=doc.uploaded_at
            )
            for doc in documents
        ]
        
        return DocumentListResponse(
            documents=summaries,
            total_count=len(summaries)
        )
    except Exception as e:
        logger.error(f"Error getting documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== DOCTOR CHAT ENDPOINTS ====================

@router.post("/doctor/{doctor_uuid}", response_model=DoctorChatResponse)
async def doctor_general_chat(
    doctor_uuid: uuid.UUID,
    request: DoctorGeneralChatRequest,
    db: Session = Depends(get_db)
):
    """
    Doctor general AI chat (like ChatGPT).
    """
    try:
        doctor = db.query(Doctor).filter(Doctor.doctor_uuid == doctor_uuid).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        system_prompt = f"You are an advanced medical AI assistant helping Dr. {doctor.name} ({doctor.specialization}). Provide professional, accurate, and comprehensive medical analysis."
        
        messages = [{"role": "user", "content": request.message}]
        
        ai_response = bedrock_service.chat_completion(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.5
        )
        
        response_text = ai_response.get('content', [{}])[0].get('text', 'I apologize, I encountered an error.')
        
        return DoctorChatResponse(
            conversation_id=request.conversation_id or uuid.uuid4(),
            message=response_text,
            sources=[],
            patient_summary=None
        )
    except Exception as e:
        logger.error(f"Error in doctor general chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/doctor/{doctor_uuid}/patient/{patient_uuid}", response_model=DoctorChatResponse)
async def doctor_patient_chat(
    doctor_uuid: uuid.UUID,
    patient_uuid: uuid.UUID,
    request: DoctorPatientChatRequest,
    db: Session = Depends(get_db)
):
    """
    Doctor patient-specific chat with full medical record access.
    """
    try:
        doctor = db.query(Doctor).filter(Doctor.doctor_uuid == doctor_uuid).first()
        patient = db.query(Patient).filter(Patient.patient_uuid == patient_uuid).first()
        
        if not doctor or not patient:
            raise HTTPException(status_code=404, detail="Doctor or Patient not found")
        
        health_score = db.query(HealthScore).filter(HealthScore.patient_uuid == patient_uuid).order_by(HealthScore.version.desc()).first()
        risk_assessment = db.query(RiskAssessment).filter(RiskAssessment.patient_uuid == patient_uuid).order_by(RiskAssessment.version.desc()).first()
        
        patient_summary = {
            "name": patient.demographic_data.get("name", "Unknown"),
            "age": patient.demographic_data.get("age", "Unknown"),
            "health_score": health_score.overall_score if health_score else None,
            "risk_level": risk_assessment.overall_risk if risk_assessment else None
        }
        
        try:
            context_data = rag_service.get_context_for_chat(
                query=request.message,
                patient_uuid=str(patient_uuid),
                db=db,
                is_doctor=True
            )
        except Exception as rag_error:
            logger.warning(f"RAG context failed for doctor: {str(rag_error)}")
            context_data = {'context_text': "No patient records available.", 'source_documents': []}
        
        system_prompt = f"""You are a medical AI assistant helping Dr. {doctor.name} ({doctor.specialization}) 
analyze patient medical records.
Patient: {patient_summary['name']}, Age: {patient_summary['age']}, Risk: {patient_summary['risk_level']}
Context: {context_data['context_text']}
Additional Context: {request.additional_context or 'None'}
"""
        
        ai_response = bedrock_service.chat_completion(
            messages=[{"role": "user", "content": request.message}],
            system_prompt=system_prompt,
            temperature=0.5
        )
        
        response_text = ai_response.get('content', [{}])[0].get('text', 'Error generating response.')
        
        return DoctorChatResponse(
            conversation_id=request.conversation_id or uuid.uuid4(),
            message=response_text,
            sources=list(context_data.get('source_documents', [])),
            patient_summary=patient_summary
        )
    except Exception as e:
        logger.error(f"Error in doctor patient chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/doctor/{doctor_uuid}/upload", response_model=DocumentUploadResponse)
async def doctor_upload_document(
    doctor_uuid: uuid.UUID,
    patient_uuid: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Doctor uploads document for a patient."""
    try:
        doctor = db.query(Doctor).filter(Doctor.doctor_uuid == doctor_uuid).first()
        patient = db.query(Patient).filter(Patient.patient_uuid == patient_uuid).first()
        if not doctor or not patient:
            raise HTTPException(status_code=404, detail="Doctor or Patient not found")
        
        doc_dir = Path(f"_documents/patients/{patient_uuid}")
        doc_dir.mkdir(parents=True, exist_ok=True)
        file_path = doc_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        mime_type = file.content_type or "application/octet-stream"
        document = MedicalDocument(
            document_id=uuid.uuid4(),
            patient_uuid=patient_uuid,
            file_path=str(file_path),
            original_filename=file.filename,
            file_size_bytes=file_path.stat().st_size,
            mime_type=mime_type,
            document_type=DocumentType.OTHER,
            processing_status=ProcessingStatus.UPLOADED
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        process_document_complete.delay(str(document.document_id), str(file_path), mime_type)
        
        return DocumentUploadResponse(
            document_id=document.document_id,
            patient_uuid=patient_uuid,
            filename=file.filename,
            file_size_bytes=document.file_size_bytes,
            mime_type=mime_type,
            processing_status="UPLOADED",
            message="Document uploaded by doctor. Processing started."
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error doctor uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== COMMON ENDPOINTS ====================

@router.get("/documents/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get document processing status"""
    try:
        document = db.query(MedicalDocument).filter(MedicalDocument.document_id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentStatusResponse(
            document_id=document.document_id,
            processing_status=document.processing_status.value,
            tier_1_complete=document.tier_1_complete,
            tier_2_complete=document.tier_2_complete,
            tier_3_complete=document.tier_3_complete,
            error_message=document.error_message,
            processed_at=document.processed_at
        )
    except Exception as e:
        logger.error(f"Error getting document status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
