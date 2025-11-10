# Deployment Guide

## Local Development Deployment

### Quick Start (Recommended)

The fastest way to start the entire application:

```bash
./start-all.sh
```

This script will:
- Start the backend server on port 8000
- Start the frontend development server on port 5173
- Display access URLs and process IDs
- Create log files in `logs/` directory
- Handle graceful shutdown with Ctrl+C

### Manual Start (Alternative)

If you prefer to run servers in separate terminal windows:

**Terminal 1 - Backend:**
```bash
./start-backend.sh
```

**Terminal 2 - Frontend:**
```bash
./start-frontend.sh
```

### First Time Setup

Before running the application for the first time:

**1. Backend Setup:**
```bash
cd backend

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# OR
.venv\Scripts\activate     # On Windows

# Install dependencies
uv pip install -e ".[dev]"

# Create environment file
cp .env.example .env

# Edit .env and add your Anthropic API key
# Required: ANTHROPIC_API_KEY=your_key_here
```

**2. Frontend Setup:**
```bash
cd frontend

# Install dependencies
npm install

# Create environment file (optional - defaults provided)
echo "VITE_API_URL=http://localhost:8000" > .env
```

**3. Get Anthropic API Key:**
- Visit https://console.anthropic.com/
- Create an account or sign in
- Navigate to API Keys section
- Generate a new API key
- Add to `backend/.env`: `ANTHROPIC_API_KEY=your_key_here`

## Environment Variables

### Backend Configuration

File: `backend/.env`

```bash
# Required - Anthropic API key for Claude
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Database configuration
DATABASE_URL=sqlite:///./starhub_comms.db

# Optional - API configuration
API_HOST=0.0.0.0
API_PORT=8000

# Optional - CORS settings (comma-separated origins)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend Configuration

File: `frontend/.env`

```bash
# Backend API URL
VITE_API_URL=http://localhost:8000
```

## Accessing the Application

Once both servers are running:

- **Frontend Application**: http://localhost:5173
  - Main user interface for creating and managing campaigns

- **Backend API**: http://localhost:8000
  - REST API endpoints
  - Health check: http://localhost:8000/health

- **API Documentation**: http://localhost:8000/docs
  - Interactive Swagger UI documentation
  - Test API endpoints directly from browser

## Troubleshooting

### Backend Issues

**Problem: Backend won't start**
```bash
# Check if virtual environment exists
ls backend/.venv

# If missing, recreate:
cd backend
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

**Problem: "Module not found" errors**
```bash
# Reinstall dependencies
cd backend
source .venv/bin/activate
uv pip install -e ".[dev]"
```

**Problem: "API key not configured" warning**
```bash
# Check .env file exists
ls backend/.env

# Verify API key is set
grep ANTHROPIC_API_KEY backend/.env

# Should show: ANTHROPIC_API_KEY=sk-ant-...
# If not, edit backend/.env and add your key
```

**Problem: Port 8000 already in use**
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or change port in backend/.env
API_PORT=8001
```

### Frontend Issues

**Problem: Frontend won't start**
```bash
# Check if node_modules exists
ls frontend/node_modules

# If missing, install:
cd frontend
npm install
```

**Problem: "Cannot connect to backend" errors**
```bash
# 1. Verify backend is running
curl http://localhost:8000/health

# 2. Check frontend .env points to correct backend URL
cat frontend/.env
# Should show: VITE_API_URL=http://localhost:8000

# 3. Restart frontend after changing .env
```

**Problem: Port 5173 already in use**
```bash
# Vite will automatically try the next available port
# Or specify a different port:
npm run dev -- --port 3000
```

### Common Issues

**Problem: CORS errors in browser console**
```bash
# Backend CORS configuration in backend/main.py should include frontend URL
# Default: http://localhost:5173
# If running on different port, update CORS_ORIGINS in backend/.env
```

**Problem: Database locked errors**
```bash
# SQLite database locked - another process is accessing it
# Solution: Stop all backend processes and restart

# Find backend processes
ps aux | grep uvicorn

# Kill processes
kill <PID>

# Restart backend
./start-backend.sh
```

## Production Deployment (Future Roadmap)

The current MVP is configured for local development. For production deployment:

### Backend Production

**Recommended Stack:**
- **Database**: Migrate from SQLite to PostgreSQL
- **Server**: Gunicorn with Uvicorn workers
- **Hosting**: AWS EC2, Azure App Service, or GCP Cloud Run
- **Reverse Proxy**: Nginx for SSL termination and load balancing

**Production Configuration:**

```bash
# Install production dependencies
pip install gunicorn psycopg2-binary

# Update DATABASE_URL for PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/starhub_comms

