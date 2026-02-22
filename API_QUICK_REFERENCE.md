# API Quick Reference Guide

## Base URL
```
http://localhost:8000
```

---

## 🏥 Health Check

### Check Service Status
```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Healthcare AI Microservice",
  "version": "1.0.0"
}
```

---

## 👤 Patient APIs

### 1. Patient Chat
```bash
POST /api/v1/chat/patient/{patient_uuid}
```

**Request:**
```json
{
  "message": "What do my blood test results show?",
  "conversation_id": null  // Optional: for continuing conversation
}
```

**Response:**
```json
{
  "conversation_id": "uuid",
  "message": "AI response with simplified medical info...",
  "sources": ["doc-id-1", "doc-id-2"],
  "is_emergency": false,
  "is_complex": false,
  "guardrails_applied": ["terminology_simplified", "disclaimer_added"]
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat/patient/550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are my cholesterol levels?"}'
```

---

### 2. Upload Medical Document
```bash
POST /api/v1/chat/patient/{patient_uuid}/upload
```

**Request:** (multipart/form-data)
```bash
file: <binary file>
```

**Response:**
```json
{
  "document_id": "doc-uuid",
  "patient_uuid": "patient-uuid",
  "filename": "blood_test.pdf",
  "file_size_bytes": 524288,
  "mime_type": "application/pdf",
  "processing_status": "UPLOADED",
  "message": "Document uploaded successfully. Processing started."
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat/patient/550e8400-e29b-41d4-a716-446655440000/upload" \
  -F "file=@blood_test.pdf"
```

---

### 3. Get Conversation History
```bash
GET /api/v1/chat/patient/{patient_uuid}/history
```

**Response:**
```json
{
  "conversations": [
    {
      "conversation_id": "conv-uuid",
      "title": null,
      "message_count": 5,
      "last_message": "Thank you...",
      "created_at": "2026-02-07T00:30:00Z",
      "updated_at": "2026-02-07T00:45:00Z"
    }
  ],
  "total_count": 1
}
```

---

### 4. Get Patient Documents
```bash
GET /api/v1/chat/patient/{patient_uuid}/documents
```

**Response:**
```json
{
  "documents": [
    {
      "document_id": "doc-uuid",
      "filename": "blood_test.pdf",
      "file_size_bytes": 524288,
      "mime_type": "application/pdf",
      "document_type": "LAB_REPORT",
      "processing_status": "COMPLETED",
      "uploaded_at": "2026-02-07T00:30:00Z"
    }
  ],
  "total_count": 1
}
```

---

### 5. Get Health Score
```bash
GET /api/v1/patients/{patient_uuid}/health-score
```

**Response:**
```json
{
  "score_id": "uuid",
  "patient_uuid": "uuid",
  "overall_score": 78,
  "trend": "IMPROVING",
  "component_scores": {
    "cardiovascular": {"score": 82, "weight": 0.25},
    "metabolic": {"score": 75, "weight": 0.2},
    "respiratory": {"score": 80, "weight": 0.15},
    "mental_health": {"score": 70, "weight": 0.15},
    "lifestyle": {"score": 76, "weight": 0.15},
    "preventive_care": {"score": 85, "weight": 0.1}
  },
  "version": 1,
  "calculated_at": "2026-02-03T19:20:00Z"
}
```

---

### 6. Get Risk Assessment
```bash
GET /api/v1/patients/{patient_uuid}/risk-assessment
```

**Response:**
```json
{
  "assessment_id": "uuid",
  "patient_uuid": "uuid",
  "overall_risk": "MEDIUM",
  "risk_score": 45,
  "risk_categories": {
    "cardiovascular": {
      "level": "MEDIUM",
      "score": 50,
      "factors": ["Family history", "Borderline cholesterol"]
    },
    "diabetes": {
      "level": "LOW",
      "score": 25,
      "factors": ["Normal glucose", "Healthy BMI"]
    }
  },
  "recommendations": [
    "Schedule cardiovascular screening within 6 months",
    "Maintain current exercise routine"
  ],
  "version": 1,
  "assessed_at": "2026-02-03T19:20:00Z"
}
```

---

## 👨‍⚕️ Doctor APIs

### 7. Doctor General Chat
```bash
POST /api/v1/chat/doctor/{doctor_uuid}
```

