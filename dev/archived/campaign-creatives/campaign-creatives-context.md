# Campaign Creative Generation - Context & Key Information

**Last Updated**: 2025-11-10

---

## Key Decisions

### Architecture Decision
- **Choice**: Separate Creative Module (standalone)
- **Rationale**: Clean separation of concerns, independent lifecycle, no impact on existing communication pipeline
- **Alternative Rejected**: Integrated with communications (too tightly coupled)

### Storage Decision
- **Choice**: Local File System (`backend/static/creatives/`)
- **Rationale**: Simple for MVP, no external dependencies, easy to test
- **Future Migration**: Cloud storage (S3/Azure) in Phase 2
- **Naming Convention**: `{campaign_id}_{channel}_{variant}_{timestamp}.jpg`

### AI Model Decision
- **Choice**: SeeDream 4.0 via fal.ai
- **Rationale**:
  - Fastest generation (1-3s per image)
  - Lowest cost ($0.0175/image vs $0.039-$0.10)
  - Excellent text rendering
  - Good quality for marketing creatives
- **Alternatives Available**: Gemini Nano Banana, Midjourney (future phases)

### Workflow Decision
- **Choice**: Manual API Call Trigger
- **Rationale**: Explicit user control, no automatic costs, flexible timing
- **User Flow**: Create campaign → (optional) generate creatives → select best variant

---

## Critical Files

### Existing Files (Reference Only)
| File | Purpose | Key Patterns to Follow |
|------|---------|----------------------|
| `backend/app/services/generation_service.py` | Communication generation orchestration | Service class pattern, generate_and_score() method |
| `backend/app/api/campaigns.py` | Campaign CRUD endpoints | Router structure, error handling, JSON parsing |
| `backend/app/models/campaign.py` | Campaign database model | SQLAlchemy patterns, relationships, constraints |
| `backend/app/services/config_loader.py` | YAML configuration loading | Config caching, helper functions |
| `backend/app/schemas/campaign.py` | Pydantic validation schemas | Schema patterns, from_orm_model() |

### New Files (To Create)
| File | Purpose | Lines (Est) |
|------|---------|-------------|
| `backend/app/api/creatives.py` | Creative API endpoints | ~250 |
| `backend/app/services/creative_generator.py` | Image generation service | ~400 |
| `backend/app/models/creative.py` | GeneratedCreative model | ~75 |
| `backend/app/schemas/creative.py` | Creative request/response schemas | ~100 |
| `backend/app/config/creatives.yaml` | Channel/brand config | ~50 |
| `tests/backend/unit/test_creative_generator.py` | Service unit tests | ~300 |
| `tests/backend/integration/test_api_creatives.py` | API integration tests | ~200 |

### Files to Modify
| File | Change | Impact |
|------|--------|--------|
| `backend/app/models/campaign.py` | Add `creatives` relationship | 3 lines, low risk |
| `backend/app/services/config_loader.py` | Add creative config helpers | ~60 lines, low risk |
| `backend/main.py` | Mount router, static files | 5 lines, low risk |
| `backend/pyproject.toml` | Add dependencies | 3 lines, managed by uv |

---

## Dependencies

### External Dependencies (via uv)
```toml
[project.dependencies]
# NEW ADDITIONS
"fal-client>=0.4.0"  # SeeDream 4.0 API access via fal.ai
"Pillow>=10.2.0"     # Image validation and manipulation
"aiofiles>=23.2.1"   # Async file operations
```

### Environment Variables
```bash
# Required for creative generation
FAL_KEY="your_fal_api_key_here"  # Get from fal.ai platform

# Existing (no changes)
ANTHROPIC_API_KEY="..."  # For text communications
```

### Internal Dependencies
- Campaign model (existing)
- Database connection (existing)
- Config loader pattern (existing)
- FastAPI application (existing)

---

## Technical Specifications

### Database Schema

**Table**: `generated_creatives`
```sql
CREATE TABLE generated_creatives (
    creative_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    variant_number INTEGER NOT NULL,  -- 1, 2, or 3
    channel_type TEXT NOT NULL,  -- email_header, push_header
    image_filename TEXT NOT NULL,
    image_url TEXT NOT NULL,  -- /static/creatives/{filename}
    prompt_used TEXT NOT NULL,
    generation_params TEXT,  -- JSON
    model_used TEXT NOT NULL DEFAULT 'seedream-4',
    recommendation_score REAL,
    score_reasoning TEXT,
    is_selected BOOLEAN DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id),
    CHECK (channel_type IN ('email_header', 'push_header')),
    CHECK (variant_number BETWEEN 1 AND 3)
);

CREATE INDEX idx_creatives_campaign ON generated_creatives(campaign_id);
CREATE INDEX idx_creatives_created ON generated_creatives(created_at);
```

