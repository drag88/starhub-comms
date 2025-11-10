# StarHub Customer Communications Generator - Implementation Plan

## Project Overview

**Objective**: Build an MVP system that enables StarHub marketing teams to generate customer communications across multiple channels (SMS, email, push notifications) with AI-powered recommendations.

**Key Features**:
- Multi-channel support (Email, SMS, Push Notifications)
- Generate 5 communication variations per request
- AI-powered recommendation scoring
- Comprehensive customization options
- Export functionality (TXT, CSV, JSON)
- SQLite backend + React/TypeScript frontend

**Build Sequence**: Backend First → Test → Frontend → Integration

---

## Project Structure

```
/backend/                           # FastAPI Python backend
  /app/
    /models/                        # SQLAlchemy database models
      __init__.py
      campaign.py                   # Campaign model
      communication.py              # GeneratedCommunication model
      error_log.py                  # ErrorLog model
      promotion.py                  # PromotionUpload model
    /services/                      # Business logic layer
      __init__.py
      communication_generator.py    # Claude API integration & generation
      recommendation_scorer.py      # Scoring algorithm (4 pillars)
      validation.py                 # Input validation logic
    /api/                          # API endpoints
      __init__.py
      campaigns.py                  # Campaign CRUD endpoints
      communications.py             # Communication management endpoints
      utilities.py                  # Cohorts, products, objectives, health
    /config/                       # Configuration files
      products.yaml                 # Product lines definition
      cohorts.yaml                  # Customer cohorts with characteristics
      objectives.yaml               # Communication objectives
    /schemas/                      # Pydantic request/response models
      __init__.py
      campaign.py
      communication.py
      common.py
  /tests/                          # Backend tests
    test_scoring.py
    test_api.py
    test_generation.py
  database.py                      # SQLite database setup
  main.py                          # FastAPI application entry point
  requirements.txt                 # Python dependencies

/frontend/                         # React/TypeScript frontend
  /src/
    /components/
      /CampaignForm/              # Form input components
        ChannelSelector.tsx
        CohortSelector.tsx
        ProductSelector.tsx
        PromotionInput.tsx
        CustomizationPanel.tsx
        index.tsx
      /GenerationInterface/       # Results display
        ChatInterface.tsx
        GenerationStatus.tsx
        index.tsx
      /ResultsDisplay/            # Communication cards
        CommunicationCard.tsx
        RecommendationBadge.tsx
        ScoreBreakdown.tsx
        index.tsx
      /ActionPanel/               # Edit and export
        EditModal.tsx
        ExportOptions.tsx
        index.tsx
      /shared/                    # Reusable UI components
        Button.tsx
        Input.tsx
        Select.tsx
        Textarea.tsx
    /contexts/                    # React Context state management
      CampaignContext.tsx
      GenerationContext.tsx
    /hooks/                       # Custom React hooks
      useCampaign.ts
      useGeneration.ts
      useExport.ts
    /services/                    # API client layer
      api.ts
      validation.ts
      export.ts
    /types/                       # TypeScript type definitions
      campaign.ts
      communication.ts
      api.ts
    /utils/                       # Utility functions
      formatters.ts
      validators.ts
    App.tsx
    main.tsx
  package.json
  tsconfig.json
  vite.config.ts
  tailwind.config.js

/docs/                            # Documentation
  API_DOCUMENTATION.md
  USER_GUIDE.md
  REQUIREMENTS_SPECIFICATION.md   # Comprehensive requirements from analyst

.env                              # Environment variables (not committed)
.gitignore
README.md
```

---

# PHASE 1: Backend Foundation & Database

## Objectives
- Set up FastAPI project structure
- Implement SQLite database with complete schema
- Create configuration files for products, cohorts, objectives
- Build core database models

## Tasks

### 1.1 Project Initialization
**Goal**: Set up Python environment and install dependencies

**Steps**:
1. Create virtual environment
2. Install core dependencies:
   - fastapi
   - uvicorn[standard]
   - sqlalchemy
   - anthropic
   - pydantic
   - python-dotenv
   - pyyaml
3. Create .env file with ANTHROPIC_API_KEY
4. Create .gitignore (exclude .env, venv/, __pycache__, *.db)
5. Create requirements.txt

**Deliverable**: Working Python environment with all dependencies installed

---

### 1.2 Database Schema Implementation
**Goal**: Create SQLite database with complete schema

**Database Models**:

**campaigns table**:
```sql
CREATE TABLE campaigns (
    campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_name TEXT NOT NULL,
    channel TEXT NOT NULL CHECK(channel IN ('email', 'sms', 'push')),
    objective TEXT NOT NULL,
    product_lines TEXT NOT NULL,      -- JSON array
    cohorts TEXT NOT NULL,            -- JSON array
    promotion_details TEXT,           -- JSON object
    customization TEXT,               -- JSON object
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_campaigns_created ON campaigns(created_at);
CREATE INDEX idx_campaigns_channel ON campaigns(channel);
```

**generated_communications table**:
```sql
CREATE TABLE generated_communications (
    communication_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    variation_number INTEGER NOT NULL CHECK(variation_number BETWEEN 1 AND 5),
    communication_text TEXT NOT NULL,
    recommendation_score INTEGER NOT NULL,
    score_breakdown TEXT NOT NULL,    -- JSON object
    recommendation_reasoning TEXT,
    compliance_notes TEXT,
    is_selected BOOLEAN DEFAULT 0,
    edited_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id) ON DELETE CASCADE
);

CREATE INDEX idx_gencomm_campaign ON generated_communications(campaign_id);
CREATE INDEX idx_gencomm_score ON generated_communications(recommendation_score DESC);
```

