"""
Unit tests for config_loader module.
"""
import pytest
from app.services.config_loader import (
    get_cohorts,
    get_cohort_by_id,
    get_cohort_characteristics,
    get_objectives,
    get_objective_by_id,
    get_objective_guidance,
    get_products,
    get_product_by_id,
    get_channel_constraints,
    get_cohort_keywords,
    get_objective_keywords,
    clear_cache,
)


class TestCohortLoading:
    """Test cohort configuration loading."""

    def test_get_cohorts_returns_dict(self):
        """Test that get_cohorts returns a dictionary."""
        cohorts = get_cohorts()
        assert isinstance(cohorts, dict)
        assert len(cohorts) > 0

    def test_get_cohorts_has_categories(self):
        """Test that cohorts are organized by category."""
        cohorts = get_cohorts()
        expected_categories = ["service_based", "value_based", "demographic", "behavioral"]
        for category in expected_categories:
            assert category in cohorts

    def test_get_cohort_by_id_returns_cohort(self):
        """Test retrieving a specific cohort by ID."""
        cohort = get_cohort_by_id("high_value")
        assert cohort is not None
        assert cohort["id"] == "high_value"
        assert "name" in cohort
        assert "description" in cohort

    def test_get_cohort_by_id_invalid(self):
        """Test retrieving a non-existent cohort."""
        cohort = get_cohort_by_id("nonexistent_cohort")
        assert cohort is None

    def test_get_cohort_characteristics(self):
        """Test getting characteristics for multiple cohorts."""
        cohort_ids = ["high_value", "sports_fans", "families"]
        characteristics = get_cohort_characteristics(cohort_ids)

        assert isinstance(characteristics, dict)
        assert len(characteristics) == 3
        assert "high_value" in characteristics
        assert characteristics["high_value"]["id"] == "high_value"

    def test_get_cohort_characteristics_with_invalid(self):
        """Test getting characteristics with some invalid cohorts."""
        cohort_ids = ["high_value", "invalid_cohort", "sports_fans"]
        characteristics = get_cohort_characteristics(cohort_ids)

        assert len(characteristics) == 2
        assert "high_value" in characteristics
        assert "invalid_cohort" not in characteristics


class TestObjectiveLoading:
    """Test objective configuration loading."""

    def test_get_objectives_returns_list(self):
        """Test that get_objectives returns a list."""
        objectives = get_objectives()
        assert isinstance(objectives, list)
        assert len(objectives) > 0

    def test_get_objective_by_id(self):
        """Test retrieving a specific objective."""
        objective = get_objective_by_id("promotion")
        assert objective is not None
        assert objective["id"] == "promotion"
        assert "name" in objective
        assert "description" in objective

    def test_get_objective_guidance(self):
        """Test getting objective guidance."""
        guidance = get_objective_guidance("retention")
        assert isinstance(guidance, dict)
        assert "name" in guidance
        assert "description" in guidance
        assert "typical_channels" in guidance

    def test_get_objective_guidance_invalid(self):
        """Test getting guidance for invalid objective."""
        guidance = get_objective_guidance("invalid_objective")
        assert guidance == {}


class TestProductLoading:
    """Test product configuration loading."""

    def test_get_products_returns_dict(self):
        """Test that get_products returns a dictionary."""
        products = get_products()
        assert isinstance(products, dict)
        assert len(products) > 0

    def test_get_product_by_id(self):
        """Test retrieving a specific product."""
        product = get_product_by_id("mobile_postpaid")
        assert product is not None
        assert product["id"] == "mobile_postpaid"
        assert "name" in product
        assert "category" in product

    def test_get_product_by_id_invalid(self):
        """Test retrieving invalid product."""
        product = get_product_by_id("nonexistent_product")
        assert product is None


class TestChannelConstraints:
    """Test channel constraint loading."""

    def test_get_channel_constraints_sms(self):
        """Test SMS channel constraints."""
        constraints = get_channel_constraints("sms")
        assert isinstance(constraints, dict)
        assert "max_length" in constraints
        assert constraints["max_length"] == 160
        assert "requires_opt_out" in constraints

    def test_get_channel_constraints_email(self):
        """Test email channel constraints."""
        constraints = get_channel_constraints("email")
        assert isinstance(constraints, dict)
        assert "subject_min" in constraints
        assert "subject_max" in constraints
        assert "requires_unsubscribe" in constraints

    def test_get_channel_constraints_push(self):
        """Test push notification constraints."""
        constraints = get_channel_constraints("push")
        assert isinstance(constraints, dict)
        assert "title_min" in constraints
        assert "title_max" in constraints
        assert "supports_emojis" in constraints

    def test_get_channel_constraints_invalid(self):
        """Test invalid channel."""
        constraints = get_channel_constraints("invalid_channel")
        assert constraints == {}


class TestKeywordMappings:
    """Test keyword mappings for scoring."""

    def test_get_cohort_keywords_high_value(self):
        """Test high-value cohort keywords."""
        keywords = get_cohort_keywords("high_value")
        assert isinstance(keywords, dict)
        assert "positive" in keywords
        assert "negative" in keywords
        assert "exclusive" in keywords["positive"]
        assert "cheap" in keywords["negative"]

    def test_get_cohort_keywords_sports_fans(self):
        """Test sports fans keywords."""
        keywords = get_cohort_keywords("sports_fans")
        assert "sports" in keywords["positive"]
        assert "match" in keywords["positive"]

    def test_get_cohort_keywords_unknown(self):
        """Test unknown cohort returns empty lists."""
        keywords = get_cohort_keywords("unknown_cohort")
        assert keywords == {"positive": [], "negative": []}

    def test_get_objective_keywords_promotion(self):
        """Test promotion objective keywords."""
        keywords = get_objective_keywords("promotion")
        assert isinstance(keywords, dict)
        assert "urgency" in keywords
        assert "value" in keywords
        assert "limited" in keywords["urgency"]

    def test_get_objective_keywords_retention(self):
        """Test retention objective keywords."""
        keywords = get_objective_keywords("retention")
        assert "personalization" in keywords
        assert "exclusive" in keywords
        assert "you" in keywords["personalization"]

    def test_get_objective_keywords_unknown(self):
        """Test unknown objective returns empty dict."""
        keywords = get_objective_keywords("unknown_objective")
        assert keywords == {}


class TestCaching:
    """Test configuration caching."""

    def test_cache_clear(self):
        """Test cache clearing."""
        # Load some config to populate cache
        get_cohorts()
        get_objectives()

        # Clear cache
        clear_cache()

        # Should still work after clearing
        cohorts = get_cohorts()
        assert isinstance(cohorts, dict)
        assert len(cohorts) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
