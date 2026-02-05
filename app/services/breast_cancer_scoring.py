"""
Breast Cancer Risk Scoring Service
Calculates breast health scores, risk levels, and lab test recommendations
"""

from typing import Dict, List, Tuple
from app.schemas.breast_cancer_assessment import (
    BreastCancerAssessmentRequest,
    BreastCancerAssessmentResponse,
    RiskLevel,
    LabTestStage
)
import logging

logger = logging.getLogger(__name__)


class BreastCancerScoringService:
    """Service for calculating breast cancer risk scores and recommendations"""
    
    # Lab test mappings based on stages
    STAGE_1_TESTS = [
        # Cardiovascular/Lipid Panel
        "Total Cholesterol",
        "HDL Cholesterol",
        "LDL Cholesterol",
        "Triglycerides",
        
        # Insulin/Diabetes Panel
        "Fasting Glucose",
        "HbA1c (Glycated Hemoglobin)",
        
        # Kidney Function
        "Serum Creatinine",
        "eGFR (Estimated Glomerular Filtration Rate)",
        "Blood Urea Nitrogen (BUN)",
        
        # Liver Function
        "ALT (Alanine Aminotransferase)",
        "ALP (Alkaline Phosphatase)",
        "Total Bilirubin",
        "Albumin",
        
        # Complete Blood Count
        "Hemoglobin",
        "Hematocrit",
        "White Blood Cell Count",
        "Platelet Count",
        "Iron",
        "Ferritin",
        
        # Thyroid Function
        "TSH (Thyroid Stimulating Hormone)",
        "Free T3",
        "Free T4",
        
        # Vitamins and Minerals
        "Vitamin D (25-OH)",
        "Vitamin B12",
        "Serum Calcium",
        "Magnesium"
    ]
    
    STAGE_2_TESTS = STAGE_1_TESTS + [
        # Genetic Testing
        "BRCA1 Gene Mutation Test",
        "BRCA2 Gene Mutation Test",
        
        # Tumor Markers
        "CA 15-3 (Cancer Antigen 15-3)",
        "CA 27-29 (Cancer Antigen 27-29)",
        "CEA (Carcinoembryonic Antigen)",
        
        # Additional Imaging Recommendations
        "Mammogram (Diagnostic)",
        "Breast Ultrasound",
        "Breast MRI (if high genetic risk)"
    ]
    
    STAGE_3_TESTS = STAGE_1_TESTS + [
        # Biopsy and Pathology
        "Core Needle Biopsy",
        "Histopathology Report",
        "Immunohistochemistry (ER, PR, HER2)",
        "Ki-67 Proliferation Index",
        
        # Advanced Tumor Markers
        "CA 15-3 (Cancer Antigen 15-3)",
        "CA 27-29 (Cancer Antigen 27-29)",
        "CEA (Carcinoembryonic Antigen)",
        
        # Genetic Testing
        "BRCA1/BRCA2 Mutation Analysis",
        "Oncotype DX (if applicable)",
        
        # Treatment Monitoring
        "Complete Blood Count (CBC) - Frequent",
        "Liver Function Tests - Monthly",
        "Kidney Function Tests - Monthly",
        
        # Imaging Follow-up
        "PET-CT Scan (Staging)",
        "Bone Scan",
        "Chest CT Scan",
        
        # Radiation Therapy Markers (if applicable)",
        "Radiation Treatment Planning Scan",
        "Post-Radiation Follow-up Imaging"
    ]
    
    def calculate_assessment(self, request: BreastCancerAssessmentRequest) -> BreastCancerAssessmentResponse:
        """
        Calculate comprehensive breast cancer risk assessment
        
        Args:
            request: Assessment request with patient data
            
        Returns:
            BreastCancerAssessmentResponse with score, risk level, and recommendations
        """
        logger.info(f"Calculating breast cancer assessment for patient: {request.patientId}")
        
        # Check if patient has previous cancer (Stage 3)
        if request.priorCancerRadiation.previousCancer:
            return self._create_stage_3_response(request)
        
        # Calculate score and identify critical flags
        score, critical_flags, reasoning_parts = self._calculate_score(request)
        
        # Determine risk level and recommendations
        risk_level, recommendation, lab_stage = self._determine_risk_level(score, critical_flags)
        
        # Get lab tests based on stage
        lab_tests = self._get_lab_tests(lab_stage)
        
        # Build reasoning
        reasoning = self._build_reasoning(score, critical_flags, reasoning_parts)
        
        return BreastCancerAssessmentResponse(
            patientId=request.patientId,
            score=score,
            riskLevel=risk_level,
            recommendation=recommendation,
            requiredLabTests=lab_tests,
            labTestStage=lab_stage,
            reasoning=reasoning,
            criticalFlags=critical_flags
        )
    
    def _calculate_score(self, request: BreastCancerAssessmentRequest) -> Tuple[int, List[str], List[str]]:
        """
        Calculate score starting from 100 and applying deductions
        
        Returns:
            Tuple of (score, critical_flags, reasoning_parts)
        """
        score = 100
        critical_flags = []
        reasoning_parts = []
        
        # HIGH RISK CRITICAL FLAGS (Immediate specialist referral)
        # These are identified first as they override other scoring
        
        if request.currentSymptoms.hardOrFixedLump:
            critical_flags.append("Hard or fixed breast lump detected")
            score -= 50
            reasoning_parts.append("Hard/fixed lump: -50 points (critical finding)")
        
        if request.skinNippleChanges.dischargeType == "BLOODY":
            critical_flags.append("Bloody nipple discharge")
            score -= 40
            reasoning_parts.append("Bloody nipple discharge: -40 points (critical finding)")
        
        if request.skinNippleChanges.dimpling:
            critical_flags.append("Skin dimpling (peau d'orange)")
            score -= 35
            reasoning_parts.append("Skin dimpling: -35 points (critical finding)")
        
        if request.skinNippleChanges.nippleRetraction:
            critical_flags.append("Nipple retraction/inversion")
            score -= 30
            reasoning_parts.append("Nipple retraction: -30 points (critical finding)")
        
        if request.familyGeneticRisk.knownBRCAMutation:
            critical_flags.append("Known BRCA1/BRCA2 mutation")
            score -= 45
            reasoning_parts.append("BRCA mutation: -45 points (high genetic risk)")
        
        if request.priorCancerRadiation.chestRadiationBefore30:
            critical_flags.append("Prior chest radiation before age 30")
            score -= 35
            reasoning_parts.append("Prior chest radiation: -35 points (high risk factor)")
        
        # MEDIUM RISK FACTORS
        
        if request.currentSymptoms.newLump and not request.currentSymptoms.hardOrFixedLump:
            score -= 20
            reasoning_parts.append("New breast lump (soft): -20 points")
        
        if request.currentSymptoms.localizedPain and not request.currentSymptoms.cyclicalPainOnly:
            score -= 15
            reasoning_parts.append("Localized non-cyclical pain: -15 points")
        
        if request.currentSymptoms.persistentPain:
            score -= 12
            reasoning_parts.append("Persistent pain: -12 points")
        
        if request.screeningHistory.denseBreastTissue:
            score -= 15
            reasoning_parts.append("Dense breast tissue: -15 points")
        
        if request.familyGeneticRisk.firstDegreeRelativeBreastCancer:
            score -= 18
            reasoning_parts.append("First-degree relative with breast cancer: -18 points")
        
        if request.familyGeneticRisk.familyCancerBefore50:
            score -= 15
            reasoning_parts.append("Family cancer history before age 50: -15 points")
        
        if request.hormonalHistory.longTermHRTUse:
            score -= 12
            reasoning_parts.append("Long-term HRT use: -12 points")
        
        if request.hormonalHistory.longTermOCPUse:
            score -= 10
            reasoning_parts.append("Long-term OCP use: -10 points")
        
        # LOW-MEDIUM RISK FACTORS
        
        if request.familyGeneticRisk.secondDegreeRelativeBreastCancer:
            score -= 8
            reasoning_parts.append("Second-degree relative with breast cancer: -8 points")
        
        if request.shapeSizeChanges.sizeChange or request.shapeSizeChanges.shapeChange:
            score -= 10
            reasoning_parts.append("Breast size/shape changes: -10 points")
        
        if request.skinNippleChanges.nippleSores:
            score -= 12
            reasoning_parts.append("Nipple sores or crusting: -12 points")
        
        if request.skinNippleChanges.skinRedness:
            score -= 8
            reasoning_parts.append("Skin redness: -8 points")
        
        # LIFESTYLE FACTORS
        
        if request.lifestyle.obesity:
            score -= 8
            reasoning_parts.append("Obesity (BMI > 30): -8 points")
        
        if request.lifestyle.alcoholUse:
            score -= 5
            reasoning_parts.append("Regular alcohol use: -5 points")
        
        if request.lifestyle.tobaccoUse:
            score -= 6
            reasoning_parts.append("Tobacco use: -6 points")
        
        if request.lifestyle.sedentaryLifestyle:
            score -= 5
            reasoning_parts.append("Sedentary lifestyle: -5 points")
        
        # POSITIVE FACTORS (Minor adjustments)
        
        if request.screeningHistory.screeningUpToDate and score > 75:
            reasoning_parts.append("Regular screening up to date: Good preventive care")
        
        if request.currentSymptoms.cyclicalPainOnly and not any([
            request.currentSymptoms.newLump,
            request.currentSymptoms.localizedPain,
            request.currentSymptoms.persistentPain
        ]):
            reasoning_parts.append("Only cyclical pain: Normal physiological finding")
        
        # Ensure score stays within bounds
        score = max(0, min(100, score))
        
        return score, critical_flags, reasoning_parts
    
    def _determine_risk_level(self, score: int, critical_flags: List[str]) -> Tuple[RiskLevel, str, LabTestStage]:
        """
        Determine risk level, recommendation, and lab stage based on score and flags
        
        Returns:
            Tuple of (RiskLevel, recommendation_text, LabTestStage)
        """
        # HIGH RISK: 0-40 or any critical flags present
        if score <= 40 or critical_flags:
            return (
                RiskLevel.HIGH,
                "⚠️ URGENT: Consult a specialist immediately. Your assessment indicates high-risk factors that require prompt medical evaluation and diagnostic imaging.",
                LabTestStage.STAGE_2
            )
        
        # MEDIUM RISK: 41-75
        elif score <= 75:
            return (
                RiskLevel.MEDIUM,
                "⚡ Consult a doctor for further evaluation. Your assessment indicates moderate risk factors that warrant professional medical review and additional testing.",
                LabTestStage.STAGE_2
            )
        
        # LOW RISK: 76-100
        else:
            return (
                RiskLevel.LOW,
                "✅ Continue regular screening and maintain a healthy lifestyle. Your current breast health status is good. Maintain annual mammograms as recommended for your age group.",
                LabTestStage.STAGE_1
            )
    
    def _get_lab_tests(self, lab_stage: LabTestStage) -> List[str]:
        """Get lab tests based on stage"""
        if lab_stage == LabTestStage.STAGE_1:
            return self.STAGE_1_TESTS
        elif lab_stage == LabTestStage.STAGE_2:
            return self.STAGE_2_TESTS
        elif lab_stage == LabTestStage.STAGE_3:
            return self.STAGE_3_TESTS
        return self.STAGE_1_TESTS
    
    def _build_reasoning(self, score: int, critical_flags: List[str], reasoning_parts: List[str]) -> str:
        """Build comprehensive reasoning text"""
        reasoning = f"Breast Health Score: {score}/100\n\n"
        
        if critical_flags:
            reasoning += "❗ CRITICAL FINDINGS:\n"
            for flag in critical_flags:
                reasoning += f"  • {flag}\n"
            reasoning += "\n"
        
        if reasoning_parts:
            reasoning += "SCORE CALCULATION:\n"
            for part in reasoning_parts:
                reasoning += f"  • {part}\n"
        
        return reasoning.strip()
    
    def _create_stage_3_response(self, request: BreastCancerAssessmentRequest) -> BreastCancerAssessmentResponse:
        """Create response for Stage 3 (cancer patients)"""
        return BreastCancerAssessmentResponse(
            patientId=request.patientId,
            score=0,  # Not applicable for diagnosed cancer patients
            riskLevel=RiskLevel.HIGH,
            recommendation="🏥 CANCER CARE: You are under active cancer treatment or surveillance. Please follow your oncologist's treatment plan and monitoring schedule.",
            requiredLabTests=self.STAGE_3_TESTS,
            labTestStage=LabTestStage.STAGE_3,
            reasoning="Patient has a previous breast cancer diagnosis. Assessment moved to Stage 3 clinical monitoring with comprehensive biopsy, treatment tracking, and radiation follow-up protocols.",
            criticalFlags=["Previous breast cancer diagnosis - Stage 3 monitoring required"]
        )


# Global instance
breast_cancer_scoring_service = BreastCancerScoringService()