**error_logs table**:
```sql
CREATE TABLE error_logs (
    error_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER,
    error_type TEXT NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    request_params TEXT,              -- JSON object
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id) ON DELETE SET NULL
);

CREATE INDEX idx_errors_created ON error_logs(created_at);
CREATE INDEX idx_errors_type ON error_logs(error_type);
```

**promotion_uploads table**:
```sql
CREATE TABLE promotion_uploads (
    promotion_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    promotion_name TEXT NOT NULL,
    pricing_details TEXT,             -- JSON object
    features_benefits TEXT,           -- JSON array
    terms_conditions TEXT,
    validity_start DATE,
    validity_end DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id) ON DELETE CASCADE
);
```

**Steps**:
1. Create `backend/database.py` with SQLAlchemy setup
2. Create SQLAlchemy models in `backend/app/models/`
3. Implement database initialization function
4. Create database migration/setup script

**Deliverable**: Complete database schema with all tables and indexes

---

### 1.3 Configuration Files
**Goal**: Create YAML configuration files for products, cohorts, and objectives

**products.yaml**:
```yaml
products:
  mobile:
    - id: "mobile_postpaid"
      name: "Postpaid Plans"
      category: "Mobile"
      description: "Contract-based mobile plans with device options"
    - id: "mobile_prepaid"
      name: "Prepaid Plans"
      category: "Mobile"
      description: "No-contract prepaid mobile services"
  broadband:
    - id: "broadband_fiber"
      name: "Fiber Broadband"
      category: "Broadband"
      description: "High-speed fiber internet up to 10Gbps"
    - id: "broadband_10gbps"
      name: "10Gbps Broadband"
      category: "Broadband"
      description: "Ultra-fast 10Gbps fiber broadband"
  entertainment:
    - id: "entertainment_tv"
      name: "TV+ Entertainment"
      category: "Entertainment"
      description: "Streaming and cable TV services"
    - id: "entertainment_sports"
      name: "Sports+"
      category: "Entertainment"
      description: "Premium sports content (Premier League, Cricket)"
  bundles:
    - id: "bundle_homehub"
      name: "HomeHub"
      category: "Bundle"
      description: "Broadband + TV bundle"
    - id: "bundle_homehub_plus"
      name: "HomeHub+"
      category: "Bundle"
      description: "Premium bundle with broadband, TV, and streaming"
```

**cohorts.yaml**:
```yaml
cohorts:
  service_based:
    - id: "mobile_postpaid"
      name: "Mobile Postpaid"
      category: "Service-Based"
      characteristics: "Contract-based, higher ARPU, value stability"
      messaging_focus: "Premium features, data plans, roaming"
      tone_guidance: "Professional, value-focused"
    - id: "mobile_prepaid"
      name: "Mobile Prepaid"
      category: "Service-Based"
      characteristics: "No contract, lower ARPU, price-sensitive"
      messaging_focus: "Top-up promotions, data add-ons, value deals"
      tone_guidance: "Friendly, value-focused"

  value_based:
    - id: "high_value"
      name: "High-Value Customers"
      category: "Value-Based"
      characteristics: "Multiple services, high ARPU, long tenure"
      messaging_focus: "Exclusive offers, VIP treatment, latest features"
      tone_guidance: "Premium, exclusive, appreciative"
    - id: "mass_market"
      name: "Mass Market"
      category: "Value-Based"
      characteristics: "Single service or basic bundle, moderate ARPU"
      messaging_focus: "Value propositions, savings through bundles"
      tone_guidance: "Friendly, clear value"
    - id: "at_risk"
      name: "At-Risk/Churning"
      category: "Value-Based"
      characteristics: "Service issues, competitor offers, contract ending"
      messaging_focus: "Retention offers, problem resolution"
      tone_guidance: "Understanding, solution-oriented, generous"

  demographic:
    - id: "young_adults"
      name: "Young Adults (18-30)"
      category: "Demographic"
      characteristics: "Mobile-first, data-heavy, streaming-focused"
      messaging_focus: "Data plans, streaming bundles, mobile features"
      tone_guidance: "Casual, energetic"
    - id: "young_families"
      name: "Young Families (30-45)"
      category: "Demographic"
      characteristics: "Family entertainment, reliable broadband"
      messaging_focus: "Family bundles, home connectivity, value"
      tone_guidance: "Warm, family-oriented"

  behavioral:
    - id: "sports_enthusiasts"
      name: "Sports Enthusiasts"
      category: "Behavioral"
      messaging_focus: "Premier League, cricket, Sports+, live events"
      tone_guidance: "Exciting, passionate"
    - id: "entertainment_bingers"
      name: "Entertainment Bingers"
      category: "Behavioral"
      messaging_focus: "Netflix, HBO Max, K-dramas, binge content"
      tone_guidance: "Engaging, entertainment-focused"
    - id: "deal_seekers"
      name: "Deal Seekers"
      category: "Behavioral"
      messaging_focus: "Promotions, bundle savings, limited-time offers"
      tone_guidance: "Urgent, value-focused, promotional"
```

