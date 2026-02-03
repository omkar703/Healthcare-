"""
Pydantic schemas for Patient API requests and responses.
"""

from pydantic import BaseModel, Field, UUID4
from typing import Dict, Any, List, Optional
from datetime import datetime


# ==================== PATIENT ONBOARDING ====================

class PatientOnboardingRequest(BaseModel):
    """Patient onboarding request with questionnaire"""
    demographic_data: Dict[str, Any] = Field(
        ...,
        description="Patient demographic information (name, age, gender, contact)"
    )
    onboarding_questionnaire: Dict[str, Any] = Field(
        ...,
        description="40-question health questionnaire responses"
    )


class PatientOnboardingResponse(BaseModel):
    """Patient onboarding response"""
    patient_uuid: UUID4
    message: str
    health_score_calculated: bool = False
    risk_assessment_calculated: bool = False
    
    class Config:
        from_attributes = True


# ==================== HEALTH SCORE ====================

class ComponentScore(BaseModel):
    """Individual component score"""
    score: int = Field(..., ge=0, le=100)
    status: str  # good, fair, needs_improvement
    details: str


class HealthScoreResponse(BaseModel):
    """Health score response"""
    score_id: UUID4
    patient_uuid: UUID4
    overall_score: int = Field(..., ge=0, le=100)
    trend: str  # e.g., "+5", "-3", "0"
    component_scores: Dict[str, ComponentScore]
    version: int
    calculated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== RISK ASSESSMENT ====================

class RiskMarkers(BaseModel):
    """Risk markers categorized by level"""
    high_risk: List[str] = []
    medium_risk: List[str] = []
    low_risk: List[str] = []


class RiskAssessmentResponse(BaseModel):
    """Risk assessment response"""
    assessment_id: UUID4
    patient_uuid: UUID4
    overall_risk: str  # HIGH, MEDIUM, LOW
    risk_markers: RiskMarkers
    recommendations: str
    urgency: str  # HIGH, MEDIUM, LOW
    version: int
    assessed_at: datetime
    
    class Config:
        from_attributes = True


# ==================== CHAT ====================

class ChatMessage(BaseModel):
    """Chat message"""
    role: str  # user, assistant
    content: str
    timestamp: Optional[datetime] = None


class PatientChatRequest(BaseModel):
    """Patient chat request"""
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: Optional[UUID4] = None


class PatientChatResponse(BaseModel):
    """Patient chat response"""
    conversation_id: UUID4
    message: str
    sources: List[str] = []  # Source document IDs
    is_critical: bool = False  # If query detected as critical
    
    class Config:
        from_attributes = True


# ==================== DOCUMENT UPLOAD ====================

class DocumentUploadResponse(BaseModel):
    """Document upload response"""
    document_id: UUID4
    patient_uuid: UUID4
    filename: str
    processing_status: str
    message: str
    
    class Config:
        from_attributes = True


class DocumentStatusResponse(BaseModel):
    """Document processing status"""
    document_id: UUID4
    processing_status: str
    tier_1_complete: bool = False
    tier_2_complete: bool = False
    tier_3_complete: bool = False
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True
