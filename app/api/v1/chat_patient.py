"""
Unified Chat API Router for Patient and Doctor Chatbots.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import shutil
from pathlib import Path
import logging

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
    
    Features:
    - Safety filters (no diagnoses, simplified terminology)
    - Emergency detection
    - Complex query redirection to doctor
    - RAG-based context from patient's medical documents
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
        
        # Get RAG context (gracefully handle no documents)
        try:
            context_data = rag_service.get_context_for_chat(
                query=request.message,
                patient_uuid=str(patient_uuid),
                db=db,
                is_doctor=False
            )
        except Exception as rag_error:
            logger.warning(f"RAG context retrieval failed (likely no documents): {str(rag_error)}")
            # Use empty context if RAG fails
            context_data = {
                'context_text': 'No medical records available yet. Please upload your medical documents to get personalized insights.',
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
        conversation.messages.append({
            "role": "user",
            "content": request.message,
            "timestamp": str(uuid.uuid1().time)
        })
        conversation.messages.append({
            "role": "assistant",
            "content": filtered_response,
            "timestamp": str(uuid.uuid1().time),
            "sources": context_data['source_documents']
        })
        
        # Update RAG context IDs
        if context_data['chunk_ids']:
            conversation.rag_context_ids.extend([uuid.UUID(cid) for cid in context_data['chunk_ids']])
        
        db.commit()
        db.refresh(conversation)
        
        logger.info(f"Patient chat completed: {patient_uuid}, guardrails: {guardrails_metadata['guardrails_applied']}")
        
        return PatientChatResponse(
            conversation_id=conversation.conversation_id,
            message=filtered_response,
            sources=context_data['source_documents'],
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
