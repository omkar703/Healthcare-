from sqlalchemy import Column, String, DateTime, JSON, Text, ForeignKey, Integer, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.database import Base
from app.config import settings
import uuid


class DocumentChunk(Base):
    """Document chunks with embeddings for RAG system"""
    __tablename__ = "document_chunks"
    
    chunk_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # References
    patient_uuid = Column(UUID(as_uuid=True), ForeignKey("patients.patient_uuid"), nullable=False, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("medical_documents.document_id"), nullable=False, index=True)
    
    # Chunk data
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Position in document
    
    # Embedding vector (1536 dimensions for Claude/Titan)
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION), nullable=False)
    
    # Metadata (tags, dates, risk markers, etc.)
    chunk_metadata = Column(JSON, nullable=False, default=dict)  # Renamed from 'metadata' to avoid SQLAlchemy reserved name
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<DocumentChunk {self.chunk_id} for patient {self.patient_uuid}>"


# Create index for vector similarity search
Index(
    'ix_document_chunks_embedding',
    DocumentChunk.embedding,
    postgresql_using='ivfflat',
    postgresql_with={'lists': 100},
    postgresql_ops={'embedding': 'vector_cosine_ops'}
)
