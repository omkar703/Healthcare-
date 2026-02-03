# Docker Setup Instructions

## Issue: Path Sharing Error

Docker is encountering a path sharing error because the project directory is not configured as a shared path.

## Solution

### Option 1: Configure Docker Desktop (Recommended)

1. Open Docker Desktop
2. Go to **Settings** → **Resources** → **File Sharing**
3. Add the path: `/media/op/DATA/Omkar/CODE-111/Liomonk/Healthcare+`
4. Click **Apply & Restart**
5. Run `docker compose up -d` again

### Option 2: Use Docker CLI to Add Shared Path

```bash
# For Docker Desktop on Linux
docker context use default
```

### Option 3: Run Without Volume Mounts (Testing Only)

If you just want to test the services without live code reloading:

1. Edit `docker-compose.yml`
2. Comment out the `volumes:` sections in `api`, `celery_worker`, and `celery_beat` services
3. Run `docker compose up --build -d`

**Note**: This means code changes won't be reflected without rebuilding.

## Verify Services Are Running

After fixing the path sharing issue:

```bash
# Check service status
docker compose ps

# View logs
docker compose logs -f api

# Access the API
curl http://localhost:8000/health
```

## Next Steps After Docker Is Running

1. **Seed the database**:

   ```bash
   docker compose exec api python -m app.mock_data.seed_database
   ```

2. **Access Swagger UI**:
   - Open browser: http://localhost:8000/docs

3. **Test the API endpoints** (once implemented in Phase 6-7)
