"""
Unit tests for health scoring service.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid

from app.database import Base
from app.models import Patient, MedicalDocument
from app.services.health_scoring import calculate_health_score


# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_health.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def db_session():
    """Create test database session"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_health_score_low_risk_patient(db_session):
    """Test health score calculation for low risk patient"""
    # Create low risk patient
    patient = Patient(
        patient_uuid=uuid.uuid4(),
        demographic_data={"name": "Low Risk", "age": 35},
        onboarding_questionnaire={
            "screening_history": {"q22_last_mammogram": "within_1_year"},
            "lifestyle_factors": {"q29_alcohol_consumption": "no"},
            "symptoms": {"q14_new_lump": "no"},
            "family_history": {"q6_family_history": "no"}
        }
    )
    db_session.add(patient)
    db_session.commit()
    
    # Calculate score
    result = calculate_health_score(str(patient.patient_uuid), db_session)
    
    assert result["overall_score"] >= 70
    assert "component_scores" in result
    assert result["component_scores"]["screening_compliance"]["score"] == 100


def test_health_score_high_risk_patient(db_session):
    """Test health score calculation for high risk patient"""
    # Create high risk patient
    patient = Patient(
        patient_uuid=uuid.uuid4(),
        demographic_data={"name": "High Risk", "age": 55},
        onboarding_questionnaire={
            "screening_history": {"q22_last_mammogram": "never"},
            "lifestyle_factors": {"q29_alcohol_consumption": "yes"},
            "symptoms": {"q14_new_lump": "yes"},
            "family_history": {"q6_family_history": "yes"}
        }
    )
    db_session.add(patient)
    db_session.commit()
    
    # Calculate score
    result = calculate_health_score(str(patient.patient_uuid), db_session)
    
    assert result["overall_score"] < 70
    assert result["component_scores"]["screening_compliance"]["score"] == 30


def test_health_score_with_documents(db_session):
    """Test health score increases with more medical documents"""
    # Create patient
    patient = Patient(
        patient_uuid=uuid.uuid4(),
        demographic_data={"name": "Doc Test", "age": 40},
        onboarding_questionnaire={
            "screening_history": {"q22_last_mammogram": "within_1_year"},
            "symptoms": {"q14_new_lump": "no"}
        }
    )
    db_session.add(patient)
    db_session.commit()
    
    # Add documents
    for i in range(3):
        doc = MedicalDocument(
            document_id=uuid.uuid4(),
            patient_uuid=patient.patient_uuid,
            file_path=f"/test/doc{i}.pdf",
            original_filename=f"doc{i}.pdf"
        )
        db_session.add(doc)
    db_session.commit()
    
    # Calculate score
    result = calculate_health_score(str(patient.patient_uuid), db_session)
    
    # Should have high score for regular health tests
    assert result["component_scores"]["regular_health_tests"]["score"] == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
