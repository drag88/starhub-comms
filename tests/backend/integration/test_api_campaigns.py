"""
Integration tests for campaign API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db
from app.models.campaign import Campaign

# Create test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_campaigns.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Reset database before each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_campaign_success():
    """Test successful campaign creation."""
    campaign_data = {
        "campaign_name": "Test Campaign",
        "channel": "email",
        "objective": "promotion",
        "product_lines": ["bundle_homehub_plus"],
        "cohorts": ["deal_seekers", "at_risk"],
        "promotion_details": {
            "promotion_name": "Test Promo",
            "pricing": {"monthly_price": 99.99},
            "features": ["Feature 1", "Feature 2"]
        },
        "customization": {
            "tone": "urgent",
            "custom_instructions": "Test instructions",
            "required_phrases": ["exclusive"],
            "prohibited_words": [],
            "length_preference": "optimal"
        }
    }

    response = client.post("/api/v1/campaigns/", json=campaign_data)

    assert response.status_code == 201
    data = response.json()
    assert data["campaign_name"] == "Test Campaign"
    assert data["channel"] == "email"
    assert data["objective"] == "promotion"
    assert "campaign_id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert data["product_lines"] == ["bundle_homehub_plus"]
    assert data["cohorts"] == ["deal_seekers", "at_risk"]


def test_create_campaign_invalid_channel():
    """Test campaign creation with invalid channel."""
    campaign_data = {
        "campaign_name": "Test Campaign",
        "channel": "invalid_channel",
        "objective": "promotion",
        "product_lines": ["bundle_homehub_plus"],
        "cohorts": ["deal_seekers"],
        "customization": {
            "tone": "friendly",
            "length_preference": "optimal"
        }
    }

    response = client.post("/api/v1/campaigns/", json=campaign_data)

    assert response.status_code == 422
    assert "error" in response.json() or "detail" in response.json()


def test_create_campaign_invalid_tone():
    """Test campaign creation with invalid tone."""
    campaign_data = {
        "campaign_name": "Test Campaign",
        "channel": "email",
        "objective": "promotion",
        "product_lines": ["bundle_homehub_plus"],
        "cohorts": ["deal_seekers"],
        "customization": {
            "tone": "invalid_tone",
            "length_preference": "optimal"
        }
    }

    response = client.post("/api/v1/campaigns/", json=campaign_data)

    assert response.status_code == 422


def test_get_campaign_success():
    """Test retrieving existing campaign."""
    # Create campaign first
    campaign_data = {
        "campaign_name": "Test Get Campaign",
        "channel": "sms",
        "objective": "retention",
        "product_lines": ["mobile_postpaid"],
        "cohorts": ["loyal_customers"],
        "customization": {
            "tone": "friendly",
            "length_preference": "optimal"
        }
    }

    create_response = client.post("/api/v1/campaigns/", json=campaign_data)
    campaign_id = create_response.json()["campaign_id"]

    # Get the campaign
    response = client.get(f"/api/v1/campaigns/{campaign_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["campaign_id"] == campaign_id
    assert data["campaign_name"] == "Test Get Campaign"
    assert data["channel"] == "sms"


def test_get_campaign_not_found():
    """Test retrieving non-existent campaign."""
    response = client.get("/api/v1/campaigns/99999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_campaign_success():
    """Test updating campaign."""
    # Create campaign
    campaign_data = {
        "campaign_name": "Original Name",
        "channel": "email",
        "objective": "promotion",
        "product_lines": ["bundle_homehub_plus"],
        "cohorts": ["deal_seekers"],
        "customization": {
            "tone": "friendly",
            "length_preference": "optimal"
        }
    }

    create_response = client.post("/api/v1/campaigns/", json=campaign_data)
    campaign_id = create_response.json()["campaign_id"]

    # Update campaign
    update_data = {
        "campaign_name": "Updated Name",
        "customization": {
            "tone": "urgent",
            "length_preference": "shorter"
        }
    }

    response = client.put(f"/api/v1/campaigns/{campaign_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["campaign_name"] == "Updated Name"
    assert data["customization"]["tone"] == "urgent"
    # Channel should remain unchanged
    assert data["channel"] == "email"


def test_delete_campaign_success():
    """Test deleting campaign."""
    # Create campaign
    campaign_data = {
        "campaign_name": "Campaign to Delete",
        "channel": "push",
        "objective": "upsell",
        "product_lines": ["entertainment_sports"],
        "cohorts": ["sports_fans"],
        "customization": {
            "tone": "premium",
            "length_preference": "optimal"
        }
    }

    create_response = client.post("/api/v1/campaigns/", json=campaign_data)
    campaign_id = create_response.json()["campaign_id"]

    # Delete campaign
    response = client.delete(f"/api/v1/campaigns/{campaign_id}")

    assert response.status_code == 204

    # Verify it's deleted
    get_response = client.get(f"/api/v1/campaigns/{campaign_id}")
    assert get_response.status_code == 404


def test_delete_campaign_not_found():
    """Test deleting non-existent campaign."""
    response = client.delete("/api/v1/campaigns/99999")

    assert response.status_code == 404


def test_list_campaigns_empty():
    """Test listing campaigns when none exist."""
    response = client.get("/api/v1/campaigns/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_list_campaigns_with_data():
    """Test listing multiple campaigns."""
    # Create 3 campaigns
    for i in range(3):
        campaign_data = {
            "campaign_name": f"Campaign {i+1}",
            "channel": "email" if i % 2 == 0 else "sms",
            "objective": "promotion",
            "product_lines": ["bundle_homehub_plus"],
            "cohorts": ["deal_seekers"],
            "customization": {
                "tone": "friendly",
                "length_preference": "optimal"
            }
        }
        client.post("/api/v1/campaigns/", json=campaign_data)

    # List all campaigns
    response = client.get("/api/v1/campaigns/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_list_campaigns_pagination():
    """Test campaign pagination."""
    # Create 5 campaigns
    for i in range(5):
        campaign_data = {
            "campaign_name": f"Campaign {i+1}",
            "channel": "email",
            "objective": "promotion",
            "product_lines": ["bundle_homehub_plus"],
            "cohorts": ["deal_seekers"],
            "customization": {
                "tone": "friendly",
                "length_preference": "optimal"
            }
        }
        client.post("/api/v1/campaigns/", json=campaign_data)

    # Get first 2
    response = client.get("/api/v1/campaigns/?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

    # Get next 2
    response = client.get("/api/v1/campaigns/?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_list_campaigns_filter_by_channel():
    """Test filtering campaigns by channel."""
    # Create campaigns with different channels
    for channel in ["email", "sms", "push", "email"]:
        campaign_data = {
            "campaign_name": f"Campaign {channel}",
            "channel": channel,
            "objective": "promotion",
            "product_lines": ["bundle_homehub_plus"],
            "cohorts": ["deal_seekers"],
            "customization": {
                "tone": "friendly",
                "length_preference": "optimal"
            }
        }
        client.post("/api/v1/campaigns/", json=campaign_data)

    # Filter by email
    response = client.get("/api/v1/campaigns/?channel=email")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(c["channel"] == "email" for c in data)


def test_list_campaigns_filter_by_objective():
    """Test filtering campaigns by objective."""
    # Create campaigns with different objectives
    for objective in ["promotion", "retention", "promotion"]:
        campaign_data = {
            "campaign_name": f"Campaign {objective}",
            "channel": "email",
            "objective": objective,
            "product_lines": ["bundle_homehub_plus"],
            "cohorts": ["deal_seekers"],
            "customization": {
                "tone": "friendly",
                "length_preference": "optimal"
            }
        }
        client.post("/api/v1/campaigns/", json=campaign_data)

    # Filter by promotion
    response = client.get("/api/v1/campaigns/?objective=promotion")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(c["objective"] == "promotion" for c in data)


def test_create_campaign_missing_required_fields():
    """Test campaign creation with missing required fields."""
    campaign_data = {
        "campaign_name": "Incomplete Campaign",
        "channel": "email"
        # Missing objective, product_lines, cohorts, customization
    }

    response = client.post("/api/v1/campaigns/", json=campaign_data)

    assert response.status_code == 422


def test_create_campaign_empty_product_lines():
    """Test campaign creation with empty product lines."""
    campaign_data = {
        "campaign_name": "Test Campaign",
        "channel": "email",
        "objective": "promotion",
        "product_lines": [],  # Empty
        "cohorts": ["deal_seekers"],
        "customization": {
            "tone": "friendly",
            "length_preference": "optimal"
        }
    }

    response = client.post("/api/v1/campaigns/", json=campaign_data)

    assert response.status_code == 422


def test_create_campaign_empty_cohorts():
    """Test campaign creation with empty cohorts."""
    campaign_data = {
        "campaign_name": "Test Campaign",
        "channel": "email",
        "objective": "promotion",
        "product_lines": ["bundle_homehub_plus"],
        "cohorts": [],  # Empty
        "customization": {
            "tone": "friendly",
            "length_preference": "optimal"
        }
    }

    response = client.post("/api/v1/campaigns/", json=campaign_data)

    assert response.status_code == 422
