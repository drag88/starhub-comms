# Testing Guide

Comprehensive testing guide for the StarHub Customer Communications Generator.

## Test Structure

```
tests/
├── backend/          # Backend tests
│   ├── unit/        # Unit tests for services
│   ├── integration/ # API endpoint tests
│   └── performance/ # Performance benchmarks
├── frontend/        # Frontend tests (future)
└── e2e/            # End-to-end acceptance tests
```

## Backend Tests

All backend tests are organized by type in `tests/backend/`.

### Unit Tests

Location: `tests/backend/unit/`

Tests individual services and components in isolation.

| Test File | Tests | Coverage | Purpose |
|-----------|-------|----------|---------|
| test_config_loader.py | 24 | 100% | YAML configuration loading |
| test_recommendation_scorer.py | 27 | 100% | 4-pillar scoring algorithm |
| test_communication_generator.py | 21 | 84% | Claude API integration |

**Total Unit Tests**: 72 tests

#### Running Unit Tests

```bash
# All unit tests
cd backend
uv run pytest ../tests/backend/unit/ -v

# Specific test file
uv run pytest ../tests/backend/unit/test_config_loader.py -v

# Specific test
uv run pytest ../tests/backend/unit/test_config_loader.py::test_get_cohorts -v

# With coverage report
uv run pytest ../tests/backend/unit/ --cov=app/services --cov-report=html
```

### Integration Tests

Location: `tests/backend/integration/`

Tests API endpoints end-to-end with database interactions.

| Test File | Tests | Coverage | Purpose |
|-----------|-------|----------|---------|
| test_api_campaigns.py | 16 | 100% | Campaign CRUD endpoints |
| test_api_utilities.py | 10 | 100% | Utility endpoints |
| test_integration.py | 36 | 92% | Generation service integration |

**Total Integration Tests**: 62 tests

#### Running Integration Tests

```bash
# All integration tests
cd backend
uv run pytest ../tests/backend/integration/ -v

# Specific endpoint tests
uv run pytest ../tests/backend/integration/test_api_campaigns.py -v

# With detailed output
uv run pytest ../tests/backend/integration/ -v -s
```

### Performance Tests

Location: `tests/backend/performance/`

Automated performance benchmarking suite.

#### Running Performance Tests

```bash
cd backend
uv run python ../tests/backend/performance/test_performance.py
```

#### Performance Targets

| Metric | Target | Purpose |
|--------|--------|---------|
| API health check | < 100ms | Service availability |
| Campaign creation | < 2s (95th percentile) | User experience |
| Database queries | < 500ms | Data access speed |
| Concurrent users | 5+ simultaneous | Load handling |
| Communication generation | < 10s | AI integration |

### Running All Backend Tests

```bash
cd backend

# All tests
uv run pytest ../tests/backend/ -v

# All tests with coverage
uv run pytest ../tests/backend/ --cov=app --cov-report=html

# Stop on first failure
uv run pytest ../tests/backend/ -x

# Run last failed tests
uv run pytest ../tests/backend/ --lf

# Parallel execution (if pytest-xdist installed)
uv run pytest ../tests/backend/ -n auto
```

## Frontend Tests

Location: `tests/frontend/`

**Status**: Planned for future implementation

**Proposed Stack**:
- Jest - Test framework
- React Testing Library - Component testing
- Cypress - E2E testing

**Planned Coverage**:
- Component unit tests
- Form validation tests
- API integration tests
- User interaction tests

## End-to-End Tests

Location: `tests/e2e/`

Manual acceptance test scenarios covering complete user workflows.

### Test Scenarios

6 comprehensive scenarios documented in `tests/e2e/test_scenarios.md`:

1. **Email Promotion for Deal Seekers**
   - Create email campaign
   - Generate 5 variations
   - Verify scoring
   - Select top recommendation

2. **SMS Service Update for Mass Market**
   - Create SMS campaign
   - Verify character limits
   - Check opt-out compliance
   - Export to TXT

3. **Push Notification for Sports Enthusiasts**
   - Create push notification campaign
   - Verify title/body structure
   - Check emoji usage
   - Export to CSV

