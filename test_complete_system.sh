#!/bin/bash
BASE_URL="http://localhost:8000"
DOC_DIR="/media/omkar/DATA/Omkar/CODE-111/Liomonk/Healthcare/Medical-App-Website-/AI/documents"
CBC_IMG="$DOC_DIR/AHD-0425-PA-0007719_E-REPORTS_250427_2032@E.pdf_page_7.png"
OCR_IMG="$DOC_DIR/AHD-0425-PA-0007719_E-REPORTS_250427_2032@E.pdf_page_4.png"

PATIENT_UUID="c77d83ae-9483-44d5-9ae2-e72a7cc3c70e"
DOCTOR_UUID="0dfec9c8-92d4-4fb9-94e8-e7f1d34936fc"

echo "========================================="
echo "Healthcare AI Microservice - Full System Test"
echo "========================================="
echo "Using Patient UUID: $PATIENT_UUID"
echo "Using Doctor UUID: $DOCTOR_UUID"

function check_status() {
    ENDPOINT=$1
    RESPONSE=$2
    if [[ "$RESPONSE" == "200" || "$RESPONSE" == "201" || "$RESPONSE" == "202" ]]; then
        echo -e "✅ $ENDPOINT is passing (Status: $RESPONSE)"
    else
        echo -e "❌ $ENDPOINT FAILING (Status: $RESPONSE)"
    fi
}

echo -n "1. Health Check (GET /health): "
res=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health")
check_status "Health Check" "$res"

echo -n "2. Patient Chat (POST /api/v1/chat/patient/$PATIENT_UUID): "
res=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/api/v1/chat/patient/$PATIENT_UUID" -H "Content-Type: application/json" -d '{"message": "Hello, doc!"}')
check_status "Patient Chat" "$res"

echo -n "3. Patient Chat History (GET /api/v1/chat/patient/$PATIENT_UUID/history): "
res=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/v1/chat/patient/$PATIENT_UUID/history")
check_status "Patient History" "$res"

echo -n "4. Patient Health Score (GET /api/v1/patients/$PATIENT_UUID/health-score): "
res=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/v1/patients/$PATIENT_UUID/health-score")
check_status "Health Score" "$res"

echo -n "5. Doctor Chat (POST /api/v1/chat/doctor/$DOCTOR_UUID): "
res=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/api/v1/chat/doctor/$DOCTOR_UUID" -H "Content-Type: application/json" -d '{"message": "Summarize hypertension guidelines."}')
check_status "Doctor Chat" "$res"

echo -n "6. Doctors list of Patients (GET /api/v1/doctors/$DOCTOR_UUID/patients): "
res=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/v1/doctors/$DOCTOR_UUID/patients")
check_status "Doctor Patients" "$res"

echo -n "7. Doctor Patient Analysis (POST /api/v1/chat/doctor/$DOCTOR_UUID/patient/$PATIENT_UUID): "
res=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/api/v1/chat/doctor/$DOCTOR_UUID/patient/$PATIENT_UUID" -H "Content-Type: application/json" -d '{"message": "Analyze patient metrics", "patient_uuid": "'$PATIENT_UUID'"}')
check_status "Doctor Patient Insight" "$res"

echo -n "8. RAG Refresh (POST /api/v1/rag/refresh): "
res=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/api/v1/rag/refresh" -H "Content-Type: application/json" -d "{\"patient_uuid\": \"$PATIENT_UUID\"}")
check_status "RAG Index Refresh" "$res"

echo -n "10. OCR Credentials Extraction (POST /api/v1/ocr/doctor-credentials): "
res=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/api/v1/ocr/doctor-credentials" -F "file=@$OCR_IMG")
check_status "OCR Credentials" "$res"

echo -n "11. CBC Parameter Extraction AI (POST /api/v1/cbc/extract): "
res=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/api/v1/cbc/extract" -F "file=@$CBC_IMG")
check_status "CBC Data Extraction" "$res"

echo "========================================="
