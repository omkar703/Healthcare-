# Healthcare AI Microservice - Changes Summary

## Changes Made

### 1. Removed Onboarding Endpoints ✅

**Reason:** Patient and doctor onboarding is handled by the main backend system.

**Removed Endpoints:**

- ❌ `POST /api/v1/patients/onboard` - Removed
- ❌ `POST /api/v1/doctors/onboard` - Removed
- ❌ `POST /api/v1/doctors/credentials/upload` - Removed

**Files Modified:**

- `app/api/v1/patients.py` - Removed `onboard_patient()` function
- `app/api/v1/doctors.py` - Removed `onboard_doctor()` and `upload_credentials()` functions

### 2. Updated Architecture

This microservice now focuses **exclusively on AI/ML features**:

- ✅ Document Processing (OCR + Vision Analysis)
- ✅ RAG-powered Chat (Patient & Doctor)
- ✅ Health Score Calculation
- ✅ Risk Assessment
- ✅ Vector Search & Embeddings

### 3. UUID-Based Design

- Patient UUIDs come from main backend
- Doctor UUIDs come from main backend
- This microservice **assumes** the UUID already exists in the database
- No user creation/registration happens here

---

## Current API Endpoints

### Patient Endpoints

1. `POST /api/v1/patients/{patient_uuid}/documents/upload` - Upload medical document
2. `GET /api/v1/patients/documents/{document_id}/status` - Check processing status
3. `POST /api/v1/patients/{patient_uuid}/chat` - AI chat with RAG
4. `GET /api/v1/patients/{patient_uuid}/health-score` - Get health score
5. `GET /api/v1/patients/{patient_uuid}/risk-assessment` - Get risk assessment

### Doctor Endpoints

1. `POST /api/v1/doctors/{doctor_uuid}/chat` - AI chat for patient analysis
2. `GET /api/v1/doctors/{doctor_uuid}/patients` - Get patient list

### RAG Endpoints

1. `POST /api/v1/rag/refresh` - Manually refresh RAG index

### System Endpoints

1. `GET /health` - Health check
2. `GET /` - Root info
3. `GET /docs` - Swagger UI
4. `GET /redoc` - ReDoc UI

---

## Files Created

### 1. `API_FLOW.md` ⭐

**Complete API documentation for frontend developers**

Contains:

- All endpoint specifications
- Request/response JSON examples
- Complete workflow examples
- Error handling guide
- Testing instructions
- Production considerations

**Location:** `/media/op/DATA/Omkar/CODE-111/Liomonk/Healthcare+/API_FLOW.md`

### 2. `test_api_endpoints.sh`

**Automated test script**

Tests all endpoints with valid data:

- Health check
- Document upload
- Chat functionality
- Health scores
- Risk assessments

**Usage:**

```bash
chmod +x test_api_endpoints.sh
./test_api_endpoints.sh
```

---

## Testing

### Quick Test

```bash
# 1. Check service health
curl http://localhost:8000/health

# 2. View API documentation
open http://localhost:8000/docs

# 3. Run automated tests
./test_api_endpoints.sh
```

### With Test Data

To fully test the API, you need to seed the database first:

```bash
# Seed database with mock patients and doctors
docker compose exec api python app/mock_data/seed_database.py

# Then run tests
./test_api_endpoints.sh
```

---

## Integration with Main Backend

### Flow Diagram

```
Main Backend                    AI Microservice
     │                                │
     │  1. User registers             │
     ├─────────────────────────────────▶
     │  (Creates patient/doctor)      │
     │                                │
     │  2. Returns UUID               │
     ◀─────────────────────────────────┤
     │                                │
     │  3. Upload document            │
     │     with patient_uuid          │
     ├─────────────────────────────────▶
     │                                │
     │                          4. Process
     │                          (OCR + AI)
     │                                │
     │  5. Query health score         │
     ├─────────────────────────────────▶
     │                                │
     │  6. Returns AI analysis        │
     ◀─────────────────────────────────┤
```

### Key Points for Frontend Team

1. **No User Creation Here**
   - Don't call `/onboard` endpoints (they don't exist)
   - Get patient/doctor UUIDs from main backend
   - Pass UUIDs to this microservice

2. **Document Upload Flow**

   ```javascript
   // Step 1: Get patient UUID from main backend
   const patientUuid = await mainBackend.getPatientId();

   // Step 2: Upload to AI microservice
   const formData = new FormData();
   formData.append("file", file);

   const response = await fetch(
     `http://localhost:8000/api/v1/patients/${patientUuid}/documents/upload`,
     { method: "POST", body: formData },
   );

   const { document_id } = await response.json();

   // Step 3: Poll for status
   const checkStatus = async () => {
     const status = await fetch(
       `http://localhost:8000/api/v1/patients/documents/${document_id}/status`,
     );
     return status.json();
   };
   ```

3. **Chat Integration**
   ```javascript
   // Patient chat
   const chatResponse = await fetch(
     `http://localhost:8000/api/v1/patients/${patientUuid}/chat`,
     {
       method: "POST",
       headers: { "Content-Type": "application/json" },
       body: JSON.stringify({
         message: "What are my latest test results?",
         conversation_id: null, // or previous conversation_id
       }),
     },
   );
   ```

---

## Verification Checklist

- [x] Removed patient onboarding endpoint
- [x] Removed doctor onboarding endpoint
- [x] Removed credential upload endpoint
- [x] Updated API documentation
- [x] Created comprehensive API flow guide
- [x] Created test script
- [x] Verified all remaining endpoints work
- [x] Docker containers build successfully
- [x] Health check passes
- [x] Swagger UI accessible

---

## Next Steps for Frontend Team

1. **Read `API_FLOW.md`** - Complete API reference with examples
2. **Test with Postman** - Import the example requests
3. **Integrate with Main Backend** - Get UUIDs from there
4. **Test Document Upload** - Use the provided examples
5. **Implement Chat UI** - Use streaming for better UX (future)

---

## Support

**API Documentation:** http://localhost:8000/docs  
**API Flow Guide:** `API_FLOW.md`  
**Test Script:** `test_api_endpoints.sh`

For questions, contact the backend team.

**Last Updated:** 2026-02-03  
**Version:** 1.0.0
