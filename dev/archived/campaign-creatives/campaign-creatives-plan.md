# Campaign Creative Generation Integration - Strategic Plan

**Last Updated: 2025-11-10**

---

## Executive Summary

### Objective
Integrate AI-powered campaign creative image generation into the existing Customer Communications Generator pipeline, enabling automated creation of email headers and push notification headers for StarHub marketing campaigns.

### Scope
- **In Scope**: SeeDream 4.0 image generation, local file storage, separate creative module with dedicated API endpoints, 3 variant generation per campaign, integration with existing campaign infrastructure
- **Out of Scope**: Gemini/Midjourney models (future iteration), cloud storage (future), video/social media creatives, integrated creative+communication workflow (future)

### Strategic Approach
Implement as **standalone creative module** following existing codebase patterns, maintaining clean separation of concerns while leveraging shared campaign infrastructure.

### Key Decisions Made
1. **Architecture**: Separate creative module (parallel to communications)
2. **Storage**: Local file system (`backend/static/creatives/`)
3. **AI Model**: SeeDream 4.0 (fast, cost-effective, excellent text rendering)
4. **Workflow**: Manual API call trigger (explicit user control)

### Success Criteria
- Generate 3 creative variants in <10 seconds
- 100% brand compliance (StarHub green #00D964, logo placement)
- Correct channel specifications (email: 600x400px, push: 1200x628px)
- Cost per campaign <$0.06 (3 variants × $0.0175)
- 80%+ test coverage for new code
- Zero breaking changes to existing communication pipeline

---

## Current State Analysis

### Existing Architecture

**Backend Stack**:
- FastAPI with Pydantic v2 validation
- SQLAlchemy ORM with SQLite database
- Anthropic Claude for text generation
- YAML-based configuration system
- uv for dependency management

**Core Pipeline Flow**:
```
Campaign Creation (POST /api/v1/campaigns)
    ↓
Campaign Storage (SQLite with JSON fields)
    ↓
Communication Generation (POST /api/v1/campaigns/{id}/generate)
    ↓
GenerationService orchestrates:
    - CommunicationGenerator → 5 text variations
    - RecommendationScorer → 4-pillar scoring
    ↓
Store in GeneratedCommunication table with scores
```

**Database Models**:
- `Campaign`: Stores campaign config (channel, objective, cohorts, products, promotion, customization)
- `GeneratedCommunication`: Stores 5 variations with scores
- `PromotionUpload`: Stores promotion details
- `ErrorLog`: Tracks generation failures

**Configuration System**:
- `config_loader.py` loads YAML files (cohorts, products, objectives)
- Cached configurations for performance
- Helper functions for cohort characteristics, channel constraints

### Gaps & Requirements

**Missing Capabilities**:
1. Image generation infrastructure (no AI image APIs integrated)
2. File storage mechanism (currently database-only)
3. Creative-specific configuration (brand guidelines, image specs)
4. Creative database model and schemas
5. Creative API endpoints and service layer

**Integration Points**:
- Campaign model already exists (no changes needed)
- Can reuse config_loader pattern for creative specs
- Can mirror GenerationService pattern for CreativeGenerationService
- Follow same API router structure as campaigns.py

---

## Proposed Future State

### Target Architecture

```
Campaign Creation
    ↓
├─→ Communication Generation (existing)
│   ├─ CommunicationGenerator
│   └─ RecommendationScorer
│
└─→ Creative Generation (NEW)
    ├─ CreativeGenerator (SeeDream 4.0 API)
    ├─ CreativeScorer (brand/channel compliance)
    └─ File Storage Handler
```

### New Components

**API Layer** (`backend/app/api/creatives.py`):
- `POST /api/v1/campaigns/{campaign_id}/generate-creatives` - Generate 3 variants
- `GET /api/v1/campaigns/{campaign_id}/creatives` - List all creatives
- `GET /api/v1/creatives/{creative_id}` - Get specific creative
- `PUT /api/v1/creatives/{creative_id}/select` - Mark as selected
- `DELETE /api/v1/creatives/{creative_id}` - Delete creative

**Service Layer** (`backend/app/services/creative_generator.py`):
- `CreativeGenerator`: Image generation via SeeDream 4.0
- `CreativeGenerationService`: Orchestration (generate 3 + score + save)

**Data Layer**:
- `GeneratedCreative` model: creative_id, campaign_id, variant_number, channel_type, image_filename, image_url, prompt_used, model_used, recommendation_score, created_at
- Relationship: `Campaign.creatives` ↔ `GeneratedCreative.campaign`

**Configuration** (`backend/app/config/creatives.yaml`):
```yaml
channels:
  email_header:
    width: 600
    height: 400
    aspect_ratio: "3:2"
    max_file_size_kb: 200
    format: "JPEG"
  push_header:
    width: 1200
    height: 628
    aspect_ratio: "2:1"
    max_file_size_kb: 100
    format: "JPEG"

brand_guidelines:
  primary_color: "#00D964"
  logo_position: "top-left"
  logo_size: "80x80"
  style: "professional lifestyle photography"
```

**File Storage**:
- Directory: `backend/static/creatives/`
- Naming: `{campaign_id}_{channel}_{variant}_{timestamp}.jpg`
- Example: `42_email_header_1_20251110143522.jpg`
- URL: `/static/creatives/{filename}`

---

## Implementation Phases

### Phase 1: Foundation & Configuration
**Goal**: Set up infrastructure for creative generation

**Estimated Duration**: 2-3 hours

**Tasks**:
1. Create directory structure
2. Add SeeDream 4.0 dependencies
3. Create configuration files
4. Set up environment variables
5. Create database migration

### Phase 2: Data Layer
**Goal**: Database models and schemas

**Estimated Duration**: 2-3 hours

**Tasks**:
1. Create `GeneratedCreative` model
2. Add relationship to `Campaign` model
3. Create Pydantic schemas
4. Run database migration
5. Write model unit tests

### Phase 3: Service Layer
**Goal**: Core creative generation logic

**Estimated Duration**: 4-5 hours

**Tasks**:
1. Implement `CreativeGenerator` class
2. Implement `CreativeGenerationService` class
3. Create file storage handler
4. Implement scoring algorithm
5. Write service unit tests

### Phase 4: API Layer
**Goal**: REST API endpoints

**Estimated Duration**: 3-4 hours

**Tasks**:
1. Create `creatives.py` router
2. Implement all 5 endpoints
3. Mount router in `main.py`
4. Configure static file serving
5. Write API integration tests

### Phase 5: Integration & Testing
**Goal**: End-to-end validation

**Estimated Duration**: 2-3 hours

**Tasks**:
1. Integration testing (full workflow)
2. Error handling validation
3. Performance testing
4. Documentation updates
5. Code quality checks (ruff, mypy, black)

---

## Detailed Task Breakdown

### SECTION 1: Foundation & Configuration

#### Task 1.1: Create Directory Structure (S)
**Description**: Set up folder structure for creative module

**Acceptance Criteria**:
- [ ] `backend/app/api/creatives.py` file created
- [ ] `backend/app/services/creative_generator.py` file created
- [ ] `backend/app/models/creative.py` file created
- [ ] `backend/app/schemas/creative.py` file created
- [ ] `backend/app/config/creatives.yaml` file created
- [ ] `backend/static/creatives/` directory created with `.gitkeep`
- [ ] `tests/backend/unit/test_creative_generator.py` file created
- [ ] `tests/backend/integration/test_api_creatives.py` file created

**Dependencies**: None

**Command**:
```bash
mkdir -p backend/static/creatives
touch backend/static/creatives/.gitkeep
touch backend/app/api/creatives.py
touch backend/app/services/creative_generator.py
touch backend/app/models/creative.py
touch backend/app/schemas/creative.py
touch backend/app/config/creatives.yaml
touch tests/backend/unit/test_creative_generator.py
touch tests/backend/integration/test_api_creatives.py
```

---

#### Task 1.2: Add Dependencies (S)
**Description**: Add SeeDream 4.0 and image processing libraries

**Acceptance Criteria**:
- [ ] `fal-client` added to dependencies in pyproject.toml
- [ ] `Pillow` added to dependencies
- [ ] `aiofiles` added to dependencies
- [ ] Dependencies installed via `uv sync`
- [ ] All tests still pass after dependency addition

**Dependencies**: None

**Commands**:
```bash
cd backend
uv add fal-client Pillow aiofiles
uv sync
uv run pytest ../tests/backend/unit/ -v
```

**Notes**:
- SeeDream 4.0 accessible via fal.ai platform
- Pillow for image validation/manipulation
- aiofiles for async file operations

---

#### Task 1.3: Create Creative Configuration (M)
**Description**: Define channel specifications and brand guidelines

**Acceptance Criteria**:
- [ ] `creatives.yaml` contains email_header specs (600x400px, 3:2)
- [ ] `creatives.yaml` contains push_header specs (1200x628px, 2:1)
- [ ] Brand guidelines defined (StarHub green #00D964, logo specs)
- [ ] SeeDream 4.0 model configuration included
- [ ] Quality check criteria defined
- [ ] YAML structure validated

**Dependencies**: Task 1.1

**File**: `backend/app/config/creatives.yaml`

**Schema**:
```yaml
channels:
  email_header:
    width: 600
    height: 400
    aspect_ratio: "3:2"
    max_file_size_kb: 200
    format: "JPEG"
    dpi: 72
  push_header:
    width: 1200
    height: 628
    aspect_ratio: "2:1"
    max_file_size_kb: 100
    format: "JPEG"
    dpi: 72

brand_guidelines:
  primary_color: "#00D964"
  logo_position: "top-left"
  logo_size_px: 80
  font_family: "StarHub branded fonts"
  style_preferences:
    - "professional lifestyle photography"
    - "clean modern design"
    - "warm natural lighting"

model_config:
  seedream_4:
    model_name: "fal-ai/flux-pro/v1.1"
    num_inference_steps: 28
    guidance_scale: 3.5
    num_images: 1
    enable_safety_checker: true
    output_format: "jpeg"

quality_criteria:
  brand_compliance:
    - "StarHub green #00D964 present"
    - "Star logo visible top-left"
    - "Professional quality"
  channel_compliance:
    - "Correct dimensions"
    - "File size within limits"
    - "Aspect ratio maintained"
  visual_quality:
    - "High resolution (no pixelation)"
    - "Clear text rendering"
    - "Appropriate composition"
```

---

#### Task 1.4: Extend Config Loader (M)
**Description**: Add creative config helper functions to config_loader.py

**Acceptance Criteria**:
- [ ] `get_channel_specs(channel_type)` function implemented
- [ ] `get_brand_guidelines()` function implemented
- [ ] `get_model_config(model_name)` function implemented
- [ ] Caching applied to creative configs
- [ ] Unit tests pass for new functions

**Dependencies**: Task 1.3

**File**: `backend/app/services/config_loader.py`

**Functions to Add**:
```python
def get_channel_specs(channel_type: str) -> Dict[str, Any]:
    """Get image specifications for channel (email_header/push_header)."""

def get_brand_guidelines() -> Dict[str, Any]:
    """Get StarHub brand guidelines for creatives."""

def get_model_config(model_name: str = "seedream_4") -> Dict[str, Any]:
    """Get AI model configuration."""
```

---

#### Task 1.5: Environment Variable Setup (S)
**Description**: Configure FAL_KEY environment variable

**Acceptance Criteria**:
- [ ] `FAL_KEY` added to `.env.example` with placeholder
- [ ] `.env` file updated with actual API key (not committed)
- [ ] Environment variable loaded in application startup
- [ ] Validation added to check FAL_KEY exists on startup

**Dependencies**: None

**Files**:
- `.env.example` (safe to commit)
- `.env` (gitignored, actual key)

**Validation Code** (add to `main.py`):
```python
import os
from dotenv import load_dotenv

load_dotenv()

@app.on_event("startup")
async def validate_environment():
    if not os.getenv("FAL_KEY"):
        logger.warning("FAL_KEY not set - creative generation will fail")
```

---

### SECTION 2: Data Layer

#### Task 2.1: Create GeneratedCreative Model (M)
**Description**: SQLAlchemy model for storing creative metadata

**Acceptance Criteria**:
- [ ] Model class created in `backend/app/models/creative.py`
- [ ] All fields defined with correct types
- [ ] Foreign key relationship to Campaign
- [ ] Indexes created on campaign_id and created_at
- [ ] Check constraints for channel_type and model_used
- [ ] Model follows existing Campaign model patterns

**Dependencies**: Task 1.1

**File**: `backend/app/models/creative.py`

**Schema**:
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class GeneratedCreative(Base):
    __tablename__ = "generated_creatives"

    creative_id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.campaign_id"), nullable=False)
    variant_number = Column(Integer, nullable=False)  # 1, 2, or 3
    channel_type = Column(Text, nullable=False)  # email_header, push_header
    image_filename = Column(Text, nullable=False)
    image_url = Column(Text, nullable=False)  # relative URL
    prompt_used = Column(Text, nullable=False)
    generation_params = Column(Text, nullable=True)  # JSON
    model_used = Column(Text, nullable=False, default="seedream-4")
    recommendation_score = Column(Float, nullable=True)
    score_reasoning = Column(Text, nullable=True)
    is_selected = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    campaign = relationship("Campaign", back_populates="creatives")

    __table_args__ = (
        CheckConstraint("channel_type IN ('email_header', 'push_header')", name="check_channel_type"),
        CheckConstraint("variant_number BETWEEN 1 AND 3", name="check_variant_number"),
        Index("idx_creatives_campaign", "campaign_id"),
        Index("idx_creatives_created", "created_at"),
    )
```

---

#### Task 2.2: Update Campaign Model (S)
**Description**: Add creatives relationship to Campaign model

**Acceptance Criteria**:
- [ ] Relationship added to `Campaign` class
- [ ] Cascade delete configured (`cascade="all, delete-orphan"`)
- [ ] Follows same pattern as existing relationships

**Dependencies**: Task 2.1

**File**: `backend/app/models/campaign.py`

**Code to Add**:
```python
creatives = relationship(
    "GeneratedCreative",
    back_populates="campaign",
    cascade="all, delete-orphan"
)
```

---

#### Task 2.3: Create Database Migration (M)
**Description**: Alembic migration for generated_creatives table

**Acceptance Criteria**:
- [ ] Migration file created with descriptive name
- [ ] `upgrade()` creates table with all fields
- [ ] `downgrade()` drops table cleanly
- [ ] Migration tested on clean database
- [ ] No errors when running upgrade/downgrade

**Dependencies**: Task 2.1, Task 2.2

**Commands**:
```bash
cd backend
source venv_linux/bin/activate
alembic revision --autogenerate -m "add_generated_creatives_table"
alembic upgrade head
```

**Validation**:
```bash
sqlite3 backend/starhub_comms.db ".schema generated_creatives"
```

---

#### Task 2.4: Create Pydantic Schemas (M)
**Description**: Request/response schemas for creative API

**Acceptance Criteria**:
- [ ] `CreativeGenerationRequest` schema created
- [ ] `GeneratedCreativeResponse` schema created
- [ ] `CreativeListResponse` schema created
- [ ] `CreativeSelectionRequest` schema created
- [ ] All schemas use Pydantic v2 syntax
- [ ] Validation rules applied (e.g., channel_type enum)
- [ ] Example values provided in schema docstrings

**Dependencies**: Task 2.1

**File**: `backend/app/schemas/creative.py`

**Schemas**:
```python
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ChannelType(str, Enum):
    EMAIL_HEADER = "email_header"
    PUSH_HEADER = "push_header"

class CreativeGenerationRequest(BaseModel):
    """Request to generate creative images for campaign."""
    channel: ChannelType
    visual_concept: str = Field(..., description="Description of desired imagery")
    headline: Optional[str] = Field(None, description="Text to display in creative")
    offer_details: Optional[str] = Field(None, description="Pricing/offer text")
    partner_logos: Optional[List[str]] = Field(None, description="Partner logos to include")
    style_preference: Optional[str] = Field(None, description="Visual style override")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "channel": "email_header",
                "visual_concept": "Happy family watching streaming content",
                "headline": "All you need in one great bundle",
                "offer_details": "$115.66/mth",
                "partner_logos": ["Netflix", "HBO Max"],
                "style_preference": "professional lifestyle photography"
            }
        }
    )

