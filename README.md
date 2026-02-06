# Healthcare AI Microservice Backend

A production-ready, HIPAA-compliant microservice backend for a healthcare AI system leveraging AWS Bedrock (Claude 3.5 Sonnet), AWS Textract, and a 3-Tier Data Processing Pipeline.

## 🚀 Features

- **Patient Onboarding**: 40-question health questionnaire with risk assessment
- **Doctor Credential Verification**: OCR-based credential extraction and verification
- **3-Tier Document Processing**: OCR → Vision Analysis → RAG Indexing
- **AI-Powered Chat**: Separate chat contexts for patients and doctors with RAG
- **Health & Wellness Scoring**: Dynamic scoring based on questionnaire and medical data
- **Risk Assessment**: Automatic categorization (High/Medium/Low) with recommendations
- **Mock Data System**: Pre-populated with 15 patients and 7 doctors for testing

## 📋 Prerequisites

- Docker and Docker Compose
- AWS Account with Bedrock and Textract access
- Python 3.11+ (for local development)

## 🛠️ Quick Start

### 1. Clone and Configure

```bash
cd /media/op/DATA/Omkar/CODE-111/Liomonk/Healthcare+

# Environment variables are already in .env
# Verify AWS credentials are set:
cat .env
```

### 2. Start Services with Docker

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

This will start:

- **PostgreSQL** with pgvector extension (port 5432)
- **Redis** for Celery (port 6379)
- **FastAPI Application** (port 8000)
- **Celery Worker** for async document processing
- **Celery Beat** for scheduled tasks

### 3. Seed Database with Mock Data

```bash
# Wait for services to be healthy, then seed database
docker-compose exec api python -m app.mock_data.seed_database
```

This creates:

- 15 mock patients (60% low risk, 30% medium risk, 10% high risk)
- 7 mock doctors (80% verified, 20% pending)
- 45+ medical documents (lab reports, mammography, consultation notes)

### 4. Access the API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📁 Project Structure

```
Healthcare+/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Settings and configuration
│   ├── database.py             # Database connection
│   ├── models/                 # SQLAlchemy models
│   │   ├── patient.py          # Patient & Doctor models
│   │   ├── document.py         # Medical document model
│   │   ├── health_score.py     # Health scores & risk assessments
│   │   ├── vector_store.py     # Document chunks with pgvector
│   │   └── conversation.py     # Chat conversation models
│   ├── schemas/                # Pydantic schemas (TODO)
│   ├── api/v1/                 # API endpoints (TODO)
│   ├── services/               # Business logic (TODO)
│   ├── tasks/                  # Celery tasks
│   │   └── celery_app.py       # Celery configuration
│   ├── utils/                  # Utilities (TODO)
│   └── mock_data/              # Mock data generators
│       ├── patients.py         # Patient generator
│       ├── doctors.py          # Doctor generator
│       ├── documents.py        # Document generator
│       └── seed_database.py    # Database seeding script
├── _documents/                 # Mock document storage
│   ├── patients/               # Patient documents
│   └── doctors/                # Doctor credentials
├── tests/                      # Test suite (TODO)
├── docker-compose.yml          # Docker services
├── Dockerfile                  # Application container
├── requirements.txt            # Python dependencies
└── .env                        # Environment variables
```

## 🗄️ Database Schema

### Core Tables

- **patients**: Patient demographic data and questionnaire responses (JSONB)
- **doctors**: Doctor information with OCR-extracted credentials (JSONB)
- **medical_documents**: Document metadata with 3-tier processing status
- **health_scores**: Calculated health scores with component breakdown
- **risk_assessments**: Risk categorization with markers and recommendations
- **document_chunks**: Text chunks with embeddings for RAG (pgvector)
- **patient_conversations**: Patient chat history
- **doctor_conversations**: Doctor chat history per patient

## 🧪 Mock Data Details

### Patient Questionnaire (40 Questions)

Based on `Ai Anlytics _Markers.xlsx`:

1. **Demographics**: Age, gender
2. **Breast Cancer History**: Previous diagnosis, treatment
3. **Family History**: Relatives with cancer, BRCA mutations
4. **Symptoms**: Lumps, pain, discharge, skin changes
5. **Screening History**: Mammograms, breast density
6. **Lifestyle**: Hormones, pregnancy, alcohol, smoking
7. **Medical History**: Other cancers, radiation, benign disease
8. **Current Concerns**: Recent changes, duration
9. **Infection/Inflammation**: Mastitis, fever
10. **System Intelligence**: Patient intuition, booking needs

