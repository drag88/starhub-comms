# API Reference

Complete reference for the StarHub Communications Generator REST API.

## Base URL

```
http://localhost:8000
```

Production: `https://api.starhub.com/comms` (future)

## Authentication

**MVP**: No authentication required

**Production** (planned):
- API Key authentication
- JWT bearer tokens
- Rate limiting: 100 requests/minute

---

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/campaigns/` | Create campaign |
| GET | `/campaigns/` | List campaigns |
| GET | `/campaigns/{id}` | Get campaign |
| PUT | `/campaigns/{id}` | Update campaign |
| DELETE | `/campaigns/{id}` | Delete campaign |
| POST | `/campaigns/{id}/generate` | Generate communications |
| GET | `/communications/` | List communications |
| GET | `/communications/{id}` | Get communication |
| PUT | `/communications/{id}` | Update communication |
| DELETE | `/communications/{id}` | Delete communication |

---

## Health Check

### GET /health

Check API availability and status.

**Request:**
```bash
curl -X GET "http://localhost:8000/health"
```

**Response: 200 OK**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-09T10:30:00.000Z",
  "version": "1.0.0"
}
```

---

## Campaigns

### POST /campaigns/

Create a new campaign.

**Request Body:**
```json
{
  "channel": "email",
  "cohorts": ["deal_seekers", "mass_market"],
  "product_line": "homehub_plus",
  "objective": "promotion",
  "promotion_details": "$200 discount on 24-month HomeHub+ contract with 3 months free Netflix Premium. Normal price $135.66/mth, now $115.66/mth.",
  "tone": "friendly",
  "custom_instructions": "Emphasize family benefits and value for money",
  "required_phrases": ["exclusive offer", "$115.66/mth"],
  "prohibited_words": ["competitor", "guarantee"]
}
```

**Field Specifications:**

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| channel | string | Yes | `email`, `sms`, or `push` |
| cohorts | array[string] | Yes | Min 1, max 5 cohorts |
| product_line | string | Yes | Valid product identifier |
| objective | string | Yes | Valid objective type |
| promotion_details | string | Yes | Min 10 characters |
| tone | string | No | Default: `friendly` |
| custom_instructions | string | No | Max 500 characters |
| required_phrases | array[string] | No | Max 5 phrases |
| prohibited_words | array[string] | No | Max 10 words |

**Valid Values:**

**Channels:**
- `email`
- `sms`
- `push`

**Cohorts:**
- `mass_market`
- `deal_seekers`
- `sports_enthusiasts`
- `entertainment_lovers`
- `tech_savvy`
- `family_oriented`
- `business_users`
- `young_professionals`
- `seniors`
- `high_value`
- `at_risk_churning`

**Products:**
- `mobile_prepaid`
- `mobile_postpaid`
- `homehub_plus`
- `sports_plus`
- `entertainment_plus`
- `mobile_network`
- `bundles`

**Objectives:**
- `promotion`
- `retention`
- `upsell`
- `cross_sell`
- `service_update`
- `onboarding`

**Tones:**
- `friendly`
- `professional`
- `excited`
- `urgent`
- `premium`
- `informative`
- `casual`
- `appreciative`

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/campaigns/" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "email",
    "cohorts": ["deal_seekers"],
    "product_line": "homehub_plus",
    "objective": "promotion",
    "promotion_details": "$200 discount",
    "tone": "friendly"
  }'
