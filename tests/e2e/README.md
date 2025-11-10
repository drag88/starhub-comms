# End-to-End Testing Guide

Manual end-to-end acceptance testing for the StarHub Customer Communications Generator.

## Overview

This directory contains comprehensive end-to-end test scenarios that validate the complete application workflow from a user's perspective. These tests ensure all acceptance criteria are met and the system functions correctly in real-world usage.

## Test Scenarios

See [test_scenarios.md](test_scenarios.md) for 6 detailed acceptance test scenarios:

1. **Email Promotion for Deal Seekers** - Complete email campaign workflow
2. **SMS Service Update for Mass Market** - SMS with compliance validation
3. **Push Notification for Sports Enthusiasts** - Push notification creation
4. **Regeneration with Parameter Change** - Dynamic parameter updates
5. **Manual Edit and Export** - Inline editing and export functionality
6. **Validation and Error Handling** - Error cases and edge scenarios

## Test Execution

### Prerequisites

Before executing E2E tests, ensure:

1. **Backend is running** at http://localhost:8000
2. **Frontend is running** at http://localhost:5173
3. **Valid ANTHROPIC_API_KEY** configured in `backend/.env`
4. **Fresh database** (optional, for clean test state)

### Starting the Application

#### Option 1: Quick Start

```bash
# From project root
./start-all.sh
```

This starts both backend and frontend servers.

#### Option 2: Manual Start

**Terminal 1 (Backend)**:
```bash
cd backend
source .venv/bin/activate
uv run uvicorn main:app --reload
```

**Terminal 2 (Frontend)**:
```bash
cd frontend
npm run dev
```

### Verify Application is Ready

```bash
# Check backend
curl http://localhost:8000/api/v1/health

# Expected response:
# {
#   "status": "healthy",
#   "database": "connected",
#   "timestamp": "2025-11-09T..."
# }

# Check frontend (in browser)
open http://localhost:5173  # macOS
# OR navigate to http://localhost:5173 in your browser
```

## Execution Checklist

Use this checklist to track test execution progress:

```markdown
### E2E Test Execution Status

- [ ] Scenario 1: Email Promotion for Deal Seekers
  - [ ] Part A: Create and generate campaign
  - [ ] Part B: Review results and select

- [ ] Scenario 2: SMS Service Update for Mass Market
  - [ ] Part A: Create SMS campaign
  - [ ] Part B: Verify compliance and export

- [ ] Scenario 3: Push Notification for Sports Enthusiasts
  - [ ] Part A: Create push campaign
  - [ ] Part B: Review and export

- [ ] Scenario 4: Regeneration with Parameter Change
  - [ ] Part A: Initial generation
  - [ ] Part B: Modify and regenerate

- [ ] Scenario 5: Manual Edit and Export
  - [ ] Part A: Edit communication
  - [ ] Part B: Verify rescoring
  - [ ] Part C: Export all formats

- [ ] Scenario 6: Validation and Error Handling
  - [ ] Part A: Required field validation
  - [ ] Part B: Invalid input handling
  - [ ] Part C: API error handling
```

## Test Execution Steps

### For Each Scenario

1. **Open test_scenarios.md** in your editor or browser
2. **Locate the scenario** you want to execute
3. **Follow step-by-step instructions** exactly as written
4. **Verify expected outcomes** at each step
5. **Document results** in the test file or separate log
6. **Mark as complete** when all steps pass

### Example: Executing Scenario 1

```markdown
## Test Scenario 1: Email Promotion for Deal Seekers

### Part A: Create and Generate Campaign

1. ✅ Open application at http://localhost:5173
   - Result: Application loads successfully

2. ✅ Fill in campaign details:
   - Name: "Black Friday Broadband Deals"
   - Channel: Email
   - Objective: Promotion
   - Result: Form accepts input

3. ✅ Select cohorts: Deal Seekers, At-Risk Customers
   - Result: Multi-select shows both cohorts

... (continue through all steps)

### Part A Results: PASS ✅
### Part B Results: PASS ✅
### Overall Scenario 1: PASS ✅
```

## Test Data

### Recommended Test Campaigns

