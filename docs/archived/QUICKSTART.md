# QuickStart Guide

Get the StarHub Customer Communications Generator API up and running in 5 minutes.

## Prerequisites

- Python 3.11+
- UV package manager (installed)
- Anthropic API key

## Setup (2 minutes)

### 1. Navigate to Backend Directory

```bash
cd "/Users/asreenivas/Library/CloudStorage/OneDrive-StarHubLtd/02_Data_Analytics/Scripts/29. Customer Comms Generator/backend"
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=your-api-key-here
DATABASE_URL=sqlite:///./starhub_comms.db
```

### 3. Initialize Database (if not already done)

```bash
uv run python -c "from database import init_db; init_db()"
```

## Run Server (30 seconds)

### Start Development Server

```bash
uv run uvicorn main:app --reload
```

**Server URL**: http://localhost:8000
**API Docs**: http://localhost:8000/docs

## Quick Tests (1 minute)

### 1. Health Check

```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "services": {
    "generation": "ready",
    "scoring": "ready",
    "config": "loaded"
  }
}
```

### 2. Get Available Cohorts

```bash
curl http://localhost:8000/api/v1/cohorts
```

### 3. Create a Campaign

```bash
curl -X POST http://localhost:8000/api/v1/campaigns/ \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_name": "Test Campaign",
    "channel": "email",
    "objective": "promotion",
    "product_lines": ["bundle_homehub_plus"],
    "cohorts": ["deal_seekers"],
    "customization": {
      "tone": "friendly",
      "length_preference": "optimal"
    }
  }'
```

### 4. Generate Communications

Replace `{campaign_id}` with the ID from step 3:

```bash
curl -X POST http://localhost:8000/api/v1/campaigns/{campaign_id}/generate
```

## Run Tests (30 seconds)

```bash
# All tests
uv run pytest tests/test_api*.py -v

# Just campaign tests
uv run pytest tests/test_api_campaigns.py -v

# Just utility tests
uv run pytest tests/test_api_utilities.py -v
```

## Interactive API Exploration

Open in browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Common Operations

### List All Campaigns

```bash
curl http://localhost:8000/api/v1/campaigns/
```

### List Campaigns (Filtered)

```bash
# By channel
curl http://localhost:8000/api/v1/campaigns/?channel=email

# With pagination
curl http://localhost:8000/api/v1/campaigns/?skip=0&limit=10
```

### Get Campaign Details

```bash
curl http://localhost:8000/api/v1/campaigns/{campaign_id}
```

### Update Campaign

```bash
curl -X PUT http://localhost:8000/api/v1/campaigns/{campaign_id} \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_name": "Updated Campaign Name",
    "customization": {
      "tone": "urgent",
      "length_preference": "shorter"
    }
  }'
```

### Delete Campaign

```bash
curl -X DELETE http://localhost:8000/api/v1/campaigns/{campaign_id}
```

### Get Communications for Campaign

```bash
curl http://localhost:8000/api/v1/campaigns/{campaign_id}/communications
```

### Select a Communication

```bash
curl -X PUT http://localhost:8000/api/v1/communications/{communication_id} \
  -H "Content-Type: application/json" \
  -d '{"is_selected": true}'
```

## Troubleshooting

### Server Won't Start

**Issue**: Import errors
**Fix**: Ensure you're in the backend directory and using `uv run`

```bash
cd backend
uv run uvicorn main:app --reload
```

### Database Errors

**Issue**: Table doesn't exist
**Fix**: Reinitialize database

```bash
uv run python -c "from database import reset_db; reset_db()"
```

### API Key Not Working

**Issue**: Anthropic API errors
**Fix**: Check `.env` file has correct API key

```bash
cat .env | grep ANTHROPIC_API_KEY
```

### Tests Failing

**Issue**: Old test database
**Fix**: Tests create fresh database automatically, but you can clean up:

```bash
rm -f test_campaigns.db
uv run pytest tests/test_api_campaigns.py -v
```

## Next Steps

1. **Explore API Docs**: Visit http://localhost:8000/docs
2. **Run Full Test Suite**: `uv run pytest tests/ -v`
3. **Read Phase 3 Documentation**: See `PHASE3_COMPLETE.md`
4. **Check Example Workflows**: See `PHASE2_COMPLETE.md` for generation examples
5. **Review Configuration**: Check `app/config/` for cohorts, products, objectives

## Support

- **API Documentation**: http://localhost:8000/docs
- **Project Documentation**: See `README.md`, `PHASE1_COMPLETE.md`, `PHASE2_COMPLETE.md`, `PHASE3_COMPLETE.md`
- **Test Examples**: See `tests/test_api_*.py`

## Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/campaigns/` | POST | Create campaign |
| `/api/v1/campaigns/` | GET | List campaigns |
| `/api/v1/campaigns/{id}` | GET | Get campaign |
| `/api/v1/campaigns/{id}` | PUT | Update campaign |
| `/api/v1/campaigns/{id}` | DELETE | Delete campaign |
| `/api/v1/campaigns/{id}/generate` | POST | Generate variations |
| `/api/v1/cohorts` | GET | List cohorts |
| `/api/v1/products` | GET | List products |
| `/api/v1/objectives` | GET | List objectives |
| `/api/v1/health` | GET | Health check |
| `/docs` | GET | API documentation |

---

**You're ready to go! 🚀**
