"""
Doctor API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.models import Doctor, Patient, HealthScore, RiskAssessment
from app.schemas.doctor import (
    DoctorPatientsResponse,
    PatientSummary
)

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("/{doctor_uuid}/patients", response_model=DoctorPatientsResponse)
async def get_doctor_patients(
    doctor_uuid: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Get list of patients accessible to doctor.
    """
    try:
        # Verify doctor exists
        doctor = db.query(Doctor).filter(Doctor.doctor_uuid == doctor_uuid).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        # Get all patients
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
