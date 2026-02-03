"""
RAG API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.models import Patient
from app.services.rag_service import rag_service
from pydantic import BaseModel, UUID4


router = APIRouter(prefix="/rag", tags=["rag"])


class RAGRefreshRequest(BaseModel):
    """RAG refresh request"""
    patient_uuid: UUID4


class RAGRefreshResponse(BaseModel):
    """RAG refresh response"""
    status: str
    task_id: str
    patient_uuid: UUID4
    message: str


@router.post("/refresh", response_model=RAGRefreshResponse)
async def refresh_rag_index(
    request: RAGRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Trigger RAG index refresh for a patient.
    Reprocesses all documents and recalculates health scores/risk assessments.
    """
    try:
        # Verify patient exists
        patient = db.query(Patient).filter(
            Patient.patient_uuid == request.patient_uuid
        ).first()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Trigger async RAG refresh
        result = rag_service.refresh_patient_index(
            patient_uuid=str(request.patient_uuid),
            db=db
        )
        
        return RAGRefreshResponse(
            status=result['status'],
            task_id=result['task_id'],
            patient_uuid=request.patient_uuid,
            message="RAG refresh initiated. This may take a few minutes."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing RAG index: {str(e)}")