# Run with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Environment Variables:**
```bash
# Production .env
ANTHROPIC_API_KEY=<production_key>
DATABASE_URL=postgresql://user:password@host:5432/dbname
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://comms.starhub.com
LOG_LEVEL=INFO
ENVIRONMENT=production
```

**Security Considerations:**
- Use environment variable management service (AWS Secrets Manager, Azure Key Vault)
- Enable HTTPS with valid SSL certificates
- Implement rate limiting
- Add authentication and authorization
- Set up database connection pooling
- Configure backup and disaster recovery

### Frontend Production

**Build Process:**
```bash
cd frontend

# Build for production
npm run build

# Output will be in frontend/dist/
```

**Hosting Options:**
1. **Static File Hosting**:
   - AWS S3 + CloudFront
   - Azure Static Web Apps
   - Netlify
   - Vercel

2. **Traditional Web Server**:
   - Nginx serving static files
   - Apache with mod_rewrite

**Nginx Configuration Example:**
```nginx
server {
    listen 80;
    server_name comms.starhub.com;

    root /var/www/starhub-comms/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Production Environment Variables:**
```bash
# Build-time environment variables
VITE_API_URL=https://api.starhub.com
VITE_ENVIRONMENT=production
```

### Database Migration (SQLite to PostgreSQL)

**1. Install PostgreSQL:**
```bash
# macOS
brew install postgresql

# Ubuntu
sudo apt-get install postgresql postgresql-contrib

# Windows
# Download from https://www.postgresql.org/download/windows/
```

**2. Create Database:**
```sql
CREATE DATABASE starhub_comms;
CREATE USER starhub_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE starhub_comms TO starhub_user;
```

**3. Update Connection String:**
```bash
# backend/.env
DATABASE_URL=postgresql://starhub_user:secure_password@localhost:5432/starhub_comms
```

**4. Migrate Data:**
```bash
# Export from SQLite
sqlite3 backend/starhub_comms.db .dump > backup.sql

# Import to PostgreSQL (requires manual SQL adjustment for compatibility)
psql -U starhub_user -d starhub_comms -f backup.sql
```

### Monitoring and Logging

**Production Logging:**
```python
# backend/main.py - Add logging configuration
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
handler = RotatingFileHandler('logs/app.log', maxBytes=10000000, backupCount=5)
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
```

**Monitoring Tools:**
- Application Performance: New Relic, DataDog, or Sentry
- Server Monitoring: Prometheus + Grafana
- Log Aggregation: ELK Stack (Elasticsearch, Logstash, Kibana)
- Uptime Monitoring: Pingdom, UptimeRobot

### Backup and Recovery

**Database Backup:**
```bash
# PostgreSQL backup
pg_dump -U starhub_user starhub_comms > backup_$(date +%Y%m%d).sql

# Automated daily backups (cron)
0 2 * * * /usr/bin/pg_dump -U starhub_user starhub_comms > /backups/starhub_$(date +\%Y\%m\%d).sql
```

**File Backup:**
- Backend environment files
- Static assets
- Configuration files
- SSL certificates

### Scaling Considerations

**Horizontal Scaling:**
- Load balancer (AWS ELB, Nginx)
- Multiple backend instances
- Shared PostgreSQL database
- Redis for session management (future feature)

**Vertical Scaling:**
- Increase server resources (CPU, RAM)
- Optimize database queries
- Implement caching (Redis, Memcached)
- CDN for static assets

## Development Workflow

### Local Development
```bash
# Start development environment
./start-all.sh

# Make changes to code
# Backend: Changes auto-reload with --reload flag
# Frontend: Changes auto-refresh with Vite HMR

# Run tests
cd backend && uv run pytest
cd frontend && npm test

# Stop servers
# Press Ctrl+C in terminal running start-all.sh
```

### Testing Deployment Scripts
```bash
# Test backend startup
./start-backend.sh
# Verify: http://localhost:8000/health returns 200

# Test frontend startup (new terminal)
./start-frontend.sh
# Verify: http://localhost:5173 loads

# Test full startup
./start-all.sh
# Verify: Both servers accessible
```

## Support

For issues or questions:
1. Check this deployment guide
2. Review API documentation at http://localhost:8000/docs
3. Check application logs in `logs/` directory
4. Review backend logs: `logs/backend.log`
5. Review frontend logs: `logs/frontend.log`

## Version Information

- **Backend**: FastAPI + Python 3.10+
- **Frontend**: React 18 + TypeScript + Vite
- **Database**: SQLite (MVP) / PostgreSQL (Production)
- **AI Service**: Anthropic Claude API
- **Package Management**: uv (backend) / npm (frontend)
