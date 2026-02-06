"""
Unified chat schemas for patient and doctor chatbots.
"""

from pydantic import BaseModel, Field, UUID4
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== ENUMS ====================

class UserType(str, Enum):
    """User type enum"""
    PATIENT = "patient"
    DOCTOR = "doctor"


class MessageRole(str, Enum):
    """Message role enum"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# ==================== MESSAGE SCHEMAS ====================

class ChatMessage(BaseModel):
    """Individual chat message"""
    role: MessageRole
    content: str
    timestamp: datetime
    sources: List[str] = []  # Document IDs used for RAG
    
    class Config:
        from_attributes = True


# ==================== PATIENT CHAT ====================

class PatientChatRequest(BaseModel):
    """Patient chat request"""
    message: str = Field(..., min_length=1, max_length=5000, description="Patient's question or message")
    conversation_id: Optional[UUID4] = Field(None, description="Existing conversation ID (optional)")


class PatientChatResponse(BaseModel):
    """Patient chat response"""
    conversation_id: UUID4
    message: str
    sources: List[str] = []  # Source document IDs
    is_emergency: bool = False  # Emergency detected
    is_complex: bool = False  # Complex query redirected to doctor
    guardrails_applied: List[str] = []  # List of guardrails that were applied
    
    class Config:
        from_attributes = True


# ==================== DOCTOR CHAT ====================

class DoctorGeneralChatRequest(BaseModel):
    """Doctor general chat request (like ChatGPT)"""
    message: str = Field(..., min_length=1, max_length=5000, description="Doctor's question or message")
    conversation_id: Optional[UUID4] = Field(None, description="Existing conversation ID (optional)")


class DoctorPatientChatRequest(BaseModel):
    """Doctor patient-specific chat request"""
    patient_uuid: UUID4 = Field(..., description="Patient UUID to discuss")
    message: str = Field(..., min_length=1, max_length=5000, description="Doctor's question about the patient")
    conversation_id: Optional[UUID4] = Field(None, description="Existing conversation ID (optional)")
    additional_context: Optional[str] = Field(None, description="Additional context from doctor")


class DoctorChatResponse(BaseModel):
    """Doctor chat response"""
    conversation_id: UUID4
    message: str
    sources: List[str] = []  # Source document IDs (for patient-specific chats)
    patient_summary: Optional[Dict[str, Any]] = None  # Patient summary (for patient-specific chats)
    
    class Config:
        from_attributes = True


# ==================== DOCUMENT UPLOAD ====================

class DocumentUploadRequest(BaseModel):
    """Document upload metadata"""
    patient_uuid: Optional[UUID4] = Field(None, description="Patient UUID (for doctor uploads)")
    document_type: Optional[str] = Field(None, description="Document type hint (e.g., 'lab_report', 'scan')")


class DocumentUploadResponse(BaseModel):
    """Document upload response"""
    document_id: UUID4
    patient_uuid: UUID4
    filename: str
    file_size_bytes: int
    mime_type: str
    processing_status: str
    message: str
    
    class Config:
        from_attributes = True


class DocumentStatusResponse(BaseModel):
    """Document processing status"""
    document_id: UUID4
    processing_status: str
    tier_1_complete: bool = False  # OCR/Text extraction
    tier_2_complete: bool = False  # Vision analysis
    tier_3_complete: bool = False  # RAG indexing
    error_message: Optional[str] = None
    processed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ==================== CONVERSATION HISTORY ====================

class ConversationSummary(BaseModel):
    """Conversation summary for list view"""
    conversation_id: UUID4
    title: Optional[str] = None
    message_count: int
    last_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ConversationDetail(BaseModel):
    """Full conversation with all messages"""
    conversation_id: UUID4
    user_uuid: UUID4
    user_type: UserType
    patient_uuid: Optional[UUID4] = None  # For doctor-patient chats
    title: Optional[str] = None
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ConversationHistoryResponse(BaseModel):
    """List of conversations"""
    conversations: List[ConversationSummary]
    total_count: int
    
    class Config:
        from_attributes = True


# ==================== DOCUMENT LIST ====================

class DocumentSummary(BaseModel):
    """Document summary for list view"""
    document_id: UUID4
    filename: str
    file_size_bytes: int
    mime_type: str
    document_type: str
    processing_status: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """List of documents"""
    documents: List[DocumentSummary]
    total_count: int
    
    class Config:
        from_attributes = True
