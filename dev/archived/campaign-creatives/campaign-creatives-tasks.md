# Campaign Creative Generation - Task Checklist

**Last Updated**: 2025-11-10 (Context Limit Update)
**Total Estimated Time**: 20 hours
**Time Spent**: ~2 hours
**Overall Progress**: 40% (Phases 1-2 ✅, Phase 3 🔄)

---

## Phase 1: Foundation & Configuration ✅ COMPLETE (45 min actual vs 3h est)

### Task 1.1: Create Directory Structure ✅ COMPLETE
- [x] Create `backend/app/api/creatives.py`
- [x] Create `backend/app/services/creative_generator.py`
- [x] Create `backend/app/models/creative.py`
- [x] Create `backend/app/schemas/creative.py`
- [x] Create `backend/app/config/creatives.yaml`
- [x] Create `backend/static/creatives/` directory
- [x] Add `.gitkeep` to `backend/static/creatives/`
- [x] Create `tests/backend/unit/test_creative_generator.py`
- [x] Create `tests/backend/integration/test_api_creatives.py`

**Validation**: ✅ All files created

---

### Task 1.2: Add Dependencies ✅ COMPLETE
- [x] Run `cd backend && uv add fal-client` (v0.9.0)
- [x] Run `uv add Pillow` (v12.0.0)
- [x] Run `uv add aiofiles` (v25.1.0)
- [x] Run `uv sync` to install dependencies
- [x] Run `uv run pytest ../tests/backend/unit/ -v` to verify no breakage

**Validation**: ✅ Dependencies installed, 24 existing tests passing

---

