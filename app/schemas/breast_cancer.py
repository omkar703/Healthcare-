from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Optional
from datetime import date, datetime
from enum import Enum

class ScreeningType(str, Enum):
    MAMMOGRAM = "MAMMOGRAM"
    ULTRASOUND = "ULTRASOUND"
    MRI = "MRI"
    NEVER = "NEVER"

class PriorBreastCondition(str, Enum):
    BENIGN_LUMP = "BENIGN_LUMP"
    FIBROADENOMA = "FIBROADENOMA"
    CYST = "CYST"
    ATYPICAL_HYPERPLASIA = "ATYPICAL_HYPERPLASIA"
    DCIS = "DCIS"
    BREAST_CANCER = "BREAST_CANCER"
    NONE = "NONE"

class SkinChange(str, Enum):
    DIMPLING = "DIMPLING"
    REDNESS = "REDNESS"
    THICKENING = "THICKENING"
    PEAU_D_ORANGE = "PEAU_D_ORANGE"

class NippleDischargeType(str, Enum):
    CLEAR = "CLEAR"
    MILKY = "MILKY"
    BLOODY = "BLOODY"
    YELLOW_GREEN = "YELLOW_GREEN"
    NONE = "NONE"

class ExerciseFrequency(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"

class RiskLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"

class ScreeningHistory(BaseModel):
    age: int = Field(..., ge=0)
    previousScreening: List[ScreeningType]
    lastScreeningDate: Optional[date] = None
    denseBreastTissue: bool
    priorBreastCondition: List[PriorBreastCondition]

class FamilyGeneticRisk(BaseModel):
    firstDegreeRelativeBreastCancer: bool
    familyOtherCancers: bool
    knownBRCAMutation: bool
    relativeBefore50: bool

class CurrentSymptoms(BaseModel):
    newLump: bool
    hardOrFixedLump: Optional[bool] = None
    increasingSize: Optional[bool] = None
    localizedPain: Optional[bool] = None
    persistentPain: Optional[bool] = None

class SkinNippleChanges(BaseModel):
    skinChanges: Optional[List[SkinChange]] = None
    nippleInversion: Optional[bool] = None
    nippleDischargeType: Optional[NippleDischargeType] = None
    dischargeOneSide: Optional[bool] = None
    nippleSoresOrCrusting: Optional[bool] = None

class ShapeSizeChanges(BaseModel):
    sizeOrShapeChange: Optional[bool] = None
    asymmetry: Optional[bool] = None
    swelling: Optional[bool] = None

class HormonalHistory(BaseModel):
    menarcheAge: Optional[int] = None
    menopause: Optional[bool] = None
    menopauseAge: Optional[int] = None
    everPregnant: Optional[bool] = None
    ageFirstFullTermPregnancy: Optional[int] = None
    usedHRT: Optional[bool] = None
    longTermOCPUse: Optional[bool] = None

class Lifestyle(BaseModel):
    alcoholUse: Optional[bool] = None
    exerciseFrequency: Optional[ExerciseFrequency] = None
    heightCm: Optional[int] = None
    weightKg: Optional[int] = None
    tobaccoUse: Optional[bool] = None

class PriorCancerRadiation(BaseModel):
    chestRadiationBefore30: Optional[bool] = None
    previousCancer: Optional[bool] = None

class InfectionHistory(BaseModel):
    currentlyBreastfeeding: Optional[bool] = None
    recentMastitis: Optional[bool] = None
    rednessWithFever: Optional[bool] = None

class SystemEscalation(BaseModel):
    patientConcernDespiteNormalTests: Optional[bool] = None
    wantsDoctorConsultation: Optional[bool] = None

class BreastCancerRiskSchema(BaseModel):
    patientId: UUID
    screeningHistory: ScreeningHistory
    familyGeneticRisk: FamilyGeneticRisk
    currentSymptoms: CurrentSymptoms
    skinNippleChanges: SkinNippleChanges
    shapeSizeChanges: ShapeSizeChanges
    hormonalHistory: HormonalHistory
    lifestyle: Lifestyle
    priorCancerRadiation: PriorCancerRadiation
    infectionHistory: InfectionHistory
    systemEscalation: SystemEscalation
    riskScore: Optional[int] = None
    riskLevel: Optional[RiskLevel] = None

    class Config:
        from_attributes = True
