# StarHub Customer Communications Generator

AI-powered multi-channel customer communications generator with intelligent recommendation scoring and compliance validation.

## Overview

The StarHub Customer Communications Generator is an intelligent system that helps marketing teams create effective, compliant customer communications across multiple channels (Email, SMS, Push Notifications). Powered by Anthropic's Claude AI, it generates multiple variations of communications and uses a sophisticated 4-pillar scoring system to recommend the most effective option.

## Key Features

- **Multi-Channel Support**: Generate communications optimized for Email, SMS, and Push Notifications
- **AI-Powered Generation**: Creates 5 unique variations per campaign using Claude AI
- **Intelligent Recommendations**: 4-pillar scoring system identifies the best performing variation
  - Cohort Alignment: How well the message resonates with target audience
  - Channel Optimization: Appropriate formatting and length for the channel
  - Brand Consistency: Adherence to StarHub's brand voice and guidelines
  - Engagement Potential: Likelihood to drive customer action
- **Compliance Validation**: Automatic checking for regulatory and brand compliance
- **Flexible Targeting**: Support for 10+ customer cohorts (Deal Seekers, Sports Enthusiasts, etc.)
- **Product Coverage**: All major StarHub product lines (Mobile, HomeHub+, Sports+, etc.)
- **Multiple Objectives**: Promotion, Retention, Upsell, Cross-sell, Service Updates, Onboarding
- **Edit & Export**: Manual editing capability with export to TXT, CSV, and JSON formats
- **Tone Customization**: 8 tone options from Friendly to Urgent to Premium
- **Custom Instructions**: Add specific requirements or context for generation

## Technology Stack

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy (ORM for database operations)
- SQLite (MVP database) / PostgreSQL-ready for production
- Anthropic Claude API (AI generation)
- Pydantic (data validation)

**Frontend:**
- React 18 (UI framework)
- TypeScript (type-safe JavaScript)
- Tailwind CSS (utility-first styling)
- Vite (build tool and dev server)
- Axios (HTTP client)

**Development Tools:**
- uv (Python package manager)
- npm (Node package manager)
- pytest (backend testing)
- ESLint (code linting)

## Quick Start

### Prerequisites

- **Python 3.11 or higher** (automatically managed by UV)
- **Node.js 18 or higher**
- **UV package manager** - Install: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Anthropic API Key** - Get from https://console.anthropic.com/
- **FAL AI API Key** - Get from https://fal.ai/ (for creative generation)

### Automated Setup (Recommended)

```bash
# 1. Clone or navigate to project
cd /path/to/customer-comms-generator

# 2. Run automated setup
./setup.sh

# 3. Configure API keys
cd backend
# Edit .env and add:
#   ANTHROPIC_API_KEY=your_key_here
#   FAL_KEY=your_fal_key_here

# 4. Start the application
./start-all.sh
```

That's it! The setup script handles all dependency installation and configuration.

### Manual Setup (Advanced Users)

For detailed setup instructions, troubleshooting, and UV usage guide, see **[SETUP.md](./SETUP.md)**.

**Quick manual setup:**
```bash
# Backend
cd backend
uv sync --dev              # Install all dependencies (no venv activation needed!)
cp .env.example .env       # Create environment file
# Edit .env with your API keys
uv run alembic upgrade head  # Initialize database

# Frontend
cd frontend
npm install

# Start
./start-backend.sh  # Terminal 1
./start-frontend.sh # Terminal 2
```

**Why UV?** UV is 10-100x faster than pip and ensures reproducible builds across all machines via the `uv.lock` file.

### Access Points

Once running, access the application at:

- **Frontend**: http://localhost:5173 - Main user interface
- **Backend API**: http://localhost:8000 - REST API
- **API Documentation**: http://localhost:8000/docs - Interactive Swagger UI

## Usage

### Creating a Campaign

1. **Select Channel**: Choose Email, SMS, or Push Notification
2. **Choose Cohorts**: Select one or more target customer segments
3. **Select Product**: Pick the product or service to promote
4. **Set Objective**: Choose campaign goal (promotion, retention, etc.)
5. **Enter Promotion Details**: Describe the offer or message
6. **Customize** (Optional):
   - Select tone of voice
   - Add custom instructions
   - Specify required phrases
   - List prohibited words
7. **Generate**: Click "Generate Communications"

### Understanding Results

The system generates 5 unique variations, each with:

- **Overall Score**: 0-100, combining all 4 pillars
- **Cohort Alignment** (30%): Relevance to target audience
- **Channel Optimization** (25%): Format and length appropriateness
- **Brand Consistency** (25%): StarHub brand voice adherence
- **Engagement Potential** (20%): Likelihood to drive action

The **top-scoring variation** is highlighted as the recommended option.

### Editing Communications

1. Select any variation
2. Click "Edit"
3. Modify text while respecting channel limits:
   - Email: Subject 40-60 chars, flexible body
   - SMS: 160 characters total
   - Push: Title 40-50 chars, Body 100-120 chars
4. Save changes - marked with "Edited" badge

### Exporting Communications

