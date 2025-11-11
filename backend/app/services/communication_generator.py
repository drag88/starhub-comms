"""
Communication generation service using Claude AI.

This service constructs prompts and invokes Claude AI to generate
customer communication variations for StarHub campaigns.
"""

import logging
import os

# Load environment variables
import pathlib
import re
import time
from typing import Any

import httpx
from anthropic import Anthropic, APIError, APITimeoutError
from dotenv import load_dotenv

env_path = pathlib.Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from app.services.config_loader import (
    get_channel_constraints,
    get_cohort_characteristics,
    get_objective_guidance,
    get_product_by_id,
)

logger = logging.getLogger(__name__)


class CommunicationGenerator:
    """
    Generates customer communications using Claude AI.

    This service builds comprehensive prompts incorporating campaign parameters,
    cohort characteristics, channel constraints, and customization options,
    then invokes Claude AI to generate multiple communication variations.
    """

    # Claude model configuration
    MODEL = "claude-sonnet-4-5-20250929"
    MAX_TOKENS = 4096
    MAX_RETRIES = 2
    RETRY_DELAY = 2  # seconds

    def __init__(self, api_key: str | None = None):
        """
        Initialize the communication generator.

        Args:
            api_key: Anthropic API key (if None, will use environment variable)
        """
        # Initialize logger FIRST before any other operations
        self.logger = logging.getLogger(self.__class__.__name__)

        # Use provided key or get from environment
        final_api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if not final_api_key:
            self.logger.error("ANTHROPIC_API_KEY not found in environment variables")
            raise ValueError(
                "ANTHROPIC_API_KEY is required. Please set it in the .env file or pass it explicitly."
            )

        # Configure HTTP client with SSL handling for corporate proxies
        # Check if SSL verification should be disabled (for corporate environments)
        # This handles cases where corporate proxies use self-signed certificates
        verify_ssl = os.getenv("ANTHROPIC_VERIFY_SSL", "true").lower() != "false"

        if not verify_ssl:
            self.logger.warning(
                "SSL verification disabled - this should only be used in corporate proxy environments"
            )
            # Create custom HTTP client with SSL verification disabled
            # This is necessary when corporate proxies use self-signed certificates
            http_client = httpx.Client(verify=False, timeout=60.0)
        else:
            # Use default client with SSL verification
            http_client = httpx.Client(timeout=60.0)

        self.client = Anthropic(api_key=final_api_key, http_client=http_client)
        self.logger.info(
            f"CommunicationGenerator initialized with API key (SSL verification: {verify_ssl})"
        )

    def generate_variations(
        self,
        channel: str,
        cohorts: list[str],
        objective: str,
        product_lines: list[str],
        promotion_details: dict[str, Any] | None = None,
        customization: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Generate 5 communication variations for a campaign.

        Args:
            channel: Communication channel (sms, email, push)
            cohorts: List of target cohort IDs
            objective: Campaign objective
            product_lines: List of product line IDs
            promotion_details: Optional promotion information
            customization: Optional customization parameters

        Returns:
            List of variation dictionaries with variation_number and text

        Raises:
            ValueError: If parameters are invalid
            APIError: If Claude API fails after retries
        """
        # Validate inputs
        self._validate_inputs(channel, cohorts, objective, product_lines)

        # Build comprehensive prompt
        prompt = self._build_prompt(
            channel=channel,
            cohorts=cohorts,
            objective=objective,
            product_lines=product_lines,
            promotion_details=promotion_details or {},
            customization=customization or {},
        )

        # Call Claude API with retry logic
        response_text = self._call_claude_api(prompt)

        # Parse variations from response
        variations = self._parse_variations(response_text)

        self.logger.info(
            f"Successfully generated {len(variations)} variations for {channel}/{objective}"
        )
        return variations

    def _validate_inputs(
        self, channel: str, cohorts: list[str], objective: str, product_lines: list[str]
    ) -> None:
        """
        Validate input parameters.

        Args:
            channel: Communication channel
            cohorts: Target cohorts
            objective: Campaign objective
            product_lines: Product lines

        Raises:
            ValueError: If any parameter is invalid
        """
        valid_channels = ["sms", "email", "push"]
        if channel not in valid_channels:
            raise ValueError(f"Invalid channel: {channel}. Must be one of {valid_channels}")

        if not cohorts:
            raise ValueError("At least one cohort must be specified")

        if not objective:
            raise ValueError("Objective must be specified")

        if not product_lines:
            raise ValueError("At least one product line must be specified")

    def _build_prompt(
        self,
        channel: str,
        cohorts: list[str],
        objective: str,
        product_lines: list[str],
        promotion_details: dict[str, Any],
        customization: dict[str, Any],
    ) -> str:
        """
        Build comprehensive prompt for Claude AI.

        Args:
            channel: Communication channel
            cohorts: Target cohorts
            objective: Campaign objective
            product_lines: Product lines
            promotion_details: Promotion information
            customization: Customization parameters

        Returns:
            Formatted prompt string
        """
        # Load configuration data
        cohort_chars = get_cohort_characteristics(cohorts)
        channel_constraints = get_channel_constraints(channel)
        objective_info = get_objective_guidance(objective)

        # Build product information
        product_info = []
        for product_id in product_lines:
            product = get_product_by_id(product_id)
            if product:
                product_info.append(f"- {product['name']}: {product['description']}")

        # Build cohort information
        cohort_info = []
        for cohort_id, cohort_data in cohort_chars.items():
            cohort_info.append(f"- {cohort_data['name']}: {cohort_data['description']}")

        # Extract customization options
        tone = customization.get("tone", "professional")
        required_phrases = customization.get("required_phrases", [])
        prohibited_words = customization.get("prohibited_words", [])
        length_preference = customization.get("length_preference", "optimal")
        custom_instructions = customization.get("custom_instructions")

        # Build channel constraints section
        constraints_text = self._format_channel_constraints(channel, channel_constraints)

        # Build promotion details section
        promotion_text = self._format_promotion_details(promotion_details)

        # Build customization section
        customization_text = self._format_customization(
            tone, required_phrases, prohibited_words, length_preference, custom_instructions
        )

        # Construct full prompt
        prompt = f"""Using the starhub-comms skill, generate 5 unique customer communication variations.

CAMPAIGN PARAMETERS:
Channel: {channel.upper()}
Objective: {objective_info.get("name", objective)} - {objective_info.get("description", "")}

TARGET COHORTS:
{chr(10).join(cohort_info)}

PRODUCTS/SERVICES:
{chr(10).join(product_info)}

{promotion_text}

{constraints_text}

{customization_text}

REQUIREMENTS:
- Generate EXACTLY 5 distinct variations
- Each variation must be clearly labeled as "VARIATION 1:", "VARIATION 2:", "VARIATION 3:", "VARIATION 4:", "VARIATION 5:"
- Each variation should take a different creative approach while meeting all constraints
- Ensure all variations are appropriate for the target cohorts
- Follow StarHub brand guidelines and tone
- Comply with all regulatory requirements for {channel.upper()} communications

Generate the 5 variations now:"""

        return prompt

    def _format_channel_constraints(self, channel: str, constraints: dict[str, Any]) -> str:
        """Format channel constraints for the prompt."""
        if channel == "sms":
            return f"""CHANNEL CONSTRAINTS (SMS):
- Maximum length: {constraints.get("max_length", 160)} characters
- Optimal length: {constraints.get("optimal_min", 140)}-{constraints.get("optimal_max", 160)} characters
- Must include opt-out for promotional messages (e.g., "Reply STOP to opt out")
- Include clear call-to-action"""

        elif channel == "email":
            return f"""CHANNEL CONSTRAINTS (Email):
- Subject line: {constraints.get("subject_min", 40)}-{constraints.get("subject_max", 60)} characters (optimal)
- Must include unsubscribe option for promotional messages
- Clear structure with engaging subject line and informative body
- Include preheader text (first 50 characters of body)"""

        elif channel == "push":
            return f"""CHANNEL CONSTRAINTS (Push Notification):
- Title: {constraints.get("title_min", 40)}-{constraints.get("title_max", 50)} characters (optimal)
- Body: {constraints.get("body_min", 100)}-{constraints.get("body_max", 120)} characters (optimal)
- May include 1-2 relevant emojis (not excessive)
- Include clear call-to-action or deep link"""

        return ""

    def _format_promotion_details(self, promotion_details: dict[str, Any]) -> str:
        """Format promotion details for the prompt."""
        if not promotion_details:
            return ""

        parts = ["PROMOTION DETAILS:"]

        # Add promotion name if present
        if promotion_details.get("promotion_name"):
            parts.append(f"- Promotion: {promotion_details['promotion_name']}")

        # Handle pricing object (not string!)
        if promotion_details.get("pricing"):
            pricing = promotion_details["pricing"]
            pricing_parts = []

            if pricing.get("monthly_price"):
                pricing_parts.append(f"${pricing['monthly_price']}/month")

            if pricing.get("contract_duration"):
                pricing_parts.append(f"{pricing['contract_duration']}-month contract")

            if pricing.get("discount"):
                pricing_parts.append(f"{pricing['discount']}% discount")

            if pricing.get("bonus"):
                pricing_parts.append(f"Bonus: {pricing['bonus']}")

            if pricing_parts:
                parts.append(f"- Pricing: {', '.join(pricing_parts)}")

        # Add features
        if promotion_details.get("features"):
            features = promotion_details["features"]
            if isinstance(features, list):
                parts.append(f"- Features: {', '.join(features)}")
            else:
                parts.append(f"- Features: {features}")

        # Add terms_conditions (not 'terms'!)
        if promotion_details.get("terms_conditions"):
            parts.append(f"- Terms & Conditions: {promotion_details['terms_conditions']}")

        # Add validity dates
        validity_parts = []
        if promotion_details.get("validity_start"):
            validity_parts.append(f"from {promotion_details['validity_start']}")
        if promotion_details.get("validity_end"):
            validity_parts.append(f"until {promotion_details['validity_end']}")
        if validity_parts:
            parts.append(f"- Validity: {' '.join(validity_parts)}")

        return "\n".join(parts) if len(parts) > 1 else ""

    def _format_customization(
        self,
        tone: str,
        required_phrases: list[str],
        prohibited_words: list[str],
        length_preference: str,
        custom_instructions: str | None = None,
    ) -> str:
        """Format customization options for the prompt."""
        parts = ["CUSTOMIZATION:"]

        parts.append(f"- Tone: {tone}")

        if length_preference and length_preference != "optimal":
            parts.append(f"- Length preference: {length_preference}")

        if custom_instructions:
            parts.append(f"- Custom Instructions: {custom_instructions}")

        if required_phrases:
            phrases_str = ", ".join(f'"{phrase}"' for phrase in required_phrases)
            parts.append(f"- Required phrases (must include): {phrases_str}")

        if prohibited_words:
            words_str = ", ".join(f'"{word}"' for word in prohibited_words)
            parts.append(f"- Prohibited words (avoid): {words_str}")

        return "\n".join(parts)

    def _call_claude_api(self, prompt: str) -> str:
        """
        Call Claude API with retry logic.

        Args:
            prompt: The prompt to send to Claude

        Returns:
            Response text from Claude

        Raises:
            APIError: If all retries fail
        """
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                self.logger.info(
                    f"Calling Claude API (attempt {attempt + 1}/{self.MAX_RETRIES + 1})"
                )

                response = self.client.messages.create(
                    model=self.MODEL,
                    max_tokens=self.MAX_TOKENS,
                    messages=[{"role": "user", "content": prompt}],
                )

                # Extract text from response
                if response.content and len(response.content) > 0:
                    response_text = response.content[0].text
                    self.logger.info(
                        f"Successfully received response from Claude ({len(response_text)} chars)"
                    )
                    return response_text
                else:
                    raise ValueError("Empty response from Claude API")

            except APITimeoutError as e:
                self.logger.warning(f"Claude API timeout on attempt {attempt + 1}: {e}")
                if attempt < self.MAX_RETRIES:
                    time.sleep(self.RETRY_DELAY * (attempt + 1))  # Exponential backoff
                else:
                    raise TimeoutError(
                        f"Claude API timeout after {self.MAX_RETRIES + 1} attempts: {str(e)}"
                    ) from e

            except APIError as e:
                error_msg = str(e)
                self.logger.error(f"Claude API error on attempt {attempt + 1}: {error_msg}")

                # Check for authentication errors
                if (
                    "api_key" in error_msg.lower()
                    or "authentication" in error_msg.lower()
                    or "401" in error_msg
                    or hasattr(e, "status_code")
                    and e.status_code == 401
                ):
                    # Re-raise with original error but better message
                    raise ValueError(
                        f"Authentication failed: Invalid or missing API key. {error_msg}"
                    ) from e

                if attempt < self.MAX_RETRIES:
                    time.sleep(self.RETRY_DELAY * (attempt + 1))
                else:
                    # Re-raise the original APIError
                    raise

            except Exception as e:
                error_msg = str(e)
                self.logger.error(
                    f"Unexpected error calling Claude API: {error_msg}", exc_info=True
                )

                # Check for connection errors
                if (
                    "connection" in error_msg.lower()
                    or "network" in error_msg.lower()
                    or "timeout" in error_msg.lower()
                ):
                    raise ConnectionError(
                        f"Connection error: Unable to connect to Claude API. Please check your network connection and API key. {error_msg}"
                    ) from e

                raise RuntimeError(f"Unexpected error calling Claude API: {error_msg}") from e

        raise RuntimeError("Failed to get response from Claude API after all retries")

    def _parse_variations(self, response_text: str) -> list[dict[str, Any]]:
        """
        Parse variations from Claude's response.

        Args:
            response_text: Raw response text from Claude

        Returns:
            List of variation dictionaries

        Raises:
            ValueError: If variations cannot be parsed correctly
        """
        variations = []

        # Look for "VARIATION N:" patterns
        pattern = r"VARIATION\s+(\d+):\s*(.+?)(?=VARIATION\s+\d+:|$)"
        matches = re.findall(pattern, response_text, re.DOTALL | re.IGNORECASE)

        if not matches:
            # Fallback: try splitting by numbered lists
            pattern = r"(\d+)\.\s*(.+?)(?=\d+\.|$)"
            matches = re.findall(pattern, response_text, re.DOTALL)

        if not matches:
            self.logger.error("Failed to parse variations from response")
            raise ValueError("Could not parse variations from Claude response")

        for variation_num, variation_text in matches:
            # Clean up the variation text
            cleaned_text = variation_text.strip()

            # Remove any leading/trailing quotes or formatting
            cleaned_text = re.sub(r'^["\'\s]+|["\'\s]+$', "", cleaned_text)

            variations.append(
                {
                    "variation_number": int(variation_num),
                    "text": cleaned_text,
                }
            )

        # Validate we got exactly 5 variations
        if len(variations) != 5:
            self.logger.warning(f"Expected 5 variations but got {len(variations)}")

        # Sort by variation number
        variations.sort(key=lambda x: x["variation_number"])

        return variations
