"""
Patient API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.models import Patient, HealthScore, RiskAssessment
from app.schemas.patient import (
    HealthScoreResponse,
    RiskAssessmentResponse
)

router = APIRouter(prefix="/patients", tags=["patients"])


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
