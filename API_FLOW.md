# Healthcare AI Microservice - API Flow Documentation

## Overview

This microservice handles AI-powered features for the healthcare platform:

- **Document Processing**: OCR + Vision analysis of medical documents
- **RAG Chat**: AI chat with context from patient medical records
- **Health Scoring**: Automated health score calculation
- **Risk Assessment**: Medical risk evaluation

**Important**: Patient and Doctor onboarding is handled by the main backend. This microservice only receives UUIDs.

---

## Base URL

```
http://localhost:8000
```

---

## Authentication

Currently using UUID-based identification. JWT authentication will be added in Phase 11.

---

## API Endpoints

### 1. Health Check

**GET** `/health`

**Response:**

```json
{
  "status": "healthy",
  "service": "Healthcare AI Microservice",
  "version": "1.0.0"
}
```

---

## Patient Endpoints

### 2. Upload Medical Document

**POST** `/api/v1/patients/{patient_uuid}/documents/upload`

Upload a medical document (PDF, JPG, PNG) for AI processing.

**Path Parameters:**

- `patient_uuid` (UUID): Patient identifier from main backend

**Request:**

- Content-Type: `multipart/form-data`
- Body: `file` (File)

**Example using cURL:**

```bash
curl -X POST "http://localhost:8000/api/v1/patients/550e8400-e29b-41d4-a716-446655440000/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/medical_report.pdf"
```

**Response (201 Created):**

```json
{
  "document_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "patient_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "medical_report.pdf",
  "file_size_bytes": 245632,
  "mime_type": "application/pdf",
  "processing_status": "UPLOADED",
  "message": "Document uploaded successfully. Processing started.",
  "uploaded_at": "2026-02-03T19:15:30.123456"
}
```

**Processing Statuses:**

- `UPLOADED`: Document received
- `PROCESSING`: OCR and AI analysis in progress
- `COMPLETED`: Processing finished
- `FAILED`: Processing error

**🔍 What Happens After Upload (Automatic OCR Pipeline):**

When you upload a document, the system automatically processes it through a **3-tier pipeline**:

**Tier 1: OCR Extraction (AWS Textract)**

- Extracts all text from the document
- Recognizes tables, forms, and structured data
- Handles PDFs, images (JPG, PNG)
- Stores raw extracted text

**Tier 2: Vision Analysis (Claude 3.5 Sonnet Vision)**

- AI analyzes the document image
- Extracts medical insights and context
- Identifies document type (lab report, prescription, etc.)
- Detects risk markers and abnormalities
- Provides structured medical data in JSON format

**Tier 3: RAG Indexing (Vector Embeddings)**

- Chunks the text into semantic segments
- Generates embeddings using Amazon Titan
- Stores in pgvector database
- Makes document searchable for AI chat

**Example Processing Timeline:**

- Upload: Instant
- Tier 1 (OCR): 5-15 seconds
- Tier 2 (Vision): 10-20 seconds
- Tier 3 (RAG): 5-10 seconds
- **Total: ~30-45 seconds** for a typical medical document

**OCR Output Example:**
After processing, the extracted data includes:

```json
{
  "tier_1_text": "Complete Blood Count\nHemoglobin: 13.5 g/dL\nWBC: 7200/μL...",
  "tier_2_enriched": {
    "document_type": "LAB_REPORT",
    "findings": ["Hemoglobin within normal range", "..."],
    "risk_markers": ["Mild anemia indicators"]
  },
  "tier_3_indexed": true
}
```

This OCR data is then used for:

- ✅ AI Chat (RAG retrieves relevant chunks)
- ✅ Health Score calculation
- ✅ Risk Assessment
- ✅ Doctor analysis

---

### 3. Check Document Processing Status

**GET** `/api/v1/patients/documents/{document_id}/status`

**Path Parameters:**

- `document_id` (UUID): Document identifier

**Response:**

