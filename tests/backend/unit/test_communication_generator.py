"""
Unit tests for communication_generator module.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from anthropic import APIError, APITimeoutError

from app.services.communication_generator import CommunicationGenerator
from tests.backend.mock_responses import (
    SMS_PROMOTION_DEAL_SEEKERS,
    EMAIL_RETENTION_HIGH_VALUE,
    PUSH_SPORTS_FANS,
)


class TestCommunicationGenerator:
    """Test the CommunicationGenerator class."""

    @pytest.fixture
    def mock_anthropic_client(self):
        """Create a mock Anthropic client."""
        with patch("app.services.communication_generator.Anthropic") as mock:
            yield mock

    @pytest.fixture
    def generator(self, mock_anthropic_client):
        """Create a generator instance with mocked client."""
        return CommunicationGenerator()

    def test_generator_initialization(self, generator):
        """Test that generator initializes correctly."""
        assert generator is not None
        assert generator.MODEL == "claude-sonnet-4-5-20250929"
        assert generator.MAX_TOKENS == 4096

    def test_validate_inputs_valid(self, generator):
        """Test input validation with valid inputs."""
        # Should not raise
        generator._validate_inputs(
            channel="sms",
            cohorts=["high_value"],
            objective="promotion",
            product_lines=["mobile_postpaid"],
        )

    def test_validate_inputs_invalid_channel(self, generator):
        """Test input validation with invalid channel."""
        with pytest.raises(ValueError, match="Invalid channel"):
            generator._validate_inputs(
                channel="invalid",
                cohorts=["high_value"],
                objective="promotion",
                product_lines=["mobile_postpaid"],
            )

    def test_validate_inputs_empty_cohorts(self, generator):
        """Test input validation with empty cohorts."""
        with pytest.raises(ValueError, match="At least one cohort"):
            generator._validate_inputs(
                channel="sms", cohorts=[], objective="promotion", product_lines=["mobile_postpaid"]
            )

    def test_validate_inputs_empty_objective(self, generator):
        """Test input validation with empty objective."""
        with pytest.raises(ValueError, match="Objective must be specified"):
            generator._validate_inputs(
                channel="sms",
                cohorts=["high_value"],
                objective="",
                product_lines=["mobile_postpaid"],
            )

    def test_validate_inputs_empty_products(self, generator):
        """Test input validation with empty products."""
        with pytest.raises(ValueError, match="At least one product"):
            generator._validate_inputs(
                channel="sms", cohorts=["high_value"], objective="promotion", product_lines=[]
            )

    def test_build_prompt_structure(self, generator):
        """Test that prompt building creates proper structure."""
        prompt = generator._build_prompt(
            channel="sms",
            cohorts=["high_value", "sports_fans"],
            objective="promotion",
            product_lines=["entertainment_sports"],
            promotion_details={"pricing": "$29/mth", "terms": "12-month contract"},
            customization={"tone": "energetic", "required_phrases": ["Premier League"]},
        )

        assert isinstance(prompt, str)
        assert "sms" in prompt.lower()
        assert "promotion" in prompt.lower()
        assert "high_value" in prompt.lower() or "High-Value" in prompt
        assert "sports" in prompt.lower()
        assert "$29/mth" in prompt
        assert "energetic" in prompt.lower()
        assert "Premier League" in prompt
        assert "VARIATION 1" in prompt
        assert "VARIATION 5" in prompt

    def test_build_prompt_with_customization(self, generator):
        """Test prompt building with customization options."""
        prompt = generator._build_prompt(
            channel="email",
            cohorts=["families"],
            objective="upsell",
            product_lines=["bundle_homehub_plus"],
            promotion_details={},
            customization={
                "tone": "warm",
                "required_phrases": ["family", "together"],
                "prohibited_words": ["expensive", "costly"],
                "length_preference": "concise",
            },
        )

        assert "warm" in prompt.lower()
        assert "family" in prompt
        assert "together" in prompt
        assert "expensive" in prompt
        assert "costly" in prompt
        assert "concise" in prompt.lower()

    def test_format_channel_constraints_sms(self, generator):
        """Test SMS channel constraint formatting."""
        from backend.app.services.config_loader import get_channel_constraints

        constraints = get_channel_constraints("sms")
        formatted = generator._format_channel_constraints("sms", constraints)

        assert "160" in formatted
        assert "opt-out" in formatted.lower() or "opt out" in formatted.lower()

    def test_format_channel_constraints_email(self, generator):
        """Test email channel constraint formatting."""
        from backend.app.services.config_loader import get_channel_constraints

        constraints = get_channel_constraints("email")
        formatted = generator._format_channel_constraints("email", constraints)

        assert "subject" in formatted.lower()
        assert "unsubscribe" in formatted.lower()

    def test_format_promotion_details(self, generator):
        """Test promotion details formatting."""
        promotion_details = {
            "pricing": "$49/mth",
            "features": ["10Gbps", "Free installation"],
            "terms": "12-month contract required",
            "validity": "Until Dec 31",
        }

        formatted = generator._format_promotion_details(promotion_details)

        assert "$49/mth" in formatted
        assert "10Gbps" in formatted
        assert "12-month contract" in formatted
        assert "Dec 31" in formatted

    def test_format_promotion_details_empty(self, generator):
        """Test promotion details formatting with empty dict."""
        formatted = generator._format_promotion_details({})
        assert formatted == ""

    def test_parse_variations_standard_format(self, generator):
        """Test parsing variations in standard format."""
        response = SMS_PROMOTION_DEAL_SEEKERS
        variations = generator._parse_variations(response)

        assert len(variations) == 5
        assert all("variation_number" in v for v in variations)
        assert all("text" in v for v in variations)
        assert variations[0]["variation_number"] == 1
        assert variations[4]["variation_number"] == 5

    def test_parse_variations_email_format(self, generator):
        """Test parsing email variations."""
        response = EMAIL_RETENTION_HIGH_VALUE
        variations = generator._parse_variations(response)

        assert len(variations) == 5
        # Check that email structure is preserved
        assert "Subject:" in variations[0]["text"]

    def test_parse_variations_invalid_format(self, generator):
        """Test parsing with invalid format raises error."""
        invalid_response = "This is just some random text without variation markers."

        with pytest.raises(ValueError, match="Could not parse variations"):
            generator._parse_variations(invalid_response)

    def test_call_claude_api_success(self, generator):
        """Test successful Claude API call."""
        # Mock the response
        mock_response = Mock()
        mock_response.content = [Mock(text=SMS_PROMOTION_DEAL_SEEKERS)]
        generator.client.messages.create = Mock(return_value=mock_response)

        result = generator._call_claude_api("Test prompt")

        assert result == SMS_PROMOTION_DEAL_SEEKERS
        generator.client.messages.create.assert_called_once()

    def test_call_claude_api_timeout_retry(self, generator):
        """Test Claude API timeout with retry."""
        # First call times out, second succeeds
        mock_response = Mock()
        mock_response.content = [Mock(text=SMS_PROMOTION_DEAL_SEEKERS)]

        generator.client.messages.create = Mock(
            side_effect=[APITimeoutError("Timeout"), mock_response]
        )

        result = generator._call_claude_api("Test prompt")

        assert result == SMS_PROMOTION_DEAL_SEEKERS
        assert generator.client.messages.create.call_count == 2

    def test_call_claude_api_max_retries_exceeded(self, generator):
        """Test Claude API fails after max retries."""
        generator.client.messages.create = Mock(side_effect=APITimeoutError("Timeout"))

        with pytest.raises(APIError, match="timeout after"):
            generator._call_claude_api("Test prompt")

        assert generator.client.messages.create.call_count == generator.MAX_RETRIES + 1

    def test_generate_variations_success(self, generator):
        """Test successful end-to-end variation generation."""
        # Mock the API response
        mock_response = Mock()
        mock_response.content = [Mock(text=SMS_PROMOTION_DEAL_SEEKERS)]
        generator.client.messages.create = Mock(return_value=mock_response)

        variations = generator.generate_variations(
            channel="sms",
            cohorts=["at_risk_churn"],
            objective="promotion",
            product_lines=["broadband_10gbps"],
            promotion_details={"pricing": "$49/mth"},
            customization={"tone": "urgent"},
        )

        assert len(variations) == 5
        assert all(isinstance(v["text"], str) for v in variations)
        assert all(v["variation_number"] in range(1, 6) for v in variations)

    def test_generate_variations_with_minimal_params(self, generator):
        """Test generation with minimal parameters."""
        mock_response = Mock()
        mock_response.content = [Mock(text=PUSH_SPORTS_FANS)]
        generator.client.messages.create = Mock(return_value=mock_response)

        variations = generator.generate_variations(
            channel="push",
            cohorts=["sports_fans"],
            objective="promotion",
            product_lines=["entertainment_sports"],
        )

        assert len(variations) == 5

    def test_generate_variations_invalid_inputs(self, generator):
        """Test generation with invalid inputs."""
        with pytest.raises(ValueError):
            generator.generate_variations(
                channel="invalid_channel",
                cohorts=["sports_fans"],
                objective="promotion",
                product_lines=["entertainment_sports"],
            )

    def test_generate_variations_api_error(self, generator):
        """Test generation handles API errors."""
        generator.client.messages.create = Mock(side_effect=APIError("API Error"))

        with pytest.raises(APIError):
            generator.generate_variations(
                channel="sms",
                cohorts=["high_value"],
                objective="promotion",
                product_lines=["mobile_postpaid"],
            )


class TestPromptBuilding:
    """Test prompt building in detail."""

    @pytest.fixture
    def generator(self):
        """Create a generator instance."""
        with patch("app.services.communication_generator.Anthropic"):
            return CommunicationGenerator()

    def test_prompt_includes_cohort_info(self, generator):
        """Test that prompt includes cohort information."""
        prompt = generator._build_prompt(
            channel="email",
            cohorts=["high_value", "loyal_customers"],
            objective="retention",
            product_lines=["broadband_10gbps"],
            promotion_details={},
            customization={},
        )

        # Should mention cohorts
        assert "high" in prompt.lower() and "value" in prompt.lower()
        assert "loyal" in prompt.lower()

    def test_prompt_includes_product_info(self, generator):
        """Test that prompt includes product information."""
        prompt = generator._build_prompt(
            channel="sms",
            cohorts=["tech_enthusiasts"],
            objective="promotion",
            product_lines=["broadband_10gbps", "mobile_postpaid"],
            promotion_details={},
            customization={},
        )

        # Should mention products
        assert "10gbps" in prompt.lower() or "broadband" in prompt.lower()
        assert "mobile" in prompt.lower() or "postpaid" in prompt.lower()

    def test_prompt_includes_objective_guidance(self, generator):
        """Test that prompt includes objective guidance."""
        prompt = generator._build_prompt(
            channel="email",
            cohorts=["at_risk_churn"],
            objective="retention",
            product_lines=["broadband_fiber"],
            promotion_details={},
            customization={},
        )

        # Should mention retention objective
        assert "retention" in prompt.lower() or "retain" in prompt.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
