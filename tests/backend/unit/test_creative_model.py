"""
Unit tests for GeneratedCreative model and creative schemas.
"""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from app.models.campaign import Campaign
from app.models.creative import GeneratedCreative
from app.schemas.creative import (
    ChannelType,
    CreativeGenerationRequest,
    GeneratedCreativeResponse,
    CreativeListResponse,
    CreativeSelectionRequest,
)
import json


# Create in-memory SQLite database for testing
@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_campaign(db_session):
    """Create a sample campaign for testing."""
    campaign = Campaign(
        campaign_name="5G Launch Campaign",
        channel="email",
        objective="promotion",
        product_lines=json.dumps(["mobile_postpaid"]),
        cohorts=json.dumps(["high_value"]),
        customization=json.dumps({"tone": "friendly"})
    )
    db_session.add(campaign)
    db_session.commit()
    db_session.refresh(campaign)
    return campaign


class TestGeneratedCreativeModel:
    """Test GeneratedCreative model operations."""

    def test_create_creative(self, db_session, sample_campaign):
        """Test creating a GeneratedCreative instance."""
        creative = GeneratedCreative(
            campaign_id=sample_campaign.campaign_id,
            variant_number=1,
            channel_type="email_header",
            image_filename="creative_001.png",
            image_url="/static/creatives/creative_001.png",
            prompt_used="Generate a modern 5G creative with young professionals",
            generation_params=json.dumps({"model": "gemini-nano-banana", "style": "modern"}),
            model_used="gemini-nano-banana",
            recommendation_score=85,
            score_reasoning="Strong visual appeal and clear messaging",
            is_selected=False
        )

        db_session.add(creative)
        db_session.commit()
        db_session.refresh(creative)

        assert creative.creative_id is not None
        assert creative.campaign_id == sample_campaign.campaign_id
        assert creative.variant_number == 1
        assert creative.channel_type == "email_header"
        assert creative.recommendation_score == 85
        assert creative.is_selected is False
        assert isinstance(creative.created_at, datetime)

    def test_campaign_creative_relationship(self, db_session, sample_campaign):
        """Test Campaign-Creative relationship."""
        # Create multiple creatives for the campaign
        creative1 = GeneratedCreative(
            campaign_id=sample_campaign.campaign_id,
            variant_number=1,
            channel_type="email_header",
            image_filename="creative_001.png",
            image_url="/static/creatives/creative_001.png",
            prompt_used="Test prompt 1",
            generation_params=json.dumps({"model": "test"}),
            model_used="test-model",
            recommendation_score=80
        )
        creative2 = GeneratedCreative(
            campaign_id=sample_campaign.campaign_id,
            variant_number=2,
            channel_type="email_header",
            image_filename="creative_002.png",
            image_url="/static/creatives/creative_002.png",
            prompt_used="Test prompt 2",
            generation_params=json.dumps({"model": "test"}),
            model_used="test-model",
            recommendation_score=90
        )

        db_session.add_all([creative1, creative2])
        db_session.commit()

        # Refresh campaign to load relationship
        db_session.refresh(sample_campaign)

        assert len(sample_campaign.creatives) == 2
        assert creative1 in sample_campaign.creatives
        assert creative2 in sample_campaign.creatives

    def test_creative_repr(self, db_session, sample_campaign):
        """Test GeneratedCreative __repr__ method."""
        creative = GeneratedCreative(
            campaign_id=sample_campaign.campaign_id,
            variant_number=1,
            channel_type="push_header",
            image_filename="creative_001.png",
            image_url="/static/creatives/creative_001.png",
            prompt_used="Test prompt",
            generation_params=json.dumps({"model": "test"}),
            model_used="test-model",
            recommendation_score=75
        )

        db_session.add(creative)
        db_session.commit()
        db_session.refresh(creative)

        repr_str = repr(creative)
        assert "GeneratedCreative" in repr_str
        assert str(creative.creative_id) in repr_str
        assert str(sample_campaign.campaign_id) in repr_str
        assert "variant=1" in repr_str
        assert "push_header" in repr_str
        assert "score=75" in repr_str


