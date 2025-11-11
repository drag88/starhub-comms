"""
Test runner for demonstrating generation and scoring workflow without API calls.

This script demonstrates the complete workflow using mock data, allowing
validation of the scoring algorithm without requiring API credentials.
"""

import sys
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.mock_responses import (
    EMAIL_RETENTION_HIGH_VALUE,
    PUSH_SPORTS_FANS,
    SCORING_TEST_CASES,
    SMS_PROMOTION_DEAL_SEEKERS,
)

from app.services.recommendation_scorer import RecommendationScorer


def print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_variation(variation_num: int, text: str, score_result: dict[str, Any]) -> None:
    """Print a variation with its score."""
    print(f"\n--- VARIATION {variation_num} ---")
    print(f"Text: {text[:100]}..." if len(text) > 100 else f"Text: {text}")
    print("\nScores:")
    print(f"  Total Score:      {score_result['total_score']}/100")
    print(f"  Channel Score:    {score_result['channel_score']}/100")
    print(f"  Cohort Score:     {score_result['cohort_score']}/100")
    print(f"  Objective Score:  {score_result['objective_score']}/100")
    print(f"  Compliance Score: {score_result['compliance_score']}/100")
    print("\nReasoning:")
    print(f"  {score_result['reasoning']}")
    print("\nCompliance Notes:")
    for note in score_result["compliance_notes"]:
        print(f"  - {note}")


def parse_mock_variations(mock_text: str) -> list:
    """Parse variations from mock response text."""
    import re

    variations = []
    pattern = r"VARIATION\s+(\d+):\s*(.+?)(?=VARIATION\s+\d+:|$)"
    matches = re.findall(pattern, mock_text, re.DOTALL | re.IGNORECASE)

    for variation_num, variation_text in matches:
        variations.append({"number": int(variation_num), "text": variation_text.strip()})

    return variations


def test_scenario_1():
    """Test Scenario 1: SMS Promotion for Deal Seekers."""
    print_header("Scenario 1: SMS Promotion for Deal Seekers")

    scorer = RecommendationScorer()
    variations = parse_mock_variations(SMS_PROMOTION_DEAL_SEEKERS)

    print("\nChannel: SMS")
    print("Cohorts: At-Risk Churn, Deal Seekers")
    print("Objective: Promotion")
    print("Product: 10Gbps Fiber Broadband")
    print(f"\nGenerated {len(variations)} variations. Scoring each...\n")

    scored_variations = []
    for var in variations:
        score_result = scorer.score_communication(
            text=var["text"],
            channel="sms",
            cohorts=["at_risk_churn"],
            objective="promotion",
            is_promotional=True,
        )
        scored_variations.append(
            {
                "variation_number": var["number"],
                "text": var["text"],
                "score": score_result["total_score"],
                "result": score_result,
            }
        )

    # Sort by score
    scored_variations.sort(key=lambda x: x["score"], reverse=True)

    # Print top 3
    print("\nTOP 3 RECOMMENDATIONS:")
    for i, var in enumerate(scored_variations[:3], start=1):
        print(f"\n{'#' * 80}")
        print(f"  RANK {i} (Score: {var['score']}/100)")
        print(f"{'#' * 80}")
        print_variation(var["variation_number"], var["text"], var["result"])


def test_scenario_2():
    """Test Scenario 2: Email Retention for High-Value Customers."""
    print_header("Scenario 2: Email Retention for High-Value Customers")

    scorer = RecommendationScorer()
    variations = parse_mock_variations(EMAIL_RETENTION_HIGH_VALUE)

    print("\nChannel: Email")
    print("Cohorts: High-Value Customers")
    print("Objective: Retention")
    print("Product: Premium 10Gbps Plan")
    print(f"\nGenerated {len(variations)} variations. Scoring each...\n")

    scored_variations = []
    for var in variations:
        score_result = scorer.score_communication(
            text=var["text"],
            channel="email",
            cohorts=["high_value"],
            objective="retention",
            is_promotional=True,
        )
        scored_variations.append(
            {
                "variation_number": var["number"],
                "text": var["text"],
                "score": score_result["total_score"],
                "result": score_result,
            }
        )

    # Sort by score
    scored_variations.sort(key=lambda x: x["score"], reverse=True)

    # Print top recommendation
    print("\nTOP RECOMMENDATION:")
    var = scored_variations[0]
    print(f"\n{'#' * 80}")
    print(f"  RANK 1 (Score: {var['score']}/100)")
    print(f"{'#' * 80}")
    print_variation(var["variation_number"], var["text"], var["result"])


def test_scenario_3():
    """Test Scenario 3: Push Notification for Sports Fans."""
    print_header("Scenario 3: Push Notification for Sports Fans")

    scorer = RecommendationScorer()
    variations = parse_mock_variations(PUSH_SPORTS_FANS)

    print("\nChannel: Push Notification")
    print("Cohorts: Sports Fans")
    print("Objective: Promotion")
    print("Product: Sports+ Subscription")
    print(f"\nGenerated {len(variations)} variations. Scoring each...\n")

    scored_variations = []
    for var in variations:
        score_result = scorer.score_communication(
            text=var["text"],
            channel="push",
            cohorts=["sports_fans"],
            objective="promotion",
            is_promotional=False,  # Push doesn't require opt-out
        )
        scored_variations.append(
            {
                "variation_number": var["number"],
                "text": var["text"],
                "score": score_result["total_score"],
                "result": score_result,
            }
        )

    # Sort by score
    scored_variations.sort(key=lambda x: x["score"], reverse=True)

    # Print all scores
    print("\nALL VARIATIONS RANKED:")
    for i, var in enumerate(scored_variations, start=1):
        print(f"\nRank {i}: Variation {var['variation_number']} - Score: {var['score']}/100")
        print(f"  Text: {var['text'][:80]}...")


