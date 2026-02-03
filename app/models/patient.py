from sqlalchemy import Column, String, DateTime, JSON, Integer, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import uuid
import enum


class VerificationStatus(str, enum.Enum):
    """Doctor verification status"""
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class Patient(Base):
    """Patient model with onboarding questionnaire data"""
    __tablename__ = "patients"
    
    patient_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Demographic data stored as JSONB
    demographic_data = Column(JSON, nullable=False, default=dict)
    
    # Onboarding questionnaire responses (40 questions from Excel)
    # Structure: {"demographics": {...}, "breast_cancer_history": {...}, ...}
    onboarding_questionnaire = Column(JSON, nullable=False, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # RAG refresh tracking
    last_rag_refresh = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Patient {self.patient_uuid}>"


class Doctor(Base):
    """Doctor model with credential verification"""
    __tablename__ = "doctors"
    
    doctor_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Personal information
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    specialization = Column(String(255), nullable=True)
    
    # Credentials extracted from OCR (stored as JSONB)
    # Structure: {"universityName": "...", "degreeName": "...", "licenseNumber": "...", ...}
    credentials = Column(JSON, nullable=False, default=dict)
    
    # Verification status
    verification_status = Column(
        SQLEnum(VerificationStatus),
        nullable=False,
        default=VerificationStatus.PENDING
    )
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Doctor {self.name} ({self.verification_status})>"