### Risk Levels

**High Risk Markers**:

- New hard lump
- Bloody nipple discharge
- Skin dimpling
- BRCA1/BRCA2 mutation
- Strong family history (mother/sister)
- Prior chest radiation

**Medium Risk Markers**:

- Localized breast pain
- Dense breasts
- Family history (2nd degree relative)
- Hormonal risk factors
- Prior benign breast disease

**Low Risk Markers**:

- No symptoms
- Regular screening up to date
- No family history

### Blood Test Markers

**Stage 1 (Low Risk)**:

- Heart: Cholesterol, HDL, LDL, Triglycerides
- Insulin: Glucose, HbA1c
- Kidney: Creatinine, eGFR, Urea
- Liver: ALT, ALP, Bilirubin
- Blood Count: Hemoglobin, Iron, Ferritin
- Thyroid: TSH, T3, T4
- Vitamins: D, B12, Calcium

**Stage 2 (Medium/High Risk)**:

- All Stage 1 tests
- BRCA1 & BRCA2 genetic testing
- Tumor marker tests (CA 15-3, CA 27-29)

**Stage 3 (Breast Cancer Patients)**:

- All Stage 1 & 2 tests
- Biopsy results
- Treatment monitoring
- Radiation results

## 🔧 Development

### Local Development (without Docker)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL and Redis manually or use Docker for just these services
docker-compose up postgres redis -d

# Run FastAPI
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# End-to-end tests
pytest tests/e2e/ -v

# With coverage
pytest --cov=app --cov-report=html
```

## 📊 API Endpoints (Planned)

### Chat & Document Endpoints (Unified)

- `POST /api/v1/chat/patient/{uuid}` - Patient chat with AI guardrails
- `POST /api/v1/chat/doctor/{uuid}` - Doctor general AI chat
- `POST /api/v1/chat/doctor/{uuid}/patient/{p_uuid}` - Doctor chat specific to a patient
- `POST /api/v1/chat/patient/{uuid}/upload` - Patient document upload
- `POST /api/v1/chat/doctor/{uuid}/upload` - Doctor document upload for patient
- `GET /api/v1/chat/documents/{id}/status` - Document processing status
- `GET /api/v1/chat/patient/{uuid}/history` - Patient chat history
- `GET /api/v1/chat/patient/{uuid}/documents` - List of patient documents

### Patient Management Endpoints

- `GET /api/v1/patients/{uuid}/health-score` - View latest health score
- `GET /api/v1/patients/{uuid}/risk-assessment` - View latest risk assessment

### Doctor Management Endpoints

- `GET /api/v1/doctors/{uuid}/patients` - List all patients accessible to doctor

### Utility Endpoints

- `POST /api/v1/rag/refresh` - Manually trigger RAG index refresh
- `POST /api/v1/ocr/doctor-credentials` - Standalone OCR for medical credentials

## 🔐 Security

- AI Guardrails for Patients (Emergency detection, complex query redirection)
- Unrestricted AI access for Doctors (Medical analysis mode)
- JWT-based authentication (TODO)
- Data encryption at rest
- HIPAA compliance measures

## 🚧 Current Status

**Completed**:

- ✅ Project structure and Docker setup
- ✅ Database models with pgvector and pgvector search indexing
- ✅ Mock data system with 15 patients and 7 doctors
- ✅ Unified Chat API for Patients and Doctors
- ✅ AI Guardrails service for Patient Safety
- ✅ RAG system with direct SQL vector similarity search
- ✅ Standalone OCR service for Doctor Credentials using Bedrock Vision
- ✅ 3-Tier document processing pipeline (OCR → Analysis → RAG)
- ✅ Comprehensive API Documentation (CHATBOT_API_FLOW.md)
- ✅ Health scoring and Risk assessment logic

**TODO**:

- ⏳ Authentication & Role-Based Access Control (RBAC)
- ⏳ Multi-modal chat (Images/PDFs directly in chat)
- ⏳ Full test suite with unit/integration tests
- ⏳ Production deployment configuration

## 📝 License

Proprietary - Healthcare AI System

## 👥 Contributors

- Development Team: Liomonk Healthcare+

---

For detailed implementation plan, see `implementation_plan.md` in the artifacts directory.
