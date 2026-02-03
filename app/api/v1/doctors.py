"""
Doctor API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
import uuid
from pathlib import Path

from app.database import get_db
from app.models import Doctor, Patient, HealthScore, RiskAssessment, VerificationStatus
from app.schemas.doctor import (
    DoctorOnboardingRequest,
    DoctorOnboardingResponse,
    DoctorChatRequest,
    DoctorChatResponse,
    DoctorPatientsResponse,
    PatientSummary,
    CredentialUploadResponse
)
from app.services.document_processor import document_processor
from app.services.rag_service import rag_service
from app.services.aws_bedrock import bedrock_service

router = APIRouter(prefix="/doctors", tags=["doctors"])


# Doctor onboarding and credential verification are handled by the main backend
# This microservice only receives doctor UUIDs



@router.post("/{doctor_uuid}/chat", response_model=DoctorChatResponse)
async def doctor_chat(
    doctor_uuid: uuid.UUID,
    request: DoctorChatRequest,
    db: Session = Depends(get_db)
):
    """
    Doctor chat with AI for specific patient.
    Uses higher top_k for RAG to provide comprehensive medical context.
    """
    try:
        # Verify doctor exists
        doctor = db.query(Doctor).filter(Doctor.doctor_uuid == doctor_uuid).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        # Verify patient exists
        patient = db.query(Patient).filter(Patient.patient_uuid == request.patient_uuid).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Get patient summary
        health_score = db.query(HealthScore).filter(
            HealthScore.patient_uuid == request.patient_uuid
        ).order_by(HealthScore.version.desc()).first()
        
        risk_assessment = db.query(RiskAssessment).filter(
            RiskAssessment.patient_uuid == request.patient_uuid
        ).order_by(RiskAssessment.version.desc()).first()
        
        patient_summary = {
            "name": patient.demographic_data.get("name", "Unknown"),
            "age": patient.demographic_data.get("age", "Unknown"),
            "health_score": health_score.overall_score if health_score else None,
            "risk_level": risk_assessment.overall_risk if risk_assessment else None
        }
        
        # Get RAG context (higher top_k for doctors)
        context_data = rag_service.get_context_for_chat(
            query=request.message,
            patient_uuid=str(request.patient_uuid),
            db=db,
            is_doctor=True  # Uses higher top_k
        )
        
        # Build system prompt for doctor
        system_prompt = f"""You are a medical AI assistant helping Dr. {doctor.name} ({doctor.specialization}) 
        analyze patient medical records and provide clinical insights.
        
        Patient Summary:
        - Name: {patient_summary['name']}
        - Age: {patient_summary['age']}
        - Health Score: {patient_summary['health_score']}/100
        - Risk Level: {patient_summary['risk_level']}
        
        Guidelines:
        - Provide detailed medical analysis
        - Use medical terminology appropriately
        - Highlight concerning findings
        - Suggest further tests or interventions if needed
        - Reference specific values and dates from medical records
        
        Additional Context: {request.additional_context or 'None'}
        
        Medical Records Context:
        """ + context_data['context_text']
        
        # Generate response
        messages = [
            {"role": "user", "content": request.message}
        ]
        
        response = bedrock_service.chat_completion(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.5  # Lower temperature for medical accuracy
        )
        
        # Extract response text
        response_text = response.get('content', [{}])[0].get('text', 'I apologize, I encountered an error.')
        
        return DoctorChatResponse(
            conversation_id=request.conversation_id or uuid.uuid4(),
            message=response_text,
            sources=context_data['source_documents'],
            patient_summary=patient_summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in doctor chat: {str(e)}")


@router.get("/{doctor_uuid}/patients", response_model=DoctorPatientsResponse)
async def get_doctor_patients(
    doctor_uuid: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Get list of patients accessible to doctor.
    In production, this would be filtered by access permissions.
    For now, returns all patients.
    """
    try:
        # Verify doctor exists
        doctor = db.query(Doctor).filter(Doctor.doctor_uuid == doctor_uuid).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        # Get all patients (in production, filter by access permissions)
        patients = db.query(Patient).all()
        
        patient_summaries = []
        for patient in patients:
            # Get latest health score
            health_score = db.query(HealthScore).filter(
                HealthScore.patient_uuid == patient.patient_uuid
            ).order_by(HealthScore.version.desc()).first()
            
            # Get latest risk assessment
            risk_assessment = db.query(RiskAssessment).filter(
                RiskAssessment.patient_uuid == patient.patient_uuid
            ).order_by(RiskAssessment.version.desc()).first()
            
            patient_summaries.append(PatientSummary(
                patient_uuid=patient.patient_uuid,
                name=patient.demographic_data.get("name", "Unknown"),
                age=patient.demographic_data.get("age", 0),
                overall_risk=risk_assessment.overall_risk if risk_assessment else None,
                health_score=health_score.overall_score if health_score else None,
                last_updated=patient.updated_at
            ))
        
        return DoctorPatientsResponse(
            doctor_uuid=doctor_uuid,
            patients=patient_summaries,
            total_count=len(patient_summaries)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving patients: {str(e)}")
