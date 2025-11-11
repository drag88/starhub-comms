"""
Integration tests for creative API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, AsyncMock, MagicMock
import os
from pathlib import Path

from main import app
from database import Base, get_db
from app.models.campaign import Campaign
from app.models.creative import GeneratedCreative

# Create test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_creatives.db"
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


@pytest.fixture
def sample_campaign():
    """Create a sample campaign for testing."""
    campaign_data = {
        "campaign_name": "Test Creative Campaign",
        "channel": "email",
        "objective": "promotion",
        "product_lines": ["bundle_homehub_plus"],
        "cohorts": ["deal_seekers"],
        "customization": {
            "tone": "friendly",
            "length_preference": "optimal"
        }
    }

    response = client.post("/api/v1/campaigns/", json=campaign_data)
    return response.json()


@pytest.fixture
def mock_creative_service():
    """Mock CreativeGenerationService for testing."""
    with patch("app.api.creatives.CreativeGenerationService") as mock_service:
        # Mock the generate_and_score method to return sample results
        mock_instance = MagicMock()
        mock_instance.generate_and_score = AsyncMock(return_value=[
            {
                "creative_id": 1,
                "variant_number": 1,
                "image_url": "/static/creatives/test_1.jpg",
                "score": 95,
                "reasoning": "High quality variant 1",
                "rank": 1
            },
            {
                "creative_id": 2,
                "variant_number": 2,
                "image_url": "/static/creatives/test_2.jpg",
                "score": 88,
                "reasoning": "Good quality variant 2",
                "rank": 2
            },
            {
                "creative_id": 3,
                "variant_number": 3,
                "image_url": "/static/creatives/test_3.jpg",
                "score": 82,
                "reasoning": "Acceptable variant 3",
                "rank": 3
            }
        ])
        mock_service.return_value = mock_instance
        yield mock_service


def test_generate_campaign_creatives_campaign_not_found():
    """Test creative generation with non-existent campaign."""
    response = client.post("/api/v1/campaigns/99999/generate-creatives")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_generate_campaign_creatives_success(sample_campaign, mock_creative_service):
    """Test successful creative generation."""
    campaign_id = sample_campaign["campaign_id"]

    # Create sample creatives directly in database (since we're mocking the service)
    db = next(override_get_db())
    try:
        for variant in range(1, 4):
            creative = GeneratedCreative(
                campaign_id=campaign_id,
                variant_number=variant,
                channel_type="email_header",
                image_filename=f"test_{variant}.jpg",
                image_url=f"/static/creatives/test_{variant}.jpg",
                prompt_used=f"Test prompt {variant}",
                generation_params='{"width": 600, "height": 200}',
                model_used="seedream-4",
                recommendation_score=95 - (variant * 5),
                score_reasoning=f"Test reasoning {variant}",
                is_selected=False
            )
            db.add(creative)
        db.commit()
    finally:
        db.close()

    response = client.post(f"/api/v1/campaigns/{campaign_id}/generate-creatives")

    assert response.status_code == 201
    data = response.json()
    assert data["campaign_id"] == campaign_id
    assert len(data["creatives"]) == 3
    assert data["total"] == 3

    # Verify creatives are sorted by score descending
    scores = [c["recommendation_score"] for c in data["creatives"]]
    assert scores == sorted(scores, reverse=True)


def test_generate_campaign_creatives_api_key_missing(sample_campaign):
    """Test creative generation with missing API key."""
    campaign_id = sample_campaign["campaign_id"]

    with patch("app.api.creatives.CreativeGenerationService") as mock_service:
        mock_service.side_effect = ValueError("FAL_KEY not found in environment variables")

        response = client.post(f"/api/v1/campaigns/{campaign_id}/generate-creatives")

        assert response.status_code == 500
        assert "FAL_KEY" in response.json()["detail"]


def test_get_campaign_creatives_campaign_not_found():
    """Test getting creatives for non-existent campaign."""
    response = client.get("/api/v1/campaigns/99999/creatives")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_campaign_creatives_empty(sample_campaign):
    """Test getting creatives when none exist for campaign."""
    campaign_id = sample_campaign["campaign_id"]

    response = client.get(f"/api/v1/campaigns/{campaign_id}/creatives")

    assert response.status_code == 200
    data = response.json()
    assert data["campaign_id"] == campaign_id
    assert len(data["creatives"]) == 0
    assert data["total"] == 0


def test_get_campaign_creatives_with_data(sample_campaign):
    """Test getting creatives when they exist."""
    campaign_id = sample_campaign["campaign_id"]

    # Create sample creatives
    db = next(override_get_db())
    try:
        for variant in range(1, 4):
            creative = GeneratedCreative(
                campaign_id=campaign_id,
                variant_number=variant,
                channel_type="email_header",
                image_filename=f"test_{variant}.jpg",
                image_url=f"/static/creatives/test_{variant}.jpg",
                prompt_used=f"Test prompt {variant}",
                generation_params='{"width": 600, "height": 200}',
                model_used="seedream-4",
                recommendation_score=90 - (variant * 10),
                score_reasoning=f"Test reasoning {variant}",
                is_selected=False
            )
            db.add(creative)
        db.commit()
    finally:
        db.close()

    response = client.get(f"/api/v1/campaigns/{campaign_id}/creatives")

    assert response.status_code == 200
    data = response.json()
    assert data["campaign_id"] == campaign_id
    assert len(data["creatives"]) == 3
    assert data["total"] == 3

    # Verify sorted by score descending
    scores = [c["recommendation_score"] for c in data["creatives"]]
    assert scores == sorted(scores, reverse=True), "Creatives should be sorted by score descending"
    # Verify we have 3 different scores
    assert len(set(scores)) == 3, "Should have 3 different score values"


def test_get_creative_not_found():
    """Test getting non-existent creative."""
    response = client.get("/api/v1/creatives/99999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_get_creative_success(sample_campaign):
    """Test getting specific creative by ID."""
    campaign_id = sample_campaign["campaign_id"]

    # Create sample creative
    db = next(override_get_db())
    try:
        creative = GeneratedCreative(
            campaign_id=campaign_id,
            variant_number=1,
            channel_type="email_header",
            image_filename="test_1.jpg",
            image_url="/static/creatives/test_1.jpg",
            prompt_used="Test prompt",
            generation_params='{"width": 600, "height": 200}',
            model_used="seedream-4",
            recommendation_score=92,
            score_reasoning="High quality creative",
            is_selected=False
        )
        db.add(creative)
        db.commit()
        db.refresh(creative)
        creative_id = creative.creative_id
    finally:
        db.close()

    response = client.get(f"/api/v1/creatives/{creative_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["creative_id"] == creative_id
    assert data["campaign_id"] == campaign_id
    assert data["variant_number"] == 1
    assert data["channel_type"] == "email_header"
    assert data["image_url"] == "/static/creatives/test_1.jpg"
    assert data["recommendation_score"] == 92
    assert data["is_selected"] is False


def test_select_creative_not_found():
    """Test selecting non-existent creative."""
    response = client.put(
        "/api/v1/creatives/99999/select",
        json={"is_selected": True}
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_select_creative_success(sample_campaign):
    """Test marking creative as selected."""
    campaign_id = sample_campaign["campaign_id"]

    # Create sample creatives
    db = next(override_get_db())
    try:
        creative_ids = []
        for variant in range(1, 4):
            creative = GeneratedCreative(
                campaign_id=campaign_id,
                variant_number=variant,
                channel_type="email_header",
                image_filename=f"test_{variant}.jpg",
                image_url=f"/static/creatives/test_{variant}.jpg",
                prompt_used=f"Test prompt {variant}",
                generation_params='{"width": 600, "height": 200}',
                model_used="seedream-4",
                recommendation_score=90,
                score_reasoning="Test reasoning",
                is_selected=False
            )
            db.add(creative)
            db.commit()
            db.refresh(creative)
            creative_ids.append(creative.creative_id)
    finally:
        db.close()

    # Select the first creative
    response = client.put(
        f"/api/v1/creatives/{creative_ids[0]}/select",
        json={"is_selected": True}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["creative_id"] == creative_ids[0]
    assert data["is_selected"] is True

    # Verify other creatives are unselected
    for creative_id in creative_ids[1:]:
        response = client.get(f"/api/v1/creatives/{creative_id}")
        assert response.json()["is_selected"] is False


def test_unselect_creative_success(sample_campaign):
    """Test unmarking creative as selected."""
    campaign_id = sample_campaign["campaign_id"]

    # Create sample creative with is_selected=True
    db = next(override_get_db())
    try:
        creative = GeneratedCreative(
            campaign_id=campaign_id,
            variant_number=1,
            channel_type="email_header",
            image_filename="test_1.jpg",
            image_url="/static/creatives/test_1.jpg",
            prompt_used="Test prompt",
            generation_params='{"width": 600, "height": 200}',
            model_used="seedream-4",
            recommendation_score=92,
            score_reasoning="Test reasoning",
            is_selected=True
        )
        db.add(creative)
        db.commit()
        db.refresh(creative)
        creative_id = creative.creative_id
    finally:
        db.close()

    # Unselect the creative
    response = client.put(
        f"/api/v1/creatives/{creative_id}/select",
        json={"is_selected": False}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["creative_id"] == creative_id
    assert data["is_selected"] is False


def test_delete_creative_not_found():
    """Test deleting non-existent creative."""
    response = client.delete("/api/v1/creatives/99999")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_delete_creative_success(sample_campaign):
    """Test deleting creative and verifying file removal."""
    campaign_id = sample_campaign["campaign_id"]

    # Create sample creative
    db = next(override_get_db())
    try:
        creative = GeneratedCreative(
            campaign_id=campaign_id,
            variant_number=1,
            channel_type="email_header",
            image_filename="test_delete.jpg",
            image_url="/static/creatives/test_delete.jpg",
            prompt_used="Test prompt",
            generation_params='{"width": 600, "height": 200}',
            model_used="seedream-4",
            recommendation_score=92,
            score_reasoning="Test reasoning",
            is_selected=False
        )
        db.add(creative)
        db.commit()
        db.refresh(creative)
        creative_id = creative.creative_id
    finally:
        db.close()

    # Create dummy image file
    test_image_path = Path("backend/static/creatives/test_delete.jpg")
    test_image_path.parent.mkdir(parents=True, exist_ok=True)
    test_image_path.write_text("test image content")

    try:
        # Delete creative
        response = client.delete(f"/api/v1/creatives/{creative_id}")

        assert response.status_code == 204

        # Verify database record is deleted
        get_response = client.get(f"/api/v1/creatives/{creative_id}")
        assert get_response.status_code == 404

        # Verify image file is deleted
        assert not test_image_path.exists()
    finally:
        # Cleanup in case test fails
        if test_image_path.exists():
            test_image_path.unlink()


def test_delete_creative_file_not_found(sample_campaign):
    """Test deleting creative when image file doesn't exist."""
    campaign_id = sample_campaign["campaign_id"]

    # Create sample creative
    db = next(override_get_db())
    try:
        creative = GeneratedCreative(
            campaign_id=campaign_id,
            variant_number=1,
            channel_type="email_header",
            image_filename="nonexistent.jpg",
            image_url="/static/creatives/nonexistent.jpg",
            prompt_used="Test prompt",
            generation_params='{"width": 600, "height": 200}',
            model_used="seedream-4",
            recommendation_score=92,
            score_reasoning="Test reasoning",
            is_selected=False
        )
        db.add(creative)
        db.commit()
        db.refresh(creative)
        creative_id = creative.creative_id
    finally:
        db.close()

    # Delete creative (file doesn't exist, should still delete DB record)
    response = client.delete(f"/api/v1/creatives/{creative_id}")

    assert response.status_code == 204

    # Verify database record is deleted
    get_response = client.get(f"/api/v1/creatives/{creative_id}")
    assert get_response.status_code == 404


