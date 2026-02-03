from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import uuid


class PatientConversation(Base):
    """Patient chat conversation model"""
    __tablename__ = "patient_conversations"
    
    conversation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_uuid = Column(UUID(as_uuid=True), ForeignKey("patients.patient_uuid"), nullable=False, index=True)
    
    # Messages array stored as JSONB
    # Structure: [{"role": "user", "content": "...", "timestamp": "..."}, ...]
    messages = Column(JSON, nullable=False, default=list)
    
    # RAG context chunk IDs used in this conversation
    rag_context_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=False, default=list)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<PatientConversation {self.conversation_id}>"


class DoctorConversation(Base):
    """Doctor chat conversation model (per patient)"""
    __tablename__ = "doctor_conversations"
    
    conversation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    doctor_uuid = Column(UUID(as_uuid=True), ForeignKey("doctors.doctor_uuid"), nullable=False, index=True)
    patient_uuid = Column(UUID(as_uuid=True), ForeignKey("patients.patient_uuid"), nullable=False, index=True)
    
    # Messages array stored as JSONB
    messages = Column(JSON, nullable=False, default=list)
    
    # Additional context provided by doctor
    additional_context = Column(String(2000), nullable=True)
    
    # RAG context chunk IDs used
    rag_context_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=False, default=list)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<DoctorConversation {self.conversation_id} (Doctor: {self.doctor_uuid}, Patient: {self.patient_uuid})>"