**Request:**
```json
{
  "message": "Explain the mechanism of action of metformin",
  "conversation_id": null
}
```

**Response:**
```json
{
  "conversation_id": "uuid",
  "message": "Detailed medical explanation...",
  "sources": [],
  "patient_summary": null
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/chat/doctor/660f9511-f30c-52e5-b827-557766551111" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the contraindications for warfarin?"}'
```

---

### 8. Doctor Patient-Specific Chat
```bash
POST /api/v1/chat/doctor/{doctor_uuid}/patient/{patient_uuid}
```

**Request:**
```json
{
  "patient_uuid": "patient-uuid",
  "message": "Analyze this patient's tumor marker trends",
  "conversation_id": null,
  "additional_context": "Patient presented with palpable mass"
}
```

**Response:**
```json
{
  "conversation_id": "uuid",
  "message": "Detailed medical analysis...",
  "sources": ["doc-id-1", "doc-id-2"],
  "patient_summary": {
    "name": "Jane Doe",
    "age": 45,
    "health_score": 47,
    "risk_level": "HIGH"
  }
}
```

---

### 9. Doctor Upload Document
```bash
POST /api/v1/chat/doctor/{doctor_uuid}/upload
```

**Request:** (multipart/form-data)
```bash
file: <binary file>
patient_uuid: "patient-uuid"
```

**Response:**
```json
{
  "document_id": "doc-uuid",
  "patient_uuid": "patient-uuid",
  "filename": "mammogram.jpg",
  "file_size_bytes": 2097152,
  "mime_type": "image/jpeg",
  "processing_status": "UPLOADED",
  "message": "Document uploaded successfully."
}
```

---

### 10. Get Doctor's Patients
```bash
GET /api/v1/doctors/{doctor_uuid}/patients
```

**Response:**
```json
{
  "doctor_uuid": "uuid",
  "patients": [
    {
      "patient_uuid": "uuid",
      "name": "John Doe",
      "age": 45,
      "overall_risk": "MEDIUM",
      "health_score": 78,
      "last_updated": "2026-02-03T19:20:00Z"
    }
  ],
  "total_count": 2
}
```

---

## 🎗️ Breast Cancer Assessment

### 11. Calculate Breast Cancer Risk
```bash
POST /api/v1/breast-cancer/assess
```

**Request:**
```json
{
  "patientId": "uuid",
  "screeningHistory": {
    "age": 45,
    "denseBreastTissue": true,
    "priorConditions": ["BENIGN_LUMP"],
    "screeningUpToDate": true
  },
  "familyGeneticRisk": {
    "knownBRCAMutation": false,
    "firstDegreeRelativeBreastCancer": true,
    "familyCancerBefore50": true
  },
  "currentSymptoms": {
    "newLump": true,
    "hardOrFixedLump": false,
    "localizedPain": true
  },
  "skinNippleChanges": {
    "dimpling": false,
    "nippleRetraction": false,
    "dischargeType": "NONE"
  },
  "shapeSizeChanges": {
    "asymmetry": false
  },
  "hormonalHistory": {
    "longTermOCPUse": true,
    "earlyMenarcheAge": false
  },
  "lifestyle": {
    "alcoholUse": false,
    "tobaccoUse": false
  },
  "priorCancerRadiation": {
    "previousCancer": false
  }
}
```

**Response:**
```json
{
  "patientId": "uuid",
  "score": 47,
  "riskScore": 47,
  "riskLevel": "Medium",
  "recommendation": "⚡ Consult a doctor for further evaluation...",
  "requiredLabTests": [
    "Total Cholesterol",
    "BRCA1 Gene Mutation Test",
    "CA 15-3 (Cancer Antigen 15-3)",
    "Mammogram (Diagnostic)"
  ],
  "labTestStage": "Stage 2",
  "reasoning": "Breast Health Score: 47/100...",
  "criticalFlags": []
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/breast-cancer/assess" \
  -H "Content-Type: application/json" \
  -d @breast_cancer_request.json
```

---

### 12. Get Latest Breast Cancer Assessment
```bash
GET /api/v1/breast-cancer/assess/{patient_uuid}
```

**Response:** Same as POST response

---

## 📄 Document Processing

