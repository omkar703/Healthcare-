# Healthcare AI Microservice Backend - System Design Prompt

## Project Overview

Design and implement a production-ready, HIPAA-compliant microservice backend for a healthcare AI system that serves two primary user roles: Patients and Doctors. The system leverages AWS Bedrock (Claude 3.5 Sonnet), AWS Textract, and a 3-Tier Data Processing Pipeline to provide intelligent health insights, risk assessments, and conversational AI capabilities.

---

## Core Technology Stack

### AI & Processing Layer

- **Foundation Model**: Anthropic Claude 3.5 Sonnet (`anthropic.claude-3-sonnet-20240229-v1:0`)
  - Configuration: `max_tokens: 2048`, API version: `bedrock-2023-05-31`
  - Streaming responses via `invoke_model_with_response_stream`
- **OCR/Text Extraction**: AWS Textract (Synchronous `detect_document_text`)
- **PDF Processing**: PyPDF2 (fallback for local processing)
- **Vision Analysis**: Claude Vision (multi-modal image analysis)
- **Vector Database**: PostgreSQL with `pgvector` extension for semantic search
- **Asynchronous Processing**: Celery with Redis for background jobs

### Storage & Database Architecture

- **Primary Database**: PostgreSQL (patient data, medical history, documents metadata)
- **Vector Database**: pgvector-enabled PostgreSQL (RAG system, embeddings)
- **Separate Chat Databases**:
  - Patient Chat DB: Stores patient-AI conversations with context
  - Doctor Chat DB: Stores doctor-AI conversations per patient UUID (1 doctor → N patients → N chat contexts)
- **Document Storage**: S3 or equivalent for raw medical documents

---

## System Architecture Requirements

### 1. User Roles & Authentication

#### Patient Role

- Unique UUID per patient
- Onboarding questionnaire data (medical history)
- Medical documents (PDFs, images)
- Ongoing updates from doctor consultations
- Chat history with AI assistant

#### Doctor Role

- Unique UUID per doctor
- Verified credentials (degree, license via OCR)
- Access to multiple patient records via patient UUID
- Separate chat context per patient
- Example: 1 doctor with 5 patients = 5 separate chat threads with AI, each trained on respective patient's RAG data

---

## 2. Three-Tier Data Processing Pipeline

### Tier 1: Ingestion & Raw Extraction

**Trigger**: Document upload endpoint
**Process**:

- Validate file type (PDF, JPG, PNG) and size
- Route to appropriate extraction method:
  - Images → AWS Textract OCR
  - PDFs → PyPDF2 text extraction
- Store raw unstructured text blocks
- Mark document status: `INGESTED`

**Output**: Raw text content linked to patient UUID

### Tier 2: Structure & Vision Analysis

**Trigger**: Automatic post-Tier 1 processing
**Process**:

- Identify embedded images in documents
- Use Claude Vision to analyze medical images (X-rays, charts, lab results)
- Convert visual data to descriptive text annotations
- Extract medical markers and risk indicators (reference uploaded images for risk categorization)
- Enhance text blocks with visual descriptions

**Output**: Enriched structured text with visual analysis

### Tier 3: Indexing & RAG Preparation

**Process**:

- Chunk text into semantic window-sized segments
- Generate embeddings using Claude
- Apply metadata tagging (patient UUID, document type, date, risk markers)
- Store in vector database (pgvector)
- Update patient's RAG index
- Mark document status: `INDEXED`

**Output**: Queryable vector store ready for RAG-based retrieval

**Important**: Use Celery workers for Tier 2 and 3 processing to handle asynchronous heavy AI workloads. Return `202 Accepted` immediately after Tier 1.

---

## 3. API Endpoints Specification

### A. Patient Onboarding

**Endpoint**: `POST /api/v1/patients/onboard`
**Purpose**: Collect initial medical history questionnaire
**Input**:

- Patient demographic data
- Answers to medical history questions (reference uploaded spreadsheet)
- Initial risk assessment data
  **Output**: Patient UUID
  **Action**: Store in primary database, trigger initial health score calculation

### B. Document Upload

**Endpoint**: `POST /api/v1/documents/upload`
**Input**:

- Patient UUID
- Document file (PDF/image)
- Document type metadata
  **Output**: `202 Accepted` with job ID
  **Action**: Initiate 3-Tier pipeline processing

### C. RAG System Trigger (Critical)

**Endpoint**: `POST /api/v1/rag/refresh`
**Input**: Patient UUID
**Purpose**: Recalculate all AI-generated insights after database updates
**Trigger Scenarios**:

- New doctor consultation notes added
- New medical reports uploaded
- Medical history updated
- Treatment changes recorded
  **Action**:
- Fetch all updated data for patient UUID
- Rebuild RAG vector index
- Recalculate health scores
- Update risk assessments
- Refresh all cached AI responses
  **Output**: Updated health metrics and confirmation

### D. Health & Wellness Score

**Endpoint**: `GET /api/v1/patients/{uuid}/health-score`
**Output Structure**:

```json
{
  "overall_score": 78,
  "trend": "+5",
  "last_updated": "2025-02-03T10:30:00Z",
  "components": {
    "screening_compliance": {
      "score": 85,
      "status": "good",
      "description": "Regular check-ups maintained"
    },
    "physical_activity": {
      "score": 70,
      "status": "moderate",
      "description": "Based on activity logs and consultations"
    },
    "stress_relaxation": {
      "score": 75,
      "status": "good",
      "description": "Stress management practices noted"
    },
    "healthy_nutrition": {
      "score": 80,
      "status": "good",
      "description": "Balanced diet patterns observed"
    },
    "regular_health_tests": {
      "score": 90,
      "status": "excellent",
      "description": "All recommended tests up to date"
    },
    "follow_up_adherence": {
      "score": 65,
      "status": "needs_improvement",
      "description": "Some missed follow-up appointments"
    }
  }
}
```

**Calculation Logic**:

- Analyze patient's complete medical history
- Review consultation notes
- Check uploaded reports and test results
- Assess adherence to recommendations
- If data unavailable for component, mark as "none" or "insufficient_data"
- Dynamic recalculation after RAG refresh trigger

### E. Risk Assessment

**Endpoint**: `GET /api/v1/patients/{uuid}/risk-assessment`
**Output Structure**:

```json
{
  "overall_risk": "MEDIUM",
  "risk_categories": {
    "high_risk": [
      {
        "indicator": "New hard lump",
        "detected_date": "2025-01-15",
        "source": "Self-reported symptom"
      },
      {
        "indicator": "Strong family history",
        "detected_date": "2024-12-01",
        "source": "Onboarding questionnaire"
      }
    ],
    "medium_risk": [
      {
        "indicator": "Dense breasts",
        "detected_date": "2024-11-20",
        "source": "Mammography report"
      },
      {
        "indicator": "Hormonal risk factors",
        "detected_date": "2024-10-10",
        "source": "Medical history"
      }
    ],
    "low_risk": [
      {
        "indicator": "Regular screening up to date",
        "detected_date": "2025-01-30",
        "source": "Lab results"
      }
    ]
  },
  "recommendation": "Schedule consultation with oncologist within 2 weeks",
  "urgency": "HIGH"
}
```

**Risk Detection Logic** (reference uploaded images):

- **High Risk Markers**: New hard lump, bloody nipple discharge, skin dimpling/peau d'orange, rapidly growing mass, nipple retraction (new), strong family history, known BRCA mutation, prior chest radiation, prior breast cancer
- **Medium Risk Markers**: Localized breast pain, family history in second-degree relative, dense breasts, hormonal risk factors, prior benign breast disease
- **Low Risk Markers**: No lump, no skin/nipple changes, cyclical breast pain only, no family history, regular screening up to date

### F. Patient Chat with AI

**Endpoint**: `POST /api/v1/patients/{uuid}/chat`
**Input**:

```json
{
  "message": "What does my recent blood test mean?",
  "conversation_id": "optional-existing-conversation-id"
}
```

**Output**:

```json
{
  "response": "Based on your recent blood test from January 28th, your hemoglobin levels are within normal range...",
  "sources": [
    "Blood Test Report - Jan 28, 2025",
    "Consultation Notes - Dr. Smith"
  ],
  "conversation_id": "conv-uuid-123",
  "requires_doctor_consultation": false
}
```

**Critical Behavior Rules**:

1. **Data Source Restriction**: Only answer based on patient's own database and uploaded documents
2. **No External Knowledge**: Do not generate medical advice from general AI knowledge
3. **Critical Query Handling**: If query involves life-threatening symptoms or requires diagnosis, respond with: "This requires immediate medical evaluation. Please consult your doctor or visit emergency services."
4. **Simple Language**: Explain medical terms in plain, understandable language
5. **Context Retention**: Maintain conversation history per conversation_id
6. **RAG Integration**: Retrieve relevant documents from patient's vector store before responding
7. **Examples of Critical Queries to Redirect**:
   - Severe chest pain
   - Sudden vision loss
   - Signs of stroke
   - Diagnostic requests ("Do I have cancer?")
   - Treatment recommendations without doctor involvement

### G. Doctor Chat with AI

**Endpoint**: `POST /api/v1/doctors/{doctor_uuid}/chat`
**Input**:

```json
{
  "patient_uuid": "patient-uuid-456",
  "message": "Analyze this patient's cardiac risk factors",
  "conversation_id": "optional-existing-conversation-id",
  "additional_context": "Patient reports occasional chest discomfort during exercise"
}
```

**Output**:

```json
{
  "response": "Comprehensive analysis of patient's cardiac profile:\n1. Current Risk Factors: [detailed analysis]\n2. Recent Test Results: [interpretation]\n3. Recommended Actions: [clinical suggestions]",
  "sources": [
    "Lipid Panel - Jan 2025",
    "ECG Report - Dec 2024",
    "Family History"
  ],
  "conversation_id": "doc-conv-uuid-789",
  "patient_summary_stats": {
    "age": 52,
    "last_consultation": "2025-01-15",
    "active_conditions": ["Hypertension", "Prediabetes"]
  }
}
```

**Key Features**:

1. **Full AI Access**: No restrictions on medical advice generation for doctors
2. **Patient Context Loading**: Automatically load complete patient RAG index when patient_uuid provided
3. **Multi-Patient Management**: Separate conversation threads per patient
   - Example: Doctor UUID `doc-001` with patients `patient-A`, `patient-B`, `patient-C`
   - Chat database structure: `doc-001-patient-A`, `doc-001-patient-B`, `doc-001-patient-C`
4. **Additional Context**: Doctors can supplement AI with real-time observations
5. **Clinical Decision Support**: Provide evidence-based suggestions with source citations
6. **Comprehensive Analysis**: Access to full medical history, lab results, imaging reports

### H. Doctor Onboarding & Credential Verification

**Endpoint**: `POST /api/v1/doctors/onboard`
**Input**:

- Doctor personal information
- Medical degree document (PDF/image)
- License certificate (PDF/image)
  **Process**:

1. Upload documents to AWS Textract
2. Extract structured data using OCR
3. Parse into required format
   **Expected Extraction Output**:

```json
{
  "universityName": "All India Institute of Medical Sciences",
  "doctorName": "Dr. Priya Singh",
  "degreeName": "Bachelor of Medicine and Bachelor of Surgery (MBBS)",
  "licenseNumber": "MCI-2015-0045",
  "issueDate": "2015-04-12",
  "verification_status": "PENDING_MANUAL_REVIEW"
}
```

**Output**: Doctor UUID with pending verification status
**Action**: Store credentials, flag for admin verification

---

## 4. Database Schema Considerations

### Primary Database (PostgreSQL)

#### Patients Table

- `patient_uuid` (PK)
- `demographic_data` (JSONB)
- `onboarding_questionnaire` (JSONB)
- `created_at`, `updated_at`
- `last_rag_refresh` (timestamp)

#### Medical_Documents Table

- `document_id` (PK)
- `patient_uuid` (FK)
- `file_path` (S3 URL)
- `document_type` (enum: lab_report, imaging, prescription, consultation_note)
- `upload_date`
- `processing_status` (enum: INGESTED, ANALYZING, INDEXED)
- `tier_1_text` (TEXT)
- `tier_2_enriched` (JSONB)
- `tier_3_indexed` (BOOLEAN)

#### Health_Scores Table

- `score_id` (PK)
- `patient_uuid` (FK)
- `overall_score` (INTEGER)
- `component_scores` (JSONB)
- `calculated_at` (timestamp)
- `version` (for tracking score history)