| Scenario | Channel | Cohorts | Objective | Products |
|----------|---------|---------|-----------|----------|
| Email | Email | Deal Seekers, At-Risk | Promotion | Broadband, Bundles |
| SMS | SMS | Prepaid Mass, Students | Service Update | Mobile |
| Push | Push | Sports Fans, Young Professionals | Cross-sell | Entertainment |

### Sample Promotion Details

```json
{
  "promotion_name": "Black Friday Special",
  "pricing": {
    "original": "$69/month",
    "discounted": "$49/month",
    "savings": "$20/month"
  },
  "features": [
    "10Gbps fiber broadband",
    "Free installation",
    "No contract lock-in"
  ],
  "validity": {
    "start": "2025-11-25",
    "end": "2025-11-30"
  }
}
```

## Expected Behavior

### Successful Campaign Creation

- Form validates all required fields
- Cohorts and products display correctly
- Generate button becomes enabled
- Campaign ID is assigned

### Successful Generation

- Loading indicator appears
- 5 variations are generated
- Scores range from 0-100
- Top recommendation is highlighted
- All variations are numbered 1-5

### Score Breakdown

Each communication should show:

- **Overall Score**: 0-100
- **Channel Score**: 0-100 (30% weight)
- **Cohort Score**: 0-100 (30% weight)
- **Objective Score**: 0-100 (25% weight)
- **Compliance Score**: 0-100 (15% weight)
- **Reasoning**: Natural language explanation
- **Compliance Flags**: If any (CRITICAL, WARNING, REVIEW, CAUTION)

### Character Counting

| Channel | Optimal Range | Penalty Range |
|---------|--------------|---------------|
| SMS | 140-160 chars | < 140 or > 160 |
| Email Subject | 40-60 chars | < 40 or > 60 |
| Push Title | 40-60 chars | > 60 |
| Push Body | 100-150 chars | > 150 |

## Logging Test Results

### Result Documentation Template

```markdown
## Test Execution: [Date]

**Tester**: [Name]
**Environment**: Development (localhost)
**Backend Version**: 1.0.0
**Frontend Version**: 1.0.0

### Scenario 1: Email Promotion for Deal Seekers
- **Status**: PASS / FAIL
- **Duration**: [time in minutes]
- **Issues Found**: [None / List issues]
- **Notes**: [Any observations]

### Scenario 2: SMS Service Update
- **Status**: PASS / FAIL
- **Duration**: [time]
- **Issues Found**: [None / List]
- **Notes**: [Observations]

... (continue for all scenarios)

### Summary
- **Total Scenarios**: 6
- **Passed**: [count]
- **Failed**: [count]
- **Blocked**: [count]
- **Success Rate**: [percentage]

### Issues Log
1. [Issue description] - Severity: [Critical/High/Medium/Low]
2. [Issue description] - Severity: [...]
```

## Common Issues and Solutions

### Issue: Application Won't Load

**Symptoms**:
- Frontend shows blank page
- Backend not responding

**Solutions**:
1. Check both servers are running
2. Verify ports 8000 and 5173 are available
3. Check browser console for errors
4. Restart both servers

### Issue: Generation Fails

**Symptoms**:
- Error message after clicking Generate
- Loading spinner never stops

**Solutions**:
1. Check `ANTHROPIC_API_KEY` is valid
2. Verify backend logs for API errors
3. Check internet connection
4. Ensure Claude API quota not exceeded

### Issue: Scores Don't Make Sense

**Symptoms**:
- All scores are 0 or 100
- Reasoning is generic or empty

**Solutions**:
1. This may indicate a scoring algorithm issue
2. Check backend logs for warnings
3. Verify cohort and objective configurations loaded
4. Document as bug with specific example

### Issue: Export Not Working

**Symptoms**:
- Export buttons don't respond
- Downloaded file is empty or corrupted

**Solutions**:
1. Check browser console for JavaScript errors
2. Verify browser allows downloads
3. Try different export format
4. Check communication is selected

## Performance Expectations

### Load Times

| Operation | Expected | Acceptable | Slow |
|-----------|----------|------------|------|
| Page load | < 2s | < 5s | > 5s |
| Form submission | < 1s | < 3s | > 3s |
| Generate (5 variations) | 5-8s | < 15s | > 15s |
| Rescore on edit | < 1s | < 3s | > 3s |
| Export | < 1s | < 2s | > 2s |

