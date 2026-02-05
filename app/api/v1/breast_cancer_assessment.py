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
    
    **Scoring Logic:**
    - Starts at 100 (Perfect Health)
    - Deductions based on risk factors
    - Final score: 0-100
    
    **Risk Levels:**
    - HIGH (0-40): Critical flags present → Immediate specialist referral + Stage 2 labs + Genetic screening
    - MEDIUM (41-75): Moderate risk factors → Doctor consultation + Stage 2 labs
    - LOW (76-100): Good health status → Continue screening + Stage 1 labs
    - STAGE 3: Previous cancer diagnosis → Oncology monitoring + Biopsy/Treatment tracking
    
    **Lab Test Stages:**
    - Stage 1: Basic health panel (lipids, insulin, kidney, liver, CBC, thyroid, vitamins)
    - Stage 2: Stage 1 + BRCA genetic testing + Tumor markers (CA 15-3, CA 27-29)
    - Stage 3: Biopsy, histopathology, treatment monitoring, radiation tracking
    
    **Critical Flags (Automatic HIGH risk):**
    - Hard/fixed lump
    - Bloody nipple discharge
    - Skin dimpling (peau d'orange)
    - Nipple retraction
    - Known BRCA1/2 mutation
    - Prior chest radiation before age 30
    """
    try:
        logger.info(f"Processing breast cancer assessment for patient: {request.patientId}")
        
        # Verify patient exists (optional - can be removed if not required)
        patient = db.query(Patient).filter(Patient.patient_uuid == request.patientId).first()
        if not patient:
            logger.warning(f"Patient {request.patientId} not found in database, proceeding with assessment")
            # Note: We don't raise an error here as this is a standalone assessment service
        
        # Calculate assessment
        assessment = breast_cancer_scoring_service.calculate_assessment(request)
        
        # Optionally store the assessment in the database
        if patient:
            # Store breast cancer screening data in patient record
            patient.breast_cancer_screening = {
                "patientId": str(request.patientId),
                "score": assessment.score,
                "riskLevel": assessment.riskLevel,
                "recommendation": assessment.recommendation,
                "labTestStage": assessment.labTestStage,
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
            logger.info(f"Stored breast cancer assessment for patient {request.patientId}")
        
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
            riskLevel=screening_data.get("riskLevel", "Low"),
            recommendation=screening_data.get("recommendation", ""),
            requiredLabTests=breast_cancer_scoring_service._get_lab_tests(screening_data.get("labTestStage", "Stage 1")),
            labTestStage=screening_data.get("labTestStage", "Stage 1"),
            reasoning=screening_data.get("reasoning", ""),
            criticalFlags=screening_data.get("criticalFlags", [])
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving assessment: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving breast cancer assessment: {str(e)}")