#### Risk_Assessments Table

- `assessment_id` (PK)
- `patient_uuid` (FK)
- `overall_risk` (enum: HIGH, MEDIUM, LOW)
- `risk_markers` (JSONB)
- `recommendations` (TEXT)
- `assessed_at` (timestamp)

#### Doctors Table

- `doctor_uuid` (PK)
- `name`, `email`, `specialization`
- `credentials` (JSONB - extracted OCR data)
- `verification_status` (enum: PENDING, VERIFIED, REJECTED)
- `created_at`

### Vector Database (pgvector Extension)

#### Document_Chunks Table

- `chunk_id` (PK)
- `patient_uuid` (FK)
- `document_id` (FK)
- `chunk_text` (TEXT)
- `embedding` (VECTOR(1536)) - Claude embeddings
- `metadata` (JSONB - tags, dates, risk markers)
- `created_at`

### Chat Databases

#### Patient_Conversations Table

- `conversation_id` (PK)
- `patient_uuid` (FK)
- `messages` (JSONB array)
- `created_at`, `updated_at`
- `rag_context_ids` (ARRAY of chunk_ids used)

#### Doctor_Conversations Table

- `conversation_id` (PK)
- `doctor_uuid` (FK)
- `patient_uuid` (FK)
- `messages` (JSONB array)
- `additional_context` (TEXT)
- `created_at`, `updated_at`
- `rag_context_ids` (ARRAY of chunk_ids used)

---

## 5. RAG System Architecture

### RAG Refresh Trigger Logic

When `POST /api/v1/rag/refresh` is called:

1. **Fetch Updated Data**:
   - Retrieve all documents for patient UUID
   - Identify new/modified documents since last refresh
   - Pull updated medical history, consultation notes

2. **Reprocess Pipeline**:
   - Run new documents through 3-Tier pipeline
   - Update existing chunks if documents modified
   - Generate new embeddings for changed content

3. **Vector Store Update**:
   - Delete outdated chunks
   - Insert new chunks with embeddings
   - Update metadata tags (risk markers, dates)

4. **Recalculate Insights**:
   - Trigger health score recalculation
   - Update risk assessment
   - Invalidate cached chat responses
   - Update patient summary statistics

5. **Versioning**:
   - Maintain version history of scores/assessments
   - Log refresh timestamp
   - Track what triggered the refresh (new_report, consultation_update, manual_trigger)

### RAG Query Flow (Chat Endpoints)

**For Patient Chat**:

1. User sends message
2. Convert message to embedding
3. Semantic search in patient's vector chunks (top-k=5)
4. Construct prompt:
   - System: "You are a health assistant. Only use provided patient documents. Redirect critical queries to doctors."
   - Context: Retrieved chunks
   - User message
5. Stream Claude response
6. Check response for critical flags
7. Store conversation in patient chat DB

**For Doctor Chat**:

1. Doctor sends message with patient UUID
2. Load patient's complete RAG index
3. Convert message to embedding
4. Semantic search with higher k (top-k=10 for comprehensive analysis)
5. Construct prompt:
   - System: "You are a clinical decision support AI. Provide evidence-based analysis."
   - Context: Retrieved chunks + doctor's additional context
   - Medical knowledge: Full Claude capabilities
   - User message
6. Stream Claude response with citations
7. Store in doctor-patient chat DB

---

## 6. Stage-Based Health Markers & Testing

Reference the uploaded image for testing protocols:

### Stage 1 (Basics - Low Risk)

**Recommended Tests**:

- Heart: Total cholesterol, HDL, LDL, triglycerides
- Insulin: Glucose, HbA1c
- Kidney: Creatinine, eGFR, Urea
- Liver: ALT, ALP, Bilirubin
- Blood Count: Hemoglobin, Hematocrit, Iron, Ferritin
- Thyroid: TSH, Free T3, Free T4
- Vitamins: Vitamin D, B12, Calcium

### Stage 2 (Medium & High Risk)

**Additional Tests**:

- BRCA1 & BRCA2 genetic testing
- Tumor marker tests

### Stage 3 (Breast Cancer Patients)

**Ongoing Monitoring**:

- All Stage 1 & 2 tests
- Biopsy results tracking
- Treatment results monitoring
- Radiation therapy results

**Implementation**: When calculating health scores, check if recommended tests for patient's risk stage are present in recent documents. Adjust component scores accordingly.

---

## 7. Security & Compliance (HIPAA)

### Data Protection

1. **Zero Retention**: Use AWS Bedrock in stateless mode - no training on patient data
2. **Encryption**:
   - TLS 1.3 for all API communications
   - Images sent as Base64 within encrypted payload
   - Text extraction in encrypted memory/temp storage
   - Database encryption at rest (AES-256)
3. **Access Control**:
   - JWT-based authentication
   - Role-based access (patient, doctor, admin)
   - Patient data isolation by UUID
   - Audit logging for all data access

### Privacy Safeguards

1. **Data Minimization**: Only store necessary medical information
2. **Patient Consent**: Explicit consent for AI processing
3. **Right to Deletion**: Implement data purge endpoints
4. **Audit Trails**: Log all AI interactions, document access, score calculations

---

## 8. Scalability & Performance

### Architecture Patterns

1. **Asynchronous Processing**:
   - Celery workers for Tier 2/3 pipeline
   - Redis queue for job management
   - Return `202 Accepted` for long-running operations

2. **Caching Strategy**:
   - Redis cache for health scores (TTL: 1 hour or until RAG refresh)
   - Cache RAG query results with patient UUID + message hash
   - Invalidate cache on data updates

3. **Database Optimization**:
   - pgvector indexes on embeddings
   - Partitioning for chat history by date
   - Connection pooling for high concurrency

4. **Streaming Responses**:
   - Use `invoke_model_with_response_stream` for chat
   - Server-sent events (SSE) for real-time AI responses

### Load Handling

- Horizontal scaling of API servers (stateless)
- Dedicated Celery worker pools for AI processing
- Read replicas for vector database queries
- CDN for static assets (if any)

---

## 9. Error Handling & Edge Cases

### Document Processing Failures

- **OCR Failure**: Fallback to manual review queue
- **Corrupted PDF**: Return clear error, request re-upload
- **Unsupported Format**: Validation before Tier 1

### AI Response Issues

- **Hallucination Detection**: Always cite sources, flag uncertain responses
- **Context Window Overflow**: Chunk conversations, summarize history
- **Rate Limiting**: Queue requests during high load

### Data Consistency

- **Concurrent Updates**: Optimistic locking on patient records
- **RAG Refresh Conflicts**: Queue multiple triggers, process sequentially
- **Chat Context Staleness**: Timestamp-based cache invalidation

---

## 10. Monitoring & Observability

### Key Metrics

1. **Performance**:
   - Document processing time (per tier)
   - RAG query latency (p50, p95, p99)
   - API response times
   - Celery queue lengths

2. **AI Quality**:
   - Chat response accuracy (user feedback)
   - Source citation rate
   - Critical query detection rate

3. **Business Metrics**:
   - Health score distribution
   - Risk assessment trends
   - Doctor-patient interaction frequency

### Logging

- Structured JSON logs (ELK stack compatible)
- Log levels: DEBUG (dev), INFO (prod)
- Sensitive data redaction (PII/PHI)
- Correlation IDs for request tracing

---

## 11. Environment Configuration

### Required Environment Variables

```
# AWS Credentials
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1

# AWS Bedrock
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
BEDROCK_MAX_TOKENS=2048

# AWS Textract
TEXTRACT_REGION=us-east-1

# Database
DATABASE_URL=postgresql://user:pass@host:5432/healthcare_db
VECTOR_DB_URL=postgresql://user:pass@host:5432/healthcare_vector_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET_KEY=
ENCRYPTION_KEY=

# Feature Flags
ENABLE_VISION_ANALYSIS=true
ENABLE_AUTO_RAG_REFRESH=true
```

---

## 12. API Response Standards

### Success Response Format

```json
{
  "status": "success",
  "data": { ... },
  "metadata": {
    "timestamp": "2025-02-03T10:30:00Z",
    "request_id": "req-uuid-123"
  }
}
```