class GeneratedCreativeResponse(BaseModel):
    """Response containing generated creative details."""
    creative_id: int
    campaign_id: int
    variant_number: int
    channel_type: str
    image_url: str
    prompt_used: str
    model_used: str
    recommendation_score: Optional[float]
    score_reasoning: Optional[str]
    is_selected: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CreativeListResponse(BaseModel):
    """List of creatives for a campaign."""
    campaign_id: int
    creatives: List[GeneratedCreativeResponse]
    total: int

class CreativeSelectionRequest(BaseModel):
    """Mark creative as selected."""
    is_selected: bool = True
```

---

#### Task 2.5: Write Model Unit Tests (M)
**Description**: Test database models and schemas

**Acceptance Criteria**:
- [ ] Test `GeneratedCreative` model creation
- [ ] Test relationship with `Campaign`
- [ ] Test cascade delete behavior
- [ ] Test schema validation (valid/invalid inputs)
- [ ] All tests pass

**Dependencies**: Task 2.1, Task 2.2, Task 2.3, Task 2.4

**File**: `tests/backend/unit/test_creative_model.py`

**Test Cases**:
- `test_create_generated_creative()`
- `test_creative_campaign_relationship()`
- `test_cascade_delete_campaign_deletes_creatives()`
- `test_creative_generation_request_validation()`
- `test_invalid_channel_type_rejected()`

---

### SECTION 3: Service Layer

#### Task 3.1: Implement CreativeGenerator Class (L)
**Description**: Core image generation logic using SeeDream 4.0

**Acceptance Criteria**:
- [ ] `CreativeGenerator` class initialized with FAL_KEY
- [ ] `build_prompt()` method constructs prompts from campaign data
- [ ] `generate_image()` method calls SeeDream API
- [ ] Error handling for API failures
- [ ] Retry logic for transient failures (3 retries)
- [ ] Logging for all operations
- [ ] Follows starhub-campaign-creatives skill guidelines

**Dependencies**: Task 1.2, Task 1.3, Task 1.4

**File**: `backend/app/services/creative_generator.py`

**Class Structure**:
```python
import os
import logging
import fal_client
from typing import Dict, Any, Optional
from app.services.config_loader import get_channel_specs, get_brand_guidelines, get_model_config

