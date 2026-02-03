from sqlalchemy import Column, String, DateTime, JSON, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import uuid


class HealthScore(Base):
    """Health and wellness score model"""
    __tablename__ = "health_scores"
    
    score_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_uuid = Column(UUID(as_uuid=True), ForeignKey("patients.patient_uuid"), nullable=False, index=True)
    
    # Overall score (0-100)
    overall_score = Column(Integer, nullable=False)
    trend = Column(String(10), nullable=True)  # e.g., "+5", "-3"
    
    # Component scores stored as JSONB
    # Structure: {"screening_compliance": {"score": 85, "status": "good", ...}, ...}
    component_scores = Column(JSON, nullable=False, default=dict)
    
    # Version tracking for history
    version = Column(Integer, nullable=False, default=1)
    
    # Timestamps
    calculated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<HealthScore {self.patient_uuid}: {self.overall_score}/100>"


class RiskAssessment(Base):
    """Risk assessment model"""
    __tablename__ = "risk_assessments"
    
    assessment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_uuid = Column(UUID(as_uuid=True), ForeignKey("patients.patient_uuid"), nullable=False, index=True)
    
    # Overall risk level
    overall_risk = Column(String(20), nullable=False)  # HIGH, MEDIUM, LOW
    
    # Risk markers categorized by level (stored as JSONB)
    # Structure: {"high_risk": [...], "medium_risk": [...], "low_risk": [...]}
    risk_markers = Column(JSON, nullable=False, default=dict)
    
    # Recommendations
    recommendations = Column(String(1000), nullable=True)
    urgency = Column(String(20), nullable=True)  # HIGH, MEDIUM, LOW
    
    # Version tracking
    version = Column(Integer, nullable=False, default=1)
    
    # Timestamps
    assessed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<RiskAssessment {self.patient_uuid}: {self.overall_risk}>"