**objectives.yaml**:
```yaml
objectives:
  - id: "promotion"
    name: "Promotion"
    description: "New offer or limited-time deal"
    tone_guidance: "Urgent, value-focused, clear CTA"
    required_elements: ["offer details", "pricing", "CTA", "opt-out (if promotional)"]

  - id: "retention"
    name: "Retention"
    description: "Prevent churn, exclusive offer for at-risk customers"
    tone_guidance: "Personal, appreciative, generous"
    required_elements: ["personalization", "exclusive offer", "value proposition"]

  - id: "upsell"
    name: "Upsell"
    description: "Upgrade to higher tier or premium service"
    tone_guidance: "Benefits-focused, comparative value"
    required_elements: ["upgrade benefits", "pricing difference", "CTA"]

  - id: "cross_sell"
    name: "Cross-Sell"
    description: "Add complementary services or bundle"
    tone_guidance: "Complementary value, bundle savings"
    required_elements: ["bundle benefits", "combined pricing", "CTA"]

  - id: "service_update"
    name: "Service Update"
    description: "Maintenance, feature launch, policy change"
    tone_guidance: "Clear, informative, professional"
    required_elements: ["what's changing", "when", "impact on customer"]

  - id: "billing"
    name: "Billing Notification"
    description: "Payment due, plan change, billing update"
    tone_guidance: "Clear, transactional, helpful"
    required_elements: ["amount", "due date", "payment method"]
```

**Steps**:
1. Create `backend/app/config/` directory
2. Create products.yaml with StarHub product lines
3. Create cohorts.yaml with customer segments and messaging guidance
4. Create objectives.yaml with communication objectives
5. Create config loader utility function

**Deliverable**: Configuration files ready for use by generation service

---

### 1.4 Pydantic Schemas
**Goal**: Create request/response models for API validation

**Key Schemas**:

```python
# backend/app/schemas/campaign.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class CustomizationOptions(BaseModel):
    tone: str = Field(..., description="Communication tone")
    custom_instructions: Optional[str] = None
    required_phrases: List[str] = Field(default_factory=list)
    prohibited_words: List[str] = Field(default_factory=list)
    length_preference: str = Field(default="optimal")

class PromotionDetails(BaseModel):
    promotion_name: str
    pricing: Optional[Dict] = None
    features: List[str] = Field(default_factory=list)
    terms_conditions: Optional[str] = None
    validity_start: Optional[str] = None
    validity_end: Optional[str] = None

class CampaignCreate(BaseModel):
    campaign_name: str
    channel: str = Field(..., pattern="^(email|sms|push)$")
    objective: str
    product_lines: List[str]
    cohorts: List[str]
    promotion_details: Optional[PromotionDetails] = None
    customization: CustomizationOptions

class CampaignResponse(CampaignCreate):
    campaign_id: int
    created_at: datetime
    updated_at: datetime

# backend/app/schemas/communication.py
class ScoreBreakdown(BaseModel):
    channel_best_practices: int
    cohort_alignment: int
    objective_effectiveness: int
    compliance_safety: int

class CommunicationResponse(BaseModel):
    variation_number: int
    text: str
    recommendation_score: int
    score_breakdown: ScoreBreakdown
    recommendation_reasoning: str
    compliance_notes: str

class GenerationResponse(BaseModel):
    campaign_id: int
    communications: List[CommunicationResponse]
    generated_at: datetime
```

**Steps**:
1. Create Pydantic schemas for all request/response models
2. Add validation rules (field constraints, patterns)
3. Create common schemas (pagination, error responses)

**Deliverable**: Complete Pydantic schemas for API validation

---

## Phase 1 Acceptance Criteria
- ✅ Virtual environment created with all dependencies installed
- ✅ SQLite database created with all tables and indexes
- ✅ Configuration files (products.yaml, cohorts.yaml, objectives.yaml) created
- ✅ SQLAlchemy models defined for all tables
- ✅ Pydantic schemas created for request/response validation
- ✅ Database initialization script working
- ✅ Can query configuration files programmatically

---

# PHASE 2: Communication Generation Service

## Objectives
- Integrate with Claude API via starhub-comms skill
- Generate 5 unique communication variations
- Implement recommendation scoring algorithm
- Build core business logic layer

## Tasks

### 2.1 Claude API Integration
**Goal**: Create service to generate communications via starhub-comms skill

**Key Components**:

```python
# backend/app/services/communication_generator.py
import anthropic
from typing import List, Dict
import os

class CommunicationGenerator:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )

    def generate_communications(
        self,
        channel: str,
        cohorts: List[str],
        objective: str,
        product_lines: List[str],
        promotion_details: Dict,
        customization: Dict
    ) -> List[Dict]:
        """
        Generate 5 communication variations using starhub-comms skill
        """
        # Build detailed prompt
        prompt = self._build_generation_prompt(
            channel, cohorts, objective,
            product_lines, promotion_details, customization
        )

        # Call Claude API with skill invocation
        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Parse 5 variations from response
        variations = self._parse_variations(response.content)

        return variations

    def _build_generation_prompt(self, ...):
        """
        Construct detailed prompt for Claude with all parameters

        Prompt structure:
        1. Invoke starhub-comms skill
        2. Specify channel and constraints
        3. Describe target cohorts and characteristics
        4. Define objective and messaging goals
        5. Include promotion details
        6. Apply customization options
        7. Request 5 unique variations
        """
        # Load cohort characteristics from config
        # Load channel constraints (SMS: 160 chars, etc.)
        # Build comprehensive prompt
        pass

    def _parse_variations(self, response_content):
        """
        Parse Claude's response to extract 5 variations
        """
        # Extract text from response
        # Split into 5 distinct variations
        # Return structured list
        pass
```

