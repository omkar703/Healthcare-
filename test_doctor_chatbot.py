"""
Test script for Doctor Chatbot with Full AI Access.
"""

import requests
import json
import uuid

BASE_URL = "http://localhost:8000/api/v1/chat"

# Use known UUIDs from seeded data
DOCTOR_UUID = "550e8400-e29b-41d4-a716-446655440001"  # Mock doctor UUID
PATIENT_UUID = "66c9a8f1-2a1b-9c00-9876-543298765432"


def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"TEST: {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"\nResponse:")
        print(json.dumps(data, indent=2))
    else:
        print(f"Error: {response.text}")
    print(f"{'='*60}\n")


def test_doctor_general_chat():
    """Test 1: General medical AI chat (like ChatGPT)"""
    data = {
        "message": "Explain the mechanism of action of metformin in type 2 diabetes"
    }
    response = requests.post(f"{BASE_URL}/doctor/{DOCTOR_UUID}", json=data)
    print_response("General Medical AI Chat (Full Access)", response)
    return response


def test_doctor_complex_medical_query():
    """Test 2: Complex medical query (no restrictions)"""
    data = {
        "message": "What are the differential diagnoses for elevated CA 15-3 and CA 27-29 tumor markers?"
    }
    response = requests.post(f"{BASE_URL}/doctor/{DOCTOR_UUID}", json=data)
    print_response("Complex Medical Query (No Guardrails)", response)
    return response


def test_doctor_patient_specific_chat():
    """Test 3: Patient-specific chat with medical records"""
    data = {
        "patient_uuid": PATIENT_UUID,
        "message": "Analyze this patient's tumor marker trends and provide clinical recommendations"
    }
    response = requests.post(f"{BASE_URL}/doctor/{DOCTOR_UUID}/patient/{PATIENT_UUID}", json=data)
    print_response("Patient-Specific Analysis", response)
    return response


def test_doctor_patient_diagnosis_query():
    """Test 4: Diagnostic query for specific patient"""
    data = {
        "patient_uuid": PATIENT_UUID,
        "message": "Based on the available medical records, what is the likely stage and prognosis?",
        "additional_context": "Patient presented with palpable mass in upper outer quadrant"
    }
    response = requests.post(f"{BASE_URL}/doctor/{DOCTOR_UUID}/patient/{PATIENT_UUID}", json=data)
    print_response("Diagnostic Query with Context", response)
    return response


def test_doctor_document_upload():
    """Test 5: Doctor uploads document for patient"""
    file_path = "_documents/AHD-0425-PA-0007719_E-REPORTS_250427_2032@E.pdf_page_7.png"
    
    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_path.split("/")[-1], f, "image/png")}
            data = {"patient_uuid": PATIENT_UUID}
            response = requests.post(f"{BASE_URL}/doctor/{DOCTOR_UUID}/upload", files=files, data=data)
            print_response("Doctor Document Upload", response)
            return response
    except FileNotFoundError:
        print(f"\n⚠️  Test file not found: {file_path}")
        print("Skipping document upload test\n")
        return None


def test_doctor_treatment_planning():
    """Test 6: Treatment planning query"""
    data = {
        "patient_uuid": PATIENT_UUID,
        "message": "Suggest a comprehensive treatment plan including chemotherapy regimen, radiation therapy, and follow-up schedule"
    }
    response = requests.post(f"{BASE_URL}/doctor/{DOCTOR_UUID}/patient/{PATIENT_UUID}", json=data)
    print_response("Treatment Planning", response)
    return response


def run_all_doctor_tests():
    """Run all doctor chatbot tests"""
    print("\n" + "="*60)
    print("DOCTOR CHATBOT TESTS - FULL AI ACCESS")
    print("="*60)
    
    # Run tests
    test_doctor_general_chat()
    test_doctor_complex_medical_query()
    test_doctor_patient_specific_chat()
    test_doctor_patient_diagnosis_query()
    test_doctor_document_upload()
    test_doctor_treatment_planning()
    
    print("\n" + "="*60)
    print("ALL DOCTOR TESTS COMPLETED")
    print("="*60)


if __name__ == "__main__":
    run_all_doctor_tests()
