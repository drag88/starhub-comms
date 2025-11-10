# End-to-End Test Scenarios

## Overview

This document contains all acceptance test scenarios for the StarHub Customer Communications Generator MVP. Each scenario should be executed manually to validate the system meets requirements.

## Prerequisites

- Backend running on http://localhost:8000
- Frontend running on http://localhost:5173
- Valid ANTHROPIC_API_KEY configured
- Fresh database state (recommended)

## Test Execution Log

**Date**: _______________
**Tester**: _______________
**Environment**: Local Development

---

## Test Scenario 1: Email Promotion for Deal Seekers

**Objective**: Validate email generation with specific cohorts, required phrases, and promotional content

**Priority**: Critical
**Estimated Duration**: 5 minutes

### Input Parameters

| Field | Value |
|-------|-------|
| Channel | Email |
| Cohorts | Deal Seekers, At-Risk/Churning |
| Product | HomeHub+ |
| Objective | Retention |
| Promotion Details | $200 discount, 3 months free Netflix, 24-month contract |
| Tone | Urgent |
| Required Phrases | "exclusive offer", "$115.66/mth" |

### Expected Outputs

1. 5 unique email communications generated
2. All variations include both required phrases: "exclusive offer" AND "$115.66/mth"
3. Urgent tone evident in language (e.g., "limited time", "act now", "don't miss")
4. Email-specific formatting:
   - Subject lines: 40-60 characters
   - Unsubscribe link present
   - Professional HTML-ready format
5. Top recommendation score >80
6. Compliance notes: "No issues detected" or only minor suggestions
7. 4-pillar scores visible for each variation:
   - Cohort Alignment
   - Channel Optimization
   - Brand Consistency
   - Engagement Potential

### Test Steps

1. **Start Application**
   ```bash
   # Terminal 1
   ./start-backend.sh

   # Terminal 2
   ./start-frontend.sh
   ```
   - [ ] Backend started successfully
   - [ ] Frontend accessible at http://localhost:5173

2. **Fill Campaign Form**
   - [ ] Select "Email" channel
   - [ ] Select cohorts: "Deal Seekers" and "At-Risk/Churning"
   - [ ] Select product: "HomeHub+"
   - [ ] Select objective: "Retention"
   - [ ] Enter promotion details: "$200 discount, 3 months free Netflix, 24-month contract"
   - [ ] Select tone: "Urgent"
   - [ ] Enter required phrases: "exclusive offer", "$115.66/mth"

3. **Generate Communications**
   - [ ] Click "Generate Communications" button
   - [ ] Loading state displayed
   - [ ] Generation completes within 10 seconds

4. **Verify Outputs**
   - [ ] Exactly 5 variations generated
   - [ ] All variations display complete (subject + body)
   - [ ] Top recommendation highlighted clearly
   - [ ] Top recommendation score >80

5. **Verify Required Phrases**
   - [ ] Variation 1 contains "exclusive offer" and "$115.66/mth"
   - [ ] Variation 2 contains "exclusive offer" and "$115.66/mth"
   - [ ] Variation 3 contains "exclusive offer" and "$115.66/mth"
   - [ ] Variation 4 contains "exclusive offer" and "$115.66/mth"
   - [ ] Variation 5 contains "exclusive offer" and "$115.66/mth"

6. **Verify Tone**
   - [ ] Urgency language present (e.g., "limited time", "act now", "hurry")
   - [ ] Tone appropriate for retention objective

7. **Verify Email Specifics**
   - [ ] Subject lines between 40-60 characters
   - [ ] Unsubscribe link present in all variations
   - [ ] Professional formatting suitable for email

8. **Verify Compliance**
   - [ ] Compliance notes displayed
   - [ ] No critical issues flagged
   - [ ] Pricing terms included ("/mth", "contract")

9. **Verify Scoring**
   - [ ] 4-pillar breakdown visible
   - [ ] Scores make logical sense
   - [ ] Top recommendation explanation provided

10. **Test Export**
    - [ ] Select top recommendation
    - [ ] Export as TXT - file downloads
    - [ ] Export as CSV - file downloads
    - [ ] Export as JSON - file downloads
    - [ ] Exported content matches displayed communication

### Acceptance Criteria