```

**Response: 200 OK**
```json
{
  "id": 123,
  "channel": "email",
  "cohorts": ["deal_seekers", "mass_market"],
  "product_line": "homehub_plus",
  "objective": "promotion",
  "promotion_details": "$200 discount on 24-month HomeHub+ contract...",
  "tone": "friendly",
  "custom_instructions": "Emphasize family benefits...",
  "required_phrases": ["exclusive offer", "$115.66/mth"],
  "prohibited_words": ["competitor", "guarantee"],
  "created_at": "2024-11-09T10:30:00.000Z",
  "updated_at": "2024-11-09T10:30:00.000Z"
}
```

**Error Responses:**

**422 Validation Error**
```json
{
  "detail": [
    {
      "loc": ["body", "channel"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "cohorts"],
      "msg": "ensure this value has at least 1 items",
      "type": "value_error.list.min_items"
    }
  ]
}
```

---

### GET /campaigns/

List all campaigns with pagination.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| skip | integer | No | 0 | Number of records to skip |
| limit | integer | No | 100 | Maximum records to return |

**Request:**
```bash
curl -X GET "http://localhost:8000/campaigns/?skip=0&limit=10"
```

**Response: 200 OK**
```json
[
  {
    "id": 123,
    "channel": "email",
    "cohorts": ["deal_seekers"],
    "product_line": "homehub_plus",
    "objective": "promotion",
    "promotion_details": "$200 discount...",
    "tone": "friendly",
    "custom_instructions": null,
    "required_phrases": [],
    "prohibited_words": [],
    "created_at": "2024-11-09T10:30:00.000Z",
    "updated_at": "2024-11-09T10:30:00.000Z"
  },
  {
    "id": 122,
    "channel": "sms",
    // ... more campaigns
  }
]
```

---

### GET /campaigns/{campaign_id}

Get a specific campaign by ID.

**Path Parameters:**
- `campaign_id` (integer): Campaign ID

**Request:**
```bash
curl -X GET "http://localhost:8000/campaigns/123"
```

**Response: 200 OK**
```json
{
  "id": 123,
  "channel": "email",
  "cohorts": ["deal_seekers", "mass_market"],
  "product_line": "homehub_plus",
  "objective": "promotion",
  "promotion_details": "$200 discount...",
  "tone": "friendly",
  "custom_instructions": "Emphasize family benefits",
  "required_phrases": ["exclusive offer"],
  "prohibited_words": [],
  "created_at": "2024-11-09T10:30:00.000Z",
  "updated_at": "2024-11-09T10:30:00.000Z"
}
```

**Error: 404 Not Found**
```json
{
  "detail": "Campaign not found"
}
```

---

### PUT /campaigns/{campaign_id}

Update an existing campaign.

**Path Parameters:**
- `campaign_id` (integer): Campaign ID

**Request Body:** Same structure as POST /campaigns/

**Request:**
```bash
curl -X PUT "http://localhost:8000/campaigns/123" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "email",
    "cohorts": ["deal_seekers", "high_value"],
    "product_line": "homehub_plus",
    "objective": "retention",
    "promotion_details": "Updated promotion details",
    "tone": "premium"
  }'
```

**Response: 200 OK**
```json
{
  "id": 123,
  "channel": "email",
  "cohorts": ["deal_seekers", "high_value"],
  "product_line": "homehub_plus",
  "objective": "retention",
  "promotion_details": "Updated promotion details",
  "tone": "premium",
  // ... other fields
  "updated_at": "2024-11-09T11:00:00.000Z"
}
```

**Error: 404 Not Found**
```json
{
  "detail": "Campaign not found"
}
```

---

### DELETE /campaigns/{campaign_id}

Delete a campaign and all associated communications.

**Path Parameters:**
- `campaign_id` (integer): Campaign ID

**Request:**
```bash
curl -X DELETE "http://localhost:8000/campaigns/123"
```

**Response: 200 OK**
```json
{
  "id": 123,
  "channel": "email",
  // ... deleted campaign data
}
```

**Error: 404 Not Found**
```json
{
  "detail": "Campaign not found"
}
```

**Note:** Cascade delete removes all communications associated with this campaign.

---

### POST /campaigns/{campaign_id}/generate

Generate 5 AI-powered communication variations for a campaign.

**Path Parameters:**
- `campaign_id` (integer): Campaign ID

**Request:**
```bash
curl -X POST "http://localhost:8000/campaigns/123/generate"
```

**Processing:**
1. Retrieves campaign details
2. Calls Anthropic Claude API
3. Generates 5 unique variations
4. Calculates 4-pillar scores
5. Validates compliance
6. Identifies top recommendation
7. Saves to database

**Response: 200 OK**
```json
[
  {
    "id": 456,
    "campaign_id": 123,
    "channel": "email",
    "subject": "Exclusive HomeHub+ Offer - Save $200!",
    "title": null,
    "body": "Dear Valued Customer,\n\nWe have an exclusive offer just for you! Upgrade to HomeHub+ and save $200 on a 24-month contract. Plus, enjoy 3 months of Netflix Premium on us.\n\nSpecial price: $115.66/mth (normally $135.66/mth)\n\nThis exclusive offer is available for a limited time. Click here to claim yours today!\n\nBest regards,\nStarHub Team\n\nUnsubscribe | View in browser",
    "score_cohort_alignment": 85.0,
    "score_channel_optimization": 90.0,
    "score_brand_consistency": 88.0,
    "score_engagement_potential": 82.0,
    "overall_score": 86.5,
    "is_recommended": true,
    "edited": false,
    "compliance_notes": {
      "status": "pass",
      "issues": [],
      "warnings": []
    },
    "created_at": "2024-11-09T10:31:00.000Z"
  },
  {
    "id": 457,
    "campaign_id": 123,
    "channel": "email",
    "subject": "Save Big on HomeHub+ - Limited Time!",
    "title": null,
    "body": "Hello,\n\nLooking for value? You've found it! Our exclusive offer gives you HomeHub+ for just $115.66/mth with a $200 discount and 3 months free Netflix.\n\n...",
    "score_cohort_alignment": 82.0,
    "score_channel_optimization": 88.0,
    "score_brand_consistency": 85.0,
    "score_engagement_potential": 80.0,
    "overall_score": 84.0,
    "is_recommended": false,
    "edited": false,
    "compliance_notes": {
      "status": "pass",
      "issues": []
    },
    "created_at": "2024-11-09T10:31:00.000Z"
  },
  // ... 3 more variations (total 5)
]
```

**Error Responses:**

**404 Not Found**
```json
{
  "detail": "Campaign not found"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Generation failed: API key invalid"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Generation failed: Network error"
}
```

**Typical Response Time:** 5-10 seconds

---

## Communications

### GET /communications/

List all communications with optional filtering.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| campaign_id | integer | No | null | Filter by campaign |
| skip | integer | No | 0 | Pagination offset |
| limit | integer | No | 100 | Max records |

**Request:**
```bash
# All communications
curl -X GET "http://localhost:8000/communications/"

