"""
Risk assessment service for categorizing patient risk levels.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models import Patient, MedicalDocument
import logging

logger = logging.getLogger(__name__)


def calculate_risk_assessment(patient_uuid: str, db: Session) -> Dict[str, Any]:
    """
    Calculate risk assessment for a patient.
    
    Args:
        patient_uuid: Patient UUID
        db: Database session
        
    Returns:
        Dict with overall risk, markers, and recommendations
    """
    try:
        # Get patient
        patient = db.query(Patient).filter(
            Patient.patient_uuid == patient_uuid
        ).first()
        
        if not patient:
            raise ValueError(f"Patient not found: {patient_uuid}")
        
        questionnaire = patient.onboarding_questionnaire
        
        # Collect risk markers
        high_risk_markers = []
        medium_risk_markers = []
        low_risk_markers = []
        
        # Analyze symptoms
        symptoms = questionnaire.get("symptoms", {})
        
        # HIGH RISK markers
        if symptoms.get("q14_new_lump") == "yes":
            high_risk_markers.append("New hard lump detected")
        
        if symptoms.get("q17_nipple_discharge") == "yes":
            discharge_type = symptoms.get("q18_discharge_type", "")
            if discharge_type == "bloody":
                high_risk_markers.append("Bloody nipple discharge")
            else:
                medium_risk_markers.append(f"Nipple discharge ({discharge_type})")
        
        if symptoms.get("q19_skin_changes") in ["dimpling", "peau_dorange"]:
            high_risk_markers.append(f"Skin changes: {symptoms.get('q19_skin_changes')}")
        
        # Family history
        family_history = questionnaire.get("family_history", {})
        
        if family_history.get("q9_brca_mutation") == "yes":
            high_risk_markers.append("BRCA1/BRCA2 mutation confirmed")
        
        relatives = family_history.get("q7_which_relatives", "")
        if "mother" in str(relatives).lower() or "sister" in str(relatives).lower():
            high_risk_markers.append("First-degree relative with breast cancer")
        elif family_history.get("q6_family_history") == "yes":
            medium_risk_markers.append("Family history of breast cancer")
        
        # Medical history
        medical_history = questionnaire.get("medical_history", {})
        
        if medical_history.get("q32_chest_radiation") == "yes":
            high_risk_markers.append("Prior chest radiation")
        
        if medical_history.get("q34_benign_breast_disease") == "yes":
            medium_risk_markers.append("History of benign breast disease")
        
        # Screening history
        screening = questionnaire.get("screening_history", {})
        
        if screening.get("q24_breast_density") in ["heterogeneously_dense", "extremely_dense"]:
            medium_risk_markers.append(f"Dense breast tissue: {screening.get('q24_breast_density')}")
        
        # Lifestyle factors
        lifestyle = questionnaire.get("lifestyle_factors", {})
        
        if lifestyle.get("q28_hormone_therapy") == "yes":
            medium_risk_markers.append("Current hormone therapy")
        
        # Determine overall risk
        if len(high_risk_markers) > 0:
            overall_risk = "HIGH"
            urgency = "HIGH"
        elif len(medium_risk_markers) >= 3:
            overall_risk = "MEDIUM"
            urgency = "MEDIUM"
        elif len(medium_risk_markers) > 0:
            overall_risk = "MEDIUM"
            urgency = "LOW"
        else:
            overall_risk = "LOW"
            urgency = "LOW"
            low_risk_markers.append("No significant risk factors identified")
        
        # Generate recommendations
        recommendations = generate_recommendations(
            overall_risk,
            high_risk_markers,
            medium_risk_markers
        )
        
        risk_markers = {
            "high_risk": high_risk_markers,
            "medium_risk": medium_risk_markers,
            "low_risk": low_risk_markers
        }
        
        logger.info(f"Risk assessment for patient {patient_uuid}: {overall_risk}")
        
        return {
            "overall_risk": overall_risk,
            "risk_markers": risk_markers,
            "recommendations": recommendations,
            "urgency": urgency
        }
        
    except Exception as e:
        logger.error(f"Error calculating risk assessment: {e}")
        raise


def generate_recommendations(
    overall_risk: str,
    high_risk_markers: List[str],
    medium_risk_markers: List[str]
) -> str:
    """Generate recommendations based on risk level"""
    
    if overall_risk == "HIGH":
        recommendations = """
URGENT RECOMMENDATIONS:
1. Schedule immediate consultation with breast surgeon or oncologist
2. Diagnostic mammogram and ultrasound within 1-2 weeks
3. Consider genetic counseling if BRCA mutation present
4. Biopsy may be recommended based on imaging results
5. Do not delay - early detection is critical

FOLLOW-UP:
- Weekly monitoring until diagnosis confirmed
- Bring all previous medical records to appointment
- Consider second opinion from breast cancer specialist
"""
    elif overall_risk == "MEDIUM":
        recommendations = """
RECOMMENDATIONS:
1. Schedule appointment with primary care physician within 2-4 weeks
2. Annual mammogram screening (or more frequent if recommended)
3. Consider breast MRI if dense breast tissue
4. Monthly self-breast examinations
5. Genetic counseling if strong family history

LIFESTYLE:
- Maintain healthy weight
- Limit alcohol consumption
- Regular physical activity
- Stress management

FOLLOW-UP:
- Re-assess in 3-6 months
- Track any changes in symptoms
"""
    else:  # LOW
        recommendations = """
RECOMMENDATIONS:
1. Continue routine annual mammogram screening (age 40+)
2. Monthly self-breast examinations
3. Annual clinical breast exam
4. Maintain healthy lifestyle

PREVENTION:
- Healthy diet rich in fruits and vegetables
- Regular exercise (150 minutes/week)
- Limit alcohol consumption
- Maintain healthy weight
- Manage stress

FOLLOW-UP:
- Annual wellness check
- Report any new symptoms immediately
"""
    
    return recommendations.strip()
