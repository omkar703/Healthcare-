"""
Mock medical document generator based on blood test markers from Excel.
"""

import uuid
from datetime import datetime, timedelta
import random


class MockDocumentGenerator:
    """Generate realistic mock medical documents"""
    
    @staticmethod
    def generate_lab_report_stage1(patient_name, patient_age):
        """Generate Stage 1 (Low Risk) lab report"""
        report_date = datetime.now() - timedelta(days=random.randint(30, 180))
        
        content = f"""
LABORATORY REPORT
=================

Patient Name: {patient_name}
Patient Age: {patient_age}
Report Date: {report_date.strftime("%B %d, %Y")}
Report Type: Comprehensive Blood Panel - Stage 1 (Routine Screening)

HEART MARKERS:
- Total Cholesterol: {random.randint(150, 200)} mg/dL (Normal: <200)
- HDL (Good Cholesterol): {random.randint(50, 70)} mg/dL (Normal: >40)
- LDL (Bad Cholesterol): {random.randint(80, 120)} mg/dL (Normal: <130)
- Triglycerides: {random.randint(80, 150)} mg/dL (Normal: <150)

INSULIN/GLUCOSE:
- Fasting Glucose: {random.randint(70, 100)} mg/dL (Normal: 70-100)
- HbA1c: {random.uniform(4.5, 5.6):.1f}% (Normal: <5.7%)

KIDNEY FUNCTION:
- Creatinine: {random.uniform(0.6, 1.2):.2f} mg/dL (Normal: 0.6-1.2)
- eGFR: {random.randint(90, 120)} mL/min (Normal: >90)
- Urea: {random.randint(15, 40)} mg/dL (Normal: 15-40)

LIVER FUNCTION:
- ALT: {random.randint(10, 40)} U/L (Normal: 7-56)
- ALP: {random.randint(40, 120)} U/L (Normal: 44-147)
- Bilirubin: {random.uniform(0.3, 1.0):.2f} mg/dL (Normal: 0.3-1.2)

BLOOD COUNT:
- Hemoglobin: {random.uniform(12.0, 16.0):.1f} g/dL (Normal: 12-16)
- Hematocrit: {random.uniform(36, 46):.1f}% (Normal: 36-46%)
- Iron: {random.randint(60, 170)} µg/dL (Normal: 60-170)
- Ferritin: {random.randint(20, 200)} ng/mL (Normal: 20-200)

THYROID:
- TSH: {random.uniform(0.5, 4.5):.2f} mIU/L (Normal: 0.5-5.0)
- Free T3: {random.uniform(2.3, 4.2):.2f} pg/mL (Normal: 2.3-4.2)
- Free T4: {random.uniform(0.8, 1.8):.2f} ng/dL (Normal: 0.8-1.8)

VITAMINS:
- Vitamin D: {random.randint(30, 60)} ng/mL (Normal: 30-100)
- Vitamin B12: {random.randint(200, 900)} pg/mL (Normal: 200-900)
- Calcium: {random.uniform(8.5, 10.5):.1f} mg/dL (Normal: 8.5-10.5)

INTERPRETATION:
All values within normal range. Continue routine screening annually.

Reviewed by: Dr. {random.choice(['Smith', 'Johnson', 'Williams', 'Brown'])}
Lab: HealthCare Diagnostics Center
"""
        return content.strip()
    
    @staticmethod
    def generate_lab_report_stage2(patient_name, patient_age):
        """Generate Stage 2 (Medium/High Risk) lab report with BRCA testing"""
        report_date = datetime.now() - timedelta(days=random.randint(30, 90))
        
        # Some values slightly abnormal
        content = f"""
LABORATORY REPORT
=================

Patient Name: {patient_name}
Patient Age: {patient_age}
Report Date: {report_date.strftime("%B %d, %Y")}
Report Type: Comprehensive Blood Panel + Genetic Testing - Stage 2 (Medium/High Risk)

HEART MARKERS:
- Total Cholesterol: {random.randint(200, 240)} mg/dL (Borderline High: 200-239)
- HDL (Good Cholesterol): {random.randint(35, 50)} mg/dL (Low: <40)
- LDL (Bad Cholesterol): {random.randint(130, 160)} mg/dL (Borderline High: 130-159)
- Triglycerides: {random.randint(150, 200)} mg/dL (Borderline High: 150-199)

INSULIN/GLUCOSE:
- Fasting Glucose: {random.randint(100, 125)} mg/dL (Prediabetes: 100-125)
- HbA1c: {random.uniform(5.7, 6.4):.1f}% (Prediabetes: 5.7-6.4%)

KIDNEY FUNCTION:
- Creatinine: {random.uniform(0.8, 1.3):.2f} mg/dL (Normal: 0.6-1.2)
- eGFR: {random.randint(60, 89)} mL/min (Mildly Decreased: 60-89)
- Urea: {random.randint(40, 50)} mg/dL (Slightly Elevated)

LIVER FUNCTION:
- ALT: {random.randint(40, 60)} U/L (Slightly Elevated)
- ALP: {random.randint(120, 150)} U/L (Slightly Elevated)
- Bilirubin: {random.uniform(0.8, 1.3):.2f} mg/dL (Normal: 0.3-1.2)

BLOOD COUNT:
- Hemoglobin: {random.uniform(11.0, 12.0):.1f} g/dL (Mild Anemia: <12)
- Hematocrit: {random.uniform(33, 36):.1f}% (Low: <36%)
- Iron: {random.randint(40, 60)} µg/dL (Low: <60)
- Ferritin: {random.randint(10, 20)} ng/mL (Low: <20)

THYROID:
- TSH: {random.uniform(4.5, 6.0):.2f} mIU/L (Slightly Elevated)
- Free T3: {random.uniform(2.0, 2.3):.2f} pg/mL (Low Normal)
- Free T4: {random.uniform(0.7, 0.9):.2f} ng/dL (Low Normal)

VITAMINS:
- Vitamin D: {random.randint(15, 30)} ng/mL (Insufficient: 20-30)
- Vitamin B12: {random.randint(150, 200)} pg/mL (Low Normal)
- Calcium: {random.uniform(8.2, 8.5):.1f} mg/dL (Low Normal)

GENETIC TESTING:
- BRCA1 Gene: {"MUTATION DETECTED" if random.random() < 0.3 else "No mutation detected"}
- BRCA2 Gene: {"MUTATION DETECTED" if random.random() < 0.3 else "No mutation detected"}

TUMOR MARKERS:
- CA 15-3: {random.randint(25, 35)} U/mL (Normal: <30)
- CA 27-29: {random.randint(35, 45)} U/mL (Normal: <38)

INTERPRETATION:
Several markers indicate increased risk. Recommend follow-up with oncologist.
Iron supplementation advised. Vitamin D supplementation recommended.

Reviewed by: Dr. {random.choice(['Singh', 'Patel', 'Kumar', 'Sharma'])}
Lab: Advanced Diagnostics & Genetics Center
"""
        return content.strip()
    
    @staticmethod
    def generate_mammography_report(patient_name, patient_age, risk_level="low"):
        """Generate mammography report"""
        report_date = datetime.now() - timedelta(days=random.randint(60, 365))
        
        if risk_level == "low":
            findings = "No suspicious masses or calcifications detected."
            birads = "BI-RADS 1 (Negative)"
            density = "Scattered fibroglandular densities"
            recommendation = "Continue routine annual screening."
        elif risk_level == "medium":
            findings = "Heterogeneously dense breast tissue. No definite masses."
            birads = "BI-RADS 2 (Benign)"
            density = "Heterogeneously dense"
            recommendation = "Consider supplemental ultrasound. Annual screening recommended."
        else:  # high risk
            findings = "Irregular mass in upper outer quadrant of right breast, measuring 1.2 cm. Suspicious microcalcifications noted."
            birads = "BI-RADS 4 (Suspicious)"
            density = "Extremely dense"
            recommendation = "URGENT: Biopsy recommended. Follow-up with breast surgeon within 2 weeks."
        
        content = f"""
MAMMOGRAPHY REPORT
==================

Patient Name: {patient_name}
Patient Age: {patient_age}
Exam Date: {report_date.strftime("%B %d, %Y")}
Exam Type: Digital Screening Mammography (Bilateral)

TECHNIQUE:
Standard CC and MLO views obtained of both breasts.

BREAST COMPOSITION:
{density}

FINDINGS:
{findings}

ASSESSMENT:
{birads}

RECOMMENDATION:
{recommendation}

Radiologist: Dr. {random.choice(['Anderson', 'Martinez', 'Taylor', 'Wilson'])}
Facility: Women's Imaging Center
"""
        return content.strip()
    
    @staticmethod
    def generate_consultation_note(patient_name, doctor_name, risk_level="low"):
        """Generate doctor consultation note"""
        consult_date = datetime.now() - timedelta(days=random.randint(7, 60))
        
        if risk_level == "low":
            chief_complaint = "Routine annual check-up"
            assessment = "Patient is healthy with no concerning symptoms. Continue routine screening."
            plan = "Annual mammogram. Maintain healthy lifestyle."
        elif risk_level == "medium":
            chief_complaint = "Breast pain and family history concerns"
            assessment = "Patient reports localized breast pain. Family history of breast cancer in aunt. Dense breast tissue noted on recent mammogram."
            plan = "Ultrasound ordered. Consider genetic counseling. Follow-up in 3 months."
        else:  # high risk
            chief_complaint = "New breast lump with discharge"
            assessment = "Patient presents with palpable mass in right breast, bloody nipple discharge, and strong family history (mother and sister). BRCA1 mutation confirmed."
            plan = "URGENT: Biopsy scheduled. Referral to surgical oncologist. MRI ordered. Close monitoring required."
        
        content = f"""
CONSULTATION NOTE
=================

Patient Name: {patient_name}
Date of Visit: {consult_date.strftime("%B %d, %Y")}
Provider: {doctor_name}

CHIEF COMPLAINT:
{chief_complaint}

HISTORY OF PRESENT ILLNESS:
Patient is a {random.randint(35, 65)}-year-old female presenting for evaluation.

PAST MEDICAL HISTORY:
- No significant past medical history

FAMILY HISTORY:
- {"Mother and sister with breast cancer" if risk_level == "high" else "Aunt with breast cancer at age 55" if risk_level == "medium" else "No family history of breast cancer"}

PHYSICAL EXAMINATION:
- Vital Signs: BP {random.randint(110, 130)}/{random.randint(70, 85)}, HR {random.randint(60, 80)}, Temp 98.{random.randint(0, 9)}°F
- Breast Exam: {"Palpable mass right breast upper outer quadrant" if risk_level == "high" else "No masses palpated" if risk_level == "low" else "Mild tenderness, no discrete masses"}

ASSESSMENT:
{assessment}

PLAN:
{plan}

Electronically signed by: {doctor_name}
"""
        return content.strip()
    
    @staticmethod
    def generate_documents_for_patient(patient_data):
        """Generate appropriate documents based on patient risk level"""
        documents = []
        
        patient_name = patient_data["demographic_data"]["name"]
        patient_age = patient_data["demographic_data"]["age"]
        patient_uuid = patient_data["patient_uuid"]
        
        # Determine risk level from questionnaire
        questionnaire = patient_data["onboarding_questionnaire"]
        
        has_lump = questionnaire["symptoms"]["q14_new_lump"] == "yes"
        has_brca = questionnaire["family_history"]["q9_brca_mutation"] == "yes"
        has_strong_family_history = "mother" in str(questionnaire["family_history"].get("q7_which_relatives", "")).lower()
        
        if has_lump or has_brca or has_strong_family_history:
            risk_level = "high"
        elif questionnaire["family_history"]["q6_family_history"] == "yes" or questionnaire["screening_history"]["q24_breast_density"] == "heterogeneously_dense":
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Generate lab report
        if risk_level in ["medium", "high"]:
            lab_content = MockDocumentGenerator.generate_lab_report_stage2(patient_name, patient_age)
        else:
            lab_content = MockDocumentGenerator.generate_lab_report_stage1(patient_name, patient_age)
        
        documents.append({
            "document_id": str(uuid.uuid4()),
            "patient_uuid": patient_uuid,
            "filename": f"lab_report_{patient_uuid[:8]}.txt",
            "content": lab_content,
            "document_type": "lab_report"
        })
        
        # Generate mammography report
        mammo_content = MockDocumentGenerator.generate_mammography_report(patient_name, patient_age, risk_level)
        documents.append({
            "document_id": str(uuid.uuid4()),
            "patient_uuid": patient_uuid,
            "filename": f"mammography_{patient_uuid[:8]}.txt",
            "content": mammo_content,
            "document_type": "imaging"
        })
        
        # Generate consultation note
        doctor_name = f"Dr. {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Singh', 'Patel'])}"
        consult_content = MockDocumentGenerator.generate_consultation_note(patient_name, doctor_name, risk_level)
        documents.append({
            "document_id": str(uuid.uuid4()),
            "patient_uuid": patient_uuid,
            "filename": f"consultation_{patient_uuid[:8]}.txt",
            "content": consult_content,
            "document_type": "consultation_note"
        })
        
        return documents


if __name__ == "__main__":
    # Test generation
    from app.mock_data.patients import MockPatientGenerator
    
    patient = MockPatientGenerator.generate_high_risk_patient()
    documents = MockDocumentGenerator.generate_documents_for_patient(patient)
    
    print(f"Generated {len(documents)} documents for patient")
    for doc in documents:
        print(f"\n{'='*80}")
        print(f"Document Type: {doc['document_type']}")
        print(f"Filename: {doc['filename']}")
        print(f"\nContent Preview:")
        print(doc['content'][:500] + "...")