### API Endpoints

| Method | Endpoint | Purpose | Request | Response |
|--------|----------|---------|---------|----------|
| POST | `/api/v1/campaigns/{id}/generate-creatives` | Generate 3 variants | CreativeGenerationRequest | CreativeListResponse (201) |
| GET | `/api/v1/campaigns/{id}/creatives` | List all creatives | - | CreativeListResponse (200) |
| GET | `/api/v1/creatives/{id}` | Get specific creative | - | GeneratedCreativeResponse (200) |
| PUT | `/api/v1/creatives/{id}/select` | Mark as selected | CreativeSelectionRequest | GeneratedCreativeResponse (200) |
| DELETE | `/api/v1/creatives/{id}` | Delete creative + file | - | 204 No Content |

### Channel Specifications

**Email Header**:
- Dimensions: 600×400px
- Aspect Ratio: 3:2
- Format: JPEG
- Max File Size: 200KB
- DPI: 72

**Push Notification Header**:
- Dimensions: 1200×628px
- Aspect Ratio: 2:1 (universal compatibility)
- Format: JPEG
- Max File Size: 100KB
- DPI: 72

### Brand Guidelines

- **Primary Color**: `#00D964` (StarHub Green)
- **Logo**: Star logo, top-left corner, 80×80px
- **Style**: Professional lifestyle photography, clean modern design, warm natural lighting
- **Font**: StarHub branded fonts (specified in creatives.yaml)

---

## Integration Points

### With Existing Campaign System

**Flow**:
1. User creates campaign via `POST /api/v1/campaigns`
2. Campaign stored with `campaign_id`
3. User requests creatives via `POST /api/v1/campaigns/{campaign_id}/generate-creatives`
4. `CreativeGenerationService` loads campaign data
5. Generates 3 variants using campaign context (cohorts, products, objectives)
6. Stores creatives in database with foreign key to campaign
7. Returns ranked results

**Shared Data**:
- Campaign configuration (channel, objective, cohorts, products)
- Promotion details (pricing, offers)
- Customization parameters (brand elements, style preferences)

**No Changes Required**:
- Campaign model structure (only add relationship)
- Campaign API endpoints (fully independent)
- Communication generation (completely separate)

### With starhub-campaign-creatives Skill

**Skill Location**: `~/.claude/skills/starhub-campaign-creatives/`

**Integration Method**:
- Skill provides guidelines and patterns
- Service implementation references skill documentation
- Prompt templates follow skill examples
- Brand guidelines sourced from skill references

**Key Skill Sections Used**:
- Workflow (prompt construction process)
- Brand Guidelines (color, logo, style)
- Channel Specifications (dimensions, format)
- Prompt Templates (example prompts for different campaign types)
- Quality Criteria (compliance checklist)

---

## Testing Strategy

### Unit Tests
**Coverage Target**: 80%+

**Components to Test**:
- `CreativeGenerator.build_prompt()` - various inputs
- `CreativeGenerator.generate_image()` - with mocked API
- `save_image()` - with test images
- `score_creative()` - scoring logic
- `CreativeGenerationService.generate_and_score()` - orchestration

**Mocking Strategy**:
- Mock fal_client API calls
- Use in-memory test database
- Create temporary test file directory

### Integration Tests
**Coverage Target**: All API endpoints

**Scenarios to Test**:
- Full workflow: create campaign → generate → list → select → delete
- Error cases: campaign not found, API failures
- File operations: image save/delete
- Database operations: CRUD, relationships
- Static file serving

**Test Data**:
- Sample campaign configurations
- Mock image URLs
- Test image files

### Performance Tests
**Benchmarks**:
- Generation time: <10s for 3 variants
- File size validation: within channel limits
- Database query efficiency: no N+1 queries

---

## Common Patterns to Follow

### Service Class Pattern
```python
class CreativeGenerationService:
    def __init__(self, api_key: Optional[str] = None):
        self.generator = CreativeGenerator(api_key)
        self.logger = logging.getLogger(self.__class__.__name__)

    async def generate_and_score(self, ...) -> List[Dict[str, Any]]:
        # Generate → Score → Save → Return ranked results
```

### Router Pattern
```python
router = APIRouter(prefix="/api/v1", tags=["creatives"])

@router.post("/campaigns/{campaign_id}/generate-creatives", ...)
async def generate_creatives(...):
    # Validate campaign exists
    # Parse JSON fields with Pydantic
    # Call service
    # Handle errors
    # Return response
```

### Error Handling Pattern
```python
try:
    # Operation
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Descriptive error: {str(e)}"
    )
```

### Configuration Loading Pattern
```python
@lru_cache
def get_config_section(section: str) -> Dict[str, Any]:
    """Load and cache configuration section."""
    # Load YAML
    # Validate structure
    # Return cached result
```