# Filter by campaign
curl -X GET "http://localhost:8000/communications/?campaign_id=123"

# Pagination
curl -X GET "http://localhost:8000/communications/?skip=0&limit=10"
```

**Response: 200 OK**
```json
[
  {
    "id": 456,
    "campaign_id": 123,
    "channel": "email",
    "subject": "Exclusive Offer...",
    "title": null,
    "body": "Full body text...",
    "score_cohort_alignment": 85.0,
    "score_channel_optimization": 90.0,
    "score_brand_consistency": 88.0,
    "score_engagement_potential": 82.0,
    "overall_score": 86.5,
    "is_recommended": true,
    "edited": false,
    "compliance_notes": {
      "status": "pass",
      "issues": []
    },
    "created_at": "2024-11-09T10:31:00.000Z"
  }
  // ... more communications
]
```

---

### GET /communications/{communication_id}

Get a specific communication by ID.

**Path Parameters:**
- `communication_id` (integer): Communication ID

**Request:**
```bash
curl -X GET "http://localhost:8000/communications/456"
```

**Response: 200 OK**

**Email Response:**
```json
{
  "id": 456,
  "campaign_id": 123,
  "channel": "email",
  "subject": "Exclusive HomeHub+ Offer - Save $200!",
  "title": null,
  "body": "Dear Valued Customer,\n\nWe have an exclusive offer...",
  "score_cohort_alignment": 85.0,
  "score_channel_optimization": 90.0,
  "score_brand_consistency": 88.0,
  "score_engagement_potential": 82.0,
  "overall_score": 86.5,
  "is_recommended": true,
  "edited": false,
  "compliance_notes": {
    "status": "pass",
    "issues": [],
    "warnings": []
  },
  "created_at": "2024-11-09T10:31:00.000Z"
}
```

**SMS Response:**
```json
{
  "id": 458,
  "campaign_id": 124,
  "channel": "sms",
  "subject": null,
  "title": null,
  "body": "StarHub: Network maintenance tonight 1-3AM in Central region. Services may be briefly unavailable. No action needed.",
  "score_cohort_alignment": 75.0,
  "score_channel_optimization": 95.0,
  "score_brand_consistency": 90.0,
  "score_engagement_potential": 70.0,
  "overall_score": 82.5,
  "is_recommended": true,
  "edited": false,
  "compliance_notes": {
    "status": "pass",
    "issues": [],
    "warnings": ["Transactional message - opt-out not required"]
  },
  "created_at": "2024-11-09T10:32:00.000Z"
}
```

**Push Notification Response:**
```json
{
  "id": 459,
  "campaign_id": 125,
  "channel": "push",
  "subject": null,
  "title": "Premier League is Back! 3 Months Free",
  "body": "Get Sports+ now and watch every match live. $76 value - yours free! Don't miss the action. Tap to claim.",
  "score_cohort_alignment": 92.0,
  "score_channel_optimization": 88.0,
  "score_brand_consistency": 85.0,
  "score_engagement_potential": 90.0,
  "overall_score": 89.0,
  "is_recommended": true,
  "edited": false,
  "compliance_notes": {
    "status": "pass",
    "issues": []
  },
  "created_at": "2024-11-09T10:33:00.000Z"
}
```

**Error: 404 Not Found**
```json
{
  "detail": "Communication not found"
}
```

---

### PUT /communications/{communication_id}

Update/edit a communication (manual editing).

**Path Parameters:**
- `communication_id` (integer): Communication ID

**Request Body:**

**For Email:**
```json
{
  "subject": "Updated Subject Line",
  "body": "Updated body content with changes...",
  "edited": true
}
```

**For SMS:**
```json
{
  "body": "Updated SMS message text under 160 characters",
  "edited": true
}
```

**For Push:**
```json
{
  "title": "Updated Title",
  "body": "Updated body text for push notification",
  "edited": true
}
```

**Request Example:**
```bash
curl -X PUT "http://localhost:8000/communications/456" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "UPDATED: Exclusive HomeHub+ Offer",
    "body": "Updated body content...",
    "edited": true
  }'
