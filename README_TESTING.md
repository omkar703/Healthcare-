# Testing Instructions

## 🚀 Getting Started

This backend is packaged with Docker for easy testing.

### Prerequisites

- Docker Desktop installed and running.

### 1. Start the Application

Open a terminal in this folder and run:

```bash
docker compose up -d
```

Wait about 1-2 minutes for all services to start.

### 2. Verify It's Running

Run the health check:

```bash
curl http://localhost:8000/health
```

You should see `{"status":"healthy"}`.

### 3. Access the API

Open your browser to:
**http://localhost:8000/docs**
You will see the interactive Swagger UI where you can test all endpoints.

### 4. Test OCR & Documents

The system is pre-loaded with mock documents in `_documents/`.
You can upload new documents via the `/api/v1/patients/{uuid}/documents/upload` endpoint.
Supported formats: JPG, PNG, PDF.

### Troubleshooting

If something fails to start:

```bash
docker compose down
docker compose up -d
```

Check logs:

```bash
docker compose logs api
```