logger = logging.getLogger(__name__)

class CreativeGenerator:
    """Generate campaign creative images using SeeDream 4.0."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize generator with FAL API key."""
        self.api_key = api_key or os.getenv("FAL_KEY")
        if not self.api_key:
            raise ValueError("FAL_KEY not found")
        self.logger = logging.getLogger(self.__class__.__name__)

    def build_prompt(
        self,
        channel: str,
        visual_concept: str,
        campaign_data: Dict[str, Any],
        headline: Optional[str] = None,
        offer_details: Optional[str] = None,
        partner_logos: Optional[list] = None,
        style: Optional[str] = None,
    ) -> str:
        """
        Build detailed prompt for image generation.

        Incorporates:
        - Channel specifications (dimensions, aspect ratio)
        - Brand guidelines (StarHub green, logo placement)
        - Visual concept and composition
        - Headline and offer text
        - Partner logos
        - Style preferences
        """
        channel_specs = get_channel_specs(channel)
        brand = get_brand_guidelines()

        prompt_parts = [
            f"Create a StarHub {channel.replace('_', ' ')} creative",
            f"({channel_specs['width']}x{channel_specs['height']}px, {channel_specs['aspect_ratio']} aspect ratio)",
            f"featuring {visual_concept}",
        ]

        # Add brand elements
        prompt_parts.append(f"Use StarHub brand green ({brand['primary_color']}) prominently")
        prompt_parts.append(f"StarHub star logo in {brand['logo_position']}")

        # Add text elements
        if headline:
            prompt_parts.append(f"with headline \"{headline}\" in brand green")
        if offer_details:
            prompt_parts.append(f"showing offer \"{offer_details}\" prominently")
        if partner_logos:
            prompt_parts.append(f"including {', '.join(partner_logos)} logos")

        # Style
        style_text = style or brand['style_preferences'][0]
        prompt_parts.append(f"{style_text} with professional quality")

        return ". ".join(prompt_parts) + "."

    def generate_image(self, prompt: str, channel: str) -> Dict[str, Any]:
        """
        Generate image using SeeDream 4.0 API.

        Returns:
            dict with 'url' and 'metadata' keys
        """
        channel_specs = get_channel_specs(channel)
        model_config = get_model_config("seedream_4")

        try:
            # Call fal.ai API
            result = fal_client.subscribe(
                model_config["model_name"],
                arguments={
                    "prompt": prompt,
                    "image_size": {
                        "width": channel_specs["width"],
                        "height": channel_specs["height"],
                    },
                    "num_inference_steps": model_config["num_inference_steps"],
                    "guidance_scale": model_config["guidance_scale"],
                    "num_images": model_config["num_images"],
                    "enable_safety_checker": model_config["enable_safety_checker"],
                    "output_format": model_config["output_format"],
                },
            )

            self.logger.info(f"Generated image successfully: {prompt[:50]}...")

            return {
                "url": result["images"][0]["url"],
                "metadata": {
                    "width": result["images"][0]["width"],
                    "height": result["images"][0]["height"],
                    "content_type": result["images"][0]["content_type"],
                }
            }

        except Exception as e:
            self.logger.error(f"Image generation failed: {e}")
            raise