def test_creatives_workflow_complete(sample_campaign, mock_creative_service):
    """Test complete workflow: generate -> list -> select -> delete."""
    campaign_id = sample_campaign["campaign_id"]

    # Create sample creatives
    db = next(override_get_db())
    try:
        creative_ids = []
        for variant in range(1, 4):
            creative = GeneratedCreative(
                campaign_id=campaign_id,
                variant_number=variant,
                channel_type="email_header",
                image_filename=f"workflow_{variant}.jpg",
                image_url=f"/static/creatives/workflow_{variant}.jpg",
                prompt_used=f"Workflow prompt {variant}",
                generation_params='{"width": 600, "height": 200}',
                model_used="seedream-4",
                recommendation_score=95 - (variant * 5),
                score_reasoning=f"Workflow reasoning {variant}",
                is_selected=False
            )
            db.add(creative)
            db.commit()
            db.refresh(creative)
            creative_ids.append(creative.creative_id)
    finally:
        db.close()

    # 1. Generate creatives (already created above)
    gen_response = client.post(f"/api/v1/campaigns/{campaign_id}/generate-creatives")
    assert gen_response.status_code == 201

    # 2. List all creatives
    list_response = client.get(f"/api/v1/campaigns/{campaign_id}/creatives")
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 3

    # 3. Select the top-scoring creative
    select_response = client.put(
        f"/api/v1/creatives/{creative_ids[0]}/select",
        json={"is_selected": True}
    )
    assert select_response.status_code == 200
    assert select_response.json()["is_selected"] is True

    # 4. Delete the lowest-scoring creative
    # Create dummy file for deletion test
    test_file = Path("backend/static/creatives/workflow_3.jpg")
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("test")

    try:
        delete_response = client.delete(f"/api/v1/creatives/{creative_ids[2]}")
        assert delete_response.status_code == 204

        # Verify only 2 creatives remain
        final_list = client.get(f"/api/v1/campaigns/{campaign_id}/creatives")
        assert final_list.json()["total"] == 2
    finally:
        # Cleanup
        for variant in range(1, 4):
            test_file = Path(f"backend/static/creatives/workflow_{variant}.jpg")
            if test_file.exists():
                test_file.unlink()
