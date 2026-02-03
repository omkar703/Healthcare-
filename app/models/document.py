from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.sql import func
from app.database import Base
import uuid
import enum


class DocumentType(str, enum.Enum):
    """Types of medical documents"""
    LAB_REPORT = "lab_report"
    IMAGING = "imaging"
    PRESCRIPTION = "prescription"
    CONSULTATION_NOTE = "consultation_note"
    CREDENTIAL = "credential"  # For doctor credentials
    OTHER = "other"


class ProcessingStatus(str, enum.Enum):
    """Document processing status through 3-tier pipeline"""
    UPLOADED = "UPLOADED"
    INGESTED = "INGESTED"  # Tier 1 complete
    ANALYZING = "ANALYZING"  # Tier 2 in progress
    INDEXED = "INDEXED"  # Tier 3 complete
    FAILED = "FAILED"


class MedicalDocument(Base):
    """Medical document model with 3-tier processing results"""
    __tablename__ = "medical_documents"
    
    document_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Owner (patient or doctor)
    patient_uuid = Column(UUID(as_uuid=True), ForeignKey("patients.patient_uuid"), nullable=True, index=True)
    doctor_uuid = Column(UUID(as_uuid=True), ForeignKey("doctors.doctor_uuid"), nullable=True, index=True)
    
    # File storage (local filesystem path instead of S3)
    file_path = Column(String(512), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    
    # Document metadata
    document_type = Column(SQLEnum(DocumentType), nullable=False, default=DocumentType.OTHER)
    processing_status = Column(SQLEnum(ProcessingStatus), nullable=False, default=ProcessingStatus.UPLOADED)
    
    # Tier 1: Raw text extraction
    tier_1_text = Column(Text, nullable=True)
    tier_1_completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Tier 2: Vision analysis and enrichment
    tier_2_enriched = Column(JSON, nullable=True, default=dict)
    tier_2_completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Tier 3: Indexing status
    tier_3_indexed = Column(Boolean, default=False)
    tier_3_completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    upload_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<MedicalDocument {self.document_id} ({self.processing_status})>"