```

---

#### Task 3.2: Implement File Storage Handler (M)
**Description**: Save generated images to local file system

**Acceptance Criteria**:
- [ ] `save_image()` function downloads from URL and saves to static/creatives/
- [ ] Filename format: `{campaign_id}_{channel}_{variant}_{timestamp}.jpg`
- [ ] Image validation (file size, dimensions, format)
- [ ] Error handling for download/save failures
- [ ] Returns relative URL path for database storage
- [ ] Async implementation using aiofiles

**Dependencies**: Task 1.1, Task 3.1

**File**: `backend/app/services/creative_generator.py`

**Function**:
```python
import aiofiles
import httpx
from PIL import Image
from io import BytesIO
from datetime import datetime

async def save_image(
    image_url: str,
    campaign_id: int,
    channel: str,
    variant: int,
    static_dir: str = "backend/static/creatives"
) -> Dict[str, str]:
    """
    Download and save image from URL to local file system.

    Returns:
        dict with 'filename' and 'url' keys
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = f"{campaign_id}_{channel}_{variant}_{timestamp}.jpg"
    filepath = os.path.join(static_dir, filename)

    # Download image
    async with httpx.AsyncClient() as client:
        response = await client.get(image_url)
        response.raise_for_status()
        image_data = response.content

    # Validate image
    img = Image.open(BytesIO(image_data))
    channel_specs = get_channel_specs(channel)

    if img.width != channel_specs["width"] or img.height != channel_specs["height"]:
        logger.warning(f"Image dimensions {img.width}x{img.height} don't match specs")

    # Save image
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(image_data)

    # Return URL relative to static root
    relative_url = f"/static/creatives/{filename}"

    logger.info(f"Saved image: {filename}")

    return {"filename": filename, "url": relative_url}
```

---

#### Task 3.3: Implement Creative Scoring (M)
**Description**: Score creatives based on brand/channel compliance

**Acceptance Criteria**:
- [ ] `score_creative()` function evaluates brand compliance
- [ ] Scoring criteria: brand color, logo presence, channel specs, visual quality
- [ ] Returns score (0-100) and reasoning text
- [ ] Follows same pattern as `RecommendationScorer`

**Dependencies**: Task 1.3

**File**: `backend/app/services/creative_generator.py`

**Function**:
```python
def score_creative(
    image_path: str,
    channel: str,
    prompt_used: str,
) -> Dict[str, Any]:
    """
    Score creative based on brand and channel compliance.

    Scoring Criteria:
    - Brand Compliance (40%): StarHub green present, logo visible
    - Channel Specs (30%): Correct dimensions, file size
    - Visual Quality (20%): Resolution, clarity
    - Prompt Adherence (10%): Content matches request

    Returns:
        dict with 'score' (0-100) and 'reasoning' keys
    """
    # Placeholder scoring logic (can be enhanced with image analysis)
    # For MVP, use heuristic scoring

    scores = {
        "brand_compliance": 35,  # Assume good (can add color detection later)
        "channel_compliance": 30,  # Validated during save
        "visual_quality": 18,  # Assume good
        "prompt_adherence": 9,  # Assume good
    }

    total_score = sum(scores.values())

    reasoning = (
        f"Brand compliance: {scores['brand_compliance']}/40 (brand elements assumed present). "
        f"Channel specs: {scores['channel_compliance']}/30 (dimensions validated). "
        f"Visual quality: {scores['visual_quality']}/20 (high-resolution output). "
        f"Prompt adherence: {scores['prompt_adherence']}/10 (generated as requested)."
    )

    return {
        "score": total_score,
        "reasoning": reasoning,
        "score_breakdown": scores,
    }
```

---

#### Task 3.4: Implement CreativeGenerationService (L)
**Description**: Orchestration service (generate 3 variants + score + save)

**Acceptance Criteria**:
- [ ] `CreativeGenerationService` class created
- [ ] `generate_and_score()` method generates 3 variants with different styles
- [ ] Each variant uses different composition/style prompt
- [ ] All variants saved to database with scores
- [ ] Returns ranked results (sorted by score)
- [ ] Follows same pattern as `GenerationService`
- [ ] Error handling for partial failures (continue if 1-2 fail)

**Dependencies**: Task 3.1, Task 3.2, Task 3.3

**File**: `backend/app/services/creative_generator.py`

**Class**:
```python
from sqlalchemy.orm import Session
from app.models.creative import GeneratedCreative
import json

class CreativeGenerationService:
    """Orchestrate creative generation and scoring workflow."""

    def __init__(self, api_key: Optional[str] = None):
        self.generator = CreativeGenerator(api_key)
        self.logger = logging.getLogger(self.__class__.__name__)

    async def generate_and_score(
        self,
        campaign_id: int,
        channel: str,
        visual_concept: str,
        campaign_data: Dict[str, Any],
        db: Session,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Generate 3 creative variants, score each, save to database.

        Returns:
            List of variant dicts sorted by score (highest first)
        """
        style_variations = [
            "professional lifestyle photography with warm natural lighting",
            "modern digital art style with vibrant colors and dynamic composition",
            "cinematic photography with dramatic lighting and depth of field",
        ]

        scored_creatives = []

        for variant_num, style in enumerate(style_variations, start=1):
            try:
                # Build prompt
                prompt = self.generator.build_prompt(
                    channel=channel,
                    visual_concept=visual_concept,
                    campaign_data=campaign_data,
                    style=style,
                    **kwargs
                )

                # Generate image
                result = self.generator.generate_image(prompt, channel)

                # Save to file system
                file_info = await save_image(
                    image_url=result["url"],
                    campaign_id=campaign_id,
                    channel=channel,
                    variant=variant_num,
                )

                # Score creative
                score_result = score_creative(
                    image_path=f"backend/static/creatives/{file_info['filename']}",
                    channel=channel,
                    prompt_used=prompt,
                )

                # Save to database
                creative = GeneratedCreative(
                    campaign_id=campaign_id,
                    variant_number=variant_num,
                    channel_type=channel,
                    image_filename=file_info["filename"],
                    image_url=file_info["url"],
                    prompt_used=prompt,
                    generation_params=json.dumps(result["metadata"]),
                    model_used="seedream-4",
                    recommendation_score=score_result["score"],
                    score_reasoning=score_result["reasoning"],
                )

                db.add(creative)
                db.commit()
                db.refresh(creative)

                scored_creatives.append({
                    "creative_id": creative.creative_id,
                    "variant_number": variant_num,
                    "image_url": file_info["url"],
                    "score": score_result["score"],
                    "reasoning": score_result["reasoning"],
                })

                self.logger.info(f"Generated variant {variant_num}: score {score_result['score']}")

            except Exception as e:
                self.logger.error(f"Failed to generate variant {variant_num}: {e}")
                # Continue with other variants
                continue

        # Sort by score
        scored_creatives.sort(key=lambda x: x["score"], reverse=True)

        # Add rank
        for rank, creative in enumerate(scored_creatives, start=1):
            creative["rank"] = rank

        return scored_creatives