4. **Regeneration with Parameter Change**
   - Create initial campaign
   - Generate variations
   - Modify parameters
   - Regenerate new variations

5. **Manual Edit and Export**
   - Select communication
   - Edit text inline
   - Verify automatic rescoring
   - Export to JSON

6. **Validation and Error Handling**
   - Test invalid inputs
   - Verify error messages
   - Check required fields
   - Test edge cases

### Executing E2E Tests

#### Prerequisites

1. Start both backend and frontend:
   ```bash
   ./start-all.sh
   ```

2. Ensure valid `ANTHROPIC_API_KEY` in `backend/.env`

#### Execution

1. Open `tests/e2e/test_scenarios.md`
2. Follow step-by-step instructions for each scenario
3. Document results in the test file
4. Mark checkboxes as complete

#### E2E Test Checklist

```markdown
- [ ] Scenario 1: Email Promotion for Deal Seekers
- [ ] Scenario 2: SMS Service Update for Mass Market
- [ ] Scenario 3: Push Notification for Sports Enthusiasts
- [ ] Scenario 4: Regeneration with Parameter Change
- [ ] Scenario 5: Manual Edit and Export
- [ ] Scenario 6: Validation and Error Handling
```

## Writing Tests

### Unit Test Template

```python
# tests/backend/unit/test_example.py

import pytest
from app.services.example import ExampleService

@pytest.fixture
def example_service():
    """Fixture to create ExampleService instance."""
    return ExampleService()

def test_example_function(example_service):
    """Test that example function returns expected result."""
    # Arrange
    input_data = {"key": "value"}

    # Act
    result = example_service.process(input_data)

    # Assert
    assert result is not None
    assert result["status"] == "success"
```

### Integration Test Template

```python
# tests/backend/integration/test_api_example.py

import pytest
from fastapi.testclient import TestClient
from main import app
from database import get_db, init_db

@pytest.fixture
def client():
    """Create test client with fresh database."""
    init_db()
    with TestClient(app) as test_client:
        yield test_client

def test_create_resource(client):
    """Test creating a resource via API."""
    # Arrange
    payload = {
        "name": "Test Resource",
        "value": 123
    }

    # Act
    response = client.post("/api/v1/resources/", json=payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Resource"
    assert "id" in data
```

## Test Best Practices

### General Principles

1. **Independent Tests**: Each test should run independently
2. **Descriptive Names**: Use clear, descriptive test names
3. **AAA Pattern**: Arrange, Act, Assert structure
4. **Single Assertion**: Test one thing per test (when practical)
5. **Fast Execution**: Keep tests fast and focused

### Backend Testing

1. **Use Fixtures**: Reuse setup code with pytest fixtures
2. **Mock External Services**: Mock Claude API in unit tests
3. **Fresh Database**: Each integration test gets clean database
4. **Test Error Cases**: Don't just test happy paths
5. **Verify Response Structure**: Check full response format

### Frontend Testing (Future)

1. **Test User Behavior**: Focus on user interactions
2. **Avoid Implementation Details**: Test what users see
3. **Use Testing Library Queries**: Semantic queries over DOM
4. **Mock API Calls**: Use MSW or similar for API mocking
5. **Test Accessibility**: Include a11y testing

## Test Coverage Goals

| Component | Target Coverage | Current Status |
|-----------|----------------|----------------|
| Backend services | > 80% | 95.6% ✅ |
| API endpoints | 100% | 100% ✅ |
| Frontend components | > 70% | Planned |
| E2E scenarios | All acceptance criteria | 6/6 documented ✅ |

## Continuous Integration (Future)

Planned CI/CD integration:

```yaml
# .github/workflows/tests.yml (example)
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: |
          cd backend
          uv venv
          source .venv/bin/activate
          uv pip install -e ".[dev]"
          pytest tests/backend/ -v

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: |
          cd frontend
          npm install
          npm run test
          npm run build
```

## Debugging Tests

### Backend Test Debugging

