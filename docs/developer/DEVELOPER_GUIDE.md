# Developer Guide

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Setup Instructions](#setup-instructions)
4. [Project Structure](#project-structure)
5. [Backend Architecture](#backend-architecture)
6. [Frontend Architecture](#frontend-architecture)
7. [Database Schema](#database-schema)
8. [AI Generation Service](#ai-generation-service)
9. [Scoring Algorithm](#scoring-algorithm)
10. [API Documentation](#api-documentation)
11. [Testing](#testing)
12. [Development Workflow](#development-workflow)
13. [Deployment](#deployment)
14. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Campaign │  │ Results  │  │  Score   │  │  Export  │   │
│  │   Form   │  │ Display  │  │Breakdown │  │  Modal   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│         │              ▲                                     │
│         │              │                                     │
│         ▼              │                                     │
│  ┌────────────────────────────────────┐                    │
│  │       API Client (Axios)           │                    │
│  └────────────────────────────────────┘                    │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/REST
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Backend (FastAPI)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              API Routes (main.py)                     │  │
│  └───┬────────────────────────────────────────────┬─────┘  │
│      │                                             │         │
│  ┌───▼─────────┐  ┌──────────────┐  ┌────────────▼─────┐  │
│  │    CRUD     │  │  Generation  │  │     Scoring      │  │
│  │ Operations  │  │   Service    │  │     Engine       │  │
│  │ (crud.py)   │  │(generation.py)  │   (scoring.py)   │  │
│  └───┬─────────┘  └──────┬───────┘  └────────┬─────────┘  │
│      │                   │                     │            │
│      │            ┌──────▼──────────┐         │            │
│      │            │  Anthropic API  │         │            │
│      │            │   (Claude AI)   │         │            │
│      │            └─────────────────┘         │            │
│      │                                        │            │
│  ┌───▼────────────────────────────────────────▼─────────┐  │
│  │         Database Layer (SQLAlchemy)                   │  │
│  │              Models (models.py)                       │  │
│  └───┬───────────────────────────────────────────────────┘  │
└──────┼───────────────────────────────────────────────────────┘
       │
┌──────▼───────────────────────────────────────────────────────┐
│              SQLite Database (MVP)                           │
│  ┌────────────────┐  ┌────────────────┐                     │
│  │   campaigns    │  │ communications │                     │
│  └────────────────┘  └────────────────┘                     │
└──────────────────────────────────────────────────────────────┘
```

### Request Flow

**Campaign Generation Flow:**

1. User fills form in Frontend
2. Frontend sends POST to `/campaigns/`
3. Backend creates campaign record in DB
4. Frontend sends POST to `/campaigns/{id}/generate`
5. Backend calls Generation Service
6. Generation Service calls Anthropic Claude API
7. Claude returns 5 communication variations
8. Scoring Engine calculates 4-pillar scores
9. Compliance validation runs
10. Backend saves communications to DB
11. Backend returns results to Frontend
12. Frontend displays variations with scores

**Data Flow Diagram:**

```
User Input → Campaign Form → API Request → FastAPI Route →
CRUD Create Campaign → Database Save → Generation Service →
Anthropic API → AI Response → Scoring Engine → Compliance Check →
Save Communications → Return Results → Display Results
```

---

## Technology Stack

### Backend

**Core Framework:**
- **FastAPI 0.104+**: Modern Python web framework
  - Automatic OpenAPI documentation
  - Type hints validation with Pydantic
  - Async support
  - High performance

**Database:**
- **SQLAlchemy 2.0+**: Python ORM
  - Declarative models
  - Relationship management
  - Query builder
- **SQLite**: File-based database (MVP)
  - Zero configuration
  - Portable
  - PostgreSQL-ready migration path

**AI Integration:**
- **Anthropic SDK**: Official Python client
  - Claude 3.5 Sonnet model
  - Streaming support
  - Error handling

**Data Validation:**
- **Pydantic v2**: Data validation
  - Type checking
  - Serialization
  - Schema generation

**Development Tools:**
- **uv**: Fast Python package manager
  - Virtual environment management
  - Dependency resolution
  - Lock file support

**Testing:**
- **pytest**: Testing framework
- **httpx**: Async HTTP client for tests

### Frontend

**Core Framework:**
- **React 18**: UI library
  - Functional components
  - Hooks (useState, useEffect)
  - Component composition

**Language:**
- **TypeScript 5+**: Type-safe JavaScript
  - Static type checking
  - Enhanced IDE support
  - Refactoring safety

**Build Tool:**
- **Vite 5+**: Next-generation build tool
  - Fast HMR (Hot Module Replacement)
  - Optimized production builds
  - ES modules native support

**Styling:**
- **Tailwind CSS 3+**: Utility-first CSS
  - Component styling
  - Responsive design
  - Custom theme

**HTTP Client:**
- **Axios**: Promise-based HTTP client
  - Request/response interceptors
  - Error handling
  - TypeScript support

**Development Tools:**
- **ESLint**: Code linting
- **TypeScript**: Type checking
- **Vite**: Dev server with HMR

---

## Setup Instructions

### Prerequisites

**Required:**
- Python 3.10 or higher
- Node.js 18 or higher
- npm 9 or higher
- uv package manager

**Optional:**
- Git (for version control)
- PostgreSQL (for production)
- Docker (for containerization)

### Backend Setup

**1. Navigate to Backend Directory:**
```bash
cd backend
```

**2. Create Virtual Environment:**
```bash
uv venv
```

**3. Activate Virtual Environment:**
```bash
# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

**4. Install Dependencies:**
```bash
uv pip install -e ".[dev]"
```

This installs:
- FastAPI and uvicorn (web server)
- SQLAlchemy (ORM)
- Anthropic SDK (AI)
- pytest (testing)
- All required dependencies

**5. Create Environment File:**
```bash
cp .env.example .env
```

**6. Configure Environment Variables:**

Edit `backend/.env`:
```bash
# Required - Get from https://console.anthropic.com/
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Database
DATABASE_URL=sqlite:///./starhub_comms.db

# API Settings (optional)
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**7. Initialize Database:**
```bash
# Database tables created automatically on first run
uv run uvicorn main:app --reload
```

**8. Verify Setup:**
```bash
# Open browser
http://localhost:8000/docs

# Should see FastAPI Swagger UI
```

### Frontend Setup

**1. Navigate to Frontend Directory:**
```bash
cd frontend
```

**2. Install Dependencies:**
```bash
npm install
```

This installs:
- React and React DOM
- TypeScript
- Vite
- Tailwind CSS
- Axios
- All required dependencies

**3. Create Environment File (Optional):**
```bash
echo "VITE_API_URL=http://localhost:8000" > .env
```

**4. Start Development Server:**
```bash
npm run dev
```

**5. Verify Setup:**
```bash
# Open browser
http://localhost:5173

# Should see StarHub Communications Generator UI
```

### Troubleshooting Setup

**Backend Issues:**

```bash
# If uv not found
curl -LsSf https://astral.sh/uv/install.sh | sh

# If module not found errors
cd backend
source .venv/bin/activate
uv pip install -e ".[dev]"

# If port 8000 in use
lsof -i :8000  # Find process
kill <PID>     # Kill process
```

**Frontend Issues:**

```bash
# If npm install fails
rm -rf node_modules package-lock.json
npm install

# If port 5173 in use
# Vite will auto-select next available port

# If can't connect to backend
# Check backend is running: curl http://localhost:8000/health
```

---

## Project Structure

### Backend Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── database.py             # Database configuration and session
├── models.py               # SQLAlchemy ORM models
├── schemas.py              # Pydantic schemas (request/response)
├── crud.py                 # CRUD operations (Create, Read, Update, Delete)
├── generation_service.py   # AI generation logic
├── scoring.py              # 4-pillar scoring algorithm
├── compliance.py           # Compliance validation rules
├── config.py               # Configuration management
├── .env                    # Environment variables (not in git)
├── .env.example            # Environment template
├── pyproject.toml          # Python project configuration
├── requirements.txt        # Python dependencies
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── test_api.py         # API endpoint tests
│   ├── test_generation.py  # Generation service tests
│   ├── test_scoring.py     # Scoring algorithm tests
│   └── performance_test.py # Performance benchmarks
└── starhub_comms.db        # SQLite database file (created at runtime)
```

### Frontend Structure

```
frontend/
├── src/
│   ├── components/         # React components
│   │   ├── CampaignForm.tsx       # Main campaign input form
│   │   ├── ResultsDisplay.tsx     # Communication variations display
│   │   ├── CommunicationCard.tsx  # Individual variation card
│   │   ├── ScoreBreakdown.tsx     # 4-pillar score visualization
│   │   ├── EditModal.tsx          # Edit communication modal
│   │   ├── ExportModal.tsx        # Export options modal
│   │   └── LoadingSpinner.tsx     # Loading state component
│   ├── services/           # API and business logic
│   │   └── api.ts                 # Axios API client
│   ├── types/              # TypeScript type definitions
│   │   └── index.ts               # Shared types and interfaces
│   ├── utils/              # Utility functions
│   │   ├── validation.ts          # Form validation
│   │   └── export.ts              # Export functionality
│   ├── App.tsx             # Root application component
│   ├── main.tsx            # Application entry point
│   ├── index.css           # Global styles and Tailwind imports
│   └── vite-env.d.ts       # Vite type definitions
├── public/                 # Static assets
│   └── starhub-logo.svg    # StarHub logo
├── index.html              # HTML entry point
├── package.json            # Node dependencies and scripts
├── tsconfig.json           # TypeScript configuration
├── tailwind.config.js      # Tailwind CSS configuration
├── vite.config.ts          # Vite build configuration
├── .env                    # Environment variables (not in git)
└── .env.example            # Environment template
```

---

## Backend Architecture

### Main Application (main.py)

**Purpose**: FastAPI application initialization and route definitions

**Key Components:**

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

app = FastAPI(
    title="StarHub Communications Generator API",
    description="AI-powered multi-channel communications",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route definitions
@app.post("/campaigns/", response_model=schemas.Campaign)
def create_campaign(campaign: schemas.CampaignCreate, db: Session = Depends(get_db)):
    return crud.create_campaign(db=db, campaign=campaign)

# Additional routes...
```

**Route Structure:**
- Health check: `GET /health`
- Campaign CRUD: `/campaigns/*`
- Communication operations: `/communications/*`
- Generation: `POST /campaigns/{id}/generate`

### Database Layer (database.py)

**Purpose**: SQLAlchemy configuration and session management

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL from environment
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./starhub_comms.db")

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite specific
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Data Models (models.py)

**Campaign Model:**

```python
class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    channel = Column(String, nullable=False)  # email, sms, push
    cohorts = Column(JSON, nullable=False)    # Array of cohort names
    product_line = Column(String, nullable=False)
    objective = Column(String, nullable=False)
    promotion_details = Column(Text, nullable=False)
    tone = Column(String)
    custom_instructions = Column(Text)
    required_phrases = Column(JSON)
    prohibited_words = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    communications = relationship("Communication", back_populates="campaign", cascade="all, delete-orphan")
```

**Communication Model:**

```python
class Communication(Base):
    __tablename__ = "communications"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    channel = Column(String, nullable=False)
    subject = Column(String)  # For email
    title = Column(String)    # For push notifications
    body = Column(Text, nullable=False)

    # Scores
    score_cohort_alignment = Column(Float)
    score_channel_optimization = Column(Float)
    score_brand_consistency = Column(Float)
    score_engagement_potential = Column(Float)
    overall_score = Column(Float)

    # Metadata
    is_recommended = Column(Boolean, default=False)
    edited = Column(Boolean, default=False)
    compliance_notes = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    campaign = relationship("Campaign", back_populates="communications")
```

### Pydantic Schemas (schemas.py)

**Purpose**: Request/response validation and serialization

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class CampaignCreate(BaseModel):
    channel: str = Field(..., description="Communication channel")
    cohorts: List[str] = Field(..., min_items=1)
    product_line: str
    objective: str
    promotion_details: str = Field(..., min_length=10)
    tone: Optional[str] = "friendly"
    custom_instructions: Optional[str] = None
    required_phrases: Optional[List[str]] = []
    prohibited_words: Optional[List[str]] = []

    @validator('channel')
    def validate_channel(cls, v):
        allowed = ['email', 'sms', 'push']
        if v not in allowed:
            raise ValueError(f'Channel must be one of {allowed}')
        return v

class Campaign(CampaignCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CommunicationResponse(BaseModel):
    id: int
    campaign_id: int
    channel: str
    subject: Optional[str]
    title: Optional[str]
    body: str
    score_cohort_alignment: float
    score_channel_optimization: float
    score_brand_consistency: float
    score_engagement_potential: float
    overall_score: float
    is_recommended: bool
    edited: bool
    compliance_notes: Optional[dict]

    class Config:
        from_attributes = True
```

### CRUD Operations (crud.py)

**Purpose**: Database operations abstraction

```python
from sqlalchemy.orm import Session
from sqlalchemy import desc
import models, schemas

def create_campaign(db: Session, campaign: schemas.CampaignCreate):
    db_campaign = models.Campaign(**campaign.dict())
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

def get_campaign(db: Session, campaign_id: int):
    return db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()

def get_campaigns(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Campaign).order_by(desc(models.Campaign.created_at)).offset(skip).limit(limit).all()

def update_campaign(db: Session, campaign_id: int, campaign_update: schemas.CampaignCreate):
    db_campaign = get_campaign(db, campaign_id)
    if db_campaign:
        for key, value in campaign_update.dict().items():
            setattr(db_campaign, key, value)
        db.commit()
        db.refresh(db_campaign)
    return db_campaign

def delete_campaign(db: Session, campaign_id: int):
    db_campaign = get_campaign(db, campaign_id)
    if db_campaign:
        db.delete(db_campaign)
        db.commit()
    return db_campaign

# Communication CRUD operations
def create_communication(db: Session, communication_data: dict):
    db_comm = models.Communication(**communication_data)
    db.add(db_comm)
    db.commit()
    db.refresh(db_comm)
    return db_comm

def get_communications_by_campaign(db: Session, campaign_id: int):
    return db.query(models.Communication).filter(
        models.Communication.campaign_id == campaign_id
    ).all()
```

---

## Frontend Architecture

### Component Hierarchy

```
App
├── CampaignForm
│   ├── ChannelSelector
│   ├── CohortSelector
│   ├── ProductSelector
│   ├── ObjectiveSelector
│   ├── ToneSelector
│   └── CustomInputs
│
└── ResultsDisplay
    ├── CommunicationCard (x5)
    │   ├── ContentDisplay
    │   ├── ScoreBreakdown
    │   └── ActionButtons
    ├── EditModal
    └── ExportModal
```

### Key Components

**App.tsx - Root Component:**

```typescript
import { useState } from 'react';
import CampaignForm from './components/CampaignForm';
import ResultsDisplay from './components/ResultsDisplay';
import { Campaign, Communication } from './types';
import { createCampaign, generateCommunications } from './services/api';

function App() {
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [communications, setCommunications] = useState<Communication[]>([]);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async (formData: CampaignFormData) => {
    setLoading(true);
    try {
      // Create campaign
      const newCampaign = await createCampaign(formData);
      setCampaign(newCampaign);

      // Generate communications
      const comms = await generateCommunications(newCampaign.id);
      setCommunications(comms);
    } catch (error) {
      console.error('Generation failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <CampaignForm onGenerate={handleGenerate} loading={loading} />
      {communications.length > 0 && (
        <ResultsDisplay communications={communications} />
      )}
    </div>
  );
}
```

**CampaignForm.tsx:**

```typescript
import { useState } from 'react';
import { CampaignFormData } from '../types';

interface Props {
  onGenerate: (data: CampaignFormData) => void;
  loading: boolean;
}

export default function CampaignForm({ onGenerate, loading }: Props) {
  const [formData, setFormData] = useState<CampaignFormData>({
    channel: '',
    cohorts: [],
    product_line: '',
    objective: '',
    promotion_details: '',
    tone: 'friendly',
    custom_instructions: '',
    required_phrases: [],
    prohibited_words: []
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.channel) newErrors.channel = 'Please select a channel';
    if (formData.cohorts.length === 0) newErrors.cohorts = 'Select at least one cohort';
    if (!formData.product_line) newErrors.product_line = 'Please select a product';
    if (!formData.objective) newErrors.objective = 'Please select an objective';
    if (!formData.promotion_details) newErrors.promotion_details = 'Please enter promotion details';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validate()) {
      onGenerate(formData);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="campaign-form">
      {/* Form fields */}
      <button type="submit" disabled={loading}>
        {loading ? 'Generating...' : 'Generate Communications'}
      </button>
    </form>
  );
}
```

### API Service (services/api.ts)

```typescript
import axios from 'axios';
import { Campaign, Communication, CampaignFormData } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Error handling interceptor
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      console.error('API Error:', error.response.data);
      throw new Error(error.response.data.detail || 'API request failed');
    } else if (error.request) {
      throw new Error('No response from server');
    } else {
      throw new Error('Request configuration error');
    }
  }
);

export const createCampaign = async (data: CampaignFormData): Promise<Campaign> => {
  const response = await apiClient.post<Campaign>('/campaigns/', data);
  return response.data;
};

export const generateCommunications = async (campaignId: number): Promise<Communication[]> => {
  const response = await apiClient.post<Communication[]>(`/campaigns/${campaignId}/generate`);
  return response.data;
};

export const updateCommunication = async (
  id: number,
  updates: Partial<Communication>
): Promise<Communication> => {
  const response = await apiClient.put<Communication>(`/communications/${id}`, updates);
  return response.data;
};

export const exportCommunication = async (id: number, format: 'txt' | 'json' | 'csv'): Promise<Blob> => {
  const response = await apiClient.get(`/communications/${id}/export?format=${format}`, {
    responseType: 'blob'
  });
  return response.data;
};
```

### TypeScript Types (types/index.ts)

```typescript
export interface Campaign {
  id: number;
  channel: 'email' | 'sms' | 'push';
  cohorts: string[];
  product_line: string;
  objective: string;
  promotion_details: string;
  tone?: string;
  custom_instructions?: string;
  required_phrases?: string[];
  prohibited_words?: string[];
  created_at: string;
  updated_at: string;
}

export interface Communication {
  id: number;
  campaign_id: number;
  channel: string;
  subject?: string;
  title?: string;
  body: string;
  score_cohort_alignment: number;
  score_channel_optimization: number;
  score_brand_consistency: number;
  score_engagement_potential: number;
  overall_score: number;
  is_recommended: boolean;
  edited: boolean;
  compliance_notes?: {
    status: 'pass' | 'warning' | 'fail';
    issues: string[];
  };
}

export interface CampaignFormData {
  channel: string;
  cohorts: string[];
  product_line: string;
  objective: string;
  promotion_details: string;
  tone?: string;
  custom_instructions?: string;
  required_phrases?: string[];
  prohibited_words?: string[];
}
```

---

## Database Schema

### Tables

**campaigns**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| channel | VARCHAR(20) | NOT NULL | email, sms, or push |
| cohorts | JSON | NOT NULL | Array of cohort names |
| product_line | VARCHAR(50) | NOT NULL | Product/service identifier |
| objective | VARCHAR(50) | NOT NULL | Campaign objective |
| promotion_details | TEXT | NOT NULL | Offer description |
| tone | VARCHAR(30) | NULL | Communication tone |
| custom_instructions | TEXT | NULL | Additional AI guidance |
| required_phrases | JSON | NULL | Mandatory phrases array |
| prohibited_words | JSON | NULL | Forbidden words array |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**communications**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| campaign_id | INTEGER | FOREIGN KEY (campaigns.id), NOT NULL | Parent campaign |
| channel | VARCHAR(20) | NOT NULL | Communication channel |
| subject | VARCHAR(255) | NULL | Email subject line |
| title | VARCHAR(100) | NULL | Push notification title |
| body | TEXT | NOT NULL | Main content |
| score_cohort_alignment | FLOAT | NULL | Cohort fit score (0-100) |
| score_channel_optimization | FLOAT | NULL | Channel optimization score |
| score_brand_consistency | FLOAT | NULL | Brand adherence score |
| score_engagement_potential | FLOAT | NULL | Engagement likelihood score |
| overall_score | FLOAT | NULL | Weighted average score |
| is_recommended | BOOLEAN | DEFAULT FALSE | Top recommendation flag |
| edited | BOOLEAN | DEFAULT FALSE | Manual edit flag |
| compliance_notes | JSON | NULL | Compliance check results |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Creation timestamp |

### Relationships

```sql
-- One campaign has many communications
campaigns.id (1) ----< (many) communications.campaign_id

-- Cascade delete: deleting campaign deletes all its communications
```

### Indexes

```sql
CREATE INDEX idx_campaign_channel ON campaigns(channel);
CREATE INDEX idx_campaign_created ON campaigns(created_at DESC);
CREATE INDEX idx_comm_campaign ON communications(campaign_id);
CREATE INDEX idx_comm_recommended ON communications(is_recommended);
```

### Sample Queries

```sql
-- Get campaign with all communications
SELECT c.*, comm.*
FROM campaigns c
LEFT JOIN communications comm ON c.id = comm.campaign_id
WHERE c.id = ?;

-- Get top recommended communications
SELECT *
FROM communications
WHERE is_recommended = TRUE
ORDER BY overall_score DESC;

-- Get recent campaigns
SELECT *
FROM campaigns
ORDER BY created_at DESC
LIMIT 10;
```

---

## AI Generation Service

### Generation Service (generation_service.py)

**Purpose**: Interface with Anthropic Claude API to generate communications

**Key Functions:**

```python
from anthropic import Anthropic
import os
from typing import List, Dict

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def generate_communications(campaign: Campaign) -> List[Dict]:
    """
    Generate 5 communication variations using Claude API

    Args:
        campaign: Campaign object with all parameters

    Returns:
        List of 5 communication dictionaries
    """

    # Build prompt
    prompt = build_generation_prompt(campaign)

    # Call Claude API
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=4000,
        temperature=0.7,
        system=get_system_prompt(),
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse response
    communications = parse_claude_response(response.content[0].text, campaign)

    return communications

def build_generation_prompt(campaign: Campaign) -> str:
    """Construct detailed prompt for Claude"""

    cohorts_str = ", ".join(campaign.cohorts)
    required_phrases_str = ", ".join(campaign.required_phrases) if campaign.required_phrases else "None"
    prohibited_words_str = ", ".join(campaign.prohibited_words) if campaign.prohibited_words else "None"

    prompt = f"""Generate 5 unique {campaign.channel} communications for a StarHub campaign.

CAMPAIGN DETAILS:
- Channel: {campaign.channel}
- Target Cohorts: {cohorts_str}
- Product: {campaign.product_line}
- Objective: {campaign.objective}
- Promotion: {campaign.promotion_details}
- Tone: {campaign.tone}
- Custom Instructions: {campaign.custom_instructions or "None"}

REQUIREMENTS:
- Required Phrases (must include): {required_phrases_str}
- Prohibited Words (never use): {prohibited_words_str}

CHANNEL SPECIFICATIONS:
{get_channel_specs(campaign.channel)}

Generate 5 creative variations following all requirements.
Format as JSON array with objects containing: subject/title, body, variation_number.
"""

    return prompt

def get_channel_specs(channel: str) -> str:
    """Channel-specific formatting requirements"""

    specs = {
        "email": """
- Subject: 40-60 characters, compelling and clear
- Body: Professional HTML-ready format
- Include unsubscribe link for promotional
- Clear call-to-action
        """,
        "sms": """
- Maximum 160 characters total
- Concise and direct
- Include opt-out for promotional: "Reply STOP to opt-out"
- Clear value proposition
        """,
        "push": """
- Title: 40-50 characters, attention-grabbing
- Body: 100-120 characters, action-oriented
- Urgent and compelling
- Single clear action
        """
    }

    return specs.get(channel, "")

def parse_claude_response(response_text: str, campaign: Campaign) -> List[Dict]:
    """Parse Claude's JSON response into communication objects"""

    import json

    # Extract JSON from response
    json_start = response_text.find('[')
    json_end = response_text.rfind(']') + 1
    json_str = response_text[json_start:json_end]

    variations = json.loads(json_str)

    communications = []
    for var in variations:
        comm = {
            "channel": campaign.channel,
            "campaign_id": campaign.id,
            "variation_number": var.get("variation_number", 0)
        }

        if campaign.channel == "email":
            comm["subject"] = var["subject"]
            comm["body"] = var["body"]
        elif campaign.channel == "sms":
            comm["body"] = var["body"]
        elif campaign.channel == "push":
            comm["title"] = var["title"]
            comm["body"] = var["body"]

        communications.append(comm)

    return communications
```

### System Prompt

```python
def get_system_prompt() -> str:
    return """You are a professional marketing communications expert for StarHub, Singapore's leading telecommunications provider.

Your role is to create compelling, compliant, and effective customer communications across email, SMS, and push notifications.

BRAND VOICE:
- Friendly yet professional
- Customer-centric and helpful
- Clear and transparent
- Trustworthy and reliable
- Modern and innovative

COMPLIANCE REQUIREMENTS:
- Always include opt-out for SMS promotional messages
- Always include unsubscribe for email promotional messages
- Include pricing terms ("/mth", "contract length", "T&Cs apply")
- Never make unsubstantiated claims
- Always mention conditions for "free" offers

COHORT UNDERSTANDING:
- Deal Seekers: Emphasize savings, value, discounts
- Sports Enthusiasts: Highlight sports content, leagues, live action
- Entertainment Lovers: Focus on streaming, shows, family content
- Tech Savvy: Emphasize features, technology, innovation
- Family Oriented: Family benefits, safety, value for whole family
- Business Users: Reliability, productivity, professional features
- Young Professionals: Flexibility, modern features, digital-first
- Seniors: Simplicity, support, ease of use
- High-Value: Exclusivity, premium features, VIP treatment
- At-Risk: Appreciation, exclusive retention offers, loyalty rewards

Always generate exactly 5 creative variations with distinct approaches while maintaining core message consistency.
"""
```

---

## Scoring Algorithm

### Scoring Service (scoring.py)

**Purpose**: Calculate 4-pillar scores for each communication variation

**Algorithm Overview:**

```python
def calculate_scores(communication: dict, campaign: Campaign) -> dict:
    """
    Calculate 4-pillar scores for a communication

    Returns dict with:
    - score_cohort_alignment (0-100)
    - score_channel_optimization (0-100)
    - score_brand_consistency (0-100)
    - score_engagement_potential (0-100)
    - overall_score (weighted average)
    """

    scores = {}

    # Pillar 1: Cohort Alignment (30%)
    scores['cohort_alignment'] = score_cohort_alignment(
        communication, campaign.cohorts, campaign.promotion_details
    )

    # Pillar 2: Channel Optimization (25%)
    scores['channel_optimization'] = score_channel_optimization(
        communication, campaign.channel
    )

    # Pillar 3: Brand Consistency (25%)
    scores['brand_consistency'] = score_brand_consistency(
        communication, campaign.tone
    )

    # Pillar 4: Engagement Potential (20%)
    scores['engagement_potential'] = score_engagement_potential(
        communication, campaign.objective
    )

    # Overall score (weighted average)
    scores['overall'] = (
        scores['cohort_alignment'] * 0.30 +
        scores['channel_optimization'] * 0.25 +
        scores['brand_consistency'] * 0.25 +
        scores['engagement_potential'] * 0.20
    )

    return scores
```

### Pillar 1: Cohort Alignment (30%)

**Scoring Criteria:**
- Keyword relevance to cohort (40%)
- Benefit emphasis for cohort (30%)
- Language style fit (30%)

```python
def score_cohort_alignment(communication: dict, cohorts: List[str], promotion: str) -> float:
    """Score how well communication resonates with target cohorts"""

    score = 0.0
    content = f"{communication.get('subject', '')} {communication.get('title', '')} {communication['body']}"
    content_lower = content.lower()

    # Cohort-specific keywords
    cohort_keywords = {
        'deal_seekers': ['save', 'discount', 'offer', 'value', 'price', '$', 'free'],
        'sports_enthusiasts': ['sports', 'game', 'match', 'league', 'live', 'premier'],
        'entertainment_lovers': ['entertainment', 'netflix', 'streaming', 'shows', 'movies'],
        'tech_savvy': ['innovation', 'technology', 'features', 'advanced', 'smart'],
        'family_oriented': ['family', 'kids', 'parental', 'safe', 'everyone'],
        'business_users': ['business', 'productivity', 'reliable', 'professional'],
        'young_professionals': ['flexible', 'modern', 'convenient', 'mobile'],
        'seniors': ['simple', 'easy', 'support', 'help', 'assistance'],
        'high_value': ['exclusive', 'premium', 'vip', 'select', 'privileged'],
        'at_risk': ['loyalty', 'valued', 'thank you', 'reward', 'appreciate']
    }

    # Check keyword presence
    keyword_score = 0
    for cohort in cohorts:
        keywords = cohort_keywords.get(cohort, [])
        matches = sum(1 for kw in keywords if kw in content_lower)
        keyword_score += min(matches / max(len(keywords), 1), 1.0)

    keyword_score = (keyword_score / len(cohorts)) * 40  # 40% weight

    # Check benefit emphasis (basic heuristic)
    benefit_indicators = ['get', 'enjoy', 'receive', 'unlock', 'access', 'experience']
    benefit_score = min(sum(1 for ind in benefit_indicators if ind in content_lower) * 10, 30)

    # Language style (length and complexity for cohort)
    style_score = 30  # Base score, adjust based on cohort preferences

    total_score = keyword_score + benefit_score + style_score

    return min(total_score, 100.0)
```

### Pillar 2: Channel Optimization (25%)

**Scoring Criteria:**
- Character length compliance (50%)
- Format appropriateness (30%)
- Required elements present (20%)

```python
def score_channel_optimization(communication: dict, channel: str) -> float:
    """Score how well communication is optimized for channel"""

    score = 0.0

    if channel == "email":
        subject = communication.get('subject', '')
        body = communication['body']

        # Subject length (40-60 chars optimal)
        subject_len = len(subject)
        if 40 <= subject_len <= 60:
            score += 40
        elif 30 <= subject_len < 40 or 60 < subject_len <= 70:
            score += 30
        else:
            score += 10

        # Body has clear structure
        if '\n' in body or len(body) > 100:  # Multi-line or substantial
            score += 20

        # Unsubscribe link present
        if 'unsubscribe' in body.lower():
            score += 20

        # Call-to-action present
        cta_words = ['click', 'visit', 'call', 'reply', 'sign up', 'learn more']
        if any(cta in body.lower() for cta in cta_words):
            score += 20

    elif channel == "sms":
        body = communication['body']
        length = len(body)

        # Length optimization (≤160 chars)
        if length <= 160:
            score += 50
        elif length <= 180:
            score += 30
        else:
            score += 0  # Exceeds SMS limit

        # Conciseness bonus
        if length <= 140:
            score += 10

        # Has opt-out (for promotional)
        if 'stop' in body.lower():
            score += 20

        # Clear and direct
        if '.' in body or '!' in body:  # Has sentence structure
            score += 20

    elif channel == "push":
        title = communication.get('title', '')
        body = communication['body']

        title_len = len(title)
        body_len = len(body)

        # Title length (40-50 chars optimal)
        if 40 <= title_len <= 50:
            score += 30
        elif 30 <= title_len < 40 or 50 < title_len <= 60:
            score += 20
        else:
            score += 5

        # Body length (100-120 chars optimal)
        if 100 <= body_len <= 120:
            score += 40
        elif 90 <= body_len < 100 or 120 < body_len <= 130:
            score += 30
        else:
            score += 10

        # Urgency indicators
        urgency_words = ['now', 'today', 'limited', 'hurry', 'don\'t miss']
        if any(urg in body.lower() for urg in urgency_words):
            score += 15

        # Action clarity
        if '!' in title or '!' in body:
            score += 15

    return min(score, 100.0)
```

### Pillar 3: Brand Consistency (25%)

**Scoring Criteria:**
- Tone appropriateness (40%)
- Professional quality (30%)
- Brand voice adherence (30%)

```python
def score_brand_consistency(communication: dict, tone: str) -> float:
    """Score brand voice and tone consistency"""

    score = 0.0
    content = f"{communication.get('subject', '')} {communication.get('title', '')} {communication['body']}"
    content_lower = content.lower()

    # Tone-specific language
    tone_keywords = {
        'friendly': ['we', 'you', 'your', 'enjoy', 'love'],
        'professional': ['we are pleased', 'we\'re excited', 'valued', 'important'],
        'excited': ['amazing', 'awesome', 'incredible', '!', 'wow'],
        'urgent': ['now', 'hurry', 'limited', 'today', 'act fast'],
        'premium': ['exclusive', 'select', 'premium', 'distinguished'],
        'informative': ['please note', 'important', 'update', 'information'],
        'casual': ['hey', 'check out', 'grab', 'cool'],
        'appreciative': ['thank you', 'appreciate', 'valued', 'loyalty']
    }

    expected_keywords = tone_keywords.get(tone, [])
    matches = sum(1 for kw in expected_keywords if kw in content_lower)
    tone_score = min((matches / max(len(expected_keywords), 1)) * 100, 40)

    score += tone_score

    # Professional quality (no errors, proper capitalization)
    professional_score = 30

    # Check for common issues
    if content.isupper():  # All caps
        professional_score -= 10
    if '...' in content:  # Excessive ellipsis
        professional_score -= 5
    if content.count('!') > 3:  # Too many exclamation marks
        professional_score -= 5

    score += max(professional_score, 0)

    # Brand voice (StarHub specific)
    brand_indicators = ['starhub', 'you', 'your', 'we']
    brand_score = min(sum(5 for ind in brand_indicators if ind in content_lower), 30)

    score += brand_score

    return min(score, 100.0)
```

### Pillar 4: Engagement Potential (20%)

**Scoring Criteria:**
- Call-to-action strength (40%)
- Value proposition clarity (35%)
- Urgency/relevance (25%)

```python
def score_engagement_potential(communication: dict, objective: str) -> float:
    """Score likelihood to drive customer engagement"""

    score = 0.0
    content = f"{communication.get('subject', '')} {communication.get('title', '')} {communication['body']}"
    content_lower = content.lower()

    # Call-to-action strength
    strong_ctas = ['claim', 'get', 'start', 'unlock', 'activate', 'sign up', 'upgrade']
    cta_count = sum(1 for cta in strong_ctas if cta in content_lower)
    cta_score = min(cta_count * 15, 40)
    score += cta_score

    # Value proposition clarity
    value_indicators = ['save', '$', 'free', 'bonus', 'extra', 'unlimited', 'get']
    value_count = sum(1 for val in value_indicators if val in content_lower)
    value_score = min(value_count * 10, 35)
    score += value_score

    # Urgency and relevance
    urgency_words = ['now', 'today', 'limited', 'exclusive', 'only', 'hurry']
    urgency_count = sum(1 for urg in urgency_words if urg in content_lower)
    urgency_score = min(urgency_count * 8, 25)
    score += urgency_score

    return min(score, 100.0)
```

### Identifying Top Recommendation

```python
def identify_recommendation(communications: List[dict]) -> List[dict]:
    """Mark the top-scoring communication as recommended"""

    if not communications:
        return communications

    # Find highest overall score
    max_score = max(comm['overall_score'] for comm in communications)

    # Mark top scorer(s) as recommended
    for comm in communications:
        comm['is_recommended'] = (comm['overall_score'] == max_score)

    return communications
```

---

## API Documentation

### Base URL

```
http://localhost:8000
```

### Authentication

MVP version has no authentication. Production should implement:
- API key authentication
- JWT tokens
- Role-based access control

### Endpoints

#### Health Check

```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-09T10:30:00Z"
}
```

#### Create Campaign

```
POST /campaigns/
```

**Request Body:**
```json
{
  "channel": "email",
  "cohorts": ["deal_seekers", "mass_market"],
  "product_line": "homehub_plus",
  "objective": "promotion",
  "promotion_details": "$200 discount on 24-month contract",
  "tone": "friendly",
  "custom_instructions": "Emphasize family benefits",
  "required_phrases": ["exclusive offer", "$115.66/mth"],
  "prohibited_words": ["competitor"]
}
```

**Response: 200 OK**
```json
{
  "id": 123,
  "channel": "email",
  "cohorts": ["deal_seekers", "mass_market"],
  "product_line": "homehub_plus",
  "objective": "promotion",
  "promotion_details": "$200 discount on 24-month contract",
  "tone": "friendly",
  "custom_instructions": "Emphasize family benefits",
  "required_phrases": ["exclusive offer", "$115.66/mth"],
  "prohibited_words": ["competitor"],
  "created_at": "2024-11-09T10:30:00Z",
  "updated_at": "2024-11-09T10:30:00Z"
}
```

**Error Responses:**
```json
// 422 Validation Error
{
  "detail": [
    {
      "loc": ["body", "channel"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### Get Campaign

```
GET /campaigns/{campaign_id}
```

**Response: 200 OK**
```json
{
  "id": 123,
  "channel": "email",
  // ... all campaign fields
}
```

**Error: 404 Not Found**
```json
{
  "detail": "Campaign not found"
}
```

#### List Campaigns

```
GET /campaigns/?skip=0&limit=100
```

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Maximum records to return (default: 100)

**Response: 200 OK**
```json
[
  {
    "id": 123,
    "channel": "email",
    // ... campaign fields
  },
  // ... more campaigns
]
```

#### Update Campaign

```
PUT /campaigns/{campaign_id}
```

**Request Body:** Same as Create Campaign

**Response: 200 OK**
```json
{
  "id": 123,
  // ... updated campaign fields
}
```

#### Delete Campaign

```
DELETE /campaigns/{campaign_id}
```

**Response: 200 OK**
```json
{
  "id": 123,
  // ... deleted campaign fields
}
```

#### Generate Communications

```
POST /campaigns/{campaign_id}/generate
```

**Response: 200 OK**
```json
[
  {
    "id": 456,
    "campaign_id": 123,
    "channel": "email",
    "subject": "Exclusive HomeHub+ Offer - Save $200!",
    "body": "Dear Valued Customer,\n\nWe have an exclusive offer...",
    "score_cohort_alignment": 85.0,
    "score_channel_optimization": 90.0,
    "score_brand_consistency": 88.0,
    "score_engagement_potential": 82.0,
    "overall_score": 87.0,
    "is_recommended": true,
    "edited": false,
    "compliance_notes": {
      "status": "pass",
      "issues": []
    }
  },
  // ... 4 more variations
]
```

**Error: 500 Internal Server Error**
```json
{
  "detail": "Generation failed: API key invalid"
}
```

#### Get Communication

```
GET /communications/{communication_id}
```

**Response: 200 OK**
```json
{
  "id": 456,
  "campaign_id": 123,
  // ... all communication fields
}
```

#### Update Communication (Edit)

```
PUT /communications/{communication_id}
```

**Request Body:**
```json
{
  "subject": "Updated subject line",
  "body": "Updated body content",
  "edited": true
}
```

**Response: 200 OK**
```json
{
  "id": 456,
  // ... updated communication fields
}
```

#### List Communications

```
GET /communications/?campaign_id=123
```

**Query Parameters:**
- `campaign_id` (int, optional): Filter by campaign

**Response: 200 OK**
```json
[
  {
    "id": 456,
    // ... communication fields
  }
]
```

#### Export Communication

```
GET /communications/{communication_id}/export?format=json
```

**Query Parameters:**
- `format` (str): `txt`, `json`, or `csv`

**Response: 200 OK**
- Content-Type: `application/json`, `text/plain`, or `text/csv`
- Content-Disposition: `attachment; filename="communication_456.json"`

### Error Handling

**Standard Error Response:**
```json
{
  "detail": "Error message description"
}
```

**HTTP Status Codes:**
- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

---

## Testing

### Backend Testing

**Test Structure:**

```
backend/tests/
├── __init__.py
├── test_api.py          # API endpoint tests
├── test_generation.py   # Generation service tests
├── test_scoring.py      # Scoring algorithm tests
└── performance_test.py  # Performance benchmarks
```

**Running Tests:**

```bash
cd backend

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=. --cov-report=html

# Run specific test file
uv run pytest tests/test_api.py

# Run specific test function
uv run pytest tests/test_api.py::test_create_campaign

# Verbose output
uv run pytest -v

# Stop on first failure
uv run pytest -x
```

**Sample Test (test_api.py):**

```python
from fastapi.testclient import TestClient
from main import app
from database import Base, engine

# Create test client
client = TestClient(app)

# Setup test database
Base.metadata.create_all(bind=engine)

def test_health_check():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_campaign():
    """Test campaign creation"""
    campaign_data = {
        "channel": "email",
        "cohorts": ["deal_seekers"],
        "product_line": "homehub_plus",
        "objective": "promotion",
        "promotion_details": "Test promotion",
        "tone": "friendly"
    }

    response = client.post("/campaigns/", json=campaign_data)
    assert response.status_code == 200

    data = response.json()
    assert data["channel"] == "email"
    assert "id" in data
    assert "created_at" in data

def test_create_campaign_validation():
    """Test campaign validation"""
    invalid_data = {
        "channel": "invalid_channel",  # Should fail validation
        "cohorts": [],  # Should fail - empty cohorts
        "objective": "promotion"
    }

    response = client.post("/campaigns/", json=invalid_data)
    assert response.status_code == 422  # Validation error

def test_generate_communications():
    """Test communication generation"""
    # First create campaign
    campaign_data = {
        "channel": "sms",
        "cohorts": ["mass_market"],
        "product_line": "mobile_postpaid",
        "objective": "service_update",
        "promotion_details": "Network maintenance tonight",
        "tone": "professional"
    }

    create_response = client.post("/campaigns/", json=campaign_data)
    campaign_id = create_response.json()["id"]

    # Generate communications
    gen_response = client.post(f"/campaigns/{campaign_id}/generate")
    assert gen_response.status_code == 200

    communications = gen_response.json()
    assert len(communications) == 5
    assert all(comm["channel"] == "sms" for comm in communications)
    assert any(comm["is_recommended"] for comm in communications)
```

### Frontend Testing

**Test Structure:**

```
frontend/src/
├── components/
│   ├── __tests__/
│   │   ├── CampaignForm.test.tsx
│   │   └── ResultsDisplay.test.tsx
├── services/
│   └── __tests__/
│       └── api.test.ts
└── utils/
    └── __tests__/
        └── validation.test.ts
```

**Running Tests:**

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch
```

**Sample Test (CampaignForm.test.tsx):**

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import CampaignForm from '../CampaignForm';

describe('CampaignForm', () => {
  test('renders form fields', () => {
    render(<CampaignForm onGenerate={jest.fn()} loading={false} />);

    expect(screen.getByLabelText(/channel/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/cohorts/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/product/i)).toBeInTheDocument();
  });

  test('validates required fields', async () => {
    const mockGenerate = jest.fn();
    render(<CampaignForm onGenerate={mockGenerate} loading={false} />);

    const submitButton = screen.getByText(/generate/i);
    fireEvent.click(submitButton);

    expect(mockGenerate).not.toHaveBeenCalled();
    expect(screen.getByText(/please select a channel/i)).toBeInTheDocument();
  });

  test('submits form with valid data', () => {
    const mockGenerate = jest.fn();
    render(<CampaignForm onGenerate={mockGenerate} loading={false} />);

    // Fill form
    fireEvent.change(screen.getByLabelText(/channel/i), { target: { value: 'email' } });
    fireEvent.change(screen.getByLabelText(/cohorts/i), { target: { value: ['deal_seekers'] } });
    // ... fill other fields

    fireEvent.click(screen.getByText(/generate/i));

    expect(mockGenerate).toHaveBeenCalledWith(expect.objectContaining({
      channel: 'email',
      cohorts: ['deal_seekers']
    }));
  });
});
```

### Performance Testing

**Run Performance Tests:**

```bash
cd backend
uv run python tests/performance_test.py
```

**Performance Targets:**
- API health check: < 100ms
- Campaign creation: < 2s (95th percentile)
- Database queries: < 500ms
- Communication generation: < 10s
- Concurrent users: 5+ without errors

---

## Development Workflow

### Local Development

**1. Start Backend:**
```bash
cd backend
source .venv/bin/activate
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**2. Start Frontend:**
```bash
cd frontend
npm run dev
```

**3. Make Changes:**
- Backend: Edit Python files → Auto-reload with `--reload`
- Frontend: Edit TypeScript/React files → Vite HMR updates instantly

**4. Test Changes:**
```bash
# Backend tests
cd backend
uv run pytest

# Frontend tests
cd frontend
npm test
```

### Adding a New Feature

**Example: Add new cohort**

1. **Backend:**
```python
# Update cohort list in schemas.py or config.py
VALID_COHORTS = [
    "mass_market",
    "deal_seekers",
    # ... existing cohorts
    "new_cohort_name"  # Add new cohort
]

# Update scoring.py with cohort-specific keywords
cohort_keywords = {
    # ... existing cohorts
    'new_cohort_name': ['keyword1', 'keyword2', 'keyword3']
}
```

2. **Frontend:**
```typescript
// Update cohort options in CampaignForm.tsx
const cohortOptions = [
  { value: 'mass_market', label: 'Mass Market' },
  // ... existing cohorts
  { value: 'new_cohort_name', label: 'New Cohort Display Name' }
];
```

3. **Test:**
```bash
# Create test campaign with new cohort
# Verify generation works
# Verify scoring accounts for new cohort
```

4. **Document:**
- Update USER_GUIDE.md with new cohort description
- Update API_REFERENCE.md if schema changed

### Code Style Guidelines

**Backend (Python):**
- Follow PEP 8 style guide
- Use type hints
- Document functions with docstrings
- Keep functions focused and single-purpose

```python
def calculate_score(communication: dict, campaign: Campaign) -> float:
    """
    Calculate overall score for a communication.

    Args:
        communication: Communication dictionary with content
        campaign: Campaign object with parameters

    Returns:
        Score between 0-100
    """
    # Implementation
```

**Frontend (TypeScript/React):**
- Use functional components with hooks
- TypeScript for type safety
- Descriptive variable names
- Component files in PascalCase
- Utility files in camelCase

```typescript
interface CampaignFormProps {
  onGenerate: (data: CampaignFormData) => void;
  loading: boolean;
}

export default function CampaignForm({ onGenerate, loading }: CampaignFormProps) {
  // Component logic
}
```

### Git Workflow

**Branch Strategy:**
```bash
# Feature development
git checkout -b feature/add-new-cohort

# Make changes and commit
git add .
git commit -m "Add new cohort: students"

# Push to remote
git push origin feature/add-new-cohort

# Create pull request for review
```

**Commit Message Format:**
```
<type>: <subject>

<body>

Types: feat, fix, docs, style, refactor, test, chore
```

Examples:
```
feat: Add student cohort targeting

- Add 'students' to valid cohorts list
- Update scoring keywords for student segment
- Add cohort option to frontend form

fix: Correct SMS character count validation

- Fix off-by-one error in character counting
- Add test case for 160-character boundary

docs: Update API reference with new endpoint

- Document /campaigns/{id}/duplicate endpoint
- Add request/response examples
```

---

## Deployment

See `DEPLOYMENT.md` for comprehensive deployment guide.

**Quick Reference:**

### Local Development
```bash
# Quick start
./start-all.sh

# Manual start
./start-backend.sh  # Terminal 1
./start-frontend.sh # Terminal 2
```

### Production Considerations

**Backend:**
- Migrate to PostgreSQL
- Use Gunicorn with multiple workers
- Environment variable management (secrets)
- Logging and monitoring
- SSL/HTTPS
- Rate limiting
- Authentication

**Frontend:**
- Build for production: `npm run build`
- Serve static files via CDN or Nginx
- Environment-specific API URLs
- Error tracking (Sentry)
- Analytics

**Database:**
- PostgreSQL setup
- Connection pooling
- Backup and recovery
- Migration scripts

---

## Troubleshooting

### Backend Issues

**Problem: Module not found**
```bash
# Solution: Reinstall dependencies
cd backend
source .venv/bin/activate
uv pip install -e ".[dev]"
```

**Problem: Database errors**
```bash
# Solution: Delete and recreate database
cd backend
rm starhub_comms.db
uv run uvicorn main:app --reload  # Recreates tables
```

**Problem: API key errors**
```bash
# Solution: Verify API key
cat backend/.env | grep ANTHROPIC_API_KEY
# Should show: ANTHROPIC_API_KEY=sk-ant-...

# Test API key
python -c "from anthropic import Anthropic; client = Anthropic(); print('API key valid')"
```

### Frontend Issues

**Problem: Can't connect to backend**
```bash
# Solution: Check backend running
curl http://localhost:8000/health

# Check frontend .env
cat frontend/.env
# Should show: VITE_API_URL=http://localhost:8000
```

**Problem: TypeScript errors**
```bash
# Solution: Check types
cd frontend
npx tsc --noEmit

# Rebuild
rm -rf node_modules
npm install
```

### Database Issues

**Problem: Database locked**
```bash
# Solution: Close all connections
# Stop all backend processes
ps aux | grep uvicorn
kill <PID>

# Restart backend
./start-backend.sh
```

### Common Errors

**Error: "CORS policy blocked"**
- Check backend CORS_ORIGINS includes frontend URL
- Verify frontend making requests to correct backend URL

**Error: "Generation failed"**
- Check ANTHROPIC_API_KEY valid
- Check API key has credits
- Check network connectivity
- Review backend logs for details

**Error: "422 Validation Error"**
- Check request body matches schema
- Verify all required fields present
- Check field types match expectations

---

## Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **React Documentation**: https://react.dev/
- **TypeScript Documentation**: https://www.typescriptlang.org/docs/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **Anthropic API Documentation**: https://docs.anthropic.com/
- **Tailwind CSS**: https://tailwindcss.com/docs

---

**Document Version**: 1.0.0
**Last Updated**: 2024-11-09
**Maintained By**: StarHub Data Analytics Team