```

**Response: 200 OK**
```json
{
  "id": 456,
  "campaign_id": 123,
  "channel": "email",
  "subject": "UPDATED: Exclusive HomeHub+ Offer",
  "body": "Updated body content...",
  "score_cohort_alignment": 85.0,
  "score_channel_optimization": 90.0,
  "score_brand_consistency": 88.0,
  "score_engagement_potential": 82.0,
  "overall_score": 86.5,
  "is_recommended": true,
  "edited": true,
  "compliance_notes": {
    "status": "pass",
    "issues": []
  },
  "created_at": "2024-11-09T10:31:00.000Z"
}
```

**Notes:**
- Scores reflect original AI-generated content, not edited version
- `edited` flag set to `true`
- Content updated immediately
- No validation on edited content (manual responsibility)

**Error: 404 Not Found**
```json
{
  "detail": "Communication not found"
}
```

---

### DELETE /communications/{communication_id}

Delete a specific communication.

**Path Parameters:**
- `communication_id` (integer): Communication ID

**Request:**
```bash
curl -X DELETE "http://localhost:8000/communications/456"
```

**Response: 200 OK**
```json
{
  "id": 456,
  "campaign_id": 123,
  // ... deleted communication data
}
```

**Error: 404 Not Found**
```json
{
  "detail": "Communication not found"
}
```

---

## Data Models

### Campaign Object

```typescript
interface Campaign {
  id: number;
  channel: "email" | "sms" | "push";
  cohorts: string[];
  product_line: string;
  objective: string;
  promotion_details: string;
  tone?: string;
  custom_instructions?: string;
  required_phrases?: string[];
  prohibited_words?: string[];
  created_at: string;  // ISO 8601 datetime
  updated_at: string;  // ISO 8601 datetime
}
```

### Communication Object

```typescript
interface Communication {
  id: number;
  campaign_id: number;
  channel: "email" | "sms" | "push";
  subject?: string;  // Email only
  title?: string;    // Push notification only
  body: string;
  score_cohort_alignment: number;     // 0-100
  score_channel_optimization: number; // 0-100
  score_brand_consistency: number;    // 0-100
  score_engagement_potential: number; // 0-100
  overall_score: number;              // 0-100, weighted average
  is_recommended: boolean;
  edited: boolean;
  compliance_notes?: {
    status: "pass" | "warning" | "fail";
    issues: string[];
    warnings?: string[];
  };
  created_at: string;  // ISO 8601 datetime
}
```

### Compliance Notes Object

```typescript
interface ComplianceNotes {
  status: "pass" | "warning" | "fail";
  issues: string[];
  warnings?: string[];
}
```

Example:
```json
{
  "status": "warning",
  "issues": [],
  "warnings": [
    "Promotional SMS should include opt-out language",
    "Pricing mentions should include terms and conditions"
  ]
}
```

---

## Error Handling

### Standard Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request format or data |
| 404 | Not Found | Resource doesn't exist |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server-side error |

### Common Error Scenarios

**Missing Required Field (422)**
```json
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

**Invalid Field Value (422)**
```json
{
  "detail": [
    {
      "loc": ["body", "channel"],
      "msg": "value is not a valid enumeration member; permitted: 'email', 'sms', 'push'",
      "type": "type_error.enum",
      "ctx": {
        "enum_values": ["email", "sms", "push"]
      }
    }
  ]
}
```

**Resource Not Found (404)**
```json
{
  "detail": "Campaign not found"
}
```

**API Generation Error (500)**
```json
{
  "detail": "Generation failed: Anthropic API returned error"
}
```

---

## Rate Limiting (Future)

**Planned for Production:**

```
Rate Limit: 100 requests per minute per API key
Burst Limit: 10 concurrent requests

Headers:
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 95
  X-RateLimit-Reset: 1699527600
```

**Rate Limit Exceeded (429)**
```json
{
  "detail": "Rate limit exceeded. Try again in 30 seconds.",
  "retry_after": 30
}
```