### Error Response Format

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_PATIENT_UUID",
    "message": "The provided patient UUID does not exist",
    "details": { ... }
  },
  "metadata": {
    "timestamp": "2025-02-03T10:30:00Z",
    "request_id": "req-uuid-123"
  }
}
```

### Async Job Response

```json
{
  "status": "accepted",
  "job_id": "job-uuid-456",
  "message": "Document processing initiated",
  "status_url": "/api/v1/jobs/job-uuid-456/status"
}
```

---

## 13. Testing Requirements

### Unit Tests

- Document processing functions (all tiers)
- Risk assessment logic
- Health score calculation
- RAG query mechanisms

### Integration Tests

- AWS Textract integration
- AWS Bedrock API calls
- Database operations
- Celery job execution

### End-to-End Tests

- Patient onboarding flow
- Document upload → processing → indexing
- RAG refresh trigger → score update
- Chat conversations with context retention

### Load Tests

- Concurrent document uploads
- Simultaneous chat sessions
- RAG query throughput
- Vector search performance

---

## 14. Future Enhancements (Planned)

1. **Audio Transcription**: AWS Transcribe for doctor consultation recordings
2. **Real-time Collaboration**: WebSocket support for live doctor-patient consultations
3. **Predictive Analytics**: ML models for health trend forecasting
4. **Multi-language Support**: Translate medical documents and chat responses
5. **Mobile SDK**: Native mobile integration for chat features

---

## 15. Deployment Specifications

### Infrastructure Requirements

- **Compute**: Auto-scaling container orchestration (ECS/Kubernetes)
- **Database**: RDS PostgreSQL with pgvector extension
- **Storage**: S3 for documents with lifecycle policies
- **Queue**: ElastiCache Redis for Celery
- **Load Balancer**: ALB with health checks

### CI/CD Pipeline

1. Code commit → automated tests
2. Docker image build
3. Security scanning (vulnerability checks)
4. Staging deployment
5. Integration tests on staging
6. Production deployment (blue-green)
7. Health checks and rollback capability

### Disaster Recovery

- Automated database backups (daily)
- Point-in-time recovery enabled
- Multi-region replication for critical data
- Backup restoration testing (monthly)

---

## 16. Documentation Deliverables

1. **API Documentation**: OpenAPI/Swagger specification
2. **Architecture Diagrams**: System flow, database schema, deployment topology
3. **Developer Guide**: Setup instructions, local development, testing
4. **Operations Manual**: Deployment, monitoring, troubleshooting
5. **Security Audit**: HIPAA compliance checklist, penetration test results

---

## Success Criteria

The system is considered production-ready when:

1. ✅ All API endpoints respond within SLA (< 2s for sync, < 30s for async jobs)
2. ✅ Document processing pipeline achieves 95%+ success rate
3. ✅ RAG system retrieves relevant context with 90%+ accuracy
4. ✅ Health score calculations update within 5 minutes of data changes
5. ✅ Chat responses cite sources 100% of the time
6. ✅ Zero unauthorized data access incidents
7. ✅ 99.9% uptime over 30-day period
8. ✅ All HIPAA compliance requirements met
9. ✅ Load tests pass with 1000 concurrent users
10. ✅ Doctor and patient feedback scores > 4.5/5

---

## Additional Context & References

- **Onboarding Questions**: Refer to uploaded spreadsheet `Ai_Anlytics__Markers.xlsx`
- **Health Score UI**: Reference uploaded image showing 78/100 wellness score with component breakdown
- **Risk Categories**: Reference uploaded images showing High/Medium/Low risk markers
- **Testing Protocols**: Reference uploaded image showing Stage 1/2/3 test requirements

---

## Final Notes

This microservice must be:

- **Scalable**: Handle thousands of patients and hundreds of concurrent doctors
- **Reliable**: 99.9% uptime with graceful degradation
- **Secure**: HIPAA-compliant with audit trails
- **Fast**: Real-time chat responses, quick document processing
- **Accurate**: AI responses grounded in patient data, not hallucinations
- **Maintainable**: Clean code, comprehensive tests, clear documentation

The RAG refresh trigger is the heartbeat of the system - it ensures all AI insights stay current as patient data evolves. Treat it as a critical path operation with high priority.

Build this system with the understanding that it will directly impact patient care and clinical decision-making. Quality, security, and reliability are non-negotiable.
