"""
Mock patient data generator based on the 40-question onboarding questionnaire.

Questionnaire Structure (from Excel):
- Section 1-2: Demographics & Basic Info
- Section 3: Breast Cancer History
- Section 4: Family History
- Section 5: Symptoms & Physical Changes
- Section 6: Screening History
- Section 7: Lifestyle & Hormonal Factors
- Section 8: Medical History
- Section 9: Current Concerns
- Section 10: Infection/Inflammation
- Section 11: System Intelligence
"""

import uuid
from datetime import datetime, timedelta
import random


class MockPatientGenerator:
    """Generate realistic mock patient data"""
    
    FIRST_NAMES = ["Sarah", "Emily", "Jessica", "Maria", "Jennifer", "Lisa", "Michelle", "Amanda", "Rachel", "Sophia"]
    LAST_NAMES = ["Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Wilson"]
    
    @staticmethod
    def generate_low_risk_patient():
        """Generate a low-risk patient profile"""
        return {
            "patient_uuid": str(uuid.uuid4()),
            "demographic_data": {
                "name": f"{random.choice(MockPatientGenerator.FIRST_NAMES)} {random.choice(MockPatientGenerator.LAST_NAMES)}",
                "age": random.randint(30, 45),
                "gender": "female",
                "email": f"patient{random.randint(1000, 9999)}@example.com",
                "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            },
            "onboarding_questionnaire": {
                "demographics": {
                    "q1_age": random.randint(30, 45),
                    "q2_gender": "female"
                },
                "breast_cancer_history": {
                    "q1_previous_breast_cancer": "no",
                    "q2_previous_diagnosis_date": None,
                    "q3_treatment_received": None
                },
                "family_history": {
                    "q6_family_history": "no",
                    "q7_which_relatives": None,
                    "q8_age_at_diagnosis": None,
                    "q9_brca_mutation": "no"
                },
                "symptoms": {
                    "q14_new_lump": "no",
                    "q15_breast_pain": "none",
                    "q16_nipple_changes": "no",
                    "q17_nipple_discharge": "no",
                    "q18_discharge_type": None,
                    "q19_skin_changes": "no",
                    "q20_breast_size_change": "no"
                },
                "screening_history": {
                    "q22_last_mammogram": (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d"),
                    "q23_mammogram_results": "normal",
                    "q24_breast_density": "scattered_fibroglandular",
                    "q25_other_imaging": "no"
                },
                "lifestyle": {
                    "q26_hormone_therapy": "no",
                    "q27_pregnancy_history": "yes",
                    "q28_breastfeeding": "yes",
                    "q29_alcohol_consumption": "occasional",
                    "q30_smoking": "no"
                },
                "medical_history": {
                    "q31_other_cancers": "no",
                    "q32_radiation_exposure": "no",
                    "q33_benign_breast_disease": "no"
                },
                "current_concerns": {
                    "q34_recent_changes": "no",
                    "q35_concerns": "routine_checkup",
                    "q36_duration": None
                },
                "infection": {
                    "q37_mastitis": "no",
                    "q38_redness_fever": "no"
                },
                "system_intelligence": {
                    "q39_intuition": "no",
                    "q40_booking_assistance": "yes"
                }
            },
            "created_at": datetime.now().isoformat(),
            "last_rag_refresh": None
        }
    
    @staticmethod
    def generate_medium_risk_patient():
        """Generate a medium-risk patient profile"""
        return {
            "patient_uuid": str(uuid.uuid4()),
            "demographic_data": {
                "name": f"{random.choice(MockPatientGenerator.FIRST_NAMES)} {random.choice(MockPatientGenerator.LAST_NAMES)}",
                "age": random.randint(45, 60),
                "gender": "female",
                "email": f"patient{random.randint(1000, 9999)}@example.com",
                "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            },
            "onboarding_questionnaire": {
                "demographics": {
                    "q1_age": random.randint(45, 60),
                    "q2_gender": "female"
                },
                "breast_cancer_history": {
                    "q1_previous_breast_cancer": "no",
                    "q2_previous_diagnosis_date": None,
                    "q3_treatment_received": None
                },
                "family_history": {
                    "q6_family_history": "yes",
                    "q7_which_relatives": "aunt",  # 2nd degree relative
                    "q8_age_at_diagnosis": 55,
                    "q9_brca_mutation": "unknown"
                },
                "symptoms": {
                    "q14_new_lump": "no",
                    "q15_breast_pain": "localized",  # Medium risk marker
                    "q16_nipple_changes": "no",
                    "q17_nipple_discharge": "no",
                    "q18_discharge_type": None,
                    "q19_skin_changes": "no",
                    "q20_breast_size_change": "no"
                },
                "screening_history": {
                    "q22_last_mammogram": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
                    "q23_mammogram_results": "normal",
                    "q24_breast_density": "heterogeneously_dense",  # Medium risk marker
                    "q25_other_imaging": "no"
                },
                "lifestyle": {
                    "q26_hormone_therapy": "yes",  # Medium risk marker
                    "q27_pregnancy_history": "yes",
                    "q28_breastfeeding": "no",
                    "q29_alcohol_consumption": "moderate",
                    "q30_smoking": "former"
                },
                "medical_history": {
                    "q31_other_cancers": "no",
                    "q32_radiation_exposure": "no",
                    "q33_benign_breast_disease": "yes"  # Medium risk marker
                },
                "current_concerns": {
                    "q34_recent_changes": "yes",
                    "q35_concerns": "breast_pain",
                    "q36_duration": "2_months"
                },
                "infection": {
                    "q37_mastitis": "no",
                    "q38_redness_fever": "no"
                },
                "system_intelligence": {
                    "q39_intuition": "no",
                    "q40_booking_assistance": "yes"
                }
            },
            "created_at": datetime.now().isoformat(),
            "last_rag_refresh": None
        }
    
    @staticmethod
    def generate_high_risk_patient():
        """Generate a high-risk patient profile"""
        return {
            "patient_uuid": str(uuid.uuid4()),
            "demographic_data": {
                "name": f"{random.choice(MockPatientGenerator.FIRST_NAMES)} {random.choice(MockPatientGenerator.LAST_NAMES)}",
                "age": random.randint(40, 65),
                "gender": "female",
                "email": f"patient{random.randint(1000, 9999)}@example.com",
                "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            },
            "onboarding_questionnaire": {
                "demographics": {
                    "q1_age": random.randint(40, 65),
                    "q2_gender": "female"
                },
                "breast_cancer_history": {
                    "q1_previous_breast_cancer": "no",
                    "q2_previous_diagnosis_date": None,
                    "q3_treatment_received": None
                },
                "family_history": {
                    "q6_family_history": "yes",
                    "q7_which_relatives": "mother_and_sister",  # Strong family history - HIGH RISK
                    "q8_age_at_diagnosis": 42,
                    "q9_brca_mutation": "yes"  # HIGH RISK
                },
                "symptoms": {
                    "q14_new_lump": "yes",  # HIGH RISK
                    "q15_breast_pain": "none",
                    "q16_nipple_changes": "yes",  # HIGH RISK
                    "q17_nipple_discharge": "yes",
                    "q18_discharge_type": "bloody",  # HIGH RISK
                    "q19_skin_changes": "dimpling",  # HIGH RISK
                    "q20_breast_size_change": "yes"
                },
                "screening_history": {
                    "q22_last_mammogram": (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),
                    "q23_mammogram_results": "abnormal_needs_followup",
                    "q24_breast_density": "extremely_dense",
                    "q25_other_imaging": "yes"
                },
                "lifestyle": {
                    "q26_hormone_therapy": "yes",
                    "q27_pregnancy_history": "no",  # Nulliparity - risk factor
                    "q28_breastfeeding": "no",
                    "q29_alcohol_consumption": "regular",
                    "q30_smoking": "current"
                },
                "medical_history": {
                    "q31_other_cancers": "no",
                    "q32_radiation_exposure": "yes",  # HIGH RISK
                    "q33_benign_breast_disease": "yes"
                },
                "current_concerns": {
                    "q34_recent_changes": "yes",
                    "q35_concerns": "new_lump_and_discharge",
                    "q36_duration": "1_month"
                },
                "infection": {
                    "q37_mastitis": "no",
                    "q38_redness_fever": "no"
                },
                "system_intelligence": {
                    "q39_intuition": "yes",  # Patient feels something is wrong
                    "q40_booking_assistance": "yes"
                }
            },
            "created_at": datetime.now().isoformat(),
            "last_rag_refresh": None
        }
    
    @staticmethod
    def generate_patients(count=15):
        """Generate a mix of low, medium, and high risk patients"""
        patients = []
        
        # Generate distribution: 60% low, 30% medium, 10% high
        low_count = int(count * 0.6)
        medium_count = int(count * 0.3)
        high_count = count - low_count - medium_count
        
        for _ in range(low_count):
            patients.append(MockPatientGenerator.generate_low_risk_patient())
        
        for _ in range(medium_count):
            patients.append(MockPatientGenerator.generate_medium_risk_patient())
        
        for _ in range(high_count):
            patients.append(MockPatientGenerator.generate_high_risk_patient())
        
        return patients


if __name__ == "__main__":
    # Test generation
    patients = MockPatientGenerator.generate_patients(15)
    print(f"Generated {len(patients)} mock patients")
    for i, patient in enumerate(patients[:3], 1):
        print(f"\nPatient {i}:")
        print(f"  Name: {patient['demographic_data']['name']}")
        print(f"  Age: {patient['demographic_data']['age']}")
        print(f"  New Lump: {patient['onboarding_questionnaire']['symptoms']['q14_new_lump']}")
        print(f"  Family History: {patient['onboarding_questionnaire']['family_history']['q6_family_history']}")
        print(f"  BRCA Mutation: {patient['onboarding_questionnaire']['family_history']['q9_brca_mutation']}")