---

## Troubleshooting Guide

### Common Issues & Solutions

**Issue**: `FAL_KEY not found`
- **Cause**: Environment variable not set
- **Solution**: Add to `.env` file, ensure `python-dotenv` loads it
- **Verify**: `echo $FAL_KEY` in terminal, check startup logs

**Issue**: Image generation timeout
- **Cause**: Network latency, API congestion
- **Solution**: Increase timeout to 30s, implement retry logic
- **Prevention**: Use exponential backoff, add monitoring

**Issue**: File size exceeds limits
- **Cause**: High-resolution images, incorrect format
- **Solution**: Adjust compression in SeeDream params, validate post-generation
- **Prevention**: Set strict output_format in model config

**Issue**: Images don't meet brand guidelines
- **Cause**: Prompt not specific enough
- **Solution**: Refine prompt with explicit brand elements
- **Prevention**: Use prompt templates from skill, add brand keywords

**Issue**: Database migration fails
- **Cause**: Alembic autogenerate misses changes
- **Solution**: Manually review and edit migration file
- **Prevention**: Always test migration on clean database first

**Issue**: Static files not served
- **Cause**: Directory doesn't exist, wrong mount path
- **Solution**: Ensure `backend/static/creatives/` exists, verify mount in main.py
- **Prevention**: Create .gitkeep in directory, test with sample file

---

## Performance Optimization Notes

### Current Implementation (MVP)
- Sequential generation (3 variants one-by-one)
- Synchronous file saves
- Basic scoring (heuristic)

### Future Optimizations
1. **Parallel Generation**: Generate 3 variants concurrently (reduce time to ~3s)
2. **Background Jobs**: Queue-based generation (celery/rq)
3. **Advanced Scoring**: Computer vision for brand compliance checking
4. **CDN Integration**: Serve images from CDN for faster loading
5. **Caching**: Cache prompts and results for similar requests

---

## Security Considerations

### API Security
- **Authentication**: Inherit from existing FastAPI auth (if implemented)
- **Input Validation**: Pydantic schemas validate all inputs
- **SQL Injection**: SQLAlchemy ORM prevents injection
- **Path Traversal**: Validate filenames, use safe path joining

### File Security
- **File Type Validation**: Only JPEG/PNG allowed
- **File Size Limits**: Enforce max sizes (email 200KB, push 100KB)
- **Storage Isolation**: Files stored in dedicated directory
- **Cleanup Policy**: Implement deletion after 30 days

### Secrets Management
- **API Keys**: Store in `.env`, never commit
- **Environment Variables**: Use `python-dotenv` for loading
- **Production**: Use secrets manager (AWS Secrets Manager, etc.)

---

## Cost Analysis

### Per Campaign Cost
- **SeeDream 4.0**: 3 variants × $0.0175 = **$0.0525**
- **Storage**: ~300KB × 3 = 900KB ≈ **$0.0001** (local)
- **Compute**: Negligible (existing backend)
- **Total per Campaign**: ~**$0.05**

### Monthly Projections
- **50 campaigns**: $2.50
- **100 campaigns**: $5.00
- **500 campaigns**: $25.00

### Cost Optimization
- SeeDream 4.0 already cheapest option
- Local storage minimal cost
- Future: Batch API calls if available
- Consider bulk pricing with fal.ai

---

## Rollback Plan

### If Major Issues Occur

**Step 1**: Stop new creative generation
- Disable creative endpoints (comment out router mount)
- Add maintenance message to API

**Step 2**: Assess impact
- Check error logs
- Identify affected campaigns
- Determine data integrity

**Step 3**: Database rollback
```bash
alembic downgrade -1  # Rollback migration
```

**Step 4**: Code rollback
```bash
git revert <commit-hash>
git push origin main
```

**Step 5**: Cleanup
- Delete generated files if needed
- Clear error logs
- Notify stakeholders

**Recovery Time Objective**: <30 minutes

---

## Future Enhancements (Roadmap)

### Phase 2: Advanced Features (Q1 2026)
- Cloud storage migration (S3/Azure Blob)
- Additional AI models (Gemini, Midjourney)
- Advanced brand compliance checking (computer vision)
- Background job queue for async generation
- Creative variant comparison UI

### Phase 3: Automation (Q2 2026)
- Automated creative generation on campaign create (optional)
- A/B testing integration
- Performance analytics (CTR tracking)
- Automated creative optimization based on metrics

### Phase 4: Scale (Q3 2026)
- Multi-region deployment
- CDN integration for image serving
- Advanced prompt engineering with templates
- Integration with design review workflow
- Video creative generation (GIFs, short videos)

---

**Document Status**: Complete
**Last Updated**: 2025-11-10
**Version**: 1.0
