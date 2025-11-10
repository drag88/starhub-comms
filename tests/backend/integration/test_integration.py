"""
Integration tests for the complete generation and scoring workflow.
"""
import pytest
from unittest.mock import Mock, patch

from app.services.generation_service import GenerationService
from tests.mock_responses import (
    SMS_PROMOTION_DEAL_SEEKERS,
    EMAIL_RETENTION_HIGH_VALUE,
    PUSH_SPORTS_FANS,
)


class TestGenerationService:
    """Test the GenerationService integration."""

    @pytest.fixture
    def mock_anthropic_client(self):
        """Create a mock Anthropic client."""
        with patch("app.services.communication_generator.Anthropic") as mock:
            yield mock

    @pytest.fixture
    def service(self, mock_anthropic_client):
        """Create a generation service with mocked API."""
        return GenerationService()

    def test_service_initialization(self, service):
        """Test service initializes with both components."""
        assert service.generator is not None
        assert service.scorer is not None

    def test_generate_and_score_success(self, service):
        """Test end-to-end generation and scoring."""
        # Mock the API response
        mock_response = Mock()
        mock_response.content = [Mock(text=SMS_PROMOTION_DEAL_SEEKERS)]
        service.generator.client.messages.create = Mock(return_value=mock_response)

        results = service.generate_and_score(
            channel="sms",
            cohorts=["at_risk_churn"],
            objective="promotion",
            product_lines=["broadband_10gbps"],
            promotion_details={"pricing": "$49/mth", "terms": "12-month contract"},
            customization={"tone": "urgent"},
            is_promotional=True,
        )

        # Should return 5 scored variations
        assert len(results) == 5

        # Check structure of results
        for result in results:
            assert "variation_number" in result
            assert "text" in result
            assert "total_score" in result
            assert "channel_score" in result
            assert "cohort_score" in result
            assert "objective_score" in result
            assert "compliance_score" in result
            assert "reasoning" in result
            assert "compliance_notes" in result
            assert "rank" in result

    def test_generate_and_score_sorted_by_score(self, service):
        """Test that results are sorted by score descending."""
        mock_response = Mock()
        mock_response.content = [Mock(text=EMAIL_RETENTION_HIGH_VALUE)]
        service.generator.client.messages.create = Mock(return_value=mock_response)

        results = service.generate_and_score(
            channel="email",
            cohorts=["high_value"],
            objective="retention",
            product_lines=["broadband_10gbps"],
            is_promotional=True,
        )

        # Check sorting
        scores = [r["total_score"] for r in results]
        assert scores == sorted(scores, reverse=True)

        # Check ranking
        for i, result in enumerate(results, start=1):
            assert result["rank"] == i

    def test_generate_and_score_ranks_properly(self, service):
        """Test that top-scoring variation gets rank 1."""
        mock_response = Mock()
        mock_response.content = [Mock(text=PUSH_SPORTS_FANS)]
        service.generator.client.messages.create = Mock(return_value=mock_response)

        results = service.generate_and_score(
            channel="push",
            cohorts=["sports_fans"],
            objective="promotion",
            product_lines=["entertainment_sports"],
        )

        # First result should have highest score and rank 1
        assert results[0]["rank"] == 1
        assert results[0]["total_score"] >= results[-1]["total_score"]

    def test_get_top_recommendation(self, service):
        """Test getting only the top recommendation."""
        mock_response = Mock()
        mock_response.content = [Mock(text=SMS_PROMOTION_DEAL_SEEKERS)]
        service.generator.client.messages.create = Mock(return_value=mock_response)

        top = service.get_top_recommendation(
            channel="sms",
            cohorts=["at_risk_churn"],
            objective="promotion",
            product_lines=["broadband_fiber"],
        )

        assert isinstance(top, dict)
        assert top["rank"] == 1
        assert "total_score" in top
        assert "text" in top

    def test_score_existing_text(self, service):
        """Test scoring an existing text."""
        text = "Exclusive VIP offer for valued customers! Upgrade now. Reply STOP to opt out."

        result = service.score_existing_text(
            text=text,
            channel="sms",
            cohorts=["high_value"],
            objective="retention",
            is_promotional=True,
        )

        assert "total_score" in result
        assert "reasoning" in result
        assert result["total_score"] > 0

    def test_batch_score(self, service):
        """Test scoring multiple existing variations."""
        variations = [
            {"text": "Great deal! Sign up now. Reply STOP.", "variation_number": 1},
            {"text": "Exclusive VIP offer for you. Reply STOP.", "variation_number": 2},
            {"text": "Limited time savings! Reply STOP.", "variation_number": 3},
        ]

        results = service.batch_score(
            variations=variations,
            channel="sms",
            cohorts=["high_value"],
            objective="promotion",
            is_promotional=True,
        )

        assert len(results) == 3
        # Should be sorted by score
        scores = [r["total_score"] for r in results]
        assert scores == sorted(scores, reverse=True)