---

## Pagination

List endpoints support pagination via query parameters:

```
GET /campaigns/?skip=20&limit=10
GET /communications/?skip=0&limit=50
```

**Parameters:**
- `skip`: Number of records to skip (offset)
- `limit`: Maximum records to return (max: 1000)

**Example:**
```bash
# Get campaigns 11-20
curl -X GET "http://localhost:8000/campaigns/?skip=10&limit=10"
```

---

## CORS Configuration

**Allowed Origins (MVP):**
- `http://localhost:5173` (Vite dev server)
- `http://localhost:3000` (Alternative port)

**Allowed Methods:**
- GET, POST, PUT, DELETE, OPTIONS

**Allowed Headers:**
- Content-Type, Authorization

**Production:** Configure specific production domain origins

---

## Interactive API Documentation

Access interactive Swagger UI documentation:

```
http://localhost:8000/docs
```

Features:
- Try out endpoints directly
- See request/response schemas
- Copy example code
- Test authentication

Alternative ReDoc documentation:

```
http://localhost:8000/redoc
```

---

## Code Examples

### JavaScript/TypeScript (Axios)

```typescript
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

// Create campaign
const createCampaign = async () => {
  const response = await axios.post(`${API_BASE}/campaigns/`, {
    channel: 'email',
    cohorts: ['deal_seekers'],
    product_line: 'homehub_plus',
    objective: 'promotion',
    promotion_details: '$200 discount on 24-month contract',
    tone: 'friendly'
  });

  console.log('Campaign created:', response.data);
  return response.data;
};

// Generate communications
const generateComms = async (campaignId: number) => {
  const response = await axios.post(
    `${API_BASE}/campaigns/${campaignId}/generate`
  );

  console.log('Generated communications:', response.data);
  return response.data;
};

// Update communication
const editCommunication = async (commId: number, updates: any) => {
  const response = await axios.put(
    `${API_BASE}/communications/${commId}`,
    updates
  );

  console.log('Communication updated:', response.data);
  return response.data;
};
```

### Python (requests)

```python
import requests

API_BASE = 'http://localhost:8000'

# Create campaign
def create_campaign():
    data = {
        'channel': 'email',
        'cohorts': ['deal_seekers'],
        'product_line': 'homehub_plus',
        'objective': 'promotion',
        'promotion_details': '$200 discount on 24-month contract',
        'tone': 'friendly'
    }

    response = requests.post(f'{API_BASE}/campaigns/', json=data)
    response.raise_for_status()

    print('Campaign created:', response.json())
    return response.json()

# Generate communications
def generate_communications(campaign_id):
    response = requests.post(
        f'{API_BASE}/campaigns/{campaign_id}/generate'
    )
    response.raise_for_status()

    print('Generated communications:', response.json())
    return response.json()

# Get communications
def get_communications(campaign_id):
    response = requests.get(
        f'{API_BASE}/communications/',
        params={'campaign_id': campaign_id}
    )
    response.raise_for_status()

    return response.json()
```

### cURL Examples

```bash
# Create campaign
curl -X POST "http://localhost:8000/campaigns/" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "email",
    "cohorts": ["deal_seekers"],
    "product_line": "homehub_plus",
    "objective": "promotion",
    "promotion_details": "$200 discount",
    "tone": "friendly"
  }'

# Generate communications
curl -X POST "http://localhost:8000/campaigns/123/generate"

# Get communications
curl -X GET "http://localhost:8000/communications/?campaign_id=123"

# Update communication
curl -X PUT "http://localhost:8000/communications/456" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Updated Subject",
    "body": "Updated body text",
    "edited": true
  }'

# Delete campaign
curl -X DELETE "http://localhost:8000/campaigns/123"
```

---

## Changelog

### Version 1.0.0 (MVP)

**Initial Release:**
- Campaign CRUD operations
- Communication generation via Claude API
- 4-pillar scoring system
- Compliance validation
- Communication editing
- Basic export functionality

**Future Enhancements:**
- Authentication and authorization
- Export endpoints with format conversion
- Batch operations
- Campaign templates
- Analytics endpoints
- Webhook notifications

---

## Support

**Documentation:**
- User Guide: `docs/USER_GUIDE.md`
- Developer Guide: `docs/DEVELOPER_GUIDE.md`
- Deployment Guide: `DEPLOYMENT.md`

**Issues:**
- Check application logs
- Review error responses
- Test with interactive docs at `/docs`

---

**API Version**: 1.0.0
**Last Updated**: 2024-11-09
**Maintained By**: StarHub Data Analytics Team