```json
{
  "document_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "patient_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "medical_report.pdf",
  "processing_status": "COMPLETED",
  "document_type": "LAB_REPORT",
  "processed_at": "2026-02-03T19:16:45.789012",
  "tier_1_completed": true,
  "tier_2_completed": true,
  "tier_3_completed": true
}
```

---

### 4. Patient Chat with AI

**POST** `/api/v1/patients/{patient_uuid}/chat`

Chat with AI assistant that has access to patient's medical records via RAG.

**Path Parameters:**

- `patient_uuid` (UUID): Patient identifier

**Request Body:**

```json
{
  "message": "What were my latest blood test results?",
  "conversation_id": null
}
```

**Response:**

```json
{
  "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "Based on your latest blood test from January 15, 2026:\n\n- Hemoglobin: 13.5 g/dL (Normal range: 13.5-17.5)\n- White Blood Cell Count: 7,200/μL (Normal)\n- Platelet Count: 250,000/μL (Normal)\n\nAll values are within normal ranges. Your iron levels show slight improvement compared to the previous test.",
  "sources": [
    "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "8d0f7680-8536-51ef-b827-f18gd2g01bf8"
  ],
  "is_critical": false
}
```

**Follow-up Chat (with conversation_id):**

```json
{
  "message": "Should I continue taking iron supplements?",
  "conversation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 5. Get Patient Health Score

**GET** `/api/v1/patients/{patient_uuid}/health-score`

Retrieve the latest calculated health score.

**Path Parameters:**

- `patient_uuid` (UUID): Patient identifier

**Response:**

```json
{
  "score_id": "b2c3d4e5-f6a7-8901-bcde-f23456789012",
  "patient_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "overall_score": 78,
  "trend": "IMPROVING",
  "component_scores": {
    "cardiovascular": {
      "score": 82,
      "weight": 0.25
    },
    "metabolic": {
      "score": 75,
      "weight": 0.2
    },
    "respiratory": {
      "score": 80,
      "weight": 0.15
    },
    "mental_health": {
      "score": 70,
      "weight": 0.15
    },
    "lifestyle": {
      "score": 76,
      "weight": 0.15
    },
    "preventive_care": {
      "score": 85,
      "weight": 0.1
    }
  },
  "version": 1,
  "calculated_at": "2026-02-03T19:20:00.000000"
}
```

---

### 6. Get Patient Risk Assessment

**GET** `/api/v1/patients/{patient_uuid}/risk-assessment`

Retrieve the latest risk assessment.

**Path Parameters:**

- `patient_uuid` (UUID): Patient identifier

**Response:**

```json
{
  "assessment_id": "c3d4e5f6-a7b8-9012-cdef-345678901234",
  "patient_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "overall_risk": "MEDIUM",
  "risk_score": 45,
  "risk_categories": {
    "cardiovascular": {
      "level": "MEDIUM",
      "score": 50,
      "factors": [
        "Family history of heart disease",
        "Borderline cholesterol levels"
      ]
    },
    "diabetes": {
      "level": "LOW",
      "score": 25,
      "factors": ["Normal glucose levels", "Healthy BMI"]
    },
    "cancer": {
      "level": "LOW",
      "score": 20,
      "factors": ["No family history", "Regular screenings up to date"]
    }
  },
  "recommendations": [
    "Schedule cardiovascular screening within 6 months",
    "Maintain current exercise routine",
    "Monitor cholesterol levels quarterly"
  ],
  "version": 1,
  "assessed_at": "2026-02-03T19:20:00.000000"
}
```

---

## Doctor Endpoints

### 7. Doctor Chat for Patient

**POST** `/api/v1/doctors/{doctor_uuid}/chat`

AI chat for doctors with enhanced medical context for a specific patient.

**Path Parameters:**

- `doctor_uuid` (UUID): Doctor identifier

**Request Body:**

```json
{
  "patient_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Analyze the patient's recent lab trends and suggest next steps",
  "conversation_id": null,
  "additional_context": "Patient reports fatigue"
}
```

**Response:**

```json
{
  "conversation_id": "d4e5f6a7-b8c9-0123-defg-456789012345",
  "message": "Based on the patient's lab history over the past 6 months:\n\n**Trends:**\n- Hemoglobin: Gradual decline from 14.2 → 13.5 g/dL\n- Ferritin: Low at 18 ng/mL (Normal: 30-400)\n- MCV: 78 fL (slightly microcytic)\n\n**Analysis:**\nThe data suggests developing iron deficiency anemia, which correlates with the reported fatigue.\n\n**Recommendations:**\n1. Prescribe oral iron supplementation (325mg ferrous sulfate daily)\n2. Recheck CBC and iron panel in 8 weeks\n3. Consider GI evaluation if no improvement\n4. Dietary counseling for iron-rich foods",
  "sources": [
    "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "8d0f7680-8536-51ef-b827-f18gd2g01bf8",
    "9e1g8791-9647-62fg-c938-g29he3h12cg9"
  ],
  "patient_summary": {
    "patient_uuid": "550e8400-e29b-41d4-a716-446655440000",
    "health_score": 78,
    "risk_level": "MEDIUM",
    "recent_documents": 5,
    "last_updated": "2026-02-03T19:15:30.123456"
  }
}
```

---

### 8. Get Doctor's Patient List

**GET** `/api/v1/doctors/{doctor_uuid}/patients`

Get list of patients with summaries (filtered by access permissions).

**Path Parameters:**

- `doctor_uuid` (UUID): Doctor identifier

**Response:**

```json
{
  "doctor_uuid": "660f9511-f30c-52e5-b827-557766551111",
  "patients": [
    {
      "patient_uuid": "550e8400-e29b-41d4-a716-446655440000",
      "name": "John Doe",
      "age": 45,
      "overall_risk": "MEDIUM",
      "health_score": 78,
      "last_updated": "2026-02-03T19:20:00.000000"
    },
    {
      "patient_uuid": "661g0622-g41d-63f6-c938-668877662222",
      "name": "Jane Smith",
      "age": 32,
      "overall_risk": "LOW",
      "health_score": 92,
      "last_updated": "2026-02-03T18:45:00.000000"
    }
  ],
  "total_count": 2
}
```

---

## OCR Endpoints

### 8. Extract Doctor Credentials (OCR)

**POST** `/api/v1/ocr/doctor-credentials`

Extract structured data from doctor degree/license images using AI-powered OCR.

**Request:**

- Content-Type: `multipart/form-data`
- Body: `file` (Image file: JPG, PNG, WEBP)

**Example using cURL:**

```bash
curl -X POST "http://localhost:8000/api/v1/ocr/doctor-credentials" \
  -F "file=@doctor_degree.jpg"
