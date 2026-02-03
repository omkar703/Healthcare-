"""
Patient API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from pathlib import Path
import shutil

from app.database import get_db
from app.models import Patient, HealthScore, RiskAssessment, MedicalDocument, DocumentType, ProcessingStatus
from app.schemas.patient import (
    PatientOnboardingRequest,
    PatientOnboardingResponse,
    HealthScoreResponse,
    RiskAssessmentResponse,
    PatientChatRequest,
    PatientChatResponse,
    DocumentUploadResponse,
    DocumentStatusResponse
)
from app.services.health_scoring import calculate_health_score
from app.services.risk_assessment import calculate_risk_assessment
from app.services.rag_service import rag_service
from app.services.aws_bedrock import bedrock_service
from app.tasks.document_tasks import process_document_complete
from app.tasks.rag_tasks import recalculate_health_score, recalculate_risk_assessment

router = APIRouter(prefix="/patients", tags=["patients"])


# Patient onboarding is handled by the main backend
# This microservice only receives patient UUIDs



@router.get("/{patient_uuid}/health-score", response_model=HealthScoreResponse)
async def get_health_score(
    patient_uuid: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get latest health score for patient"""
    try:
        # Get latest health score
        health_score = db.query(HealthScore).filter(
            HealthScore.patient_uuid == patient_uuid
        ).order_by(HealthScore.version.desc()).first()
        
        if not health_score:
            raise HTTPException(status_code=404, detail="Health score not found")
        
        return HealthScoreResponse(
            score_id=health_score.score_id,
            patient_uuid=health_score.patient_uuid,
            overall_score=health_score.overall_score,
            trend=health_score.trend,
            component_scores=health_score.component_scores,
            version=health_score.version,
            calculated_at=health_score.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving health score: {str(e)}")


@router.get("/{patient_uuid}/risk-assessment", response_model=RiskAssessmentResponse)
async def get_risk_assessment(
    patient_uuid: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get latest risk assessment for patient"""
    try:
        # Get latest risk assessment
        risk_assessment = db.query(RiskAssessment).filter(
            RiskAssessment.patient_uuid == patient_uuid
        ).order_by(RiskAssessment.version.desc()).first()
        
        if not risk_assessment:
            raise HTTPException(status_code=404, detail="Risk assessment not found")
        
        return RiskAssessmentResponse(
            assessment_id=risk_assessment.assessment_id,
            patient_uuid=risk_assessment.patient_uuid,
            overall_risk=risk_assessment.overall_risk,
            risk_markers=risk_assessment.risk_markers,
            recommendations=risk_assessment.recommendations,
            urgency=risk_assessment.urgency,
            version=risk_assessment.version,
            assessed_at=risk_assessment.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving risk assessment: {str(e)}")


@router.post("/{patient_uuid}/chat", response_model=PatientChatResponse)
async def patient_chat(
    patient_uuid: uuid.UUID,
    request: PatientChatRequest,
    db: Session = Depends(get_db)
):
    """
    Patient chat with AI using RAG.
    Retrieves relevant context from patient's medical documents.
    """
    try:
        # Verify patient exists
        patient = db.query(Patient).filter(Patient.patient_uuid == patient_uuid).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Get RAG context
        context_data = rag_service.get_context_for_chat(
            query=request.message,
            patient_uuid=str(patient_uuid),
            db=db,
            is_doctor=False
        )
        
        # Build system prompt
        system_prompt = """You are a compassionate healthcare AI assistant helping patients understand their medical information.
        
        Guidelines:
        - Be empathetic and supportive
        - Explain medical terms in simple language
        - If the query seems urgent or critical, acknowledge it and recommend seeing a doctor
        - Use the provided context from their medical records to give personalized responses
        - Never provide definitive diagnoses - always recommend consulting healthcare professionals
        - Be honest if you don't have enough information
        
        Context from patient's medical records:
        """ + context_data['context_text']
        
        # Generate response
        messages = [
            {"role": "user", "content": request.message}
        ]
        
        response = bedrock_service.chat_completion(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.7
        )
        
        # Extract response text
        response_text = response.get('content', [{}])[0].get('text', 'I apologize, I encountered an error.')
        
        # Detect if query is critical
        is_critical = any(keyword in request.message.lower() for keyword in [
            'emergency', 'urgent', 'severe pain', 'bleeding', 'chest pain', 'difficulty breathing'
        ])
        
        return PatientChatResponse(
            conversation_id=request.conversation_id or uuid.uuid4(),
            message=response_text,
            sources=context_data['source_documents'],
            is_critical=is_critical
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in patient chat: {str(e)}")


@router.post("/{patient_uuid}/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    patient_uuid: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload medical document for patient.
    Triggers async 3-tier processing pipeline.
    """
    try:
        # Verify patient exists
        patient = db.query(Patient).filter(Patient.patient_uuid == patient_uuid).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Create document directory
        doc_dir = Path(f"_documents/patients/{patient_uuid}")
        doc_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = doc_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Determine MIME type
        mime_type = file.content_type or "application/octet-stream"
        
        # Create document record
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
        
        # Trigger async processing
        process_document_complete.delay(
            str(document.document_id),
            str(file_path),
            mime_type
        )
        
        return DocumentUploadResponse(
            document_id=document.document_id,
            patient_uuid=patient_uuid,
            filename=file.filename,
            processing_status="UPLOADED",
            message="Document uploaded successfully. Processing started."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@router.get("/documents/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get document processing status"""
    try:
        document = db.query(MedicalDocument).filter(
            MedicalDocument.document_id == document_id
        ).first()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentStatusResponse(
            document_id=document.document_id,
            processing_status=document.processing_status.value,
            tier_1_complete=bool(document.tier_1_text),
            tier_2_complete=bool(document.tier_2_enriched),
            tier_3_complete=document.tier_3_indexed,
            error_message=document.error_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving document status: {str(e)}")