- [ ] All 5 variations generated successfully
- [ ] Required phrases present in all variations
- [ ] Urgent tone evident
- [ ] Email formatting correct
- [ ] Top score >80
- [ ] No critical compliance issues
- [ ] Export functionality works

### Results

**Status**: [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes**:
```
_______________________________________________________________________________
_______________________________________________________________________________
_______________________________________________________________________________
```

**Issues Found**:
```
_______________________________________________________________________________
_______________________________________________________________________________
_______________________________________________________________________________
```

---

## Test Scenario 2: SMS Service Update for Mass Market

**Objective**: Validate SMS generation with character limits and transactional messaging

**Priority**: Critical
**Estimated Duration**: 4 minutes

### Input Parameters

| Field | Value |
|-------|-------|
| Channel | SMS |
| Cohorts | Mass Market |
| Product | Mobile Network |
| Objective | Service Update |
| Promotion Details | Network maintenance notification |
| Tone | Professional |
| Custom Instructions | "Maintenance window: Tonight 1-3AM, Central region only" |

### Expected Outputs

1. 5 unique SMS communications generated
2. All variations ≤160 characters
3. Professional tone (no emojis, formal language)
4. Maintenance window clearly mentioned
5. Central region specified
6. No opt-out required (transactional message)
7. Recommendation prioritizes clarity and brevity
8. Character count displayed for each variation

### Test Steps

1. **Navigate to Campaign Form**
   - [ ] Click "New Campaign" or refresh page

2. **Fill Campaign Form**
   - [ ] Select "SMS" channel
   - [ ] Select cohort: "Mass Market"
   - [ ] Select product: "Mobile Network"
   - [ ] Select objective: "Service Update"
   - [ ] Enter promotion: "Network maintenance notification"
   - [ ] Select tone: "Professional"
   - [ ] Enter custom instructions: "Maintenance window: Tonight 1-3AM, Central region only"

3. **Generate Communications**
   - [ ] Click "Generate Communications"
   - [ ] Generation completes successfully

4. **Verify Outputs**
   - [ ] 5 SMS variations generated
   - [ ] Character count displayed for each
   - [ ] All variations ≤160 characters

5. **Verify Content**
   - [ ] Maintenance window "1-3AM" or "1AM-3AM" mentioned
   - [ ] "Tonight" or time reference included
   - [ ] "Central region" or "Central" specified
   - [ ] Professional language (no slang, emojis)

6. **Verify Compliance**
   - [ ] No opt-out text (transactional message)
   - [ ] Clear and informative
   - [ ] No marketing language

7. **Verify Scoring**
   - [ ] Recommendation prioritizes clarity
   - [ ] Shorter messages may score higher
   - [ ] Channel optimization score high

### Acceptance Criteria

- [ ] All variations ≤160 characters
- [ ] Maintenance details clear
- [ ] Professional tone maintained
- [ ] No opt-out (transactional)
- [ ] Top recommendation makes sense

### Results

**Status**: [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes**:
```
_______________________________________________________________________________
_______________________________________________________________________________
_______________________________________________________________________________
```

**Issues Found**:
```
_______________________________________________________________________________
_______________________________________________________________________________
_______________________________________________________________________________
```

---

## Test Scenario 3: Push Notification for Sports Enthusiasts

**Objective**: Validate push notification generation with title/body structure and character limits

**Priority**: High
**Estimated Duration**: 4 minutes

### Input Parameters

| Field | Value |
|-------|-------|
| Channel | Push Notification |
| Cohorts | Sports Enthusiasts, High-Value Customers |
| Product | Sports+ |
| Objective | Promotion |
| Promotion Details | 3 months free Sports+ ($76 value), Premier League season starting |
| Tone | Excited |
| Required Phrases | "Premier League" |

### Expected Outputs

1. 5 unique push notifications generated
2. Title: 40-50 characters (strict limit)
3. Body: 100-120 characters (strict limit)
4. "Premier League" appears in all variations
5. Excited tone (exclamation marks, energetic language)
6. High cohort alignment score (Sports Enthusiasts + Sports+ product)
7. Clear value proposition ($76 value, 3 months free)

### Test Steps

1. **Navigate to Campaign Form**
   - [ ] Start new campaign

2. **Fill Campaign Form**
   - [ ] Select "Push Notification" channel
   - [ ] Select cohorts: "Sports Enthusiasts", "High-Value Customers"
   - [ ] Select product: "Sports+"
   - [ ] Select objective: "Promotion"
   - [ ] Enter promotion: "3 months free Sports+ ($76 value), Premier League season starting"
   - [ ] Select tone: "Excited"
   - [ ] Enter required phrase: "Premier League"

3. **Generate Communications**
   - [ ] Click "Generate Communications"
   - [ ] Generation completes successfully

4. **Verify Structure**
   - [ ] 5 push notifications generated
   - [ ] Each has distinct Title and Body
   - [ ] Character counts displayed
   - [ ] Title: 40-50 characters
   - [ ] Body: 100-120 characters

5. **Verify Required Phrase**
   - [ ] "Premier League" in variation 1
   - [ ] "Premier League" in variation 2
   - [ ] "Premier League" in variation 3
   - [ ] "Premier League" in variation 4
   - [ ] "Premier League" in variation 5

6. **Verify Tone**
   - [ ] Excited language present
   - [ ] Energetic wording
   - [ ] Appropriate use of exclamation marks

7. **Verify Cohort Alignment**
   - [ ] Cohort Alignment score >85 (highly relevant)
   - [ ] Sports-focused language
   - [ ] Value emphasized for high-value customers

8. **Verify Value Proposition**
   - [ ] "3 months free" or equivalent mentioned
   - [ ] Value ($76) referenced
   - [ ] Clear benefit stated

### Acceptance Criteria

- [ ] Title within 40-50 characters
- [ ] Body within 100-120 characters
- [ ] "Premier League" in all variations
- [ ] Excited tone evident
- [ ] High cohort alignment score
- [ ] Clear value proposition

### Results

**Status**: [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes**:
```
_______________________________________________________________________________
_______________________________________________________________________________
_______________________________________________________________________________
```

**Issues Found**:
```
_______________________________________________________________________________
_______________________________________________________________________________
_______________________________________________________________________________
```

---

## Test Scenario 4: Regeneration with Parameter Change

**Objective**: Validate regeneration functionality maintains inputs while generating new variations

**Priority**: High
**Estimated Duration**: 5 minutes

### Expected Behavior

1. Previous variations replaced with new ones
2. All input parameters preserved except modified ones
3. Tone change reflected in new variations
4. New required phrase appears in all new variations
5. Campaign history maintained (if implemented)
6. New recommendation calculated

### Test Steps

1. **Initial Generation**
   - [ ] Create campaign with any parameters
   - [ ] Set tone to "Friendly"
   - [ ] Set required phrase: "family plan"
   - [ ] Click "Generate Communications"
   - [ ] 5 variations generated successfully
   - [ ] Note top recommendation score: ___________

2. **Modify Parameters**
   - [ ] Change tone from "Friendly" to "Premium"
   - [ ] Add required phrase: "exclusive for families"
   - [ ] Keep all other parameters the same

3. **Regenerate**
   - [ ] Click "Regenerate" button
   - [ ] Loading state displayed
   - [ ] Generation completes successfully

4. **Verify New Variations**
   - [ ] 5 new variations generated
   - [ ] Variations are different from previous set
   - [ ] All variations contain "family plan" AND "exclusive for families"

5. **Verify Tone Shift**
   - [ ] Premium language present (e.g., "exclusive", "premium", "select")
   - [ ] Tone more sophisticated than friendly
   - [ ] Brand voice elevated

6. **Verify Parameters Preserved**
   - [ ] Channel unchanged
   - [ ] Cohorts unchanged
   - [ ] Product unchanged
   - [ ] Objective unchanged
   - [ ] Promotion details unchanged

7. **Verify History (if implemented)**
   - [ ] Previous variations still accessible
   - [ ] Campaign version tracking visible
   - [ ] Can switch between versions

### Acceptance Criteria

- [ ] New variations generated successfully
- [ ] Tone shift evident
- [ ] Both required phrases present
- [ ] Parameters preserved
- [ ] New recommendation calculated

### Results

**Status**: [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes**:
```
_______________________________________________________________________________
_______________________________________________________________________________
_______________________________________________________________________________
```

**Issues Found**:
```
_______________________________________________________________________________
_______________________________________________________________________________
_______________________________________________________________________________
```

---

## Test Scenario 5: Manual Edit and Export

**Objective**: Validate editing functionality and export in multiple formats

**Priority**: High
**Estimated Duration**: 6 minutes

### Expected Behavior

1. Any variation can be edited
2. Edits preserved and marked as "Edited"
3. Original text still accessible
4. Export includes both original and edited versions
5. All export formats work (TXT, CSV, JSON)

### Test Steps

1. **Generate Initial Communications**
   - [ ] Create email campaign with any parameters
   - [ ] Generate 5 variations

2. **Select Non-Recommended Variation**
   - [ ] Click on variation #3 (not top recommendation)
   - [ ] Variation details displayed

3. **Edit Communication**
   - [ ] Click "Edit" button
   - [ ] Edit modal opens
   - [ ] Modify subject line: Change first few words
   - [ ] Modify body: Add one sentence
   - [ ] Character count updates in real-time

4. **Save Edited Version**
   - [ ] Click "Save" button
   - [ ] Modal closes
   - [ ] "Edited" badge appears on variation #3
   - [ ] Edited text displayed in preview

5. **Verify Edit Preservation**
   - [ ] Refresh page (with campaign saved)
   - [ ] Edited version still shows "Edited" badge
   - [ ] Edited text preserved

6. **Export as JSON**
   - [ ] Select edited variation #3
   - [ ] Click "Export" → "JSON"
   - [ ] File downloads: `communication_[id].json`
   - [ ] Open JSON file
   - [ ] Verify contains:
     - [ ] Original subject and body
     - [ ] Edited subject and body
     - [ ] Metadata (channel, cohorts, scores)

7. **Export as TXT**
   - [ ] Select edited variation #3
   - [ ] Click "Export" → "TXT"
   - [ ] File downloads: `communication_[id].txt`
   - [ ] Open TXT file
   - [ ] Verify contains edited text
   - [ ] Human-readable format

8. **Export as CSV**
   - [ ] Select all 5 variations
   - [ ] Click "Export All" → "CSV"
   - [ ] File downloads: `campaign_[id]_communications.csv`
   - [ ] Open CSV file
   - [ ] Verify contains:
     - [ ] All 5 variations as rows
     - [ ] Columns: ID, Subject/Title, Body, Scores, Edited flag
     - [ ] Edited variation marked

9. **Test Multiple Edits**
   - [ ] Edit variation #3 again
   - [ ] Make different changes
   - [ ] Save
   - [ ] Previous edits overwritten (not versioned in MVP)

### Acceptance Criteria

- [ ] Edit functionality works smoothly
- [ ] "Edited" badge appears and persists
- [ ] JSON export includes original and edited
- [ ] TXT export works
- [ ] CSV export works with all variations
- [ ] File downloads successful

### Results

**Status**: [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes**:
```
_______________________________________________________________________________
_______________________________________________________________________________
_______________________________________________________________________________
```

**Issues Found**:
```
_______________________________________________________________________________
_______________________________________________________________________________
_______________________________________________________________________________
```

---

## Test Scenario 6: Validation and Error Handling

**Objective**: Validate form validation, error messages, and system resilience

**Priority**: Critical
**Estimated Duration**: 7 minutes

### Expected Behavior

1. Form validates required fields
2. Inline error messages clear and helpful
3. Generate button disabled until valid
4. API errors handled gracefully
5. User informed of errors without technical jargon
6. Recovery from errors possible

### Test Steps

#### Part A: Form Validation

1. **Test Required Fields**
   - [ ] Open new campaign form
   - [ ] Leave "Channel" empty
   - [ ] Click "Generate Communications"
   - [ ] Error message: "Please select a channel"
   - [ ] Generate button disabled or error shown

2. **Test Cohort Validation**
   - [ ] Select channel: Email
   - [ ] Leave cohorts empty
   - [ ] Click "Generate Communications"
   - [ ] Error message: "Please select at least one cohort"

3. **Test Product Validation**
   - [ ] Select channel and cohorts
   - [ ] Leave product empty
   - [ ] Click "Generate Communications"
   - [ ] Error message: "Please select a product"

4. **Test Objective Validation**
   - [ ] Fill all fields except objective
   - [ ] Click "Generate Communications"
   - [ ] Error message: "Please select an objective"

5. **Test Promotion Details**
   - [ ] Fill all required fields
   - [ ] Leave "Promotion Details" empty
   - [ ] Click "Generate Communications"
   - [ ] Error message or warning about missing promotion details

6. **Test Required Phrases Format**
   - [ ] Enter required phrases: "phrase1", "phrase2"
   - [ ] Verify comma-separated format accepted
   - [ ] Verify phrases parsed correctly

#### Part B: Backend Error Handling

7. **Simulate Backend Failure**
   - [ ] Stop backend server (Ctrl+C in backend terminal)
   - [ ] In frontend, create valid campaign
   - [ ] Click "Generate Communications"
   - [ ] Error message displayed: "Unable to connect to server" or similar
   - [ ] User-friendly message (no stack traces)
   - [ ] Retry option available or form still editable

8. **Restart and Retry**
   - [ ] Restart backend: `./start-backend.sh`
   - [ ] Wait for backend to start (check http://localhost:8000/docs)
   - [ ] In frontend, click "Generate Communications" again
   - [ ] Generation succeeds

9. **Test Invalid API Key**
   - [ ] Stop backend
   - [ ] Edit backend/.env: Set ANTHROPIC_API_KEY to invalid value
   - [ ] Restart backend
   - [ ] Generate communications
   - [ ] Error message: "AI service error" or similar
   - [ ] User informed without exposing API details

10. **Restore Valid Configuration**
    - [ ] Stop backend
    - [ ] Restore valid ANTHROPIC_API_KEY in backend/.env
    - [ ] Restart backend
    - [ ] Generate communications
    - [ ] Success

#### Part C: Frontend Validation

11. **Test Character Limits (SMS)**
    - [ ] Select SMS channel
    - [ ] Create campaign
    - [ ] Generate communications
    - [ ] Verify all variations show character count
    - [ ] If editing, verify character limit enforced at 160

12. **Test Character Limits (Push)**
    - [ ] Select Push Notification channel
    - [ ] Generate communications
    - [ ] Verify title: 40-50 chars
    - [ ] Verify body: 100-120 chars
    - [ ] Character counts displayed

13. **Test Network Timeout**
    - [ ] Generate communication (may require slow network simulation)
    - [ ] If generation takes >30 seconds
    - [ ] Verify timeout message or loading state persists
    - [ ] User not left in ambiguous state

### Acceptance Criteria

- [ ] All required field validations work
- [ ] Error messages clear and helpful
- [ ] Backend errors handled gracefully
- [ ] No stack traces shown to user
- [ ] Recovery from errors possible
- [ ] Character limits enforced
- [ ] Loading states appropriate

### Results

**Status**: [ ] PASS [ ] FAIL [ ] BLOCKED

**Notes**:
```
_______________________________________________________________________________
_______________________________________________________________________________
_______________________________________________________________________________
```

**Issues Found**:
```
_______________________________________________________________________________
_______________________________________________________________________________
_______________________________________________________________________________
```

---

## Test Execution Summary

| Scenario | Status | Critical Issues | Notes |
|----------|--------|-----------------|-------|
| 1. Email Promotion | [ ] PASS [ ] FAIL | | |
| 2. SMS Service Update | [ ] PASS [ ] FAIL | | |
| 3. Push Notification | [ ] PASS [ ] FAIL | | |
| 4. Regeneration | [ ] PASS [ ] FAIL | | |
| 5. Edit and Export | [ ] PASS [ ] FAIL | | |
| 6. Validation & Errors | [ ] PASS [ ] FAIL | | |

**Overall Status**: [ ] ALL PASS [ ] SOME FAILURES [ ] BLOCKED

**Critical Issues Requiring Fix**:
```
1. _______________________________________________________________________________
2. _______________________________________________________________________________
3. _______________________________________________________________________________
```

**Non-Critical Issues**:
```
1. _______________________________________________________________________________
2. _______________________________________________________________________________
3. _______________________________________________________________________________
```

**Testing Environment**:
- Backend Version: _____________
- Frontend Version: _____________
- Database: SQLite (MVP)
- API Provider: Anthropic Claude
- Browser: _____________
- OS: _____________

**Sign-off**:
- Tester: _______________ Date: _______________
- Reviewer: _______________ Date: _______________