### 13. Check Document Status
```bash
GET /api/v1/chat/documents/{document_id}/status
```

**Response:**
```json
{
  "document_id": "doc-uuid",
  "processing_status": "COMPLETED",
  "tier_1_complete": true,
  "tier_2_complete": true,
  "tier_3_complete": true,
  "error_message": null,
  "processed_at": "2026-02-07T00:35:00Z"
}
```

**Processing Statuses:**
- `UPLOADED` - Document received
- `PROCESSING` - Being processed
- `COMPLETED` - All tiers complete
- `FAILED` - Processing error

---

## 🔍 OCR Service

### 14. Extract Doctor Credentials
```bash
POST /api/v1/ocr/doctor-credentials
```

**Request:** (multipart/form-data)
```bash
file: <image file>
```

**Response:**
```json
{
  "universityName": "Maharashtra University of Health Sciences",
  "doctorName": "Dr. Priya Singh",
  "degreeName": "Bachelor of Medicine & Bachelor of Surgery",
  "licenseNumber": "PRN 0104140566",
  "issueDate": "2009-05-25"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/ocr/doctor-credentials" \
  -F "file=@doctor_degree.jpg"
```

---

## 🔄 RAG Service

### 15. Refresh RAG Index
```bash
POST /api/v1/rag/refresh
```

**Request:**
```json
{
  "patient_uuid": "uuid"
}
```

**Response:**
```json
{
  "patient_uuid": "uuid",
  "status": "refresh_started",
  "message": "RAG index refresh initiated",
  "timestamp": "2026-02-03T19:25:00Z"
}
```

---

## 🚨 Error Responses

### 404 Not Found
```json
{
  "detail": "Patient not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "message"],
      "msg": "String should have at least 1 character"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error in patient chat: <error details>"
}
```

---

## 📊 Common Use Cases

### Use Case 1: Patient Uploads Lab Report and Asks Question
```bash
# 1. Upload document
curl -X POST "http://localhost:8000/api/v1/chat/patient/{uuid}/upload" \
  -F "file=@lab_report.pdf"

# 2. Wait for processing (check status)
curl "http://localhost:8000/api/v1/chat/documents/{doc_id}/status"

# 3. Ask question
curl -X POST "http://localhost:8000/api/v1/chat/patient/{uuid}" \
  -H "Content-Type: application/json" \
  -d '{"message": "What do my latest results show?"}'
```

### Use Case 2: Doctor Analyzes Patient
```bash
# 1. Get patient list
curl "http://localhost:8000/api/v1/doctors/{doctor_uuid}/patients"

# 2. Chat about specific patient
curl -X POST "http://localhost:8000/api/v1/chat/doctor/{doctor_uuid}/patient/{patient_uuid}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze tumor marker trends", "patient_uuid": "patient-uuid"}'
```

### Use Case 3: Breast Cancer Risk Assessment
```bash
# 1. Submit assessment
curl -X POST "http://localhost:8000/api/v1/breast-cancer/assess" \
  -H "Content-Type: application/json" \
  -d @assessment_data.json

# 2. Retrieve later
curl "http://localhost:8000/api/v1/breast-cancer/assess/{patient_uuid}"
```

---

## 🔧 Testing Commands

### Start Services
```bash
cd /home/op/Videos/code/Medical-App-Website-/AI
docker compose up -d
```

### Seed Test Data
```bash
docker compose exec api python -m app.mock_data.seed_database
```

### Check Service Status
```bash
docker compose ps
```

### View Logs
```bash
docker compose logs -f api
```

### Run Test Scripts
```bash
bash test_api_endpoints.sh
python3 test_patient_chatbot.py
python3 test_doctor_chatbot.py
```

---

## 📝 Notes

1. **Patient UUIDs** come from main backend (not created here)
2. **Conversation IDs** are returned in first message, reuse for follow-ups
3. **Document Processing** takes 30-45 seconds (poll status endpoint)
4. **Emergency Flags** in patient chat trigger special UI
5. **Source Documents** array shows which docs were used for response
6. **File Size Limit**: 50 MB per upload
7. **Supported Formats**: PDF, JPG, JPEG, PNG, DICOM

---

**Last Updated**: 2026-02-09
**API Version**: 1.0.0
