"""
Unit tests for risk assessment service.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid

from app.database import Base
from app.models import Patient
from app.services.risk_assessment import calculate_risk_assessment


# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_risk.db"
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


def test_high_risk_assessment(db_session):
    """Test HIGH risk assessment with multiple high-risk markers"""
    patient = Patient(
        patient_uuid=uuid.uuid4(),
        demographic_data={"name": "High Risk", "age": 50},
        onboarding_questionnaire={
            "symptoms": {
                "q14_new_lump": "yes",
                "q17_nipple_discharge": "yes",
                "q18_discharge_type": "bloody",
                "q19_skin_changes": "dimpling"
            },
            "family_history": {
                "q6_family_history": "yes",
                "q7_which_relatives": "mother, sister",
                "q9_brca_mutation": "yes"
            },
            "medical_history": {
                "q32_chest_radiation": "yes"
            }
        }
    )
    db_session.add(patient)
    db_session.commit()
    
    result = calculate_risk_assessment(str(patient.patient_uuid), db_session)
    
    assert result["overall_risk"] == "HIGH"
    assert result["urgency"] == "HIGH"
    assert len(result["risk_markers"]["high_risk"]) >= 3
    assert "URGENT" in result["recommendations"]


def test_medium_risk_assessment(db_session):
    """Test MEDIUM risk assessment"""
    patient = Patient(
        patient_uuid=uuid.uuid4(),
        demographic_data={"name": "Medium Risk", "age": 45},
        onboarding_questionnaire={
            "symptoms": {
                "q14_new_lump": "no"
            },
            "family_history": {
                "q6_family_history": "yes",
                "q7_which_relatives": "aunt"
            },
            "screening_history": {
                "q24_breast_density": "heterogeneously_dense"
            },
            "lifestyle_factors": {
                "q28_hormone_therapy": "yes"
            }
        }
    )
    db_session.add(patient)
    db_session.commit()
    
    result = calculate_risk_assessment(str(patient.patient_uuid), db_session)
    
    assert result["overall_risk"] == "MEDIUM"
    assert len(result["risk_markers"]["medium_risk"]) >= 2
    assert "Annual mammogram" in result["recommendations"]


def test_low_risk_assessment(db_session):
    """Test LOW risk assessment"""
    patient = Patient(
        patient_uuid=uuid.uuid4(),
        demographic_data={"name": "Low Risk", "age": 35},
        onboarding_questionnaire={
            "symptoms": {
                "q14_new_lump": "no",
                "q17_nipple_discharge": "no"
            },
            "family_history": {
                "q6_family_history": "no",
                "q9_brca_mutation": "no"
            },
            "medical_history": {
                "q32_chest_radiation": "no"
            }
        }
    )
    db_session.add(patient)
    db_session.commit()
    
    result = calculate_risk_assessment(str(patient.patient_uuid), db_session)
    
    assert result["overall_risk"] == "LOW"
    assert result["urgency"] == "LOW"
    assert len(result["risk_markers"]["high_risk"]) == 0
    assert "routine" in result["recommendations"].lower()


def test_risk_markers_detection(db_session):
    """Test specific risk marker detection"""
    patient = Patient(
        patient_uuid=uuid.uuid4(),
        demographic_data={"name": "Marker Test", "age": 48},
        onboarding_questionnaire={
            "symptoms": {
                "q14_new_lump": "yes"
            },
            "family_history": {
                "q9_brca_mutation": "yes"
            }
        }
    )
    db_session.add(patient)
    db_session.commit()
    
    result = calculate_risk_assessment(str(patient.patient_uuid), db_session)
    
    high_risk_markers = result["risk_markers"]["high_risk"]
    assert any("lump" in marker.lower() for marker in high_risk_markers)
    assert any("BRCA" in marker for marker in high_risk_markers)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
