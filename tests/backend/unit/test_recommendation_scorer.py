"""
Unit tests for recommendation_scorer module.
"""
import pytest
from app.services.recommendation_scorer import RecommendationScorer
from tests.mock_responses import SCORING_TEST_CASES


class TestRecommendationScorer:
    """Test the RecommendationScorer class."""

    @pytest.fixture
    def scorer(self):
        """Create a scorer instance for testing."""
        return RecommendationScorer()

    def test_scorer_initialization(self, scorer):
        """Test that scorer initializes correctly."""
        assert scorer is not None
        assert scorer.CHANNEL_WEIGHT == 0.30
        assert scorer.COHORT_WEIGHT == 0.30
        assert scorer.OBJECTIVE_WEIGHT == 0.25
        assert scorer.COMPLIANCE_WEIGHT == 0.15

    def test_score_communication_returns_dict(self, scorer):
        """Test that score_communication returns proper structure."""
        result = scorer.score_communication(
            text="Test SMS message with Reply STOP to opt out.",
            channel="sms",
            cohorts=["high_value"],
            objective="promotion",
            is_promotional=True,
        )

        assert isinstance(result, dict)
        assert "total_score" in result
        assert "channel_score" in result
        assert "cohort_score" in result
        assert "objective_score" in result
        assert "compliance_score" in result
        assert "reasoning" in result
        assert "compliance_notes" in result

    def test_sms_optimal_length_scoring(self, scorer):
        """Test SMS scoring for optimal length."""
        # Optimal length (140-160 chars) - Create text that totals ~150 chars
        opt_out = " Reply STOP to opt out"  # 23 chars
        optimal_text = "X" * (150 - len(opt_out)) + opt_out  # Total 150 chars
        result = scorer.score_communication(
            text=optimal_text, channel="sms", cohorts=["high_value"], objective="promotion"
        )
        assert result["channel_score"] >= 90

    def test_sms_over_length_penalty(self, scorer):
        """Test SMS scoring penalizes over 160 characters."""
        # Over 160 characters
        long_text = "X" * 170
        result = scorer.score_communication(
            text=long_text, channel="sms", cohorts=["high_value"], objective="promotion"
        )
        assert result["channel_score"] <= 50  # Should have major penalty

    def test_sms_missing_opt_out(self, scorer):
        """Test SMS compliance scoring for missing opt-out."""
        text = "Great deal on fiber broadband! Sign up today."
        result = scorer.score_communication(
            text=text,
            channel="sms",
            cohorts=["deal_seekers"],
            objective="promotion",
            is_promotional=True,
        )

        # Should have compliance penalty
        assert result["compliance_score"] <= 60
        assert any("opt" in note.lower() for note in result["compliance_notes"])

    def test_sms_with_opt_out(self, scorer):
        """Test SMS compliance scoring with opt-out."""
        text = "Great deal on fiber! Sign up today. Reply STOP to opt out."
        result = scorer.score_communication(
            text=text,
            channel="sms",
            cohorts=["deal_seekers"],
            objective="promotion",
            is_promotional=True,
        )

        # Should have good compliance score
        assert result["compliance_score"] >= 90

    def test_email_subject_length_scoring(self, scorer):
        """Test email subject line length scoring."""
        # Optimal subject length (40-60 chars)
        email_optimal = "Subject: This is an optimal subject line length\nBody text here. Unsubscribe here."
        result = scorer.score_communication(
            text=email_optimal,
            channel="email",
            cohorts=["high_value"],
            objective="promotion",
            is_promotional=True,
        )
        assert result["channel_score"] >= 85

    def test_email_missing_unsubscribe(self, scorer):
        """Test email compliance without unsubscribe."""
        email_text = "Subject: Great Offer\nCheck out our amazing deal on fiber!"
        result = scorer.score_communication(
            text=email_text,
            channel="email",
            cohorts=["deal_seekers"],
            objective="promotion",
            is_promotional=True,
        )

        assert result["compliance_score"] <= 70
        assert any("unsubscribe" in note.lower() for note in result["compliance_notes"])

    def test_push_notification_scoring(self, scorer):
        """Test push notification scoring."""
        push_text = "Title: Get 10Gbps Fiber Today!\nUltra-fast internet from $49/mth. Limited time offer - upgrade now!"
        result = scorer.score_communication(
            text=push_text, channel="push", cohorts=["tech_enthusiasts"], objective="promotion"
        )

        assert result["total_score"] > 0
        assert result["channel_score"] > 0

    def test_cohort_alignment_high_value(self, scorer):
        """Test cohort alignment scoring for high-value customers."""
        text = "Exclusive VIP offer for our most valued customers. Premium service awaits. Reply STOP to opt out."
        result = scorer.score_communication(
            text=text, channel="sms", cohorts=["high_value"], objective="retention"
        )

        # Should have high cohort score due to premium keywords
        assert result["cohort_score"] >= 80

    def test_cohort_alignment_deal_seekers(self, scorer):
        """Test cohort alignment for deal seekers."""
        text = "Save $20/mth! Limited time deal - act now! From just $49/mth. Reply STOP to opt out."
        result = scorer.score_communication(
            text=text, channel="sms", cohorts=["at_risk_churn"], objective="promotion"
        )

        # Should have good cohort score due to savings/urgency keywords
        assert result["cohort_score"] >= 75

    def test_cohort_alignment_sports_fans(self, scorer):
        """Test cohort alignment for sports fans."""
        text = "Watch every Premier League match live! Cricket, F1, and more. Subscribe to Sports+ now!"
        result = scorer.score_communication(
            text=text, channel="push", cohorts=["sports_fans"], objective="promotion"
        )

        # Should detect sports keywords
        assert result["cohort_score"] >= 80

    def test_objective_promotion_scoring(self, scorer):
        """Test objective effectiveness for promotions."""
        text = "Limited time offer! Save $20/mth on fiber. Sign up today - expires soon! Reply STOP."
        result = scorer.score_communication(
            text=text, channel="sms", cohorts=["deal_seekers"], objective="promotion"
        )

        # Should have high objective score (urgency + value + CTA)
        assert result["objective_score"] >= 80

    def test_objective_retention_scoring(self, scorer):
        """Test objective effectiveness for retention."""
        text = "Subject: Thank you for your loyalty\nAs a valued customer, you deserve exclusive access. Unsubscribe."
        result = scorer.score_communication(
            text=text, channel="email", cohorts=["loyal_customers"], objective="retention"
        )

        # Should detect personalization and appreciation
        assert result["objective_score"] >= 70

    def test_objective_missing_cta(self, scorer):
        """Test objective scoring when CTA is missing."""
        text = "We have a new fiber plan available with great speeds and pricing."
        result = scorer.score_communication(
            text=text, channel="sms", cohorts=["high_value"], objective="promotion"
        )

        # Should penalize missing CTA
        assert result["objective_score"] <= 65

    def test_compliance_unsubstantiated_claims(self, scorer):
        """Test compliance scoring with unsubstantiated claims."""
        text = "BEST deal ever! 100% guaranteed fastest internet! Never experience slowness!"
        result = scorer.score_communication(
            text=text, channel="sms", cohorts=["deal_seekers"], objective="promotion"
        )

        # Should flag risky words
        assert result["compliance_score"] <= 85
        assert any("unsubstantiated" in note.lower() or "review" in note.lower()
                   for note in result["compliance_notes"])

    def test_compliance_pricing_without_terms(self, scorer):
        """Test compliance when pricing mentioned without T&Cs."""
        text = "Get fiber for just $49! Sign up now at starhub.com"
        result = scorer.score_communication(
            text=text, channel="sms", cohorts=["deal_seekers"], objective="promotion"
        )

        # Should flag missing terms
        compliance_notes_lower = " ".join(result["compliance_notes"]).lower()
        assert "pricing" in compliance_notes_lower or "terms" in compliance_notes_lower

    def test_compliance_free_without_terms(self, scorer):
        """Test compliance for free offers without T&Cs."""
        text = "Get free installation when you sign up! Visit starhub.com now."
        result = scorer.score_communication(
            text=text, channel="sms", cohorts=["new_customers"], objective="promotion"
        )

        # Should flag free without T&Cs
        compliance_notes_lower = " ".join(result["compliance_notes"]).lower()
        assert "free" in compliance_notes_lower or "t&c" in compliance_notes_lower

    def test_weighted_score_calculation(self, scorer):
        """Test that weighted scoring is calculated correctly."""
        text = "Great offer! Sign up for fiber broadband. Reply STOP to opt out."
        result = scorer.score_communication(
            text=text, channel="sms", cohorts=["deal_seekers"], objective="promotion"
        )

        # Calculate expected weighted score
        expected = round(
            result["channel_score"] * 0.30
            + result["cohort_score"] * 0.30
            + result["objective_score"] * 0.25
            + result["compliance_score"] * 0.15
        )

        assert result["total_score"] == expected

    def test_reasoning_generation(self, scorer):
        """Test that reasoning is generated."""
        text = "Exclusive VIP offer with premium benefits. Sign up today! Reply STOP to opt out."
        result = scorer.score_communication(
            text=text, channel="sms", cohorts=["high_value"], objective="retention"
        )

        assert isinstance(result["reasoning"], str)
        assert len(result["reasoning"]) > 50
        assert "Objective:" in result["reasoning"] or "objective" in result["reasoning"].lower()
        assert str(result["total_score"]) in result["reasoning"]

    def test_score_breakdown_structure(self, scorer):
        """Test that score breakdown has proper structure."""
        text = "Test message. Reply STOP."
        result = scorer.score_communication(
            text=text, channel="sms", cohorts=["high_value"], objective="promotion"
        )

        assert "score_breakdown" in result
        breakdown = result["score_breakdown"]
        assert "channel" in breakdown
        assert "cohort" in breakdown
        assert "objective" in breakdown