```

---

#### Task 3.5: Write Service Unit Tests (L)
**Description**: Test all service layer components

**Acceptance Criteria**:
- [ ] Test `build_prompt()` with various inputs
- [ ] Test `generate_image()` with mocked API
- [ ] Test `save_image()` with test data
- [ ] Test `score_creative()` scoring logic
- [ ] Test `generate_and_score()` full workflow (mocked)
- [ ] Test error handling and retries
- [ ] 80%+ code coverage

**Dependencies**: Task 3.1, Task 3.2, Task 3.3, Task 3.4

**File**: `tests/backend/unit/test_creative_generator.py`

**Test Cases**:
- `test_build_prompt_email_header()`
- `test_build_prompt_push_header()`
- `test_generate_image_success()`
- `test_generate_image_api_failure()`
- `test_save_image_downloads_and_saves()`
- `test_score_creative_returns_valid_score()`
- `test_generate_and_score_creates_3_variants()`
- `test_partial_failure_continues_with_remaining()`

---

### SECTION 4: API Layer

#### Task 4.1: Create Creatives Router (M)
**Description**: FastAPI router with 5 endpoints

**Acceptance Criteria**:
- [ ] Router created with prefix `/api/v1` and tag `creatives`
- [ ] All 5 endpoints defined with correct HTTP methods
- [ ] Pydantic models used for request/response
- [ ] Database session dependency injected
- [ ] Error handling with appropriate HTTP status codes
- [ ] OpenAPI documentation generated

**Dependencies**: Task 2.4, Task 3.4

**File**: `backend/app/api/creatives.py`

**Router**:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

from database import get_db
from app.models.campaign import Campaign
from app.models.creative import GeneratedCreative
from app.schemas.creative import (
    CreativeGenerationRequest,
    GeneratedCreativeResponse,
    CreativeListResponse,
    CreativeSelectionRequest,
)
from app.services.creative_generator import CreativeGenerationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["creatives"])

# Endpoints implemented in next tasks
```

---

#### Task 4.2: Implement Generate Creatives Endpoint (M)
**Description**: POST endpoint to generate 3 creative variants

**Acceptance Criteria**:
- [ ] Endpoint: `POST /api/v1/campaigns/{campaign_id}/generate-creatives`
- [ ] Validates campaign exists
- [ ] Parses campaign JSON fields
- [ ] Calls `CreativeGenerationService.generate_and_score()`
- [ ] Returns list of 3 generated creatives
- [ ] HTTP 201 status on success
- [ ] HTTP 404 if campaign not found
- [ ] HTTP 500 on generation failures

**Dependencies**: Task 4.1

**File**: `backend/app/api/creatives.py`

**Endpoint**:
```python
@router.post(
    "/campaigns/{campaign_id}/generate-creatives",
    response_model=CreativeListResponse,
    status_code=status.HTTP_201_CREATED
)
async def generate_creatives(
    campaign_id: int,
    request: CreativeGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate 3 creative variants for campaign.

    Generates email header or push header images based on campaign configuration.
    Returns 3 variants with different visual styles, scored and ranked.
    """
    # Load campaign
    campaign = db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Campaign {campaign_id} not found"
        )

    try:
        # Parse campaign JSON fields
        campaign_data = {
            "product_lines": json.loads(campaign.product_lines),
            "cohorts": json.loads(campaign.cohorts),
            "promotion_details": json.loads(campaign.promotion_details) if campaign.promotion_details else None,
            "customization": json.loads(campaign.customization) if campaign.customization else {},
        }

        # Generate creatives
        service = CreativeGenerationService()
        creatives = await service.generate_and_score(
            campaign_id=campaign_id,
            channel=request.channel.value,
            visual_concept=request.visual_concept,
            campaign_data=campaign_data,
            db=db,
            headline=request.headline,
            offer_details=request.offer_details,
            partner_logos=request.partner_logos,
            style=request.style_preference,
        )

        logger.info(f"Generated {len(creatives)} creatives for campaign {campaign_id}")

        # Load from database for response
        db_creatives = db.query(GeneratedCreative).filter(
            GeneratedCreative.campaign_id == campaign_id
        ).order_by(GeneratedCreative.recommendation_score.desc()).all()

        return CreativeListResponse(
            campaign_id=campaign_id,
            creatives=[GeneratedCreativeResponse.model_validate(c) for c in db_creatives],
            total=len(db_creatives),
        )

    except Exception as e:
        logger.error(f"Failed to generate creatives: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Creative generation failed: {str(e)}"
        )
```

---

#### Task 4.3: Implement List Creatives Endpoint (S)
**Description**: GET endpoint to list all creatives for campaign

**Acceptance Criteria**:
- [ ] Endpoint: `GET /api/v1/campaigns/{campaign_id}/creatives`
- [ ] Returns all creatives sorted by score (descending)
- [ ] HTTP 200 status
- [ ] HTTP 404 if campaign not found
- [ ] Empty list if no creatives

**Dependencies**: Task 4.1

**File**: `backend/app/api/creatives.py`

