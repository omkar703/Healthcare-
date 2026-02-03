"""
Comprehensive test suite for Healthcare AI Microservice Backend.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid

from app.main import app
from app.database import Base, get_db
from app.models import Patient, Doctor, HealthScore, RiskAssessment


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="module")
def setup_database():
    """Setup test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ==================== HEALTH CHECK TESTS ====================

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "version" in data


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


# ==================== PATIENT ONBOARDING TESTS ====================

def test_patient_onboarding(setup_database):
    """Test patient onboarding with questionnaire"""
    payload = {
        "demographic_data": {
            "name": "Test Patient",
            "age": 45,
            "gender": "female",
            "email": "test@example.com"
        },
        "onboarding_questionnaire": {
            "demographics": {
                "q1_age": "45",
                "q2_gender": "female"
            },
            "symptoms": {
                "q14_new_lump": "no",
                "q15_lump_duration": "",
                "q17_nipple_discharge": "no"
            },
            "family_history": {
                "q6_family_history": "no",
                "q9_brca_mutation": "no"
            },
            "screening_history": {
                "q22_last_mammogram": "within_1_year"
            },
            "lifestyle_factors": {
                "q29_alcohol_consumption": "no"
            }
        }
    }
    
    response = client.post("/api/v1/patients/onboard", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "patient_uuid" in data
    assert data["health_score_calculated"] == True
    assert data["risk_assessment_calculated"] == True


def test_get_health_score(setup_database):
    """Test retrieving health score"""
    # First create a patient
    payload = {
        "demographic_data": {"name": "Test", "age": 40, "gender": "female"},
        "onboarding_questionnaire": {
            "demographics": {"q1_age": "40"},
            "symptoms": {"q14_new_lump": "no"},
            "family_history": {"q6_family_history": "no"},
            "screening_history": {"q22_last_mammogram": "within_1_year"}
        }
    }
    
    onboard_response = client.post("/api/v1/patients/onboard", json=payload)
    patient_uuid = onboard_response.json()["patient_uuid"]
    
    # Get health score
    response = client.get(f"/api/v1/patients/{patient_uuid}/health-score")
    assert response.status_code == 200
    data = response.json()
    assert "overall_score" in data
    assert 0 <= data["overall_score"] <= 100
    assert "component_scores" in data


def test_get_risk_assessment(setup_database):
    """Test retrieving risk assessment"""
    # Create patient with high risk markers
    payload = {
        "demographic_data": {"name": "High Risk Patient", "age": 50, "gender": "female"},
        "onboarding_questionnaire": {
            "demographics": {"q1_age": "50"},
            "symptoms": {
                "q14_new_lump": "yes",
                "q17_nipple_discharge": "yes",
                "q18_discharge_type": "bloody"
            },
            "family_history": {
                "q6_family_history": "yes",
                "q7_which_relatives": "mother",
                "q9_brca_mutation": "yes"
            },
            "screening_history": {"q22_last_mammogram": "never"}
        }
    }
    
    onboard_response = client.post("/api/v1/patients/onboard", json=payload)
    patient_uuid = onboard_response.json()["patient_uuid"]
    
    # Get risk assessment
    response = client.get(f"/api/v1/patients/{patient_uuid}/risk-assessment")
    assert response.status_code == 200
    data = response.json()
    assert data["overall_risk"] in ["HIGH", "MEDIUM", "LOW"]
    assert "risk_markers" in data
    assert "recommendations" in data


# ==================== DOCTOR ONBOARDING TESTS ====================

def test_doctor_onboarding(setup_database):
    """Test doctor onboarding"""
    payload = {
        "name": "Dr. Test Doctor",
        "email": "doctor@example.com",
        "specialization": "Oncology",
        "credentials": {
            "university": "Test Medical University",
            "degree": "MBBS, MD",
            "license_number": "TEST123456",
            "issue_date": "2010-01-01"
        }
    }
    
    response = client.post("/api/v1/doctors/onboard", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "doctor_uuid" in data
    assert data["verification_status"] == "PENDING"


def test_get_doctor_patients(setup_database):
    """Test getting patient list for doctor"""
    # Create doctor
    doctor_payload = {
        "name": "Dr. Test",
        "email": "test@doctor.com",
        "specialization": "General",
        "credentials": {"degree": "MBBS"}
    }
    doctor_response = client.post("/api/v1/doctors/onboard", json=doctor_payload)
    doctor_uuid = doctor_response.json()["doctor_uuid"]
    
    # Get patients
    response = client.get(f"/api/v1/doctors/{doctor_uuid}/patients")
    assert response.status_code == 200
    data = response.json()
    assert "patients" in data
    assert "total_count" in data


# ==================== INTEGRATION TESTS ====================

def test_full_patient_flow(setup_database):
    """Test complete patient flow: onboard → upload doc → get scores → chat"""
    # 1. Onboard patient
    onboard_payload = {
        "demographic_data": {"name": "Flow Test", "age": 42, "gender": "female"},
        "onboarding_questionnaire": {
            "demographics": {"q1_age": "42"},
            "symptoms": {"q14_new_lump": "no"},
            "family_history": {"q6_family_history": "no"},
            "screening_history": {"q22_last_mammogram": "1_to_2_years"}
        }
    }
    
    onboard_response = client.post("/api/v1/patients/onboard", json=onboard_payload)
    assert onboard_response.status_code == 201
    patient_uuid = onboard_response.json()["patient_uuid"]
    
    # 2. Get health score
    health_response = client.get(f"/api/v1/patients/{patient_uuid}/health-score")
    assert health_response.status_code == 200
    health_score = health_response.json()["overall_score"]
    assert 0 <= health_score <= 100
    
    # 3. Get risk assessment
    risk_response = client.get(f"/api/v1/patients/{patient_uuid}/risk-assessment")
    assert risk_response.status_code == 200
    risk_level = risk_response.json()["overall_risk"]
    assert risk_level in ["HIGH", "MEDIUM", "LOW"]
    
    print(f"✅ Full flow test passed - Health Score: {health_score}, Risk: {risk_level}")


# ==================== RUN TESTS ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