```bash
# Run with verbose output
uv run pytest ../tests/backend/ -v -s

# Run specific test with pdb
uv run pytest ../tests/backend/unit/test_config_loader.py::test_get_cohorts -v --pdb

# Show local variables on failure
uv run pytest ../tests/backend/ -v -l

# Increase log level
uv run pytest ../tests/backend/ -v --log-cli-level=DEBUG
```

### Common Test Failures

#### 1. Import Errors

**Error**: `ModuleNotFoundError: No module named 'app'`

**Fix**: Ensure tests are run from correct directory and conftest.py sets up paths:

```python
# tests/backend/conftest.py
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))
```

#### 2. Database Errors

**Error**: `sqlalchemy.exc.OperationalError: no such table`

**Fix**: Ensure test database is initialized in fixture:

```python
@pytest.fixture
def client():
    from database import init_db
    init_db()
    # ... rest of fixture
```

#### 3. API Key Errors

**Error**: `anthropic.APIConnectionError`

**Fix**: Set mock API key or use mocks in tests:

```python
import os
os.environ["ANTHROPIC_API_KEY"] = "test-key"
```

## Test Maintenance

### Keeping Tests Green

1. **Run tests before commits**:
   ```bash
   uv run pytest ../tests/backend/ -v
   ```

2. **Fix failing tests immediately**: Don't let them accumulate

3. **Update tests with code changes**: Keep tests synchronized

4. **Review test output**: Don't ignore warnings

### Test Refactoring

When to refactor tests:

- Duplicated setup code → Create fixtures
- Long test functions → Break into smaller tests
- Brittle tests → Use better test data
- Slow tests → Mock external dependencies

## Performance Testing

### Running Performance Suite

```bash
cd backend
uv run python ../tests/backend/performance/test_performance.py
```

### Performance Metrics Collected

- Request latency (min, max, avg, p95, p99)
- Throughput (requests/second)
- Concurrent user handling
- Database query time
- Memory usage

### Performance Regression

Monitor these metrics over time to detect regressions:

```bash
# Run and save baseline
uv run python ../tests/backend/performance/test_performance.py > baseline.txt

# Compare after changes
uv run python ../tests/backend/performance/test_performance.py > current.txt
diff baseline.txt current.txt
```

## Test Documentation

Each test should be documented with:

1. **Docstring**: What the test validates
2. **Comments**: Why specific assertions matter
3. **Clear naming**: test_<function>_<scenario>_<expected>

Example:

```python
def test_score_communication_with_missing_opt_out_returns_low_compliance_score():
    """
    Test that scoring a promotional SMS without opt-out instruction
    returns a low compliance score and CRITICAL flag.

    This ensures the system properly validates regulatory requirements.
    """
    # Test implementation...
```

## Test Reports

### Generate Coverage Report

```bash
cd backend
uv run pytest ../tests/backend/ --cov=app --cov-report=html

# Open report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Generate Test Report

```bash
# JUnit XML (for CI/CD)
uv run pytest ../tests/backend/ --junitxml=report.xml

# HTML report (requires pytest-html)
uv run pytest ../tests/backend/ --html=report.html
```

## Quick Reference

### Common Commands

```bash
# All backend tests
uv run pytest ../tests/backend/ -v

# Unit tests only
uv run pytest ../tests/backend/unit/ -v

# Integration tests only
uv run pytest ../tests/backend/integration/ -v

# Performance tests
uv run python ../tests/backend/performance/test_performance.py

# Specific test file
uv run pytest ../tests/backend/unit/test_config_loader.py -v

# With coverage
uv run pytest ../tests/backend/ --cov=app --cov-report=html

# Stop on first failure
uv run pytest ../tests/backend/ -x

# Verbose with stdout
uv run pytest ../tests/backend/ -v -s
```

### Test Fixtures

Located in `tests/backend/conftest.py`:

- `client`: TestClient with fresh database
- `example_campaign`: Sample campaign for testing
- `mock_claude_response`: Mock Claude API responses

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [React Testing Library](https://testing-library.com/react)
- [Testing Best Practices](https://testingjavascript.com/)

---

**Last Updated**: 2025-11-09
**Maintained By**: Data Analytics Team, StarHub Ltd.