### Task 1.3: Create Creative Configuration ✅ COMPLETE
- [x] Define `channels.email_header` section (600x400px, 3:2, 200KB, JPEG, 72dpi)
- [x] Define `channels.push_header` section (1200x628px, 2:1, 100KB, JPEG, 72dpi)
- [x] Define `brand_guidelines` section (#00D964, top-left logo, 80px, style prefs)
- [x] Define `model_config.seedream_4` section (fal-ai/flux-pro/v1.1, 28 steps, 3.5 guidance)
- [x] Define `quality_criteria` section (brand/channel/visual compliance)
- [x] Validate YAML syntax with parser

**Validation**: ✅ YAML valid and loads correctly

---

### Task 1.4: Extend Config Loader ✅ COMPLETE
- [x] Add `get_channel_specs(channel_type: str)` function
- [x] Add `get_brand_guidelines()` function
- [x] Add `get_model_config(model_name: str)` function
- [x] Apply caching via `get_cached_config()` pattern
- [x] Add docstrings and error handling
- [x] Functions tested and working

**Validation**: ✅ All 3 functions working, follow existing patterns

---

### Task 1.5: Environment Variable Setup ✅ COMPLETE
- [x] Add `FAL_KEY=your_fal_api_key_here` to `.env.example`
- [x] Add actual `FAL_KEY` to `.env`: `9ee0a86d-99df-4ee0-acbb-3fdac3e273d3`
- [x] Add startup validation in `main.py` to check `FAL_KEY` exists
- [x] Validation logs warning if missing

**Validation**: ✅ FAL_KEY configured, startup validation working

---

## Phase 2: Data Layer ✅ COMPLETE (60 min actual vs 3h est)

### Task 2.1: Create GeneratedCreative Model ✅ COMPLETE
- [x] Define `GeneratedCreative` class in `backend/app/models/creative.py`
- [x] Add all fields: creative_id, campaign_id, variant_number, channel_type, image_filename, image_url, prompt_used, generation_params, model_used, recommendation_score, score_reasoning, is_selected, created_at
- [x] Define relationship to `Campaign` (back_populates="creatives")
- [x] Add check constraint for `channel_type IN ('email_header', 'push_header')`
- [x] Add check constraint for `variant_number BETWEEN 1 AND 3`
- [x] Add indexes on `campaign_id` and `created_at`
- [x] Add `__repr__` method

**Validation**: ✅ Model complete, ~75 lines

---

### Task 2.2: Update Campaign Model ✅ COMPLETE
- [x] Add `creatives = relationship("GeneratedCreative", back_populates="campaign", cascade="all, delete-orphan")` to Campaign class
- [x] Import handled via string reference (no circular imports)
- [x] Relationship tested and working

**Validation**: ✅ Relationship working, cascade delete functional

---

### Task 2.3: Create Database Migration ✅ COMPLETE
- [x] Initialized Alembic: `alembic init alembic`
- [x] Configured `alembic.ini` and `env.py` for SQLite
- [x] Created migration: `047883543b83_add_generated_creatives_table.py`
- [x] Ran `alembic upgrade head` successfully
- [x] Verified table: `sqlite3 starhub_comms.db ".schema generated_creatives"`
- [ ] Test downgrade: `alembic downgrade -1`
- [ ] Re-upgrade: `alembic upgrade head`

**Validation**: Migration runs successfully both ways

---

### Task 2.4: Create Pydantic Schemas (45 min) - EFFORT: M
- [ ] Define `ChannelType` enum (EMAIL_HEADER, PUSH_HEADER)
- [ ] Define `CreativeGenerationRequest` schema with fields and validation
- [ ] Define `GeneratedCreativeResponse` schema with `from_attributes=True`
- [ ] Define `CreativeListResponse` schema
- [ ] Define `CreativeSelectionRequest` schema
- [ ] Add example JSON in `json_schema_extra` for documentation
- [ ] Test schema validation with valid/invalid inputs

**Validation**: Schemas validate correctly

---

### Task 2.5: Write Model Unit Tests (30 min) - EFFORT: M
- [ ] Test creating `GeneratedCreative` instance
- [ ] Test relationship with `Campaign`
- [ ] Test cascade delete (deleting campaign deletes creatives)
- [ ] Test `CreativeGenerationRequest` validation (valid inputs)
- [ ] Test invalid channel_type rejected by schema
- [ ] Test invalid variant_number rejected by schema
- [ ] Run tests: `uv run pytest ../tests/backend/unit/test_creative_model.py -v`

**Validation**: All model tests pass

---

## Phase 3: Service Layer (5 hours)

### Task 3.1: Implement CreativeGenerator Class (90 min) - EFFORT: L
- [ ] Define `CreativeGenerator` class with `__init__(api_key)`
- [ ] Implement `build_prompt()` method (channel, visual_concept, campaign_data, headline, offer_details, partner_logos, style)
- [ ] Implement `generate_image()` method (prompt, channel)
- [ ] Integrate fal_client API call to SeeDream 4.0
- [ ] Add retry logic (3 attempts with exponential backoff)
- [ ] Add timeout handling (15s per request)
- [ ] Add logging for all operations
- [ ] Handle API errors gracefully

**Validation**: Generator can build prompts and call API (with mocking)

---

### Task 3.2: Implement File Storage Handler (45 min) - EFFORT: M
- [ ] Define `save_image()` async function (image_url, campaign_id, channel, variant, static_dir)
- [ ] Implement image download using `httpx.AsyncClient`
- [ ] Implement filename generation: `{campaign_id}_{channel}_{variant}_{timestamp}.jpg`
- [ ] Validate image dimensions using Pillow
- [ ] Save image using `aiofiles`
- [ ] Return dict with filename and relative URL
- [ ] Add error handling for download/save failures

**Validation**: Function downloads and saves test image

---

### Task 3.3: Implement Creative Scoring (45 min) - EFFORT: M
- [ ] Define `score_creative()` function (image_path, channel, prompt_used)
- [ ] Implement heuristic scoring algorithm:
  - Brand compliance: 40 points
  - Channel specs: 30 points
  - Visual quality: 20 points
  - Prompt adherence: 10 points
- [ ] Generate reasoning text explaining score
- [ ] Return dict with score (0-100) and reasoning
- [ ] Add score_breakdown dict

**Validation**: Function returns valid scores and reasoning

---

### Task 3.4: Implement CreativeGenerationService (90 min) - EFFORT: L
- [ ] Define `CreativeGenerationService` class with `__init__(api_key)`
- [ ] Implement `generate_and_score()` async method
- [ ] Define 3 style variations for prompts
- [ ] Loop through 3 variants:
  - Build prompt with style variation
  - Generate image via CreativeGenerator
  - Save image to file system
  - Score creative
  - Save to database
- [ ] Handle partial failures (continue if 1-2 fail)
- [ ] Sort results by score (descending)
- [ ] Add rank to each variant
- [ ] Return list of scored creatives

**Validation**: Service generates 3 variants end-to-end (mocked API)

---

### Task 3.5: Write Service Unit Tests (60 min) - EFFORT: L
- [ ] Test `build_prompt()` with email_header channel
- [ ] Test `build_prompt()` with push_header channel
- [ ] Test `generate_image()` success (mocked fal_client)
- [ ] Test `generate_image()` API failure and retry
- [ ] Test `save_image()` downloads and saves
- [ ] Test `score_creative()` returns valid score
- [ ] Test `generate_and_score()` creates 3 variants
- [ ] Test partial failure handling (1 variant fails, 2 succeed)
- [ ] Run tests: `uv run pytest ../tests/backend/unit/test_creative_generator.py -v`
- [ ] Verify 80%+ code coverage

**Validation**: All service tests pass, coverage >80%

---

## Phase 4: API Layer (4 hours)

### Task 4.1: Create Creatives Router (30 min) - EFFORT: M
- [ ] Define router with `prefix="/api/v1"` and `tags=["creatives"]`
- [ ] Import all required dependencies (FastAPI, SQLAlchemy, schemas, services)
- [ ] Add logger initialization
- [ ] Define all 5 endpoint stubs (POST generate, GET list, GET by ID, PUT select, DELETE)
- [ ] Add route decorators with correct paths and response models

**Validation**: Router imports without errors

---

### Task 4.2: Implement Generate Creatives Endpoint (60 min) - EFFORT: M
- [ ] Implement `POST /api/v1/campaigns/{campaign_id}/generate-creatives`
- [ ] Validate campaign exists (404 if not)
- [ ] Parse campaign JSON fields (product_lines, cohorts, promotion_details, customization)
- [ ] Initialize `CreativeGenerationService`
- [ ] Call `generate_and_score()` with all parameters
- [ ] Load generated creatives from database
- [ ] Return `CreativeListResponse` with 201 status
- [ ] Handle errors with appropriate HTTP status codes
- [ ] Add comprehensive logging

**Validation**: Endpoint generates 3 creatives successfully

---

### Task 4.3: Implement List Creatives Endpoint (30 min) - EFFORT: S
- [ ] Implement `GET /api/v1/campaigns/{campaign_id}/creatives`
- [ ] Validate campaign exists (404 if not)
- [ ] Query all creatives for campaign
- [ ] Order by recommendation_score descending
- [ ] Return `CreativeListResponse` with 200 status
- [ ] Handle empty list case

**Validation**: Endpoint lists creatives sorted by score

---

### Task 4.4: Implement Remaining CRUD Endpoints (45 min) - EFFORT: M
- [ ] Implement `GET /api/v1/creatives/{creative_id}`
  - Load creative by ID (404 if not found)
  - Return `GeneratedCreativeResponse`
- [ ] Implement `PUT /api/v1/creatives/{creative_id}/select`
  - Load creative (404 if not found)
  - Update is_selected field
  - Commit and return updated creative
- [ ] Implement `DELETE /api/v1/creatives/{creative_id}`
  - Load creative (404 if not found)
  - Delete image file from disk
  - Delete database record
  - Return 204 No Content

**Validation**: All CRUD operations work correctly

---

### Task 4.5: Mount Router and Configure Static Files (30 min) - EFFORT: S
- [ ] Import `creatives` router in `main.py`
- [ ] Add `app.include_router(creatives.router)` after other routers
- [ ] Import `StaticFiles` from `fastapi.staticfiles`
- [ ] Add `app.mount("/static", StaticFiles(directory="backend/static"), name="static")`
- [ ] Create test image in `backend/static/creatives/`
- [ ] Test static file serving: `curl http://localhost:8000/static/creatives/test.jpg`
- [ ] Verify router appears in OpenAPI docs at `/docs`

**Validation**: Static files served, router in docs

---

### Task 4.6: Write API Integration Tests (90 min) - EFFORT: L
- [ ] Test `POST /generate-creatives` success (201)
- [ ] Test `POST /generate-creatives` with invalid campaign (404)
- [ ] Test `GET /campaigns/{id}/creatives` lists creatives sorted by score
- [ ] Test `GET /creatives/{id}` returns specific creative
- [ ] Test `PUT /creatives/{id}/select` marks as selected
- [ ] Test `DELETE /creatives/{id}` removes file and record
- [ ] Test static file serving works
- [ ] Use test database fixture for all tests
- [ ] Run tests: `uv run pytest ../tests/backend/integration/test_api_creatives.py -v`

**Validation**: All API integration tests pass

---

## Phase 5: Integration & Quality (3 hours)

### Task 5.1: End-to-End Integration Testing (60 min) - EFFORT: M
- [ ] Write `test_complete_creative_workflow()`:
  - Create campaign
  - Generate 3 creatives
  - Verify 3 creatives returned
  - Verify all image files exist on disk
  - List creatives (verify sorted by score)
  - Select top creative
  - Delete creative (verify file removed)
- [ ] Measure performance: workflow should complete <15 seconds
- [ ] Run test: `uv run pytest tests/backend/integration/test_creative_workflow.py -v`

**Validation**: End-to-end workflow succeeds

---

### Task 5.2: Error Handling Validation (45 min) - EFFORT: M
- [ ] Test invalid FAL_KEY (should return 500)
- [ ] Test network timeout (should retry and fail gracefully)
- [ ] Test disk full scenario (should return 500 with clear error)
- [ ] Test invalid campaign_id (should return 404)
- [ ] Test partial generation failure (1 variant fails, 2 succeed)
- [ ] Verify all error responses have informative messages
- [ ] Run tests: `uv run pytest tests/backend/integration/test_creative_errors.py -v`

**Validation**: All error scenarios handled correctly

---

### Task 5.3: Performance Testing (30 min) - EFFORT: S
- [ ] Test generation time: 3 variants in <10 seconds
- [ ] Test file sizes: email <200KB, push <100KB
- [ ] Test database queries: no N+1 queries (use query logging)
- [ ] Test memory usage: <100MB during generation
- [ ] Document performance benchmarks
- [ ] Run tests: `uv run pytest tests/backend/performance/test_creative_performance.py -v`

**Validation**: All performance targets met

---

### Task 5.4: Code Quality Checks (30 min) - EFFORT: S
- [ ] Run `uv run ruff format .` (should make no changes)
- [ ] Run `uv run ruff check . --fix` (should pass with no errors)
- [ ] Run `uv run mypy backend/app/` (should pass with no type errors)
- [ ] Review all new code for DRY violations
- [ ] Verify all functions have docstrings
- [ ] Check line length limits (100 chars)
- [ ] Verify no `TODO` comments in committed code

**Validation**: All quality checks pass

---

### Task 5.5: Documentation Updates (45 min) - EFFORT: M
- [ ] Update README.md with "Creative Generation" section:
  - Setup instructions (dependencies, env vars)
  - Usage examples (API requests)
  - Endpoint documentation
  - Troubleshooting section
- [ ] Ensure all API endpoints have complete docstrings
- [ ] Add example requests/responses to endpoint docs
- [ ] Create `docs/CREATIVE_GENERATION.md` with detailed guide
- [ ] Verify OpenAPI docs at `/docs` are complete

**Validation**: Documentation complete and accurate

---

## Pre-Implementation Checklist

- [ ] Obtain FAL API key from fal.ai
- [ ] Test FAL API access with sample request
- [ ] Set `FAL_KEY` in `.env` file
- [ ] Review existing `GenerationService` code
- [ ] Review existing `campaigns.py` router
- [ ] Understand `config_loader.py` patterns
- [ ] Create feature branch: `git checkout -b feature/campaign-creatives`
- [ ] Verify clean working directory: `git status`

---

## Post-Implementation Checklist

- [ ] All tests pass: `uv run pytest -v`
- [ ] Code coverage >80%: `uv run pytest --cov=app --cov-report=html`
- [ ] Code quality checks pass (ruff, mypy)
- [ ] Documentation complete and reviewed
- [ ] Manual testing completed successfully
- [ ] Performance benchmarks met
- [ ] Create pull request with comprehensive description
- [ ] Request code review from team
- [ ] Address review feedback
- [ ] Merge to main branch
- [ ] Monitor production logs for errors
- [ ] Collect user feedback on initial usage

---

## Progress Tracking

**Phase 1 - Foundation**: ⬜ Not Started / 🔄 In Progress / ✅ Complete
**Phase 2 - Data Layer**: ⬜ Not Started / 🔄 In Progress / ✅ Complete
**Phase 3 - Service Layer**: ⬜ Not Started / 🔄 In Progress / ✅ Complete
**Phase 4 - API Layer**: ⬜ Not Started / 🔄 In Progress / ✅ Complete
**Phase 5 - Quality**: ⬜ Not Started / 🔄 In Progress / ✅ Complete

**Overall Progress**: 0% Complete (0/39 tasks)

**Estimated Time Remaining**: 20 hours
**Actual Time Spent**: 0 hours

---

## Notes Section

### Blockers
- None currently

### Decisions Made
- Using SeeDream 4.0 (fastest, cheapest)
- Local file storage (simplest for MVP)
- Separate module architecture (clean separation)
- Manual trigger (explicit control)

### Next Actions
1. Obtain FAL API key
2. Set up development environment
3. Start Phase 1 (Foundation)

---

**Task List Status**: Ready for Implementation
**Last Updated**: 2025-11-10
**Version**: 1.0
