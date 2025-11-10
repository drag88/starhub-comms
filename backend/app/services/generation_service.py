"""
Integration service combining communication generation and scoring.

This service orchestrates the end-to-end process of generating
communication variations and scoring them for recommendations.
"""
from typing import Dict, List, Any, Optional
import logging

from app.services.communication_generator import CommunicationGenerator
from app.services.recommendation_scorer import RecommendationScorer

logger = logging.getLogger(__name__)


class GenerationService:
    """
    Orchestrates communication generation and scoring.

    This service combines the CommunicationGenerator and RecommendationScorer
    to provide a complete workflow: generate variations, score each one,
    and return ranked recommendations.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the generation service.

        Args:
            api_key: Anthropic API key (optional, will use env var if not provided)
        """
        self.generator = CommunicationGenerator(api_key=api_key)
        self.scorer = RecommendationScorer()
        self.logger = logging.getLogger(self.__class__.__name__)

    def generate_and_score(
        self,
        channel: str,
        cohorts: List[str],
        objective: str,
        product_lines: List[str],
        promotion_details: Optional[Dict[str, Any]] = None,
        customization: Optional[Dict[str, Any]] = None,
        is_promotional: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Generate and score communication variations.

        This is the main entry point for the service. It:
        1. Generates 5 variations using Claude AI
        2. Scores each variation using the 4-pillar algorithm
        3. Sorts variations by score (descending)
        4. Returns ranked variations with full scoring details

        Args:
            channel: Communication channel (sms, email, push)
            cohorts: List of target cohort IDs
            objective: Campaign objective
            product_lines: List of product line IDs
            promotion_details: Optional promotion information
            customization: Optional customization parameters
            is_promotional: Whether this is a promotional message (for compliance)

        Returns:
            List of variation dictionaries, sorted by score (highest first).
            Each dictionary contains:
                - variation_number: Original variation number (1-5)
                - text: Communication text
                - total_score: Overall recommendation score
                - channel_score: Channel best practices score
                - cohort_score: Cohort alignment score
                - objective_score: Objective effectiveness score
                - compliance_score: Compliance safety score
                - reasoning: Natural language explanation
                - compliance_notes: List of compliance issues/notes
                - score_breakdown: Detailed scoring breakdown
                - rank: Final ranking position (1-5)

        Raises:
            ValueError: If parameters are invalid
            APIError: If Claude API fails
        """
        self.logger.info(
            f"Starting generation and scoring for {channel}/{objective} "
            f"targeting cohorts: {', '.join(cohorts)}"
        )

        # Step 1: Generate variations
        try:
            variations = self.generator.generate_variations(
                channel=channel,
                cohorts=cohorts,
                objective=objective,
                product_lines=product_lines,
                promotion_details=promotion_details,
                customization=customization,
            )
            self.logger.info(f"Generated {len(variations)} variations")
        except Exception as e:
            self.logger.error(f"Failed to generate variations: {e}")
            raise

        # Step 2: Score each variation
        scored_variations = []
        for variation in variations:
            try:
                score_result = self.scorer.score_communication(
                    text=variation["text"],
                    channel=channel,
                    cohorts=cohorts,
                    objective=objective,
                    is_promotional=is_promotional,
                )

                # Combine variation and score data
                scored_variation = {
                    "variation_number": variation["variation_number"],
                    "text": variation["text"],
                    "total_score": score_result["total_score"],
                    "channel_score": score_result["channel_score"],
                    "cohort_score": score_result["cohort_score"],
                    "objective_score": score_result["objective_score"],
                    "compliance_score": score_result["compliance_score"],
                    "reasoning": score_result["reasoning"],
                    "compliance_notes": score_result["compliance_notes"],
                    "score_breakdown": score_result["score_breakdown"],
                }

                scored_variations.append(scored_variation)

                self.logger.info(
                    f"Scored variation {variation['variation_number']}: {score_result['total_score']}/100"
                )

            except Exception as e:
                self.logger.error(f"Failed to score variation {variation['variation_number']}: {e}")
                # Continue with other variations even if one fails
                continue

        # Step 3: Sort by total score (descending)
        scored_variations.sort(key=lambda x: x["total_score"], reverse=True)

        # Step 4: Add ranking
        for rank, variation in enumerate(scored_variations, start=1):
            variation["rank"] = rank

        self.logger.info(
            f"Completed generation and scoring. Top score: {scored_variations[0]['total_score'] if scored_variations else 'N/A'}"
        )

        return scored_variations

    def get_top_recommendation(
        self,
        channel: str,
        cohorts: List[str],
        objective: str,
        product_lines: List[str],
        promotion_details: Optional[Dict[str, Any]] = None,
        customization: Optional[Dict[str, Any]] = None,
        is_promotional: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate variations and return only the top recommendation.

        This is a convenience method for when you only need the best variation.

        Args:
            Same as generate_and_score()

        Returns:
            Single variation dictionary (the highest-scoring one)

        Raises:
            ValueError: If no variations could be generated or scored
        """
        variations = self.generate_and_score(
            channel=channel,
            cohorts=cohorts,
            objective=objective,
            product_lines=product_lines,
            promotion_details=promotion_details,
            customization=customization,
            is_promotional=is_promotional,
        )

        if not variations:
            raise ValueError("No variations could be generated or scored")

        return variations[0]

    def regenerate_and_score(
        self,
        channel: str,
        cohorts: List[str],
        objective: str,
        product_lines: List[str],
        exclude_texts: List[str],
        promotion_details: Optional[Dict[str, Any]] = None,
        customization: Optional[Dict[str, Any]] = None,
        is_promotional: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Regenerate variations, excluding similar ones.

        This method is useful for getting fresh variations when the user
        wants to see different options.

        Args:
            Same as generate_and_score(), plus:
            exclude_texts: List of texts to avoid (previous variations)

        Returns:
            List of scored variations (sorted by score)

        Note:
            This method adds excluded texts to the customization to guide
            the generation toward different content.
        """
        # Add exclusions to customization
        if customization is None:
            customization = {}

        if "prohibited_phrases" not in customization:
            customization["prohibited_phrases"] = []

        # Extract key phrases from excluded texts (simple approach)
        for text in exclude_texts:
            # Take first 50 characters as a key phrase identifier
            key_phrase = text[:50].strip()
            if key_phrase:
                customization["prohibited_phrases"].append(key_phrase)

        # Add instruction to be different
        if "additional_instructions" not in customization:
            customization["additional_instructions"] = ""

        customization["additional_instructions"] += (
            " Generate completely different creative approaches from previous attempts."
        )

        return self.generate_and_score(
            channel=channel,
            cohorts=cohorts,
            objective=objective,
            product_lines=product_lines,
            promotion_details=promotion_details,
            customization=customization,
            is_promotional=is_promotional,
        )

    def score_existing_text(
        self,
        text: str,
        channel: str,
        cohorts: List[str],
        objective: str,
        is_promotional: bool = True,
    ) -> Dict[str, Any]:
        """
        Score an existing communication text.

        This method allows scoring user-edited or externally-created communications.

        Args:
            text: The communication text to score
            channel: Communication channel
            cohorts: Target cohorts
            objective: Campaign objective
            is_promotional: Whether this is promotional

        Returns:
            Scoring result dictionary
        """
        return self.scorer.score_communication(
            text=text,
            channel=channel,
            cohorts=cohorts,
            objective=objective,
            is_promotional=is_promotional,
        )

    def batch_score(
        self,
        variations: List[Dict[str, str]],
        channel: str,
        cohorts: List[str],
        objective: str,
        is_promotional: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Score multiple existing variations in batch.

        Args:
            variations: List of dicts with 'text' and optional 'variation_number'
            channel: Communication channel
            cohorts: Target cohorts
            objective: Campaign objective
            is_promotional: Whether these are promotional

        Returns:
            List of scored variations (sorted by score)
        """
        scored_variations = []

        for idx, variation in enumerate(variations, start=1):
            text = variation.get("text", "")
            variation_number = variation.get("variation_number", idx)

            try:
                score_result = self.scorer.score_communication(
                    text=text,
                    channel=channel,
                    cohorts=cohorts,
                    objective=objective,
                    is_promotional=is_promotional,
                )

                scored_variation = {
                    "variation_number": variation_number,
                    "text": text,
                    "total_score": score_result["total_score"],
                    "channel_score": score_result["channel_score"],
                    "cohort_score": score_result["cohort_score"],
                    "objective_score": score_result["objective_score"],
                    "compliance_score": score_result["compliance_score"],
                    "reasoning": score_result["reasoning"],
                    "compliance_notes": score_result["compliance_notes"],
                    "score_breakdown": score_result["score_breakdown"],
                }

                scored_variations.append(scored_variation)

            except Exception as e:
                self.logger.error(f"Failed to score variation {variation_number}: {e}")
                continue

        # Sort by score
        scored_variations.sort(key=lambda x: x["total_score"], reverse=True)

        # Add ranking
        for rank, variation in enumerate(scored_variations, start=1):
            variation["rank"] = rank

        return scored_variations