```

**Response (200 OK):**

```json
{
  "universityName": "Maharashtra University of Health Sciences, Nashik",
  "doctorName": "Dr. Priya Singh",
  "degreeName": "Bachelor of Medicine & Bachelor of Surgery",
  "licenseNumber": "PRN 0104140566",
  "issueDate": "2009-05-25"
}
```

**Field Descriptions:**

- `universityName`: Name of the issuing university/institution
- `doctorName`: Full name of the doctor (with title)
- `degreeName`: Complete degree name (MBBS, MD, etc.)
- `licenseNumber`: Medical license/registration number
- `issueDate`: Date of issue in YYYY-MM-DD format

**Notes:**

- This is a **standalone OCR service** - no database storage
- Returns `null` for fields not visible in the image
- Supports rotated images (AI auto-corrects orientation)
- Processing time: ~5-10 seconds per image
- Uses Claude 3.5 Sonnet Vision for high accuracy

**Use Case:**
The main backend can call this endpoint during doctor onboarding to extract and verify credentials before creating the doctor record.

---

## RAG Endpoints

### 9. Refresh RAG Index

**POST** `/api/v1/rag/refresh`

Manually trigger RAG index refresh for a patient (usually automatic after document processing).

**Request Body:**

```json
{
  "patient_uuid": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**

```json
{
  "patient_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "status": "refresh_started",
  "message": "RAG index refresh initiated",
  "timestamp": "2026-02-03T19:25:00.000000"
}
```

---

## Complete Workflow Example

### Scenario: Patient uploads lab report and asks about results

#### Step 1: Upload Document

```bash
curl -X POST "http://localhost:8000/api/v1/patients/550e8400-e29b-41d4-a716-446655440000/documents/upload" \
  -F "file=@lab_report_jan_2026.pdf"
```

#### Step 2: Wait for Processing (check status)

```bash
curl "http://localhost:8000/api/v1/patients/documents/7c9e6679-7425-40de-944b-e07fc1f90ae7/status"
```

#### Step 3: Patient Asks Question

```bash
curl -X POST "http://localhost:8000/api/v1/patients/550e8400-e29b-41d4-a716-446655440000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What do my latest lab results show?"
  }'
```

#### Step 4: Check Health Score (Auto-updated)

```bash
curl "http://localhost:8000/api/v1/patients/550e8400-e29b-41d4-a716-446655440000/health-score"
```

#### Step 5: Doctor Reviews Patient

```bash
curl -X POST "http://localhost:8000/api/v1/doctors/660f9511-f30c-52e5-b827-557766551111/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_uuid": "550e8400-e29b-41d4-a716-446655440000",
    "message": "Summarize this patient'\''s recent health trends"
  }'
```

---

## Error Responses

### 404 Not Found

```json
{
  "detail": "Patient not found"
}
```

### 400 Bad Request

```json
{
  "detail": "Invalid file format. Supported formats: PDF, JPG, PNG"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Document processing failed: AWS Textract error"
}
```

---

## Notes for Frontend Developers

### 1. Patient/Doctor Creation

- **Do NOT call onboarding endpoints** - they don't exist in this microservice
- Patient and doctor UUIDs come from the main backend
- This microservice assumes the UUID already exists

### 2. Document Upload Flow

1. Upload document → Get `document_id`
2. Poll status endpoint every 2-3 seconds
3. When status = `COMPLETED`, document is ready for RAG
4. Health score and risk assessment auto-update

### 3. Chat Conversations

- First message: `conversation_id` = `null`
- Subsequent messages: Include the returned `conversation_id`
- Each doctor-patient pair has separate conversations

### 4. Real-time Updates

- Use polling for document status (every 2-3 seconds)
- Health scores update automatically after document processing
- Consider WebSocket implementation for real-time chat (future enhancement)

### 5. File Upload Limits

- Max file size: 50 MB
- Supported formats: PDF, JPG, JPEG, PNG
- Files are stored in `_documents/patients/{patient_uuid}/`

---

## Testing with Postman

### Import Collection

Create a Postman collection with these environment variables:

```json
{
  "base_url": "http://localhost:8000",
  "patient_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "doctor_uuid": "660f9511-f30c-52e5-b827-557766551111"
}
```

### Test Sequence

1. Health Check → Verify service is running
2. Upload Document → Get `document_id`
3. Check Status → Wait for `COMPLETED`
4. Patient Chat → Test RAG functionality
5. Get Health Score → Verify auto-calculation
6. Doctor Chat → Test doctor-specific features

---

## Production Considerations

### Security (Phase 11)

- Add JWT authentication
- Implement RBAC (Role-Based Access Control)
- Encrypt sensitive data
- Add audit logging

### Performance

- Document processing is async (Celery)
- RAG queries use vector similarity (fast)
- Consider caching for health scores

### Monitoring

- Track document processing success rate
- Monitor RAG response times
- Alert on failed document processing

---

## Support

For issues or questions, contact the backend team.

**Last Updated:** 2026-02-03
**API Version:** 1.0.0
