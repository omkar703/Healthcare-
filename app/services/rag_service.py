"""
RAG (Retrieval-Augmented Generation) service for semantic search.
"""

from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models import DocumentChunk, Patient
from app.services.aws_bedrock import bedrock_service
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class RAGService:
    """RAG service for semantic search and context retrieval"""
    
    def __init__(self):
        self.bedrock = bedrock_service
    
    def semantic_search(
        self,
        query: str,
        patient_uuid: str,
        db: Session,
        top_k: int = None
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        Perform semantic search using pgvector.
        
        Args:
            query: Search query
            patient_uuid: Patient UUID to search within
            db: Database session
            top_k: Number of results to return (default from settings)
            
        Returns:
            List of (chunk, similarity_score) tuples
        """
        try:
            if top_k is None:
                top_k = settings.TOP_K_PATIENT_CHAT
            
            # Generate embedding for query
            query_embedding = self.bedrock.generate_embedding(query)
            
            # Convert embedding to PostgreSQL array format
            embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
            
            # Perform vector similarity search using cosine distance
            sql = text("""
                SELECT 
                    chunk_id,
                    chunk_text,
                    metadata,
                    1 - (embedding <=> :query_embedding::vector) as similarity
                FROM document_chunks
                WHERE patient_uuid = :patient_uuid
                ORDER BY embedding <=> :query_embedding::vector
                LIMIT :top_k
            """)
            
            result = db.execute(
                sql,
                {
                    "query_embedding": embedding_str,
                    "patient_uuid": str(patient_uuid),
                    "top_k": top_k
                }
            )
            
            # Fetch chunks with similarity scores
            chunks_with_scores = []
            for row in result:
                chunk = db.query(DocumentChunk).filter(
                    DocumentChunk.chunk_id == row.chunk_id
                ).first()
                if chunk:
                    chunks_with_scores.append((chunk, row.similarity))
            
            logger.info(f"Found {len(chunks_with_scores)} relevant chunks for query")
            return chunks_with_scores
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            raise
    
    def get_context_for_chat(
        self,
        query: str,
        patient_uuid: str,
        db: Session,
        is_doctor: bool = False
    ) -> Dict[str, Any]:
        """
        Get relevant context for chat query.
        
        Args:
            query: User query
            patient_uuid: Patient UUID
            db: Database session
            is_doctor: Whether this is a doctor chat (uses higher top_k)
            
        Returns:
            Dict with context chunks and metadata
        """
        try:
            # Determine top_k based on user type
            top_k = settings.TOP_K_DOCTOR_CHAT if is_doctor else settings.TOP_K_PATIENT_CHAT
            
            # Perform semantic search
            chunks_with_scores = self.semantic_search(
                query=query,
                patient_uuid=patient_uuid,
                db=db,
                top_k=top_k
            )
            
            # Prepare context
            context_chunks = []
            source_documents = set()
            chunk_ids = []
            
            for chunk, similarity in chunks_with_scores:
                context_chunks.append({
                    'chunk_id': str(chunk.chunk_id),
                    'text': chunk.chunk_text,
                    'similarity': float(similarity),
                    'chunk_metadata': chunk.chunk_metadata
                })
                
                # Track source documents
                if chunk.chunk_metadata and 'document_id' in chunk.chunk_metadata:
                    source_documents.add(chunk.chunk_metadata['document_id'])
                
                chunk_ids.append(str(chunk.chunk_id))
            
            # Combine context text
            combined_context = '\n\n---\n\n'.join([
                f"[Document Excerpt {i+1}]\n{c['text']}"
                for i, c in enumerate(context_chunks)
            ])
            
            return {
                'context_text': combined_context,
                'chunks': context_chunks,
                'source_documents': list(source_documents),
                'chunk_ids': chunk_ids,
                'total_chunks': len(context_chunks)
            }
            
        except Exception as e:
            logger.error(f"Error getting context for chat: {e}")
            raise
    
    def refresh_patient_index(self, patient_uuid: str, db: Session):
        """
        Trigger RAG index refresh for a patient.
        
        Args:
            patient_uuid: Patient UUID
            db: Database session
        """
        try:
            # Import here to avoid circular dependency
            from app.tasks.rag_tasks import refresh_patient_rag
            
            # Trigger async refresh
            task = refresh_patient_rag.delay(str(patient_uuid))
            
            logger.info(f"Triggered RAG refresh for patient: {patient_uuid}, task_id: {task.id}")
            
            return {
                "status": "accepted",
                "task_id": task.id,
                "patient_uuid": str(patient_uuid)
            }
            
        except Exception as e:
            logger.error(f"Error triggering RAG refresh: {e}")
            raise


# Global instance
rag_service = RAGService()