**Single Communication:**
- Select a variation
- Click "Export" → Choose format (TXT, CSV, JSON)

**All Variations:**
- Click "Export All" → Choose format
- CSV includes all variations with scores

## Project Structure

```
customer-comms-generator/
├── backend/                    # FastAPI backend
│   ├── main.py                # Application entry point
│   ├── database.py            # Database configuration
│   ├── models.py              # SQLAlchemy models
│   ├── schemas.py             # Pydantic schemas
│   ├── crud.py                # Database operations
│   ├── generation_service.py # AI generation logic
│   ├── scoring.py             # 4-pillar scoring system
│   ├── compliance.py          # Compliance validation
│   ├── tests/                 # Backend tests
│   │   ├── test_api.py
│   │   └── performance_test.py
│   ├── .env                   # Environment variables
│   └── requirements.txt       # Python dependencies
│
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── CampaignForm.tsx
│   │   │   ├── ResultsDisplay.tsx
│   │   │   ├── ScoreBreakdown.tsx
│   │   │   └── EditModal.tsx
│   │   ├── services/         # API client
│   │   │   └── api.ts
│   │   ├── types/            # TypeScript types
│   │   │   └── index.ts
│   │   ├── App.tsx           # Main application
│   │   └── main.tsx          # Entry point
│   ├── public/               # Static assets
│   ├── .env                  # Environment variables
│   └── package.json          # Node dependencies
│
├── docs/                     # Documentation
│   ├── README.md             # Documentation index
│   ├── user/                 # User documentation
│   │   └── USER_GUIDE.md     # Marketing team guide
│   ├── developer/            # Technical documentation
│   │   ├── DEVELOPER_GUIDE.md
│   │   ├── API_REFERENCE.md
│   │   ├── ARCHITECTURE.md   # System architecture
│   │   └── SETUP.md          # Setup instructions
│   ├── operations/           # Deployment documentation
│   │   ├── DEPLOYMENT.md
│   │   └── VALIDATION_CHECKLIST.md
│   ├── project/              # Project documentation
│   │   ├── IMPLEMENTATION_PLAN.md
│   │   ├── KNOWN_ISSUES.md
│   │   ├── FUTURE_ENHANCEMENTS.md
│   │   └── CHANGELOG.md
│   └── archived/             # Historical documentation
│
├── tests/                    # Test suite
│   ├── README.md             # Testing guide
│   ├── backend/              # Backend tests
│   │   ├── unit/             # Unit tests
│   │   ├── integration/      # Integration tests
│   │   └── performance/      # Performance tests
│   ├── frontend/             # Frontend tests (future)
│   └── e2e/                  # End-to-end tests
│       ├── README.md
│       └── test_scenarios.md
│
├── logs/                     # Application logs
│
├── start-all.sh             # Start both servers
├── start-backend.sh         # Start backend only
├── start-frontend.sh        # Start frontend only
├── DEPLOYMENT.md            # Deployment guide
└── README.md                # This file
```

## API Overview

The backend provides a RESTful API with the following main endpoints:

**Campaigns:**
- `POST /campaigns/` - Create a new campaign
- `GET /campaigns/` - List all campaigns
- `GET /campaigns/{id}` - Get campaign details
- `PUT /campaigns/{id}` - Update campaign
- `DELETE /campaigns/{id}` - Delete campaign
- `POST /campaigns/{id}/generate` - Generate communications

**Communications:**
- `GET /communications/` - List all communications
- `GET /communications/{id}` - Get communication details
- `PUT /communications/{id}` - Update/edit communication
- `DELETE /communications/{id}` - Delete communication

**Utility:**
- `GET /health` - Health check endpoint

Full API documentation available at http://localhost:8000/docs when running.

## Testing

All tests are in the [`tests/`](tests/) directory:

- **Backend Tests**: `tests/backend/` (unit, integration, performance)
- **Frontend Tests**: `tests/frontend/` (future)
- **E2E Tests**: `tests/e2e/` (acceptance scenarios)

### Run Backend Tests

```bash
cd backend

# All backend tests
uv run pytest ../tests/backend/ -v

# Unit tests only
uv run pytest ../tests/backend/unit/ -v

# Integration tests only
uv run pytest ../tests/backend/integration/ -v

# Performance tests
uv run python ../tests/backend/performance/test_performance.py

# With coverage
uv run pytest ../tests/backend/ --cov=app --cov-report=html
```

### Run E2E Tests

Manual test scenarios documented in `tests/e2e/test_scenarios.md`.

Execute with both backend and frontend running:

```bash
./start-all.sh
# Then follow scenarios in tests/e2e/test_scenarios.md
```

See the [Testing Guide](tests/README.md) for complete testing documentation.

## Configuration

### Backend Configuration

File: `backend/.env`

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-your_key_here

# Database (SQLite for MVP)
DATABASE_URL=sqlite:///./starhub_comms.db

