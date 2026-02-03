"""
Celery tasks for asynchronous document processing.
"""

from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models import MedicalDocument, ProcessingStatus, DocumentChunk
from app.services.document_processor import document_processor
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="process_document_tier_2")
def process_document_tier_2(self, document_id: str):
    """
    Celery task for Tier 2 processing: Vision analysis and enrichment.
    
    Args:
        document_id: UUID of the document to process
    """
    db = SessionLocal()
    
    try:
        logger.info(f"Starting Tier 2 processing for document: {document_id}")
        
        # Get document from database
        document = db.query(MedicalDocument).filter(
            MedicalDocument.document_id == document_id
        ).first()
        
        if not document:
            raise ValueError(f"Document not found: {document_id}")
        
        # Update status
        document.processing_status = ProcessingStatus.ANALYZING
        db.commit()
        
        # Process Tier 2
        enriched_data = document_processor.process_tier_2(
            file_path=document.file_path,
            tier_1_text=document.tier_1_text or "",
            mime_type=document.mime_type
        )
        
        # Update document with Tier 2 results
        document.tier_2_enriched = enriched_data
        document.tier_2_completed_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Tier 2 complete for document: {document_id}")
        
        # Trigger Tier 3 processing
        process_document_tier_3.delay(document_id)
        
        return {
            "status": "success",
            "document_id": document_id,
            "tier": 2
        }
        
    except Exception as e:
        logger.error(f"Error in Tier 2 processing: {e}")
        
        # Update document with error
        if document:
            document.processing_status = ProcessingStatus.FAILED
            document.error_message = str(e)
            db.commit()
        
        raise
        
    finally:
        db.close()


@celery_app.task(bind=True, name="process_document_tier_3")
def process_document_tier_3(self, document_id: str):
    """
    Celery task for Tier 3 processing: Chunking and vector indexing.
    
    Args:
        document_id: UUID of the document to process
    """
    db = SessionLocal()
    
    try:
        logger.info(f"Starting Tier 3 processing for document: {document_id}")
        
        # Get document from database
        document = db.query(MedicalDocument).filter(
            MedicalDocument.document_id == document_id
        ).first()
        
        if not document:
            raise ValueError(f"Document not found: {document_id}")
        
        # Get enriched data
        tier_1_text = document.tier_1_text or ""
        tier_2_enriched = document.tier_2_enriched or {}
        
        # Process Tier 3
        chunks_data = document_processor.process_tier_3(
            text=tier_1_text,
            enriched_data=tier_2_enriched,
            document_id=str(document.document_id),
            patient_uuid=str(document.patient_uuid)
        )
        
        # Store chunks in database
        for chunk_data in chunks_data:
            chunk = DocumentChunk(
                patient_uuid=document.patient_uuid,
                document_id=document.document_id,
                chunk_text=chunk_data['chunk_text'],
                chunk_index=chunk_data['chunk_index'],
                embedding=chunk_data['embedding'],
                metadata=chunk_data['metadata']
            )
            db.add(chunk)
        
        # Update document status
        document.tier_3_indexed = True
        document.tier_3_completed_at = datetime.utcnow()
        document.processing_status = ProcessingStatus.INDEXED
        db.commit()
        
        logger.info(f"Tier 3 complete for document: {document_id}, created {len(chunks_data)} chunks")
        
        return {
            "status": "success",
            "document_id": document_id,
            "tier": 3,
            "chunks_created": len(chunks_data)
        }
        
    except Exception as e:
        logger.error(f"Error in Tier 3 processing: {e}")
        
        # Update document with error
        if document:
            document.processing_status = ProcessingStatus.FAILED
            document.error_message = str(e)
            db.commit()
        
        raise
        
    finally:
        db.close()


@celery_app.task(bind=True, name="process_document_complete")
def process_document_complete(self, document_id: str, file_path: str, mime_type: str):
    """
    Complete document processing pipeline (Tier 1 → Tier 2 → Tier 3).
    
    Args:
        document_id: UUID of the document
        file_path: Path to the document file
        mime_type: MIME type of the document
    """
    db = SessionLocal()
    
    try:
        logger.info(f"Starting complete processing for document: {document_id}")
        
        # Get document from database
        document = db.query(MedicalDocument).filter(
            MedicalDocument.document_id == document_id
        ).first()
        
        if not document:
            raise ValueError(f"Document not found: {document_id}")
        
        # Tier 1: Extract text
        tier_1_text = document_processor.process_tier_1(file_path, mime_type)
        
        # Update document with Tier 1 results
        document.tier_1_text = tier_1_text
        document.tier_1_completed_at = datetime.utcnow()
        document.processing_status = ProcessingStatus.INGESTED
        db.commit()
        
        logger.info(f"Tier 1 complete for document: {document_id}")
        
        # Trigger Tier 2 processing asynchronously
        process_document_tier_2.delay(document_id)
        
        return {
            "status": "success",
            "document_id": document_id,
            "tier_1_complete": True
        }
        
    except Exception as e:
        logger.error(f"Error in complete processing: {e}")
        
        # Update document with error
        if document:
            document.processing_status = ProcessingStatus.FAILED
            document.error_message = str(e)
            db.commit()
        
        raise
        
    finally:
        db.close()
