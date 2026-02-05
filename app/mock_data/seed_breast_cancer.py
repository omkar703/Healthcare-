import uuid
import json
import sys
from sqlalchemy import text
from app.database import engine

def seed_breast_cancer_mock_data():
    primary_pid = "66c9a8f1-2a1b-9c00-9876-543298765432"
    patient_ids = [primary_pid] + [str(uuid.uuid4()) for _ in range(9)]
    
    with engine.connect() as conn:
        for i, pid_str in enumerate(patient_ids):
            print(f"[{i+1}/10] Seeding patient: {pid_str}")
            sys.stdout.flush()
            
            # Mock data bits
            age = 40 + i
            risk_score = 70 + (i * 3) % 30
            risk_level = "HIGH" if risk_score > 80 else "MODERATE" if risk_score > 60 else "LOW"

            screening_data = {
                "patientId": pid_str,
                "screeningHistory": {
                    "age": age,
                    "previousScreening": ["MAMMOGRAM", "ULTRASOUND"],
                    "lastScreeningDate": "2023-10-12",
                    "denseBreastTissue": True,
                    "priorBreastCondition": ["ATYPICAL_HYPERPLASIA"],
                },
                "familyGeneticRisk": {
                    "firstDegreeRelativeBreastCancer": True,
                    "familyOtherCancers": True,
                    "knownBRCAMutation": True,
                    "relativeBefore50": True,
                },
                "currentSymptoms": {
                    "newLump": True,
                    "hardOrFixedLump": True,
                    "increasingSize": True,
                    "localizedPain": True,
                    "persistentPain": True,
                },
                "skinNippleChanges": {
                    "skinChanges": ["DIMPLING", "PEAU_D_ORANGE"],
                    "nippleInversion": True,
                    "nippleDischargeType": "BLOODY",
                    "dischargeOneSide": True,
                    "nippleSoresOrCrusting": True,
                },
                "shapeSizeChanges": {
                    "sizeOrShapeChange": True,
                    "asymmetry": True,
                    "swelling": True,
                },
                "hormonalHistory": {
                    "menarcheAge": 11,
                    "menopause": False,
                    "everPregnant": True,
                    "ageFirstFullTermPregnancy": 32,
                    "usedHRT": False,
                    "longTermOCPUse": True,
                },
                "lifestyle": {
                    "alcoholUse": True,
                    "exerciseFrequency": "LOW",
                    "heightCm": 158,
                    "weightKg": 74,
                    "tobaccoUse": True,
                },
                "priorCancerRadiation": {
                    "chestRadiationBefore30": True,
                    "previousCancer": True,
                },
                "infectionHistory": {
                    "currentlyBreastfeeding": False,
                    "recentMastitis": False,
                    "rednessWithFever": False,
                },
                "systemEscalation": {
                    "patientConcernDespiteNormalTests": True,
                    "wantsDoctorConsultation": True,
                },
                "riskScore": risk_score,
                "riskLevel": risk_level,
            }

            try:
                # Use raw SQL to avoid SQLAlchemy state issues
                with conn.begin():
                    conn.execute(text("DELETE FROM health_scores WHERE patient_uuid = :pid"), {"pid": pid_str})
                    conn.execute(text("DELETE FROM risk_assessments WHERE patient_uuid = :pid"), {"pid": pid_str})
                    conn.execute(text("DELETE FROM medical_documents WHERE patient_uuid = :pid"), {"pid": pid_str})
                    conn.execute(text("DELETE FROM patients WHERE patient_uuid = :pid"), {"pid": pid_str})
                    
                    conn.execute(text("""
                        INSERT INTO patients (patient_uuid, demographic_data, onboarding_questionnaire, breast_cancer_screening, created_at, updated_at)
                        VALUES (:pid, :demog, :onboard, :screening, now(), now())
                    """), {
                        "pid": pid_str,
                        "demog": json.dumps({"name": f"Mock Patient {i+1}", "age": age}),
                        "onboard": json.dumps({}),
                        "screening": json.dumps(screening_data)
                    })
                    
                    conn.execute(text("""
                        INSERT INTO risk_assessments (assessment_id, patient_uuid, overall_risk, risk_markers, recommendations, urgency, version, assessed_at)
                        VALUES (:aid, :pid, :risk, :markers, :recs, :urgency, 1, now())
                    """), {
                        "aid": str(uuid.uuid4()),
                        "pid": pid_str,
                        "risk": risk_level,
                        "markers": json.dumps({"score": risk_score}),
                        "recs": "Based on high risk score, manual clinical breast exam and diagnostic mammogram recommended.",
                        "urgency": "HIGH" if risk_level == "HIGH" else "MEDIUM"
                    })
                    
                    conn.execute(text("""
                        INSERT INTO health_scores (score_id, patient_uuid, overall_score, trend, component_scores, version, calculated_at)
                        VALUES (:sid, :pid, :score, '0', :components, 1, now())
                    """), {
                        "sid": str(uuid.uuid4()),
                        "pid": pid_str,
                        "score": max(0, 100 - risk_score),
                        "components": json.dumps({"risk_deduction": {"score": risk_score, "status": "critical", "details": "High cancer risk"}})
                    })
                
                print(f"   - Successfully seeded patient {i+1}")
                sys.stdout.flush()
            except Exception as e:
                # conn.rollback() # conn.begin() handles rollback
                print(f"   - Error seeding patient {i+1}: {e}")
                sys.stdout.flush()

    print("\nSeeding complete!")
    print(f"Primary Patient ID: {primary_pid}")

if __name__ == "__main__":
    seed_breast_cancer_mock_data()
