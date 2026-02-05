"""
Breast Cancer Risk Assessment Request and Response Schemas
"""

from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Optional
from datetime import date
from enum import Enum


# ==================== REQUEST SCHEMA ====================

class ScreeningHistoryInput(BaseModel):
    age: int = Field(..., ge=0, le=120, description="Patient's age")
    denseBreastTissue: bool = Field(..., description="Has dense breast tissue")
    priorConditions: Optional[List[str]] = Field(default=[], description="Prior breast conditions (e.g., 'BENIGN_LUMP', 'FIBROADENOMA')")
    lastScreeningDate: Optional[date] = Field(default=None, description="Date of last screening")
    screeningUpToDate: bool = Field(default=True, description="Is screening up to date")


class FamilyGeneticRiskInput(BaseModel):
    knownBRCAMutation: bool = Field(default=False, description="Known BRCA1/2 mutation")
    firstDegreeRelativeBreastCancer: bool = Field(default=False, description="First-degree relative with breast cancer")
    secondDegreeRelativeBreastCancer: bool = Field(default=False, description="Second-degree relative with breast cancer")
    familyCancerBefore50: bool = Field(default=False, description="Family history of cancer diagnosed before age 50")


class CurrentSymptomsInput(BaseModel):
    newLump: bool = Field(default=False, description="New breast lump detected")
    hardOrFixedLump: bool = Field(default=False, description="Lump is hard or fixed")
    localizedPain: bool = Field(default=False, description="Localized breast pain")
    persistentPain: bool = Field(default=False, description="Persistent non-cyclical pain")
    cyclicalPainOnly: bool = Field(default=False, description="Only cyclical pain (menstrual)")


class SkinNippleChangesInput(BaseModel):
    dimpling: bool = Field(default=False, description="Skin dimpling (peau d'orange)")
    nippleRetraction: bool = Field(default=False, description="Nipple inversion or retraction")
    dischargeType: Optional[str] = Field(default="NONE", description="Nipple discharge type: 'BLOODY', 'CLEAR', 'MILKY', 'NONE'")
    nippleSores: bool = Field(default=False, description="Nipple sores or crusting")
    skinRedness: bool = Field(default=False, description="Skin redness or inflammation")


class ShapeSizeChangesInput(BaseModel):
    sizeChange: bool = Field(default=False, description="Change in breast size")
    shapeChange: bool = Field(default=False, description="Change in breast shape")
    asymmetry: bool = Field(default=False, description="Breast asymmetry")


class HormonalHistoryInput(BaseModel):
    longTermOCPUse: bool = Field(default=False, description="Long-term oral contraceptive use (>5 years)")
    longTermHRTUse: bool = Field(default=False, description="Long-term hormone replacement therapy use")
    earlyMenarcheAge: bool = Field(default=False, description="Menarche before age 12")
    lateMenopause: bool = Field(default=False, description="Menopause after age 55")


class LifestyleInput(BaseModel):
    alcoholUse: bool = Field(default=False, description="Regular alcohol consumption")
    tobaccoUse: bool = Field(default=False, description="Tobacco use")
    sedentaryLifestyle: bool = Field(default=False, description="Sedentary lifestyle (low exercise)")
    obesity: bool = Field(default=False, description="BMI > 30")


class PriorCancerRadiationInput(BaseModel):
    chestRadiationBefore30: bool = Field(default=False, description="Chest radiation before age 30")
    previousCancer: bool = Field(default=False, description="Previous breast cancer diagnosis")


class BreastCancerAssessmentRequest(BaseModel):
    """Request schema for breast cancer risk assessment"""
    patientId: UUID = Field(..., description="Patient UUID")
    screeningHistory: ScreeningHistoryInput
    familyGeneticRisk: FamilyGeneticRiskInput
    currentSymptoms: CurrentSymptomsInput
    skinNippleChanges: SkinNippleChangesInput
    shapeSizeChanges: ShapeSizeChangesInput
    hormonalHistory: HormonalHistoryInput
    lifestyle: LifestyleInput
    priorCancerRadiation: PriorCancerRadiationInput


# ==================== RESPONSE SCHEMA ====================

class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class LabTestStage(str, Enum):
    STAGE_1 = "Stage 1"
    STAGE_2 = "Stage 2"
    STAGE_3 = "Stage 3"


class BreastCancerAssessmentResponse(BaseModel):
    """Response schema for breast cancer risk assessment"""
    patientId: UUID
    score: int = Field(..., ge=0, le=100, description="Breast health score (0-100)")
    riskLevel: RiskLevel
    recommendation: str = Field(..., description="Medical recommendation based on risk")
    requiredLabTests: List[str] = Field(..., description="List of required lab tests")
    labTestStage: LabTestStage = Field(..., description="Lab test stage category")
    reasoning: str = Field(..., description="Explanation of score and risk categorization")
    criticalFlags: List[str] = Field(default=[], description="List of critical risk factors identified")
    
    class Config:
        use_enum_values = True