class TestScoringTestCases:
    """Test using predefined test cases."""

    @pytest.fixture
    def scorer(self):
        """Create a scorer instance."""
        return RecommendationScorer()

    @pytest.mark.parametrize("test_case", SCORING_TEST_CASES)
    def test_scoring_cases(self, scorer, test_case):
        """Test scoring with predefined test cases."""
        result = scorer.score_communication(
            text=test_case["text"],
            channel=test_case["channel"],
            cohorts=test_case["cohorts"],
            objective=test_case["objective"],
            is_promotional=test_case["is_promotional"],
        )

        # Check minimum score if specified
        if "expected_min_score" in test_case:
            assert (
                result["total_score"] >= test_case["expected_min_score"]
            ), f"Score {result['total_score']} below minimum {test_case['expected_min_score']} for {test_case['name']}"

        # Check maximum score if specified
        if "expected_max_score" in test_case:
            assert (
                result["total_score"] <= test_case["expected_max_score"]
            ), f"Score {result['total_score']} above maximum {test_case['expected_max_score']} for {test_case['name']}"

        # Check for critical compliance issues
        if test_case.get("expected_compliance_critical"):
            compliance_text = " ".join(result["compliance_notes"]).lower()
            assert "critical" in compliance_text or result["compliance_score"] < 70


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