class TestEndToEndScenarios:
    """Test realistic end-to-end scenarios."""

    @pytest.fixture
    def service(self):
        """Create a service with mocked API."""
        with patch("app.services.communication_generator.Anthropic"):
            return GenerationService()

    def test_sms_promotion_deal_seekers(self, service):
        """Test SMS promotion for deal seekers."""
        mock_response = Mock()
        mock_response.content = [Mock(text=SMS_PROMOTION_DEAL_SEEKERS)]
        service.generator.client.messages.create = Mock(return_value=mock_response)

        results = service.generate_and_score(
            channel="sms",
            cohorts=["at_risk_churn"],
            objective="promotion",
            product_lines=["broadband_10gbps"],
            promotion_details={"pricing": "$49/mth", "discount": "$20 off"},
            is_promotional=True,
        )

        # Top recommendation should score well
        top = results[0]
        assert top["total_score"] >= 75  # Should be decent score

        # Should detect urgency and value keywords
        assert top["objective_score"] >= 70

        # Should have good compliance (has opt-out)
        assert top["compliance_score"] >= 85

    def test_email_retention_high_value(self, service):
        """Test email retention for high-value customers."""
        mock_response = Mock()
        mock_response.content = [Mock(text=EMAIL_RETENTION_HIGH_VALUE)]
        service.generator.client.messages.create = Mock(return_value=mock_response)

        results = service.generate_and_score(
            channel="email",
            cohorts=["high_value"],
            objective="retention",
            product_lines=["broadband_10gbps"],
            is_promotional=True,
        )

        # Should have good cohort alignment (premium tone)
        top = results[0]
        assert top["cohort_score"] >= 75

        # Should detect personalization and exclusivity
        assert top["objective_score"] >= 70

    def test_push_sports_fans(self, service):
        """Test push notification for sports fans."""
        mock_response = Mock()
        mock_response.content = [Mock(text=PUSH_SPORTS_FANS)]
        service.generator.client.messages.create = Mock(return_value=mock_response)

        results = service.generate_and_score(
            channel="push",
            cohorts=["sports_fans"],
            objective="promotion",
            product_lines=["entertainment_sports"],
            is_promotional=False,  # Push notifications don't require opt-out
        )

        # Should detect sports keywords
        top = results[0]
        assert top["cohort_score"] >= 75

        # Should have good channel score (proper push format)
        assert top["channel_score"] >= 70

    def test_top_recommendation_makes_sense(self, service):
        """Test that the top recommendation is logically the best."""
        mock_response = Mock()
        mock_response.content = [Mock(text=SMS_PROMOTION_DEAL_SEEKERS)]
        service.generator.client.messages.create = Mock(return_value=mock_response)

        results = service.generate_and_score(
            channel="sms",
            cohorts=["at_risk_churn"],
            objective="promotion",
            product_lines=["broadband_10gbps"],
            is_promotional=True,
        )

        # Top result should have highest total score
        assert results[0]["total_score"] == max(r["total_score"] for r in results)

        # Top result should have rank 1
        assert results[0]["rank"] == 1

        # Reasoning should explain the score
        assert len(results[0]["reasoning"]) > 50
        assert str(results[0]["total_score"]) in results[0]["reasoning"]


class TestErrorHandling:
    """Test error handling in integration."""

    @pytest.fixture
    def service(self):
        """Create a service."""
        with patch("app.services.communication_generator.Anthropic"):
            return GenerationService()

    def test_invalid_channel(self, service):
        """Test handling of invalid channel."""
        with pytest.raises(ValueError, match="Invalid channel"):
            service.generate_and_score(
                channel="invalid",
                cohorts=["high_value"],
                objective="promotion",
                product_lines=["broadband_fiber"],
            )

    def test_empty_cohorts(self, service):
        """Test handling of empty cohorts."""
        with pytest.raises(ValueError, match="cohort"):
            service.generate_and_score(
                channel="sms",
                cohorts=[],
                objective="promotion",
                product_lines=["broadband_fiber"],
            )

    def test_get_top_recommendation_no_variations(self, service):
        """Test top recommendation when no variations generated."""
        # Mock to return empty response
        service.generator.generate_variations = Mock(return_value=[])

        with pytest.raises(ValueError, match="No variations"):
            service.get_top_recommendation(
                channel="sms",
                cohorts=["high_value"],
                objective="promotion",
                product_lines=["broadband_fiber"],
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