def test_compliance_validation():
    """Test compliance validation with edge cases."""
    print_header("Compliance Validation Tests")

    scorer = RecommendationScorer()

    print("\nTesting various compliance scenarios:\n")

    test_cases = [
        {
            "name": "Perfect SMS with opt-out",
            "text": "Save $20/mth on fiber! From $49/mth. T&Cs apply. Reply STOP to opt out.",
            "channel": "sms",
            "cohorts": ["deal_seekers"],
            "objective": "promotion",
            "expected": "High compliance score (90+)",
        },
        {
            "name": "SMS missing opt-out (CRITICAL)",
            "text": "Amazing deal on fiber broadband! Sign up at starhub.com now!",
            "channel": "sms",
            "cohorts": ["deal_seekers"],
            "objective": "promotion",
            "expected": "Critical compliance failure (<70)",
        },
        {
            "name": "Email missing unsubscribe",
            "text": "Subject: Great Offer\nCheck out our fiber broadband deals today!",
            "channel": "email",
            "cohorts": ["high_value"],
            "objective": "promotion",
            "expected": "Compliance warning (<80)",
        },
        {
            "name": "Unsubstantiated claims",
            "text": "BEST deal! 100% guaranteed fastest internet ever! Reply STOP.",
            "channel": "sms",
            "cohorts": ["deal_seekers"],
            "objective": "promotion",
            "expected": "Compliance issues flagged",
        },
        {
            "name": "Pricing without T&Cs",
            "text": "Get fiber for just $49! Sign up now. Reply STOP to opt out.",
            "channel": "sms",
            "cohorts": ["deal_seekers"],
            "objective": "promotion",
            "expected": "Pricing disclosure warning",
        },
    ]

    for test in test_cases:
        print(f"\nTest: {test['name']}")
        print(f"Expected: {test['expected']}")

        result = scorer.score_communication(
            text=test["text"],
            channel=test["channel"],
            cohorts=test["cohorts"],
            objective=test["objective"],
            is_promotional=True,
        )

        print(f"Compliance Score: {result['compliance_score']}/100")
        print("Compliance Notes:")
        for note in result["compliance_notes"]:
            print(f"  - {note}")

        # Validation
        if "High compliance" in test["expected"]:
            assert result["compliance_score"] >= 90, f"Failed: {test['name']}"
            print("  ✓ PASS")
        elif "Critical" in test["expected"]:
            assert result["compliance_score"] < 70, f"Failed: {test['name']}"
            assert any("CRITICAL" in note for note in result["compliance_notes"])
            print("  ✓ PASS (Critical issue detected)")
        elif "Pricing disclosure" in test["expected"]:
            # Check for pricing disclosure warning in compliance notes (check this before "warning" to avoid substring match)
            assert any(
                "pricing" in note.lower() or "t&cs" in note.lower() or "terms" in note.lower()
                for note in result["compliance_notes"]
            ), f"Failed: {test['name']}"
            print("  ✓ PASS (Pricing disclosure warning detected)")
        elif "warning" in test["expected"]:
            assert result["compliance_score"] < 80, f"Failed: {test['name']}"
            print("  ✓ PASS (Warning detected)")
        elif "issues flagged" in test["expected"]:
            assert any(
                "REVIEW" in note or "unsubstantiated" in note.lower()
                for note in result["compliance_notes"]
            )
            print("  ✓ PASS (Issues flagged)")


def test_scoring_algorithm_validation():
    """Test scoring algorithm with predefined test cases."""
    print_header("Scoring Algorithm Validation")

    scorer = RecommendationScorer()

    print("\nRunning predefined test cases...\n")

    passed = 0
    failed = 0

    for test_case in SCORING_TEST_CASES:
        print(f"\nTest: {test_case['name']}")

        result = scorer.score_communication(
            text=test_case["text"],
            channel=test_case["channel"],
            cohorts=test_case["cohorts"],
            objective=test_case["objective"],
            is_promotional=test_case["is_promotional"],
        )

        print(f"  Score: {result['total_score']}/100")

        # Validate expectations
        if "expected_min_score" in test_case:
            if result["total_score"] >= test_case["expected_min_score"]:
                print(f"  ✓ PASS (score >= {test_case['expected_min_score']})")
                passed += 1
            else:
                print(f"  ✗ FAIL (score < {test_case['expected_min_score']})")
                failed += 1

        if "expected_max_score" in test_case:
            if result["total_score"] <= test_case["expected_max_score"]:
                print(f"  ✓ PASS (score <= {test_case['expected_max_score']})")
                passed += 1
            else:
                print(f"  ✗ FAIL (score > {test_case['expected_max_score']})")
                failed += 1

    print(f"\n\nValidation Results: {passed} passed, {failed} failed")


def main():
    """Run all test scenarios."""
    print("\n")
    print("=" * 80)
    print("  StarHub Customer Communications Generator - Test Runner")
    print("  Phase 2: Generation and Scoring Services")
    print("=" * 80)

    try:
        # Run scenarios
        test_scenario_1()
        test_scenario_2()
        test_scenario_3()
        test_compliance_validation()
        test_scoring_algorithm_validation()

        print("\n" + "=" * 80)
        print("  All tests completed successfully!")
        print("=" * 80 + "\n")

    except AssertionError as e:
        print(f"\n\n✗ TEST FAILED: {e}\n")
        return 1
    except Exception as e:
        print(f"\n\n✗ ERROR: {e}\n")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