class TestCreativeSchemas:
    """Test creative Pydantic schemas."""

    def test_channel_type_enum(self):
        """Test ChannelType enum values."""
        assert ChannelType.EMAIL_HEADER.value == "email_header"
        assert ChannelType.PUSH_HEADER.value == "push_header"

    def test_creative_generation_request_validation(self):
        """Test CreativeGenerationRequest schema validation."""
        request = CreativeGenerationRequest(
            channel=ChannelType.EMAIL_HEADER,
            visual_concept="Young professionals using 5G in Singapore",
            headline="Experience 5G Speed",
            offer_details="From $35/month",
            partner_logos=["netflix", "spotify"],
            style_preference="modern"
        )

        assert request.channel == ChannelType.EMAIL_HEADER
        assert request.visual_concept == "Young professionals using 5G in Singapore"
        assert request.headline == "Experience 5G Speed"
        assert len(request.partner_logos) == 2

    def test_creative_generation_request_minimal(self):
        """Test CreativeGenerationRequest with minimal required fields."""
        request = CreativeGenerationRequest(
            channel=ChannelType.PUSH_HEADER,
            visual_concept="Mobile plan promotion with vibrant colors"
        )

        assert request.channel == ChannelType.PUSH_HEADER
        assert request.visual_concept == "Mobile plan promotion with vibrant colors"
        assert request.headline is None
        assert request.offer_details is None
        assert request.partner_logos == []

    def test_creative_generation_request_validation_error(self):
        """Test CreativeGenerationRequest validation error for short visual_concept."""
        with pytest.raises(Exception):  # Pydantic ValidationError
            CreativeGenerationRequest(
                channel=ChannelType.EMAIL_HEADER,
                visual_concept="Too short"  # Less than 10 characters
            )

    def test_generated_creative_response(self, db_session, sample_campaign):
        """Test GeneratedCreativeResponse schema."""
        creative = GeneratedCreative(
            campaign_id=sample_campaign.campaign_id,
            variant_number=1,
            channel_type="email_header",
            image_filename="creative_001.png",
            image_url="/static/creatives/creative_001.png",
            prompt_used="Test prompt",
            generation_params=json.dumps({"model": "test", "style": "modern"}),
            model_used="test-model",
            recommendation_score=85,
            score_reasoning="Great visuals",
            is_selected=False
        )

        db_session.add(creative)
        db_session.commit()
        db_session.refresh(creative)

        response = GeneratedCreativeResponse.from_orm_model(creative)

        assert response.creative_id == creative.creative_id
        assert response.campaign_id == sample_campaign.campaign_id
        assert response.variant_number == 1
        assert response.channel_type == ChannelType.EMAIL_HEADER
        assert response.recommendation_score == 85
        assert isinstance(response.generation_params, dict)
        assert response.generation_params["model"] == "test"

    def test_creative_list_response(self):
        """Test CreativeListResponse schema."""
        creatives = [
            GeneratedCreativeResponse(
                creative_id=1,
                campaign_id=1,
                variant_number=1,
                channel_type=ChannelType.EMAIL_HEADER,
                image_filename="creative_001.png",
                image_url="/static/creatives/creative_001.png",
                prompt_used="Test prompt 1",
                generation_params={"model": "test"},
                model_used="test-model",
                recommendation_score=80,
                created_at=datetime.utcnow()
            ),
            GeneratedCreativeResponse(
                creative_id=2,
                campaign_id=1,
                variant_number=2,
                channel_type=ChannelType.EMAIL_HEADER,
                image_filename="creative_002.png",
                image_url="/static/creatives/creative_002.png",
                prompt_used="Test prompt 2",
                generation_params={"model": "test"},
                model_used="test-model",
                recommendation_score=90,
                created_at=datetime.utcnow()
            )
        ]

        response = CreativeListResponse.create(campaign_id=1, creatives=creatives)

        assert response.campaign_id == 1
        assert response.total == 2
        assert len(response.creatives) == 2

    def test_creative_selection_request(self):
        """Test CreativeSelectionRequest schema."""
        request = CreativeSelectionRequest(is_selected=True)
        assert request.is_selected is True

        request = CreativeSelectionRequest(is_selected=False)
        assert request.is_selected is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
