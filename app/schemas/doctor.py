"""
Pydantic schemas for Doctor API requests and responses.
"""

from pydantic import BaseModel, Field, UUID4
from typing import Dict, Any, List, Optional
from datetime import datetime


# ==================== DOCTOR ONBOARDING ====================

class DoctorOnboardingRequest(BaseModel):
    """Doctor onboarding request with credentials"""
    name: str = Field(..., min_length=1, max_length=255)
    email: str
    specialization: str = Field(..., min_length=1, max_length=255)
    credentials: Dict[str, Any] = Field(
        ...,
        description="OCR-extracted credentials (university, degree, license, etc.)"
    )


class DoctorOnboardingResponse(BaseModel):
    """Doctor onboarding response"""
    doctor_uuid: UUID4
    name: str
    email: str
    verification_status: str  # PENDING, VERIFIED, REJECTED
    message: str
    
    class Config:
        from_attributes = True


# ==================== DOCTOR CHAT ====================

class DoctorChatRequest(BaseModel):
    """Doctor chat request (per patient)"""
    patient_uuid: UUID4
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: Optional[UUID4] = None
    additional_context: Optional[str] = None


class DoctorChatResponse(BaseModel):
    """Doctor chat response"""
    conversation_id: UUID4
    message: str
    sources: List[str] = []  # Source document IDs
    patient_summary: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


# ==================== PATIENT LIST ====================

class PatientSummary(BaseModel):
    """Patient summary for doctor view"""
    patient_uuid: UUID4
    name: str
    age: int
    overall_risk: Optional[str] = None
    health_score: Optional[int] = None
    last_updated: datetime
    
    class Config:
        from_attributes = True


class DoctorPatientsResponse(BaseModel):
    """List of patients accessible to doctor"""
    doctor_uuid: UUID4
    patients: List[PatientSummary]
    total_count: int
    
    class Config:
        from_attributes = True


# ==================== CREDENTIAL UPLOAD ====================

class CredentialUploadResponse(BaseModel):
    """Credential document upload response"""
    doctor_uuid: UUID4
    extracted_credentials: Dict[str, str]
    verification_status: str
    message: str
    
    class Config:
        from_attributes = True
