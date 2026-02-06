"""
Breast Cancer Risk Assessment API Endpoint
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
import logging

from app.database import get_db
from app.models import Patient
from app.schemas.breast_cancer_assessment import (
    BreastCancerAssessmentRequest,
    BreastCancerAssessmentResponse
)
from app.services.breast_cancer_scoring import breast_cancer_scoring_service

router = APIRouter(prefix="/breast-cancer", tags=["breast-cancer-assessment"])
logger = logging.getLogger(__name__)


@router.post("/assess", response_model=BreastCancerAssessmentResponse)
async def assess_breast_cancer_risk(
    request: BreastCancerAssessmentRequest,
    db: Session = Depends(get_db)
):
    """
    Calculate comprehensive breast cancer risk assessment.
    
    This is a standalone calculation service. It takes patient data and returns 
    a health score and recommendations. If the patient exists in the database, 
    the result is automatically saved.
    """
    try:
        logger.info(f"Processing breast cancer assessment for patient: {request.patientId}")
        
        # 1. Calculate assessment (Standalone logic, no DB needed)
        assessment = breast_cancer_scoring_service.calculate_assessment(request)
        
        # 2. Optionally store the assessment in the database if patient exists
        try:
            patient = db.query(Patient).filter(Patient.patient_uuid == request.patientId).first()
            if patient:
                patient.breast_cancer_screening = {
                    "patientId": str(request.patientId),
                    "score": assessment.score,
                    "riskScore": assessment.score,
                    "riskLevel": assessment.riskLevel,
                    "recommendation": assessment.recommendation,
                    "labTestStage": assessment.labTestStage,
                    "reasoning": assessment.reasoning,
                    "criticalFlags": assessment.criticalFlags,
                    "screeningHistory": request.screeningHistory.model_dump(),
                    "familyGeneticRisk": request.familyGeneticRisk.model_dump(),
                    "currentSymptoms": request.currentSymptoms.model_dump(),
                    "skinNippleChanges": request.skinNippleChanges.model_dump(),
                    "shapeSizeChanges": request.shapeSizeChanges.model_dump(),
                    "hormonalHistory": request.hormonalHistory.model_dump(),
                    "lifestyle": request.lifestyle.model_dump(),
                    "priorCancerRadiation": request.priorCancerRadiation.model_dump()
                }
                db.commit()
                logger.info(f"Stored assessment for patient {request.patientId}")
        except Exception as db_err:
            logger.warning(f"Could not store assessment in database: {str(db_err)}")
            # We don't fail the request if DB storage fails, as this is primarily a calculation service
            
        logger.info(f"Assessment complete: Score={assessment.score}, Risk={assessment.riskLevel}")
        return assessment
        
    except Exception as e:
        logger.error(f"Error in breast cancer assessment: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error calculating breast cancer assessment: {str(e)}")


@router.get("/assess/{patient_uuid}", response_model=BreastCancerAssessmentResponse)
async def get_latest_assessment(
    patient_uuid: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Retrieve the latest breast cancer assessment for a patient.
    
    This endpoint retrieves the stored assessment data from the patient's record.
    """
    try:
        patient = db.query(Patient).filter(Patient.patient_uuid == patient_uuid).first()
        
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        if not patient.breast_cancer_screening:
            raise HTTPException(
                status_code=404, 
                detail="No breast cancer assessment found for this patient. Please submit an assessment first."
            )
        
        # Convert stored data to response model
        screening_data = patient.breast_cancer_screening
        
        return BreastCancerAssessmentResponse(
            patientId=patient_uuid,
            score=screening_data.get("score", 0),
            riskScore=screening_data.get("score", screening_data.get("riskScore", 0)),
            riskLevel=screening_data.get("riskLevel", "Low"),
            recommendation=screening_data.get("recommendation", ""),
            requiredLabTests=breast_cancer_scoring_service._get_lab_tests(screening_data.get("labTestStage", "Stage 1")),
            labTestStage=screening_data.get("labTestStage", "Stage 1"),
            reasoning=screening_data.get("reasoning", "No reasoning provided."),
            criticalFlags=screening_data.get("criticalFlags", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving assessment: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving breast cancer assessment: {str(e)}")