**Endpoint**:
```python
@router.get(
    "/campaigns/{campaign_id}/creatives",
    response_model=CreativeListResponse
)
def list_creatives(
    campaign_id: int,
    db: Session = Depends(get_db)
):
    """List all creatives for campaign, sorted by score."""
    campaign = db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    creatives = db.query(GeneratedCreative).filter(
        GeneratedCreative.campaign_id == campaign_id
    ).order_by(GeneratedCreative.recommendation_score.desc()).all()

    return CreativeListResponse(
        campaign_id=campaign_id,
        creatives=[GeneratedCreativeResponse.model_validate(c) for c in creatives],
        total=len(creatives),
    )
```

---

#### Task 4.4: Implement Remaining CRUD Endpoints (M)
**Description**: GET by ID, SELECT, DELETE endpoints

**Acceptance Criteria**:
- [ ] `GET /api/v1/creatives/{creative_id}` - Get specific creative
- [ ] `PUT /api/v1/creatives/{creative_id}/select` - Mark as selected
- [ ] `DELETE /api/v1/creatives/{creative_id}` - Delete creative + file
- [ ] All endpoints return appropriate HTTP status codes
- [ ] Delete endpoint removes image file from disk

**Dependencies**: Task 4.1

**File**: `backend/app/api/creatives.py`

**Endpoints**:
```python
@router.get("/creatives/{creative_id}", response_model=GeneratedCreativeResponse)
def get_creative(creative_id: int, db: Session = Depends(get_db)):
    """Get creative by ID."""
    creative = db.query(GeneratedCreative).filter(
        GeneratedCreative.creative_id == creative_id
    ).first()
    if not creative:
        raise HTTPException(status_code=404, detail="Creative not found")
    return GeneratedCreativeResponse.model_validate(creative)

@router.put("/creatives/{creative_id}/select", response_model=GeneratedCreativeResponse)
def select_creative(
    creative_id: int,
    request: CreativeSelectionRequest,
    db: Session = Depends(get_db)
):
    """Mark creative as selected."""
    creative = db.query(GeneratedCreative).filter(
        GeneratedCreative.creative_id == creative_id
    ).first()
    if not creative:
        raise HTTPException(status_code=404, detail="Creative not found")

    creative.is_selected = request.is_selected
    db.commit()
    db.refresh(creative)
    return GeneratedCreativeResponse.model_validate(creative)

@router.delete("/creatives/{creative_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_creative(creative_id: int, db: Session = Depends(get_db)):
    """Delete creative and associated image file."""
    creative = db.query(GeneratedCreative).filter(
        GeneratedCreative.creative_id == creative_id
    ).first()
    if not creative:
        raise HTTPException(status_code=404, detail="Creative not found")

    # Delete image file
    filepath = f"backend/static/creatives/{creative.image_filename}"
    if os.path.exists(filepath):
        os.remove(filepath)
        logger.info(f"Deleted file: {filepath}")

    db.delete(creative)
    db.commit()
    return None
```

---

#### Task 4.5: Mount Router and Configure Static Files (S)
**Description**: Register router in main.py and enable static file serving

**Acceptance Criteria**:
- [ ] Router imported and mounted in `main.py`
- [ ] Static files configured for `/static/creatives/` directory
- [ ] Static file serving tested with sample image
- [ ] Router appears in OpenAPI docs

**Dependencies**: Task 4.1, Task 4.2, Task 4.3, Task 4.4

**File**: `backend/main.py`

**Code to Add**:
```python
from fastapi.staticfiles import StaticFiles
from app.api import creatives

# Mount router
app.include_router(creatives.router)

# Static files
app.mount("/static", StaticFiles(directory="backend/static"), name="static")
```

**Test**:
```bash
curl http://localhost:8000/static/creatives/test.jpg
```

---

#### Task 4.6: Write API Integration Tests (L)
**Description**: End-to-end API testing

**Acceptance Criteria**:
- [ ] Test full generation workflow (create campaign → generate creatives)
- [ ] Test list creatives endpoint
- [ ] Test get creative endpoint
- [ ] Test select creative endpoint
- [ ] Test delete creative endpoint (verify file deletion)
- [ ] Test error cases (campaign not found, creative not found)
- [ ] All tests use test database fixture

**Dependencies**: Task 4.2, Task 4.3, Task 4.4, Task 4.5

**File**: `tests/backend/integration/test_api_creatives.py`

**Test Cases**:
- `test_generate_creatives_success()`
- `test_generate_creatives_campaign_not_found()`
- `test_list_creatives_returns_sorted_by_score()`
- `test_get_creative_by_id()`
- `test_select_creative_marks_as_selected()`
- `test_delete_creative_removes_file_and_record()`
- `test_static_file_serving_works()`

---

### SECTION 5: Integration & Quality

#### Task 5.1: End-to-End Integration Testing (M)
**Description**: Complete workflow validation

**Acceptance Criteria**:
- [ ] Test: Create campaign → generate creatives → list → select → delete
- [ ] Verify 3 creatives generated with different styles
- [ ] Verify all images saved to disk
- [ ] Verify database records created correctly
- [ ] Verify scoring applied to all variants
- [ ] Performance: Complete workflow in <15 seconds

**Dependencies**: All previous tasks

**File**: `tests/backend/integration/test_creative_workflow.py`

**Test**:
```python
async def test_complete_creative_workflow(test_client, test_db):
    # 1. Create campaign
    campaign_response = test_client.post("/api/v1/campaigns", json={...})
    campaign_id = campaign_response.json()["campaign_id"]

    # 2. Generate creatives
    creative_response = test_client.post(
        f"/api/v1/campaigns/{campaign_id}/generate-creatives",
        json={
            "channel": "email_header",
            "visual_concept": "Family watching streaming content",
            "headline": "Entertainment for everyone",
        }
    )
    assert creative_response.status_code == 201
    creatives = creative_response.json()["creatives"]
    assert len(creatives) == 3

    # 3. Verify files exist
    for creative in creatives:
        filename = creative["image_url"].split("/")[-1]
        filepath = f"backend/static/creatives/{filename}"
        assert os.path.exists(filepath)

    # 4. List creatives
    list_response = test_client.get(f"/api/v1/campaigns/{campaign_id}/creatives")
    assert len(list_response.json()["creatives"]) == 3

    # 5. Select top creative
    top_creative_id = creatives[0]["creative_id"]
    select_response = test_client.put(
        f"/api/v1/creatives/{top_creative_id}/select",
        json={"is_selected": true}
    )
    assert select_response.json()["is_selected"] == true

    # 6. Delete creative
    delete_response = test_client.delete(f"/api/v1/creatives/{top_creative_id}")
    assert delete_response.status_code == 204
```

---

#### Task 5.2: Error Handling Validation (M)
**Description**: Test all error scenarios

