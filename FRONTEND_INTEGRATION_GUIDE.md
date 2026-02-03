# 📦 Files to Share with Frontend Developer

## Main Documentation

### 1. **API_FLOW.md** (12KB) ⭐ MOST IMPORTANT

**Purpose:** Complete API reference for frontend integration

**Contains:**

- All 9 API endpoints with full specifications
- Request/response JSON examples (copy-paste ready)
- Complete workflow examples
- Error handling guide
- Testing instructions with cURL examples
- Integration notes

**Frontend developer should read this FIRST.**

---

### 2. **CHANGES_SUMMARY.md** (6.5KB)

**Purpose:** Summary of architectural changes

**Contains:**

- What was removed (onboarding endpoints)
- Why it was removed (main backend handles it)
- Current endpoint list
- Integration flow diagram
- Code examples for React/JavaScript
- Verification checklist

---

### 3. **test_api_endpoints.sh** (6.9KB)

**Purpose:** Automated API testing script

**Usage:**

```bash
chmod +x test_api_endpoints.sh
./test_api_endpoints.sh
```

**Tests:**

- All 9 endpoints
- Health checks
- Document upload
- Chat functionality
- Status checks

---

### 4. **README_TESTING.md** (981B)

**Purpose:** Quick start guide for testing

**Contains:**

- Docker setup instructions
- How to verify the service is running
- Troubleshooting tips

---

## Quick Reference Card

### API Base URL

```
http://localhost:8000
```

### Key Endpoints

```
POST   /api/v1/patients/{uuid}/documents/upload
GET    /api/v1/patients/{uuid}/health-score
POST   /api/v1/patients/{uuid}/chat
POST   /api/v1/doctors/{uuid}/chat
GET    /api/v1/doctors/{uuid}/patients
```

### Important Notes

1. ⚠️ **No onboarding endpoints** - Patient/Doctor UUIDs come from main backend
2. ✅ **UUID-based** - All endpoints require existing UUIDs
3. 📄 **Document processing is async** - Poll status endpoint
4. 💬 **Chat supports conversations** - Pass `conversation_id` for follow-ups

---

## Integration Checklist for Frontend

- [ ] Read `API_FLOW.md` completely
- [ ] Understand UUID flow (main backend → AI microservice)
- [ ] Test with Postman using provided JSON examples
- [ ] Implement document upload with status polling
- [ ] Implement chat with conversation tracking
- [ ] Handle error responses (404, 400, 500)
- [ ] Test with real patient/doctor UUIDs from main backend

---

## Example Integration Code

### Document Upload (React/TypeScript)

```typescript
// Get patient UUID from main backend first
const patientUuid = await mainBackend.getCurrentPatientId();

// Upload document to AI microservice
const uploadDocument = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(
    `http://localhost:8000/api/v1/patients/${patientUuid}/documents/upload`,
    { method: "POST", body: formData },
  );

  const data = await response.json();
  return data.document_id;
};

// Poll for processing status
const checkStatus = async (documentId: string) => {
  const response = await fetch(
    `http://localhost:8000/api/v1/patients/documents/${documentId}/status`,
  );
  return response.json();
};
```

### Chat Integration (React/TypeScript)

```typescript
const sendMessage = async (message: string, conversationId?: string) => {
  const response = await fetch(
    `http://localhost:8000/api/v1/patients/${patientUuid}/chat`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
        conversation_id: conversationId || null,
      }),
    },
  );

  const data = await response.json();
  return {
    message: data.message,
    conversationId: data.conversation_id,
    sources: data.sources,
  };
};
```

---

## Testing Instructions

### 1. Verify Service is Running

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "Healthcare AI Microservice",
  "version": "1.0.0"
}
```

### 2. View API Documentation

Open in browser:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. Run Automated Tests

```bash
./test_api_endpoints.sh
```

---

## Architecture Overview

```
┌─────────────────┐
│  Main Backend   │
│  (User Mgmt)    │
└────────┬────────┘
         │
         │ 1. User registers
         │ 2. Returns UUID
         │
         ▼
┌─────────────────┐
│   Frontend      │
│   (React/Vue)   │
└────────┬────────┘
         │
         │ 3. Upload doc with UUID
         │ 4. Chat with UUID
         │
         ▼
┌─────────────────┐
│ AI Microservice │
│ (This Service)  │
│                 │
│ - OCR           │
│ - RAG Chat      │
│ - Health Score  │
│ - Risk Analysis │
└─────────────────┘
```

---

## Support

**Questions?** Contact the backend team.

**API Issues?** Check:

1. Service health: `curl http://localhost:8000/health`
2. Docker logs: `docker compose logs api`
3. Swagger UI: http://localhost:8000/docs

**Last Updated:** 2026-02-03  
**API Version:** 1.0.0