### Concurrent Users

The MVP supports **single user** only (SQLite limitation). Testing with multiple concurrent users may result in database locking errors.

## Validation Criteria

### Acceptance Criteria

For each scenario to PASS, verify:

1. **Functional Requirements**:
   - [ ] All steps complete without errors
   - [ ] Expected outputs are generated
   - [ ] Data is saved correctly
   - [ ] UI behaves as expected

2. **Performance Requirements**:
   - [ ] Operations complete within acceptable time
   - [ ] No significant delays or hangs
   - [ ] Responsive to user interactions

3. **Compliance Requirements** (where applicable):
   - [ ] SMS includes opt-out instruction
   - [ ] Email includes unsubscribe link
   - [ ] Pricing mentions T&Cs
   - [ ] No unsubstantiated claims

4. **User Experience**:
   - [ ] Clear instructions and labels
   - [ ] Appropriate error messages
   - [ ] Visual feedback for actions
   - [ ] Intuitive workflow

## Test Environment

### Browser Compatibility

Test on these browsers (minimum):

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest) - macOS only
- [ ] Edge (latest) - Windows only

### Screen Resolutions

Test responsiveness at:

- [ ] Desktop: 1920x1080
- [ ] Laptop: 1366x768
- [ ] Tablet: 768x1024 (if applicable)

## Reporting Issues

When you find an issue during E2E testing:

1. **Document the issue**:
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots or screen recordings
   - Browser and environment details

2. **Severity Classification**:
   - **Critical**: Blocks core functionality
   - **High**: Significant impact on usability
   - **Medium**: Moderate impact, workaround available
   - **Low**: Minor cosmetic or convenience issue

3. **Log in test_scenarios.md**:
   ```markdown
   ### Issue #1
   **Severity**: High
   **Scenario**: Scenario 1, Step 5
   **Description**: Generate button doesn't enable after selecting cohorts
   **Steps to Reproduce**:
   1. Fill in campaign name
   2. Select Email channel
   3. Select 2 cohorts
   4. Button remains disabled

   **Expected**: Button should be enabled
   **Actual**: Button stays disabled
   **Workaround**: Refresh page and try again
   ```

## Automated E2E Testing (Future)

Planned automation with:

- **Playwright** or **Cypress** for browser automation
- **API tests** for backend validation
- **Visual regression tests** for UI consistency
- **CI/CD integration** for automated execution

Example automated test structure:

```typescript
// tests/e2e/scenario1.spec.ts
import { test, expect } from '@playwright/test';

test('Email promotion for deal seekers', async ({ page }) => {
  // Navigate to app
  await page.goto('http://localhost:5173');

  // Fill campaign form
  await page.fill('input[name="campaignName"]', 'Black Friday Deals');
  await page.selectOption('select[name="channel"]', 'email');

  // Generate communications
  await page.click('button:text("Generate")');

  // Verify results
  await expect(page.locator('.communication-card')).toHaveCount(5);
  await expect(page.locator('.top-recommendation')).toBeVisible();
});
```

## Resources

- **Test Scenarios**: [test_scenarios.md](test_scenarios.md)
- **User Guide**: [docs/user/USER_GUIDE.md](../../docs/user/USER_GUIDE.md)
- **API Reference**: [docs/developer/API_REFERENCE.md](../../docs/developer/API_REFERENCE.md)
- **Known Issues**: [docs/project/KNOWN_ISSUES.md](../../docs/project/KNOWN_ISSUES.md)

## Quick Reference

### Essential URLs

```
Frontend:     http://localhost:5173
Backend API:  http://localhost:8000
API Docs:     http://localhost:8000/docs
Health Check: http://localhost:8000/api/v1/health
```

### Essential Commands

```bash
# Start everything
./start-all.sh

# Check backend health
curl http://localhost:8000/api/v1/health

# Reset database (if needed)
cd backend
uv run python -c "from database import reset_db; reset_db()"
```

---

**Last Updated**: 2025-11-09
**Test Coverage**: 6 comprehensive scenarios
**Execution Mode**: Manual (automation planned)