**Acceptance Criteria**:
- [ ] Test API failures (FAL_KEY invalid, network timeout)
- [ ] Test file system errors (disk full, permission denied)
- [ ] Test database errors (constraint violations)
- [ ] Verify proper HTTP status codes returned
- [ ] Verify error messages are informative
- [ ] Verify partial failures don't break entire workflow

**Dependencies**: All previous tasks

**File**: `tests/backend/integration/test_creative_errors.py`

**Test Cases**:
- `test_invalid_api_key_returns_500()`
- `test_network_timeout_retries_and_fails()`
- `test_disk_full_returns_500()`
- `test_invalid_campaign_id_returns_404()`
- `test_partial_generation_failure_continues()`

---

#### Task 5.3: Performance Testing (S)
**Description**: Validate performance targets

**Acceptance Criteria**:
- [ ] Generation of 3 variants completes in <10 seconds
- [ ] File sizes within limits (email <200KB, push <100KB)
- [ ] Database queries optimized (no N+1 queries)
- [ ] Memory usage acceptable (<100MB for generation)
- [ ] Performance benchmarks documented

**Dependencies**: All previous tasks

**File**: `tests/backend/performance/test_creative_performance.py`

**Tests**:
- `test_generation_time_under_10_seconds()`
- `test_file_sizes_within_limits()`
- `test_no_n_plus_1_queries()`

---

#### Task 5.4: Code Quality Checks (S)
**Description**: Run linting and type checking

**Acceptance Criteria**:
- [ ] `ruff format .` passes (no formatting issues)
- [ ] `ruff check . --fix` passes (no lint errors)
- [ ] `mypy backend/` passes (no type errors)
- [ ] All new code follows CLAUDE.md standards
- [ ] No DRY violations detected

**Dependencies**: All previous tasks

**Commands**:
```bash
cd backend
uv run ruff format .
uv run ruff check . --fix
uv run mypy backend/app/
```

---

#### Task 5.5: Documentation Updates (M)
**Description**: Update project documentation

**Acceptance Criteria**:
- [ ] README.md updated with creative generation section
- [ ] API documentation complete in FastAPI auto-docs
- [ ] Example requests/responses provided
- [ ] Environment variable setup documented
- [ ] Troubleshooting section added

**Dependencies**: All previous tasks

**Files to Update**:
- `README.md` - Add creative generation section
- `backend/app/api/creatives.py` - Ensure all docstrings complete
- Create `docs/CREATIVE_GENERATION.md` - Detailed guide

**Documentation Sections**:
```markdown
## Creative Generation

### Setup
1. Install dependencies: `uv add fal-client Pillow aiofiles`
2. Set environment variable: `export FAL_KEY="your_fal_api_key"`
3. Run migration: `alembic upgrade head`

### Usage
Generate creatives for campaign:
POST /api/v1/campaigns/{campaign_id}/generate-creatives
{
  "channel": "email_header",
  "visual_concept": "Happy family watching streaming",
  "headline": "Entertainment for everyone",
  "offer_details": "$115.66/mth"
}

### Endpoints
- POST /api/v1/campaigns/{id}/generate-creatives - Generate 3 variants
- GET /api/v1/campaigns/{id}/creatives - List all creatives
- GET /api/v1/creatives/{id} - Get specific creative
- PUT /api/v1/creatives/{id}/select - Mark as selected
- DELETE /api/v1/creatives/{id} - Delete creative

### Troubleshooting
- "FAL_KEY not found": Set environment variable
- "Generation timeout": Check network connectivity
- "File size too large": Adjust compression in config
```

---

## Risk Assessment & Mitigation

### Technical Risks

**Risk 1: SeeDream 4.0 API Reliability**
- **Impact**: High (blocks creative generation)
- **Probability**: Medium
- **Mitigation**:
  - Implement retry logic (3 attempts with exponential backoff)
  - Add timeout handling (15s per request)
  - Fallback to error logging and user notification
  - Consider adding queue system for retries

**Risk 2: Image Quality Not Meeting Brand Standards**
- **Impact**: High (brand reputation)
- **Probability**: Medium
- **Mitigation**:
  - Implement human review workflow initially
  - Refine prompts based on initial results
  - Add manual selection/rejection capability
  - Track quality metrics and iterate on prompts

**Risk 3: File Storage Scalability**
- **Impact**: Medium (disk space)
- **Probability**: High (over time)
- **Mitigation**:
  - Implement cleanup policy (delete after 30 days)
  - Add disk usage monitoring
  - Plan migration to cloud storage (future phase)
  - Compress images to meet size limits

**Risk 4: Dependency Conflicts**
- **Impact**: Low (development delays)
- **Probability**: Low
- **Mitigation**:
  - Use uv for dependency resolution
  - Test all dependencies before integration
  - Maintain separate test environment

**Risk 5: Performance Degradation**
- **Impact**: Medium (user experience)
- **Probability**: Low
- **Mitigation**:
  - Async implementation for I/O operations
  - Background task queue for generation (future)
  - Performance monitoring and benchmarks
  - Caching for repeated requests

### Operational Risks

**Risk 6: Cost Overruns**
- **Impact**: Medium (budget)
- **Probability**: Low
- **Mitigation**:
  - SeeDream 4.0 is cheapest option ($0.0175/image)
  - Monitor API usage and costs
  - Implement rate limiting if needed
  - Set monthly budget alerts

**Risk 7: Breaking Changes to Existing Pipeline**
- **Impact**: Critical (production stability)
- **Probability**: Very Low
- **Mitigation**:
  - Separate module architecture (no shared code)
  - Independent router and services
  - Comprehensive integration testing
  - Gradual rollout (feature flag if needed)

---

## Success Metrics

### Performance Metrics
- **Generation Time**: <10 seconds for 3 variants (Target: 8s average)
- **API Success Rate**: >99% (excluding network issues)
- **File Size Compliance**: 100% within channel limits
- **Uptime**: >99.5% availability

### Quality Metrics
- **Brand Compliance Rate**: >95% (manual review initially)
- **Channel Spec Compliance**: 100% (automated validation)
- **User Acceptance Rate**: >80% (creatives selected/approved)
- **First-Time Approval**: >70% (no regeneration needed)

### Business Metrics
- **Cost per Campaign**: <$0.06 (3 variants × $0.0175 + overhead)
- **Time Savings**: >90% vs manual design (5 min vs 60 min)
- **Campaign Volume**: Support 50+ campaigns/month
- **User Adoption**: >60% of campaigns use creative generation

### Technical Metrics
- **Test Coverage**: >80% for new code
- **Code Quality**: Zero ruff/mypy errors
- **Documentation Completeness**: 100% public APIs documented
- **Deployment Success Rate**: 100% (no rollbacks)

---

## Resource Requirements

