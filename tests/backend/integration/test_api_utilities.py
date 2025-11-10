"""
Integration tests for utility API endpoints.
"""
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_get_cohorts():
    """Test retrieving cohorts configuration."""
    response = client.get("/api/v1/cohorts")

    assert response.status_code == 200
    data = response.json()

    assert "cohorts" in data
    assert "total" in data
    assert "categories" in data
    assert isinstance(data["cohorts"], list)
    assert data["total"] > 0

    # Check cohort structure
    if data["cohorts"]:
        cohort = data["cohorts"][0]
        assert "id" in cohort
        assert "name" in cohort
        assert "category" in cohort


def test_get_products():
    """Test retrieving products configuration."""
    response = client.get("/api/v1/products")

    assert response.status_code == 200
    data = response.json()

    assert "products" in data
    assert "total" in data
    assert "categories" in data
    assert isinstance(data["products"], list)
    assert data["total"] > 0

    # Check product structure
    if data["products"]:
        product = data["products"][0]
        assert "id" in product
        assert "name" in product
        assert "category" in product


def test_get_objectives():
    """Test retrieving objectives configuration."""
    response = client.get("/api/v1/objectives")

    assert response.status_code == 200
    data = response.json()

    assert "objectives" in data
    assert "total" in data
    assert isinstance(data["objectives"], list)
    assert data["total"] > 0

    # Check objective structure
    if data["objectives"]:
        objective = data["objectives"][0]
        assert "id" in objective
        assert "name" in objective


def test_get_channels():
    """Test retrieving channels configuration."""
    response = client.get("/api/v1/channels")

    assert response.status_code == 200
    data = response.json()

    assert "channels" in data
    assert "total" in data
    assert "supported_channels" in data

    # Check for expected channels
    assert "email" in data["channels"]
    assert "sms" in data["channels"]
    assert "push" in data["channels"]
    assert data["total"] == 3

    # Check SMS constraints
    sms_constraints = data["channels"]["sms"]
    assert "max_length" in sms_constraints
    assert sms_constraints["max_length"] == 160
    assert "requires_opt_out" in sms_constraints

    # Check email constraints
    email_constraints = data["channels"]["email"]
    assert "requires_unsubscribe" in email_constraints


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert "version" in data
    assert "database" in data
    assert "services" in data

    # Check services
    assert "generation" in data["services"]
    assert "scoring" in data["services"]
    assert "config" in data["services"]

    # Status should be healthy or degraded
    assert data["status"] in ["healthy", "degraded", "unhealthy"]


def test_get_api_info():
    """Test API info endpoint."""
    response = client.get("/api/v1/info")

    assert response.status_code == 200
    data = response.json()

    assert "name" in data
    assert "version" in data
    assert "description" in data
    assert "capabilities" in data
    assert "endpoints" in data

    # Check capabilities
    capabilities = data["capabilities"]
    assert "channels" in capabilities
    assert "objectives" in capabilities
    assert "variations_per_campaign" in capabilities
    assert capabilities["variations_per_campaign"] == 5

    # Check supported channels
    assert set(capabilities["channels"]) == {"email", "sms", "push"}

    # Check endpoints
    endpoints = data["endpoints"]
    assert "campaigns" in endpoints
    assert "health" in endpoints


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "active"
    assert "/docs" in data["documentation"]


def test_openapi_endpoint():
    """Test OpenAPI schema endpoint."""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    data = response.json()

    assert "openapi" in data
    assert "info" in data
    assert "paths" in data

    # Check some expected paths
    assert "/api/v1/campaigns/" in data["paths"]
    assert "/api/v1/health" in data["paths"]


def test_docs_endpoint():
    """Test Swagger UI docs endpoint."""
    response = client.get("/docs")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_redoc_endpoint():
    """Test ReDoc endpoint."""
    response = client.get("/redoc")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