# API Settings (optional)
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173
```

### Frontend Configuration

File: `frontend/.env`

```bash
# Backend API URL
VITE_API_URL=http://localhost:8000
```

## Customer Cohorts

The system supports the following customer segments:

- **Mass Market**: General customer base
- **Deal Seekers**: Price-conscious customers
- **Sports Enthusiasts**: Sports content consumers
- **Entertainment Lovers**: Entertainment-focused customers
- **Tech Savvy**: Technology early adopters
- **Family Oriented**: Family plan customers
- **Business Users**: B2B customers
- **Young Professionals**: Young working adults
- **Seniors**: Senior citizens
- **High-Value Customers**: Premium segment
- **At-Risk/Churning**: Retention targets

## Product Lines

Supported StarHub products and services:

- Mobile Plans (Prepaid & Postpaid)
- HomeHub+ (Broadband)
- Sports+ (Sports content)
- Entertainment+ (Entertainment packages)
- Mobile Network (Service updates)
- Bundles (Combined offers)

## Communication Channels

### Email
- Subject line: 40-60 characters
- Body: Flexible length
- Includes unsubscribe link for promotional emails
- HTML-ready formatting

### SMS
- Maximum: 160 characters
- Includes opt-out for promotional messages
- Concise, direct messaging

### Push Notification
- Title: 40-50 characters
- Body: 100-120 characters
- Action-oriented, urgent tone

## Compliance Features

Automatic validation for:

- **SMS Promotional**: "Reply STOP to opt-out" requirement
- **Email Promotional**: Unsubscribe link requirement
- **Pricing Transparency**: Terms like "/mth", "contract", "T&Cs apply"
- **Claim Substantiation**: Flags unverified claims ("best", "guaranteed")
- **Free Offers**: Ensures terms and conditions mentioned
- **Character Limits**: Enforces channel-specific constraints

## Troubleshooting

### Common Issues

**Backend won't start:**
- Check Python version: `python --version` (need 3.10+)
- Verify virtual environment activated
- Ensure ANTHROPIC_API_KEY set in .env

**Frontend won't start:**
- Check Node version: `node --version` (need 18+)
- Run `npm install` to ensure dependencies installed
- Verify backend is running on port 8000

**Generation fails:**
- Verify valid ANTHROPIC_API_KEY in backend/.env
- Check API key has available credits
- Review backend logs for error details

**CORS errors:**
- Ensure frontend URL in backend CORS_ORIGINS
- Default should include http://localhost:5173

See `DEPLOYMENT.md` for detailed troubleshooting guide.

## Performance Targets

- Backend API response: < 2 seconds (95th percentile)
- Communication generation: < 10 seconds end-to-end
- Database queries: < 500ms
- Frontend page load: < 3 seconds
- Concurrent users: 5+ simultaneous without errors

## Documentation

All documentation is in the [`docs/`](docs/) directory:

- **For Users**: [User Guide](docs/user/USER_GUIDE.md)
- **For Developers**: [Developer Guide](docs/developer/DEVELOPER_GUIDE.md)
- **API Reference**: [API Documentation](docs/developer/API_REFERENCE.md)
- **Architecture**: [System Architecture](docs/developer/ARCHITECTURE.md)
- **Setup Instructions**: [Setup Guide](docs/developer/SETUP.md)
- **Deployment**: [Deployment Guide](docs/operations/DEPLOYMENT.md)
- **Validation**: [Validation Checklist](docs/operations/VALIDATION_CHECKLIST.md)
- **Known Issues**: [Known Issues](docs/project/KNOWN_ISSUES.md)
- **Roadmap**: [Future Enhancements](docs/project/FUTURE_ENHANCEMENTS.md)
- **Changelog**: [Version History](docs/project/CHANGELOG.md)

See the [Documentation Index](docs/README.md) for complete documentation.

## Roadmap

Future enhancements planned post-MVP:

- User authentication and role-based access control
- Campaign approval workflow
- Template library for common campaigns
- Analytics dashboard with performance metrics
- A/B testing framework
- Multi-language support
- Integration with email service providers
- Campaign scheduling
- Version history for communications
- Batch campaign generation

## Known Limitations (MVP)

- SQLite database (single-user, file-based)
- No user authentication
- No approval workflow
- Limited to 5 variations per campaign
- Manual testing required for generated content
- No analytics or performance tracking

See `KNOWN_ISSUES.md` for detailed list.

## Contributing

### Development Workflow

1. Create feature branch
2. Make changes
3. Run tests: `uv run pytest` (backend), `npm test` (frontend)
4. Test manually using E2E scenarios
5. Update documentation if needed
6. Submit for review

### Code Style

- **Backend**: Follow PEP 8 Python style guide
- **Frontend**: ESLint configuration enforced
- **Commits**: Descriptive commit messages

## License

Internal StarHub project - Proprietary

## Support

For questions or issues:

1. Check documentation in `docs/` folder
2. Review API documentation at http://localhost:8000/docs
3. Check application logs in `logs/` directory
4. Contact development team

## Acknowledgments

- Anthropic Claude API for AI generation capabilities
- FastAPI framework for efficient backend development
- React and Vite for modern frontend development
- StarHub marketing team for requirements and feedback

---

**Version**: 1.0.0 (MVP)
**Last Updated**: 2024
**Maintained By**: StarHub Data Analytics Team
