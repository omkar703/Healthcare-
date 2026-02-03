"""
Celery tasks for RAG system operations.
"""

from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models import Patient, MedicalDocument, DocumentChunk, HealthScore, RiskAssessment
from app.services.document_processor import document_processor
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="refresh_patient_rag")
def refresh_patient_rag(self, patient_uuid: str):
    """
    Refresh RAG index for a patient.
    Reprocesses all documents and recalculates health scores.
    
    Args:
        patient_uuid: UUID of the patient
    """
    db = SessionLocal()
    
    try:
        logger.info(f"Starting RAG refresh for patient: {patient_uuid}")
        
        # Get patient
        patient = db.query(Patient).filter(
            Patient.patient_uuid == patient_uuid
        ).first()
        
        if not patient:
            raise ValueError(f"Patient not found: {patient_uuid}")
        
        # Get all documents for patient
        documents = db.query(MedicalDocument).filter(
            MedicalDocument.patient_uuid == patient_uuid
        ).all()
        
        # Delete existing chunks
        db.query(DocumentChunk).filter(
            DocumentChunk.patient_uuid == patient_uuid
        ).delete()
        db.commit()
        
        logger.info(f"Deleted existing chunks for patient: {patient_uuid}")
        
        # Reprocess each document through Tier 3
        total_chunks = 0
        for document in documents:
            if document.tier_1_text and document.tier_2_enriched:
                chunks_data = document_processor.process_tier_3(
                    text=document.tier_1_text,
                    enriched_data=document.tier_2_enriched,
                    document_id=str(document.document_id),
                    patient_uuid=str(patient_uuid)
                )
                
                # Store chunks
                for chunk_data in chunks_data:
                    chunk = DocumentChunk(
                        patient_uuid=patient_uuid,
                        document_id=document.document_id,
                        chunk_text=chunk_data['chunk_text'],
                        chunk_index=chunk_data['chunk_index'],
                        embedding=chunk_data['embedding'],
                        metadata=chunk_data['metadata']
                    )
                    db.add(chunk)
                
                total_chunks += len(chunks_data)
        
        db.commit()
        
        # Update patient's last RAG refresh timestamp
        patient.last_rag_refresh = datetime.utcnow()
        db.commit()
        
        logger.info(f"RAG refresh complete for patient: {patient_uuid}, created {total_chunks} chunks")
        
        # Trigger health score recalculation
        recalculate_health_score.delay(patient_uuid)
        
        # Trigger risk assessment recalculation
        recalculate_risk_assessment.delay(patient_uuid)
        
        return {
            "status": "success",
            "patient_uuid": patient_uuid,
            "total_chunks": total_chunks,
            "documents_processed": len(documents)
        }
        
    except Exception as e:
        logger.error(f"Error in RAG refresh: {e}")
        raise
        
    finally:
        db.close()


@celery_app.task(bind=True, name="recalculate_health_score")
def recalculate_health_score(self, patient_uuid: str):
    """
    Recalculate health score for a patient.
    
    Args:
        patient_uuid: UUID of the patient
    """
    db = SessionLocal()
    
    try:
        logger.info(f"Recalculating health score for patient: {patient_uuid}")
        
        # Import here to avoid circular dependency
        from app.services.health_scoring import calculate_health_score
        
        # Calculate new health score
        health_score_data = calculate_health_score(patient_uuid, db)
        
        # Get current version
        latest_score = db.query(HealthScore).filter(
            HealthScore.patient_uuid == patient_uuid
        ).order_by(HealthScore.version.desc()).first()
        
        new_version = (latest_score.version + 1) if latest_score else 1
        
        # Create new health score record
        health_score = HealthScore(
            patient_uuid=patient_uuid,
            overall_score=health_score_data['overall_score'],
            trend=health_score_data.get('trend', '0'),
            component_scores=health_score_data['component_scores'],
            version=new_version
        )
        db.add(health_score)
        db.commit()
        
        logger.info(f"Health score recalculated: {health_score_data['overall_score']}/100")
        
        return {
            "status": "success",
            "patient_uuid": patient_uuid,
            "overall_score": health_score_data['overall_score']
        }
        
    except Exception as e:
        logger.error(f"Error recalculating health score: {e}")
        raise
        
    finally:
        db.close()


@celery_app.task(bind=True, name="recalculate_risk_assessment")
def recalculate_risk_assessment(self, patient_uuid: str):
    """
    Recalculate risk assessment for a patient.
    
    Args:
        patient_uuid: UUID of the patient
    """
    db = SessionLocal()
    
    try:
        logger.info(f"Recalculating risk assessment for patient: {patient_uuid}")
        
        # Import here to avoid circular dependency
        from app.services.risk_assessment import calculate_risk_assessment
        
        # Calculate new risk assessment
        risk_data = calculate_risk_assessment(patient_uuid, db)
        
        # Get current version
        latest_assessment = db.query(RiskAssessment).filter(
            RiskAssessment.patient_uuid == patient_uuid
        ).order_by(RiskAssessment.version.desc()).first()
        
        new_version = (latest_assessment.version + 1) if latest_assessment else 1
        
        # Create new risk assessment record
        risk_assessment = RiskAssessment(
            patient_uuid=patient_uuid,
            overall_risk=risk_data['overall_risk'],
            risk_markers=risk_data['risk_markers'],
            recommendations=risk_data.get('recommendations', ''),
            urgency=risk_data.get('urgency', 'LOW'),
            version=new_version
        )
        db.add(risk_assessment)
        db.commit()
        
        logger.info(f"Risk assessment recalculated: {risk_data['overall_risk']}")
        
        return {
            "status": "success",
            "patient_uuid": patient_uuid,
            "overall_risk": risk_data['overall_risk']
        }
        
    except Exception as e:
        logger.error(f"Error recalculating risk assessment: {e}")
        raise
        
    finally:
        db.close()
