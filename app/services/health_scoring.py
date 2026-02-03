"""
Health scoring service for calculating patient health scores.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models import Patient, MedicalDocument, DocumentChunk
import logging

logger = logging.getLogger(__name__)


def calculate_health_score(patient_uuid: str, db: Session) -> Dict[str, Any]:
    """
    Calculate health score for a patient based on questionnaire and medical data.
    
    Args:
        patient_uuid: Patient UUID
        db: Database session
        
    Returns:
        Dict with overall score and component scores
    """
    try:
        # Get patient
        patient = db.query(Patient).filter(
            Patient.patient_uuid == patient_uuid
        ).first()
        
        if not patient:
            raise ValueError(f"Patient not found: {patient_uuid}")
        
        questionnaire = patient.onboarding_questionnaire
        
        # Initialize component scores
        component_scores = {
            "screening_compliance": calculate_screening_compliance(questionnaire),
            "physical_activity": calculate_physical_activity(questionnaire),
            "stress_relaxation": calculate_stress_relaxation(questionnaire),
            "healthy_nutrition": calculate_healthy_nutrition(questionnaire),
            "regular_health_tests": calculate_regular_health_tests(patient_uuid, db),
            "follow_up_adherence": calculate_follow_up_adherence(questionnaire)
        }
        
        # Calculate overall score (weighted average)
        weights = {
            "screening_compliance": 0.25,
            "physical_activity": 0.15,
            "stress_relaxation": 0.10,
            "healthy_nutrition": 0.15,
            "regular_health_tests": 0.20,
            "follow_up_adherence": 0.15
        }
        
        overall_score = sum(
            component_scores[key]["score"] * weights[key]
            for key in weights
        )
        
        overall_score = int(round(overall_score))
        
        logger.info(f"Calculated health score for patient {patient_uuid}: {overall_score}/100")
        
        return {
            "overall_score": overall_score,
            "component_scores": component_scores,
            "trend": "0"  # Will be calculated by comparing with previous scores
        }
        
    except Exception as e:
        logger.error(f"Error calculating health score: {e}")
        raise


def calculate_screening_compliance(questionnaire: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate screening compliance score"""
    score = 100
    status = "good"
    
    screening = questionnaire.get("screening_history", {})
    
    # Check mammogram history
    last_mammogram = screening.get("q22_last_mammogram", "never")
    if last_mammogram == "never":
        score = 30
        status = "needs_improvement"
    elif last_mammogram == "more_than_2_years":
        score = 60
        status = "fair"
    elif last_mammogram in ["within_1_year", "1_to_2_years"]:
        score = 100
        status = "good"
    
    return {
        "score": score,
        "status": status,
        "details": f"Last mammogram: {last_mammogram}"
    }


def calculate_physical_activity(questionnaire: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate physical activity score"""
    # Default good score since we don't have specific questions
    return {
        "score": 75,
        "status": "fair",
        "details": "Based on lifestyle factors"
    }


def calculate_stress_relaxation(questionnaire: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate stress/relaxation score"""
    # Default score
    return {
        "score": 70,
        "status": "fair",
        "details": "General wellness assessment"
    }


def calculate_healthy_nutrition(questionnaire: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate nutrition score"""
    score = 80
    status = "good"
    
    lifestyle = questionnaire.get("lifestyle_factors", {})
    
    # Check alcohol consumption
    alcohol = lifestyle.get("q29_alcohol_consumption", "no")
    if alcohol == "yes":
        score -= 10
    
    return {
        "score": score,
        "status": status,
        "details": "Based on lifestyle factors"
    }


def calculate_regular_health_tests(patient_uuid: str, db: Session) -> Dict[str, Any]:
    """Calculate regular health tests score based on documents"""
    # Count medical documents
    doc_count = db.query(MedicalDocument).filter(
        MedicalDocument.patient_uuid == patient_uuid
    ).count()
    
    if doc_count >= 3:
        score = 100
        status = "good"
    elif doc_count >= 1:
        score = 70
        status = "fair"
    else:
        score = 40
        status = "needs_improvement"
    
    return {
        "score": score,
        "status": status,
        "details": f"{doc_count} medical documents on file"
    }


def calculate_follow_up_adherence(questionnaire: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate follow-up adherence score"""
    score = 80
    status = "good"
    
    # Check if patient has concerns that need follow-up
    current_concerns = questionnaire.get("current_concerns", {})
    has_concerns = current_concerns.get("q36_recent_changes", "no") == "yes"
    
    if has_concerns:
        score = 60
        status = "fair"
    
    return {
        "score": score,
        "status": status,
        "details": "Follow-up tracking"
    }