**Steps**:
1. Create CommunicationGenerator class
2. Implement prompt building logic (incorporate cohort characteristics, channel constraints)
3. Integrate with starhub-comms skill
4. Implement response parsing
5. Add error handling for API failures
6. Add retry logic (max 2 retries)

**Deliverable**: Working communication generation service

---

### 2.2 Recommendation Scoring Algorithm
**Goal**: Implement 4-pillar scoring system

**Scoring Components**:

1. **Channel Best Practices (30%)**
   - SMS: Character count optimization (140-160 ideal), opt-out required
   - Email: Subject line length (40-60 chars), unsubscribe link
   - Push: Title length (40-50 chars), body length (100-120 chars)

2. **Cohort Alignment (30%)**
   - High-Value: Exclusive, premium language
   - Deal Seekers: Savings, urgency, promotions
   - Young Adults: Streaming, data, mobile-focused
   - Sports Enthusiasts: Sports content keywords

3. **Objective Effectiveness (25%)**
   - Promotion: Urgency language, value proposition, clear CTA
   - Retention: Personalization, exclusive offers
   - Upsell: Upgrade benefits, comparative value
   - Service Update: Clarity, professionalism

4. **Compliance Safety (15%)**
   - Promotional messages: Opt-out present
   - Pricing: Terms and contract duration mentioned
   - Claims: No unsubstantiated absolutes ("best", "guaranteed")
   - Free offers: T&Cs reference

**Implementation**:

```python
# backend/app/services/recommendation_scorer.py

class RecommendationScorer:
    def calculate_score(
        self,
        text: str,
        channel: str,
        cohorts: List[str],
        objective: str,
        customization: Dict
    ) -> Dict:
        """
        Calculate weighted recommendation score
        """
        # Score each pillar
        channel_score = self._score_channel_best_practices(text, channel)
        cohort_score = self._score_cohort_alignment(text, cohorts)
        objective_score = self._score_objective_effectiveness(text, objective)
        compliance_score, compliance_notes = self._score_compliance(
            text, channel, objective
        )

        # Weighted total
        total_score = (
            channel_score * 0.30 +
            cohort_score * 0.30 +
            objective_score * 0.25 +
            compliance_score * 0.15
        )

        # Generate reasoning
        reasoning = self._generate_reasoning(
            channel_score, cohort_score,
            objective_score, compliance_score,
            text, channel, cohorts, objective
        )

        return {
            "total": int(total_score),
            "breakdown": {
                "channel_best_practices": channel_score,
                "cohort_alignment": cohort_score,
                "objective_effectiveness": objective_score,
                "compliance_safety": compliance_score
            },
            "reasoning": reasoning,
            "compliance_notes": compliance_notes
        }

    def _score_channel_best_practices(self, text: str, channel: str) -> int:
        """Score based on channel-specific constraints"""
        # Implement SMS/Email/Push specific scoring
        pass

    def _score_cohort_alignment(self, text: str, cohorts: List[str]) -> int:
        """Score based on cohort messaging alignment"""
        # Load cohort characteristics from config
        # Check for appropriate keywords and tone
        pass

    def _score_objective_effectiveness(self, text: str, objective: str) -> int:
        """Score based on objective-specific effectiveness"""
        # Check for CTA presence
        # Validate objective-specific elements
        pass

    def _score_compliance(self, text: str, channel: str, objective: str) -> tuple:
        """Score compliance safety and generate notes"""
        # Check for required opt-out
        # Validate pricing disclosure
        # Flag risky claims
        pass
```

**Steps**:
1. Create RecommendationScorer class
2. Implement each scoring pillar
3. Implement weighted scoring calculation
4. Create reasoning generation logic
5. Add compliance validation and notes
6. Write comprehensive unit tests for scoring

**Deliverable**: Complete recommendation scoring engine with tests

---

### 2.3 Integration and Testing
**Goal**: Connect generation and scoring, test end-to-end

**Integration Flow**:
```
1. Receive campaign parameters
2. Generate 5 variations via Claude API
3. Score each variation
4. Sort by score (descending)
5. Return ranked variations with scores
```

**Test Cases**:
- Email for Deal Seekers (promotion objective)
- SMS for At-Risk customers (retention objective)
- Push for Sports Enthusiasts (promotion objective)
- Email service update for Mass Market
- Each channel with all required/prohibited phrase variations

**Steps**:
1. Create integration service combining generation + scoring
2. Write integration tests with real Claude API calls
3. Test all channel + objective + cohort combinations (sample set)
4. Validate scoring accuracy manually (top recommendation makes sense)
5. Test error handling (API timeout, invalid inputs)

**Deliverable**: Tested generation + scoring pipeline

---

## Phase 2 Acceptance Criteria
- ✅ Claude API integration working with starhub-comms skill
- ✅ Successfully generates 5 unique variations
- ✅ Scoring algorithm implemented with all 4 pillars
- ✅ Variations ranked correctly by recommendation score
- ✅ Reasoning and compliance notes generated accurately
- ✅ All unit tests passing (scoring components)
- ✅ Integration tests passing (5+ test scenarios)
- ✅ Generation completes within 10 seconds
- ✅ No compliance violations in manual audit (20+ samples)

---

# PHASE 3: API Endpoints

## Objectives
- Build FastAPI REST endpoints
- Implement campaign CRUD operations
- Create generation and export endpoints
- Add error handling and validation

## Tasks