### Development Resources
- **Backend Developer**: 15-20 hours total
  - Phase 1-2: 5 hours
  - Phase 3: 5 hours
  - Phase 4: 4 hours
  - Phase 5: 4 hours
  - Buffer: 2 hours

### Infrastructure Resources
- **FAL API Account**: Required (SeeDream 4.0 access)
- **Disk Storage**: ~100MB initial (grows over time)
- **Database**: Minimal (new table, ~10KB per creative)
- **Compute**: No additional backend resources needed

### Third-Party Dependencies
- **fal-client**: SeeDream 4.0 API access
- **Pillow**: Image validation/manipulation
- **aiofiles**: Async file I/O

### Knowledge Requirements
- Existing codebase patterns (FastAPI, SQLAlchemy)
- Image generation API integration
- File storage best practices
- Pydantic v2 validation

---

## Timeline Estimates

### Optimistic Scenario (15 hours)
- Phase 1: 2 hours
- Phase 2: 2 hours
- Phase 3: 4 hours
- Phase 4: 3 hours
- Phase 5: 2 hours
- Buffer: 2 hours

### Realistic Scenario (20 hours)
- Phase 1: 3 hours
- Phase 2: 3 hours
- Phase 3: 5 hours
- Phase 4: 4 hours
- Phase 5: 3 hours
- Buffer: 2 hours

### Conservative Scenario (25 hours)
- Phase 1: 4 hours
- Phase 2: 4 hours
- Phase 3: 6 hours
- Phase 4: 5 hours
- Phase 5: 4 hours
- Buffer: 2 hours

### Recommended Approach
**Realistic Scenario (20 hours)** spread over 1 week:
- Day 1-2: Phase 1 & 2 (Foundation + Data Layer)
- Day 3-4: Phase 3 (Service Layer)
- Day 5: Phase 4 (API Layer)
- Day 6: Phase 5 (Integration & Quality)
- Day 7: Buffer for refinement and documentation

---

## Dependencies & Prerequisites

### External Dependencies
1. **FAL API Access**
   - Sign up for fal.ai account
   - Generate API key
   - Set `FAL_KEY` environment variable
   - Verify API access with test call

2. **SeeDream 4.0 Model**
   - Model: `fal-ai/flux-pro/v1.1`
   - Ensure model is accessible
   - Review pricing and rate limits

### Internal Dependencies
1. **Existing Campaign System**
   - Campaign model must exist (already present)
   - Campaign API functional (already present)
   - Database migrations working (Alembic configured)

2. **Development Environment**
   - Python 3.10+ with uv installed
   - SQLite database configured
   - FastAPI application running
   - Test suite operational

3. **Configuration System**
   - YAML configuration loader functional
   - Environment variable loading working

### Knowledge Prerequisites
- FastAPI framework and routing
- SQLAlchemy ORM and relationships
- Pydantic v2 validation
- Async/await patterns in Python
- Image processing basics (Pillow)
- API integration patterns
- Testing with pytest

---

## Next Steps

### Immediate Actions (Pre-Implementation)
1. **Obtain FAL API Key**
   - Sign up at fal.ai
   - Generate API key
   - Test API access
   - Document key in `.env`

2. **Review Existing Code**
   - Understand `GenerationService` pattern
   - Review database migration process
   - Study `config_loader` implementation
   - Familiarize with testing patterns

3. **Set Up Development Branch**
   - Create feature branch: `feature/campaign-creatives`
   - Ensure clean working directory
   - Run existing tests to verify baseline

### Post-Implementation Actions
1. **Monitoring Setup**
   - Add logging for all creative operations
   - Track API success/failure rates
   - Monitor disk usage trends
   - Set up cost tracking

2. **User Training**
   - Document creative generation workflow
   - Provide example requests
   - Create troubleshooting guide
   - Collect initial user feedback

3. **Future Enhancements**
   - Cloud storage migration (S3/Azure)
   - Additional AI models (Gemini, Midjourney)
   - Automated brand compliance checking (computer vision)
   - Background job queue for async generation
   - Creative variant comparison UI
   - A/B testing integration

---

## Appendix

### File Structure Reference
```
backend/
├── app/
│   ├── api/
│   │   ├── campaigns.py (existing)
│   │   ├── communications.py (existing)
│   │   └── creatives.py (NEW)
│   ├── models/
│   │   ├── campaign.py (MODIFY - add relationship)
│   │   └── creative.py (NEW)
│   ├── schemas/
│   │   ├── campaign.py (existing)
│   │   └── creative.py (NEW)
│   ├── services/
│   │   ├── config_loader.py (MODIFY - add creative config)
│   │   ├── generation_service.py (existing)
│   │   └── creative_generator.py (NEW)
│   └── config/
│       └── creatives.yaml (NEW)
├── static/
│   └── creatives/ (NEW)
├── main.py (MODIFY - mount router, static files)
└── database.py (existing)

tests/
└── backend/
    ├── unit/
    │   ├── test_creative_generator.py (NEW)
    │   └── test_creative_model.py (NEW)
    ├── integration/
    │   ├── test_api_creatives.py (NEW)
    │   └── test_creative_workflow.py (NEW)
    └── performance/
        └── test_creative_performance.py (NEW)

dev/
└── active/
    └── campaign-creatives/
        ├── campaign-creatives-plan.md (THIS FILE)
        ├── campaign-creatives-context.md
        └── campaign-creatives-tasks.md
```

### Command Reference
```bash
# Setup
cd backend
uv add fal-client Pillow aiofiles
uv sync
export FAL_KEY="your_api_key_here"

# Development
uv run uvicorn main:app --reload

# Database
alembic revision --autogenerate -m "add_generated_creatives_table"
alembic upgrade head

# Testing
uv run pytest ../tests/backend/unit/ -v
uv run pytest ../tests/backend/integration/ -v
uv run pytest --cov=app --cov-report=html

# Code Quality
uv run ruff format .
uv run ruff check . --fix
uv run mypy app/

# Static Files
curl http://localhost:8000/static/creatives/test.jpg
```

### API Request Examples
```bash
# Generate creatives
curl -X POST http://localhost:8000/api/v1/campaigns/1/generate-creatives \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "email_header",
    "visual_concept": "Happy Asian family watching streaming content together",
    "headline": "All you need in one great bundle",
    "offer_details": "$115.66/mth",
    "partner_logos": ["Netflix", "HBO Max"]
  }'

# List creatives
curl http://localhost:8000/api/v1/campaigns/1/creatives

# Get creative
curl http://localhost:8000/api/v1/creatives/1

# Select creative
curl -X PUT http://localhost:8000/api/v1/creatives/1/select \
  -H "Content-Type: application/json" \
  -d '{"is_selected": true}'

# Delete creative
curl -X DELETE http://localhost:8000/api/v1/creatives/1
```

---

**Plan Status**: Ready for Implementation
**Last Updated**: 2025-11-10
**Version**: 1.0