### 3.1 Campaign Management Endpoints
**Goal**: Create CRUD operations for campaigns

**Endpoints**:

```python
# backend/app/api/campaigns.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/api/v1/campaigns", tags=["campaigns"])

@router.post("/", response_model=CampaignResponse)
def create_campaign(
    campaign: CampaignCreate,
    db: Session = Depends(get_db)
):
    """Create new campaign"""
    # Validate inputs
    # Create campaign record
    # Return campaign with ID
    pass

@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Get campaign by ID"""
    pass

@router.put("/{campaign_id}", response_model=CampaignResponse)
def update_campaign(
    campaign_id: int,
    campaign: CampaignCreate,
    db: Session = Depends(get_db)
):
    """Update campaign parameters"""
    pass

@router.delete("/{campaign_id}")
def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Delete campaign and all generated communications"""
    pass

@router.get("/", response_model=List[CampaignResponse])
def list_campaigns(
    skip: int = 0,
    limit: int = 20,
    channel: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List campaigns with pagination and filtering"""
    pass
```

**Steps**:
1. Create campaign CRUD operations
2. Add input validation with Pydantic
3. Implement pagination for list endpoint
4. Add filtering by channel, objective
5. Error handling for not found, validation errors

**Deliverable**: Working campaign management endpoints

---

### 3.2 Communication Generation Endpoints
**Goal**: Create generation and regeneration endpoints

**Endpoints**:

```python
# backend/app/api/communications.py

@router.post("/{campaign_id}/generate", response_model=GenerationResponse)
def generate_communications(
    campaign_id: int,
    db: Session = Depends(get_db),
    generator: CommunicationGenerator = Depends()
):
    """
    Generate 5 communication variations for campaign
    """
    # Load campaign from database
    # Call generation service
    # Score variations
    # Save to database
    # Return ranked variations
    pass

@router.post("/{campaign_id}/regenerate", response_model=GenerationResponse)
def regenerate_communications(
    campaign_id: int,
    updated_params: Dict,
    db: Session = Depends(get_db)
):
    """
    Regenerate with parameter tweaks
    """
    # Load campaign
    # Merge updated parameters
    # Update campaign record
    # Generate new variations
    # Return new ranked variations
    pass

@router.get("/{campaign_id}/communications")
def get_campaign_communications(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """Get all generated communications for campaign"""
    pass

@router.put("/communications/{communication_id}")
def update_communication(
    communication_id: int,
    updates: Dict,
    db: Session = Depends(get_db)
):
    """Update communication (mark selected, save edited text)"""
    pass
```

**Steps**:
1. Create generation endpoint
2. Implement regeneration logic
3. Add communication retrieval and update endpoints
4. Error handling for generation failures
5. Implement retry logic with exponential backoff

**Deliverable**: Working generation and management endpoints

---

### 3.3 Utility Endpoints
**Goal**: Create helper endpoints for UI dropdowns and health checks

**Endpoints**:

```python
# backend/app/api/utilities.py

@router.get("/cohorts")
def get_cohorts():
    """List all available customer cohorts"""
    # Load from cohorts.yaml
    pass

@router.get("/products")
def get_products():
    """List all product lines"""
    # Load from products.yaml
    pass

@router.get("/objectives")
def get_objectives():
    """List supported communication objectives"""
    # Load from objectives.yaml
    pass

@router.get("/health")
def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": "connected"
    }
```

**Steps**:
1. Create utility endpoints
2. Load configuration files
3. Add health check endpoint
4. Add CORS middleware for frontend

**Deliverable**: Working utility endpoints

---

### 3.4 API Testing
**Goal**: Test all endpoints with integration tests

**Test Scenarios**:
1. Create campaign → generate → retrieve communications
2. Update campaign → regenerate
3. Edit communication → retrieve edited version
4. Delete campaign → verify cascade delete
5. List campaigns with pagination
6. Error scenarios (invalid channel, missing required fields)

**Steps**:
1. Create test fixtures (sample campaigns)
2. Write integration tests for all endpoints
3. Test error handling paths
4. Test validation rules
5. Performance testing (response times)

**Deliverable**: Comprehensive API test suite

---

## Phase 3 Acceptance Criteria
- ✅ All campaign CRUD endpoints working
- ✅ Generation endpoint produces 5 ranked variations
- ✅ Regeneration preserves previous inputs
- ✅ Utility endpoints return configuration data
- ✅ Health check endpoint responds
- ✅ All API tests passing
- ✅ Error handling works correctly
- ✅ API response times <2 seconds (95th percentile)
- ✅ OpenAPI documentation auto-generated

---

# PHASE 4: Frontend Development

## Objectives
- Build React/TypeScript frontend
- Create campaign form interface
- Implement results display with recommendation scoring
- Add edit and export functionality

## Tasks

### 4.1 Project Setup
**Goal**: Initialize React/TypeScript project with Vite

**Steps**:
1. Create Vite project: `npm create vite@latest frontend -- --template react-ts`
2. Install dependencies:
   - axios
   - react-router-dom (if multi-page needed)
3. Install Tailwind CSS: `npm install -D tailwindcss postcss autoprefixer`
4. Configure Tailwind
5. Set up TypeScript types
6. Create project structure (components, contexts, services, types)

**Deliverable**: Working React/TypeScript project with Tailwind

---

### 4.2 API Client Layer
**Goal**: Create API service for backend communication

**Implementation**:

```typescript
// src/services/api.ts
import axios from 'axios';

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
    // Handle errors globally
    return Promise.reject(error);
  }
);

export const campaignAPI = {
  create: (data: CampaignCreate) =>
    apiClient.post('/api/v1/campaigns', data),

  get: (id: number) =>
    apiClient.get(`/api/v1/campaigns/${id}`),

  update: (id: number, data: Partial<CampaignCreate>) =>
    apiClient.put(`/api/v1/campaigns/${id}`, data),

  delete: (id: number) =>
    apiClient.delete(`/api/v1/campaigns/${id}`),

  list: (params?: { skip?: number; limit?: number; channel?: string }) =>
    apiClient.get('/api/v1/campaigns', { params }),

  generate: (id: number) =>
    apiClient.post(`/api/v1/campaigns/${id}/generate`),

  regenerate: (id: number, updatedParams: any) =>
    apiClient.post(`/api/v1/campaigns/${id}/regenerate`, updatedParams),
};

export const utilityAPI = {
  getCohorts: () => apiClient.get('/api/v1/cohorts'),
  getProducts: () => apiClient.get('/api/v1/products'),
  getObjectives: () => apiClient.get('/api/v1/objectives'),
};
```

**Steps**:
1. Create axios client with base URL
2. Implement API methods for all endpoints
3. Add error handling interceptor
4. Create TypeScript types for requests/responses

**Deliverable**: Complete API client service

---

### 4.3 State Management
**Goal**: Create React Context for campaign and generation state

**Implementation**:

```typescript
// src/contexts/CampaignContext.tsx
import React, { createContext, useContext, useState } from 'react';

interface CampaignState {
  formData: CampaignFormData;
  setFormData: (data: CampaignFormData) => void;
  currentCampaignId: number | null;
  setCurrentCampaignId: (id: number | null) => void;
}

const CampaignContext = createContext<CampaignState | undefined>(undefined);

export const CampaignProvider: React.FC = ({ children }) => {
  const [formData, setFormData] = useState<CampaignFormData>({
    channel: '',
    cohorts: [],
    productLines: [],
    objective: '',
    promotionDetails: {},
    customization: {}
  });

  const [currentCampaignId, setCurrentCampaignId] = useState<number | null>(null);

  return (
    <CampaignContext.Provider value={{
      formData,
      setFormData,
      currentCampaignId,
      setCurrentCampaignId
    }}>
      {children}
    </CampaignContext.Provider>
  );
};

export const useCampaign = () => {
  const context = useContext(CampaignContext);
  if (!context) throw new Error('useCampaign must be used within CampaignProvider');
  return context;
};
```

**Steps**:
1. Create CampaignContext for form state
2. Create GenerationContext for results state
3. Implement custom hooks (useCampaign, useGeneration)
4. Add error boundaries

**Deliverable**: State management with Context API

---

### 4.4 Campaign Form Components
**Goal**: Build form interface for campaign inputs

**Components**:

1. **ChannelSelector**: Radio buttons for Email/SMS/Push
2. **CohortSelector**: Multi-select checkboxes with descriptions
3. **ProductSelector**: Dropdown with product lines
4. **PromotionInput**: Form for promotion details (name, pricing, features, terms, dates)
5. **CustomizationPanel**: Tone dropdown, custom instructions textarea, required/prohibited phrases

**Implementation**:

```typescript
// src/components/CampaignForm/index.tsx
export const CampaignForm: React.FC = () => {
  const { formData, setFormData } = useCampaign();
  const [isGenerating, setIsGenerating] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleGenerate = async () => {
    // Validate form
    const validationErrors = validateForm(formData);
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setIsGenerating(true);
    try {
      // Create campaign
      const { data: campaign } = await campaignAPI.create(formData);

      // Generate communications
      const { data: results } = await campaignAPI.generate(campaign.campaign_id);

      // Update context with results
      // Display results in chat interface
    } catch (error) {
      // Handle error
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="campaign-form">
      <ChannelSelector
        value={formData.channel}
        onChange={(channel) => setFormData({...formData, channel})}
        error={errors.channel}
      />
      <CohortSelector
        selected={formData.cohorts}
        onChange={(cohorts) => setFormData({...formData, cohorts})}
        error={errors.cohorts}
      />
      {/* Other form components */}

      <button
        onClick={handleGenerate}
        disabled={isGenerating}
        className="generate-button"
      >
        {isGenerating ? 'Generating...' : 'Generate Communications'}
      </button>
    </div>
  );
};
```

**Steps**:
1. Build individual form components
2. Implement form validation
3. Create campaign form container
4. Add loading states
5. Error handling and display

**Deliverable**: Complete campaign form interface

---

### 4.5 Results Display Components
**Goal**: Create chat-like interface for results with recommendation scoring

**Components**:

1. **CommunicationCard**: Display variation with score, reasoning, actions
2. **RecommendationBadge**: Visual score indicator (0-100)
3. **ScoreBreakdown**: Detailed breakdown of 4 scoring pillars
4. **ChatInterface**: Container for displaying results

**Implementation**:

```typescript
// src/components/ResultsDisplay/CommunicationCard.tsx
interface CommunicationCardProps {
  communication: Communication;
  isTopRecommended: boolean;
  onCopy: (text: string) => void;
  onEdit: (comm: Communication) => void;
  onExport: (comm: Communication) => void;
  onSelect: (comm: Communication) => void;
}

export const CommunicationCard: React.FC<CommunicationCardProps> = ({
  communication,
  isTopRecommended,
  onCopy,
  onEdit,
  onExport,
  onSelect
}) => {
  return (
    <div className={`communication-card ${isTopRecommended ? 'recommended' : ''}`}>
      <div className="card-header">
        <RecommendationBadge
          score={communication.recommendation_score}
          isTop={isTopRecommended}
        />
        <span className="variation-number">
          Variation {communication.variation_number}
        </span>
      </div>

      <div className="card-body">
        <pre className="communication-text">
          {communication.edited_text || communication.text}
        </pre>
      </div>

      <ScoreBreakdown breakdown={communication.score_breakdown} />

      <div className="reasoning">
        <strong>Why recommended:</strong>
        <p>{communication.recommendation_reasoning}</p>
      </div>

      {communication.compliance_notes && (
        <div className="compliance-notes">
          <strong>Compliance:</strong>
          <p>{communication.compliance_notes}</p>
        </div>
      )}

      <div className="card-actions">
        <button onClick={() => onCopy(communication.text)}>Copy</button>
        <button onClick={() => onEdit(communication)}>Edit</button>
        <button onClick={() => onExport(communication)}>Export</button>
        <button onClick={() => onSelect(communication)} className="primary">
          Select
        </button>
      </div>
    </div>
  );
};
```

**Steps**:
1. Create CommunicationCard component
2. Build RecommendationBadge with visual score indicator
3. Implement ScoreBreakdown component
4. Create ChatInterface container
5. Add animations for card appearance

**Deliverable**: Complete results display interface

---

### 4.6 Edit and Export Functionality
**Goal**: Allow users to edit communications and export in multiple formats

**Components**:

1. **EditModal**: Inline editor with character counter
2. **ExportOptions**: Export as TXT/CSV/JSON

**Implementation**:

```typescript
// src/components/ActionPanel/EditModal.tsx
interface EditModalProps {
  communication: Communication;
  channel: string;
  onSave: (editedText: string) => void;
  onClose: () => void;
}

export const EditModal: React.FC<EditModalProps> = ({
  communication,
  channel,
  onSave,
  onClose
}) => {
  const [editedText, setEditedText] = useState(communication.text);
  const characterLimit = getChannelLimit(channel);

  const handleSave = async () => {
    await communicationAPI.update(communication.communication_id, {
      edited_text: editedText
    });
    onSave(editedText);
    onClose();
  };

  return (
    <div className="modal">
      <div className="modal-content">
        <h2>Edit Communication</h2>
        <textarea
          value={editedText}
          onChange={(e) => setEditedText(e.target.value)}
          className="edit-textarea"
        />
        <div className="character-counter">
          {editedText.length} / {characterLimit} characters
        </div>
        <div className="modal-actions">
          <button onClick={onClose}>Cancel</button>
          <button onClick={handleSave} className="primary">Save</button>
        </div>
      </div>
    </div>
  );
};

// src/services/export.ts
export const exportCommunication = (
  communication: Communication,
  format: 'txt' | 'csv' | 'json',
  campaign: Campaign
) => {
  let content: string;
  let filename: string;
  let mimeType: string;

  switch (format) {
    case 'txt':
      content = communication.edited_text || communication.text;
      filename = `starhub_comm_${campaign.campaign_id}_v${communication.variation_number}.txt`;
      mimeType = 'text/plain';
      break;

    case 'csv':
      content = `"Channel","Cohorts","Objective","Text","Score"\n`;
      content += `"${campaign.channel}","${campaign.cohorts.join(', ')}","${campaign.objective}","${communication.text}","${communication.recommendation_score}"`;
      filename = `starhub_comm_${campaign.campaign_id}_v${communication.variation_number}.csv`;
      mimeType = 'text/csv';
      break;

    case 'json':
      content = JSON.stringify({
        campaign: {...},
        communication: {...},
        metadata: {
          generated_at: communication.created_at,
          exported_at: new Date().toISOString()
        }
      }, null, 2);
      filename = `starhub_comm_${campaign.campaign_id}_v${communication.variation_number}.json`;
      mimeType = 'application/json';
      break;
  }

  // Trigger download
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
};
```

**Steps**:
1. Create EditModal component
2. Implement character counter based on channel
3. Create export service
4. Add export options UI
5. Test all export formats

**Deliverable**: Working edit and export functionality

---

## Phase 4 Acceptance Criteria
- ✅ Frontend project setup complete with Tailwind CSS
- ✅ API client working with all backend endpoints
- ✅ Campaign form collects all required inputs
- ✅ Form validation working (inline errors)
- ✅ Results display shows 5 ranked variations
- ✅ Top recommendation highlighted visually
- ✅ Score breakdown displayed clearly
- ✅ Edit modal allows text modification
- ✅ Export works for TXT, CSV, JSON formats
- ✅ Regeneration preserves previous inputs
- ✅ Loading states shown during generation
- ✅ Error messages displayed appropriately
- ✅ Responsive design (desktop and tablet)

---

# PHASE 5: Integration, Testing & Deployment

## Objectives
- Connect frontend to backend
- End-to-end testing
- Performance optimization
- Documentation
- Local deployment

## Tasks

### 5.1 Frontend-Backend Integration
**Goal**: Connect React frontend to FastAPI backend

**Steps**:
1. Configure CORS in FastAPI backend
2. Set up environment variables for API URL
3. Test all user flows end-to-end
4. Handle authentication (if needed for production)
5. Test error scenarios (API timeout, network errors)

**Deliverable**: Fully integrated application

---

### 5.2 End-to-End Testing
**Goal**: Validate all acceptance test scenarios

**Test Scenarios** (from requirements spec):
1. Email promotion for Deal Seekers
2. SMS service update for Mass Market
3. Push notification for Sports Enthusiasts
4. Regeneration with parameter changes
5. Manual edit and export
6. Validation and error handling

**Steps**:
1. Execute all 6 test scenarios manually
2. Validate scoring accuracy (manual review)
3. Compliance audit (review 20+ generated samples)
4. Cross-browser testing (Chrome, Safari, Firefox)
5. Performance testing (generation time, API response times)

**Deliverable**: Test report with all scenarios passing

---

### 5.3 Documentation
**Goal**: Create user and developer documentation

**Documents**:
1. **USER_GUIDE.md**: How to use the system (marketing team)
2. **API_DOCUMENTATION.md**: API endpoints and examples
3. **DEVELOPER_SETUP.md**: Setup instructions for development
4. **README.md**: Project overview and quick start

**Steps**:
1. Write user guide with screenshots
2. Document all API endpoints (FastAPI auto-generates OpenAPI)
3. Create developer setup guide
4. Update README with project info

**Deliverable**: Complete documentation

---

### 5.4 Local Deployment
**Goal**: Run application locally for testing and use

**Deployment Steps**:

**Backend**:
```bash
# Navigate to backend
cd backend

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY=your_key_here

# Initialize database
python -m app.init_db

# Run server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**:
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Set API URL
echo "VITE_API_URL=http://localhost:8000" > .env

# Run development server
npm run dev
```

**Access**:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Steps**:
1. Create startup scripts for backend and frontend
2. Document environment setup
3. Test local deployment
4. Create Docker setup (optional for easier deployment)

**Deliverable**: Working local deployment

---

### 5.5 Performance Optimization
**Goal**: Ensure system meets performance criteria

**Optimization Areas**:
1. Backend API response times (<2s)
2. Database query optimization (indexes)
3. Frontend bundle size
4. Generation speed (<10s)

**Steps**:
1. Profile API endpoints
2. Optimize slow database queries
3. Add database indexes if needed
4. Optimize frontend bundle (code splitting if needed)
5. Test with concurrent users (5-10 simultaneous requests)

**Deliverable**: System meeting all performance criteria

---

## Phase 5 Acceptance Criteria
- ✅ Frontend and backend fully integrated
- ✅ All 6 acceptance test scenarios passing
- ✅ Compliance audit complete (0 violations)
- ✅ Cross-browser compatibility verified
- ✅ User guide and developer documentation complete
- ✅ Local deployment working smoothly
- ✅ Performance criteria met:
  - API response <2s (95th percentile)
  - Generation complete <10s
  - Database queries <500ms
  - Frontend load <3s
- ✅ Zero critical bugs
- ✅ Application ready for use by marketing team

---

# Success Metrics Summary

## Functional Success
- ✅ Generate 5 unique, compliant communication variations within 10 seconds
- ✅ AI recommendation accurately identifies best option in >70% of cases
- ✅ Zero compliance violations in generated communications
- ✅ Export functionality works across all formats (TXT, CSV, JSON)
- ✅ Regeneration preserves user inputs and generates new variations
- ✅ Manual editing allows full text modification

## Technical Success
- ✅ Backend API response time <2 seconds (95th percentile)
- ✅ Database queries <500ms (95th percentile)
- ✅ Frontend page load <3 seconds
- ✅ Zero data loss (all campaigns and communications persisted)
- ✅ Error rate <5%

## User Experience Success
- ✅ Marketing team can generate campaigns without technical support
- ✅ User completes generation flow in <5 minutes
- ✅ Interface is clear and intuitive
- ✅ Zero critical bugs in core generation flow

---

# Post-MVP Roadmap

## Phase 6: Authentication & Multi-User (Future)
- User authentication (login/logout)
- Role-based permissions (Marketing, Manager, Compliance)
- User activity tracking

## Phase 7: Advanced Features (Future)
- Template library (save successful communications)
- Promotion library (reusable promotions)
- Campaign approval workflow
- Version history and audit trail
- Analytics dashboard

## Phase 8: Production Deployment (Future)
- Migrate to PostgreSQL
- Deploy to cloud (AWS/Azure/GCP)
- CI/CD pipeline
- Monitoring and alerting
- Backup and disaster recovery

## Phase 9: Integration & Automation (Future)
- CRM/CDP integration for customer data
- Integration with marketing automation platforms
- Scheduled campaign generation
- A/B testing and performance tracking

---

# Execution Strategy with Subagents

Each phase will be executed using specialized subagents:

- **Phase 1**: `backend-architect` for database design, `system-architect` for project structure
- **Phase 2**: `python-expert` for communication generation service and scoring algorithm
- **Phase 3**: `backend-architect` for API endpoints, `quality-engineer` for testing
- **Phase 4**: `frontend-architect` for React components, UI/UX design
- **Phase 5**: `quality-engineer` for testing, `devops-architect` for deployment

Each subagent will work autonomously on their phase, with clear handoff points and deliverables.

---

# Ready to Execute

This plan provides:
- ✅ Complete project structure
- ✅ Detailed implementation tasks for each phase
- ✅ Clear acceptance criteria
- ✅ Testing strategy
- ✅ Documentation requirements
- ✅ Success metrics
- ✅ Post-MVP roadmap

**Estimated Timeline**: 10-12 days of focused development

Ready to start Phase 1 when you approve!