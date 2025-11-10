"""
Recommendation scoring service implementing 4-pillar scoring algorithm.

This module scores generated communications based on:
1. Channel Best Practices (30%)
2. Cohort Alignment (30%)
3. Objective Effectiveness (25%)
4. Compliance Safety (15%)
"""
from typing import Dict, List, Any, Tuple
import re
import logging

from app.services.config_loader import (
    get_channel_constraints,
    get_cohort_keywords,
    get_objective_keywords,
)

logger = logging.getLogger(__name__)


class RecommendationScorer:
    """
    Scores communication variations using a 4-pillar algorithm.

    The scoring system evaluates communications on:
    - Channel best practices (30% weight)
    - Cohort alignment (30% weight)
    - Objective effectiveness (25% weight)
    - Compliance safety (15% weight)
    """

    # Pillar weights
    CHANNEL_WEIGHT = 0.30
    COHORT_WEIGHT = 0.30
    OBJECTIVE_WEIGHT = 0.25
    COMPLIANCE_WEIGHT = 0.15

    def __init__(self):
        """Initialize the recommendation scorer."""
        self.logger = logging.getLogger(self.__class__.__name__)

    def score_communication(
        self,
        text: str,
        channel: str,
        cohorts: List[str],
        objective: str,
        is_promotional: bool = True,
    ) -> Dict[str, Any]:
        """
        Score a communication variation using the 4-pillar algorithm.

        Args:
            text: The communication text to score
            channel: The communication channel (sms, email, push)
            cohorts: List of target cohort IDs
            objective: The campaign objective
            is_promotional: Whether this is a promotional message

        Returns:
            Dictionary containing:
                - total_score: Overall score (0-100)
                - channel_score: Channel best practices score
                - cohort_score: Cohort alignment score
                - objective_score: Objective effectiveness score
                - compliance_score: Compliance safety score
                - reasoning: Natural language explanation
                - compliance_notes: List of compliance issues
        """
        # Score each pillar
        channel_score, channel_details = self._score_channel_practices(text, channel, is_promotional)
        cohort_score, cohort_details = self._score_cohort_alignment(text, cohorts)
        objective_score, objective_details = self._score_objective_effectiveness(text, objective)
        compliance_score, compliance_notes = self._score_compliance(text, channel, is_promotional)

        # Calculate weighted total
        total_score = round(
            channel_score * self.CHANNEL_WEIGHT
            + cohort_score * self.COHORT_WEIGHT
            + objective_score * self.OBJECTIVE_WEIGHT
            + compliance_score * self.COMPLIANCE_WEIGHT
        )

        # Generate reasoning
        reasoning = self._generate_reasoning(
            total_score,
            channel_score,
            cohort_score,
            objective_score,
            compliance_score,
            channel_details,
            cohort_details,
            objective_details,
        )

        return {
            "total_score": total_score,
            "channel_score": channel_score,
            "cohort_score": cohort_score,
            "objective_score": objective_score,
            "compliance_score": compliance_score,
            "reasoning": reasoning,
            "compliance_notes": compliance_notes,
            "score_breakdown": {
                "channel": channel_details,
                "cohort": cohort_details,
                "objective": objective_details,
            },
        }

    def _score_channel_practices(
        self, text: str, channel: str, is_promotional: bool
    ) -> Tuple[int, Dict[str, Any]]:
        """
        Score based on channel best practices (Pillar 1).

        Args:
            text: Communication text
            channel: Channel type
            is_promotional: Whether message is promotional

        Returns:
            Tuple of (score, details_dict)
        """
        score = 100
        details = {"channel": channel, "issues": [], "strengths": []}
        constraints = get_channel_constraints(channel)

        if channel == "sms":
            length = len(text)
            details["length"] = length

            # Length scoring
            if constraints["optimal_min"] <= length <= constraints["optimal_max"]:
                details["strengths"].append("Optimal length (140-160 chars)")
            elif length < 120:
                score -= 20
                details["issues"].append("Too short (under 120 chars)")
            elif length > 160:
                score -= 50
                details["issues"].append("Over 160 character limit (major penalty)")

            # Opt-out requirement for promotional
            if is_promotional:
                has_opt_out = any(
                    phrase.lower() in text.lower() for phrase in constraints.get("opt_out_phrases", [])
                )
                if has_opt_out:
                    details["strengths"].append("Includes opt-out instruction")
                else:
                    score -= 30
                    details["issues"].append("Missing required opt-out (Reply STOP)")

            # CTA presence
            if self._has_cta(text):
                score += 10
                details["strengths"].append("Clear call-to-action")

        elif channel == "email":
            # Parse subject and body
            subject, body = self._parse_email(text)
            details["subject_length"] = len(subject) if subject else 0
            details["has_body"] = bool(body)

            # Subject line length
            if subject:
                subject_len = len(subject)
                if constraints["subject_min"] <= subject_len <= constraints["subject_max"]:
                    details["strengths"].append("Optimal subject length (40-60 chars)")
                else:
                    score -= 10 if abs(subject_len - 50) < 20 else 15
                    details["issues"].append(f"Subject length suboptimal ({subject_len} chars)")

            # Unsubscribe requirement for promotional
            if is_promotional:
                unsubscribe_phrases = constraints.get("unsubscribe_phrases", [])
                has_unsubscribe = any(
                    phrase.lower() in text.lower() for phrase in unsubscribe_phrases
                )
                if has_unsubscribe:
                    details["strengths"].append("Includes unsubscribe option")
                else:
                    score -= 30
                    details["issues"].append("Missing required unsubscribe link")

            # Clear structure
            if subject and body:
                score += 10
                details["strengths"].append("Clear subject + body structure")

            # Preheader quality (first 50 chars of body)
            if body and len(body) > 50:
                score += 5
                details["strengths"].append("Good preheader text")

        elif channel == "push":
            # Parse title and body
            title, body = self._parse_push(text)
            details["title_length"] = len(title) if title else 0
            details["body_length"] = len(body) if body else 0

            # Title length
            if title:
                title_len = len(title)
                if constraints["title_min"] <= title_len <= constraints["title_max"]:
                    details["strengths"].append("Optimal title length (40-50 chars)")
                else:
                    score -= 15
                    details["issues"].append(f"Title length suboptimal ({title_len} chars)")

            # Body length
            if body:
                body_len = len(body)
                if constraints["body_min"] <= body_len <= constraints["body_max"]:
                    details["strengths"].append("Optimal body length (100-120 chars)")
                else:
                    score -= 10
                    details["issues"].append(f"Body length suboptimal ({body_len} chars)")

            # Emoji usage
            emoji_count = len(re.findall(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', text))
            if 1 <= emoji_count <= 3:
                score += 5
                details["strengths"].append("Appropriate emoji usage")
            elif emoji_count > 3:
                details["issues"].append("Excessive emoji usage")

            # CTA or deep link
            if self._has_cta(text) or "://" in text:
                score += 10
                details["strengths"].append("Includes CTA or deep link")

        return max(0, min(100, score)), details

    def _score_cohort_alignment(self, text: str, cohorts: List[str]) -> Tuple[int, Dict[str, Any]]:
        """
        Score based on cohort alignment (Pillar 2).

        Args:
            text: Communication text
            cohorts: List of target cohort IDs

        Returns:
            Tuple of (score, details_dict)
        """
        score = 70  # Base score
        details = {"cohorts": cohorts, "matched_keywords": [], "mismatched_keywords": []}

        text_lower = text.lower()

        for cohort_id in cohorts:
            keywords = get_cohort_keywords(cohort_id)
            positive_keywords = keywords.get("positive", [])
            negative_keywords = keywords.get("negative", [])

            # Check positive keywords
            matched_positive = [kw for kw in positive_keywords if kw.lower() in text_lower]
            if matched_positive:
                # Award points based on cohort type
                if cohort_id in ["high_value", "premium_segment"]:
                    score += 15
                elif cohort_id in ["at_risk_churn", "sports_fans"]:
                    score += 15
                else:
                    score += 10
                details["matched_keywords"].extend(matched_positive)

            # Check negative keywords (penalty)
            matched_negative = [kw for kw in negative_keywords if kw.lower() in text_lower]
            if matched_negative:
                score -= 20
                details["mismatched_keywords"].extend(matched_negative)

        # Tone assessment for specific cohorts
        if "high_value" in cohorts or "premium_segment" in cohorts:
            if self._has_premium_tone(text):
                score += 10
                details["matched_keywords"].append("premium tone")

        if "young_professionals" in cohorts or "students" in cohorts:
            if self._has_casual_tone(text):
                score += 5
                details["matched_keywords"].append("casual tone")

        if "sports_fans" in cohorts:
            if self._has_energetic_tone(text):
                score += 10
                details["matched_keywords"].append("energetic tone")

        if "families" in cohorts:
            if self._has_warm_tone(text):
                score += 5
                details["matched_keywords"].append("warm, inclusive tone")

        return max(0, min(100, score)), details

    def _score_objective_effectiveness(self, text: str, objective: str) -> Tuple[int, Dict[str, Any]]:
        """
        Score based on objective effectiveness (Pillar 3).

        Args:
            text: Communication text
            objective: Campaign objective

        Returns:
            Tuple of (score, details_dict)
        """
        score = 70  # Base score
        details = {"objective": objective, "matched_keywords": [], "issues": []}

        text_lower = text.lower()
        keywords = get_objective_keywords(objective)

        # All objectives benefit from clear CTA
        if self._has_cta(text):
            score += 15
            details["matched_keywords"].append("clear CTA")
        else:
            score -= 20
            details["issues"].append("Missing clear call-to-action")

        # Objective-specific scoring
        if objective == "promotion":
            # Check urgency language
            urgency_kw = keywords.get("urgency", [])
            matched_urgency = [kw for kw in urgency_kw if kw.lower() in text_lower]
            if matched_urgency:
                score += 10
                details["matched_keywords"].extend(matched_urgency)

            # Check value proposition
            value_kw = keywords.get("value", [])
            matched_value = [kw for kw in value_kw if kw.lower() in text_lower]
            if matched_value:
                score += 5
                details["matched_keywords"].extend(matched_value)

            # Benefits clearly stated
            if any(word in text_lower for word in ["get", "save", "free", "deal", "offer"]):
                score += 5
                details["matched_keywords"].append("benefits stated")

        elif objective == "retention":
            # Personalization
            personalization_kw = keywords.get("personalization", [])
            matched_personal = [kw for kw in personalization_kw if kw.lower() in text_lower]
            if matched_personal:
                score += 10
                details["matched_keywords"].extend(matched_personal)

            # Exclusive/special language
            exclusive_kw = keywords.get("exclusive", [])
            matched_exclusive = [kw for kw in exclusive_kw if kw.lower() in text_lower]
            if matched_exclusive:
                score += 10
                details["matched_keywords"].extend(matched_exclusive)

            # Appreciation tone
            appreciation_kw = keywords.get("appreciation", [])
            matched_appreciation = [kw for kw in appreciation_kw if kw.lower() in text_lower]
            if matched_appreciation:
                score += 5
                details["matched_keywords"].extend(matched_appreciation)

        elif objective == "upsell":
            # Upgrade benefits
            upgrade_kw = keywords.get("upgrade", [])
            matched_upgrade = [kw for kw in upgrade_kw if kw.lower() in text_lower]
            if matched_upgrade:
                score += 10
                details["matched_keywords"].extend(matched_upgrade)

            # Comparative value
            value_kw = keywords.get("value", [])
            matched_value = [kw for kw in value_kw if kw.lower() in text_lower]
            if matched_value:
                score += 5
                details["matched_keywords"].extend(matched_value)

        elif objective == "service_update":
            # Clarity keywords
            clarity_kw = keywords.get("clarity", [])
            matched_clarity = [kw for kw in clarity_kw if kw.lower() in text_lower]
            if matched_clarity:
                score += 5
                details["matched_keywords"].extend(matched_clarity)

            # Less urgency (deduct if too urgent)
            urgent_words = ["urgent", "immediately", "critical", "emergency"]
            if any(word in text_lower for word in urgent_words):
                score -= 5
                details["issues"].append("Too urgent for service update")

            # Professional tone
            if self._has_professional_tone(text):
                score += 10
                details["matched_keywords"].append("professional, informative tone")

        return max(0, min(100, score)), details

    def _score_compliance(
        self, text: str, channel: str, is_promotional: bool
    ) -> Tuple[int, List[str]]:
        """
        Score based on compliance safety (Pillar 4).

        Args:
            text: Communication text
            channel: Channel type
            is_promotional: Whether message is promotional

        Returns:
            Tuple of (score, compliance_notes_list)
        """
        score = 100
        notes = []
        text_lower = text.lower()

        # Promotional opt-out requirements
        if is_promotional:
            if channel == "sms":
                opt_out_phrases = ["reply stop", "stop to opt", "text stop"]
                has_opt_out = any(phrase in text_lower for phrase in opt_out_phrases)
                if not has_opt_out:
                    score -= 40
                    notes.append("CRITICAL: Missing required SMS opt-out ('Reply STOP' or similar)")

            elif channel == "email":
                unsubscribe_phrases = ["unsubscribe", "opt out", "manage preferences"]
                has_unsubscribe = any(phrase in text_lower for phrase in unsubscribe_phrases)
                if not has_unsubscribe:
                    score -= 30
                    notes.append("WARNING: Missing required email unsubscribe option")

        # Pricing disclosure
        has_price = "$" in text or "free" in text_lower
        if has_price:
            disclosure_phrases = ["/mth", "month", "/mo", "contract", "t&cs", "t&c", "terms", "conditions"]
            has_disclosure = any(phrase in text_lower for phrase in disclosure_phrases)
            if not has_disclosure:
                score -= 10
                notes.append("CAUTION: Pricing mentioned without terms/conditions disclosure")

        # Unsubstantiated claims
        risky_words = ["best", "fastest", "guaranteed", "100%", "never", "always"]
        found_risky = [word for word in risky_words if word in text_lower]
        if found_risky:
            score -= 15
            notes.append(f"REVIEW: Unsubstantiated claims detected: {', '.join(found_risky)}")

        # Free offers without T&Cs
        if "free" in text_lower:
            tc_phrases = ["t&cs", "t&c", "terms", "conditions"]
            has_tc = any(phrase in text_lower for phrase in tc_phrases)
            if not has_tc:
                score -= 5
                notes.append("NOTE: 'Free' offer without explicit T&Cs reference")

        # Final compliance status
        if not notes:
            notes.append("No compliance issues detected")

        return max(0, min(100, score)), notes

    def _generate_reasoning(
        self,
        total: int,
        channel: int,
        cohort: int,
        objective: int,
        compliance: int,
        channel_details: Dict[str, Any],
        cohort_details: Dict[str, Any],
        objective_details: Dict[str, Any],
    ) -> str:
        """
        Generate natural language reasoning for the score.

        Args:
            total: Total score
            channel: Channel score
            cohort: Cohort score
            objective: Objective score
            compliance: Compliance score
            channel_details: Channel scoring details
            cohort_details: Cohort scoring details
            objective_details: Objective scoring details

        Returns:
            Natural language explanation string
        """
        parts = []

        # Objective assessment
        if objective >= 85:
            obj_keywords = ", ".join(objective_details.get("matched_keywords", [])[:3])
            parts.append(f"Strong {objective_details['objective']} messaging with {obj_keywords} (Objective: {objective}/100)")
        elif objective >= 70:
            parts.append(f"Good {objective_details['objective']} effectiveness (Objective: {objective}/100)")
        else:
            issues = ", ".join(objective_details.get("issues", []))
            parts.append(f"Weak {objective_details['objective']} messaging - {issues} (Objective: {objective}/100)")

        # Channel assessment
        if channel >= 90:
            strengths = ", ".join(channel_details.get("strengths", [])[:2])
            parts.append(f"Excellent {channel_details['channel'].upper()} formatting - {strengths} (Channel: {channel}/100)")
        elif channel >= 70:
            parts.append(f"Good {channel_details['channel'].upper()} practices (Channel: {channel}/100)")
        else:
            issues = ", ".join(channel_details.get("issues", [])[:2])
            parts.append(f"Channel issues - {issues} (Channel: {channel}/100)")

        # Cohort assessment
        if cohort >= 85:
            keywords = ", ".join(cohort_details.get("matched_keywords", [])[:3])
            parts.append(f"Excellent cohort alignment with {keywords} (Cohort: {cohort}/100)")
        elif cohort >= 70:
            parts.append(f"Good cohort targeting (Cohort: {cohort}/100)")
        else:
            parts.append(f"Weak cohort alignment (Cohort: {cohort}/100)")

        # Compliance assessment
        if compliance >= 90:
            parts.append(f"Strong compliance (Compliance: {compliance}/100)")
        elif compliance >= 70:
            parts.append(f"Acceptable compliance (Compliance: {compliance}/100)")
        else:
            parts.append(f"Compliance concerns (Compliance: {compliance}/100)")

        # Overall summary
        parts.append(f"Overall recommendation score: {total}/100")

        return ". ".join(parts) + "."

    # Helper methods

    def _has_cta(self, text: str) -> bool:
        """Check if text contains a clear call-to-action."""
        cta_phrases = [
            "click", "tap", "visit", "call", "text", "reply", "get", "claim",
            "sign up", "subscribe", "activate", "upgrade", "start", "join",
            "shop", "buy", "order", "learn more", "find out", "discover"
        ]
        return any(phrase in text.lower() for phrase in cta_phrases)

    def _parse_email(self, text: str) -> Tuple[str, str]:
        """Parse email into subject and body."""
        # Look for "Subject:" or similar patterns
        if "subject:" in text.lower():
            parts = re.split(r'subject:\s*', text, flags=re.IGNORECASE, maxsplit=1)
            if len(parts) > 1:
                remaining = parts[1]
                # Split on newline to separate subject from body
                lines = remaining.split('\n', 1)
                subject = lines[0].strip()
                body = lines[1].strip() if len(lines) > 1 else ""
                return subject, body

        # If no explicit subject marker, assume first line is subject
        lines = text.split('\n', 1)
        subject = lines[0].strip() if lines else ""
        body = lines[1].strip() if len(lines) > 1 else ""
        return subject, body

    def _parse_push(self, text: str) -> Tuple[str, str]:
        """Parse push notification into title and body."""
        # Look for "Title:" or similar patterns
        if "title:" in text.lower():
            parts = re.split(r'title:\s*', text, flags=re.IGNORECASE, maxsplit=1)
            if len(parts) > 1:
                remaining = parts[1]
                lines = remaining.split('\n', 1)
                title = lines[0].strip()
                body = lines[1].strip() if len(lines) > 1 else ""
                return title, body

        # If no explicit title marker, assume first line is title
        lines = text.split('\n', 1)
        title = lines[0].strip() if lines else ""
        body = lines[1].strip() if len(lines) > 1 else ""
        return title, body

    def _has_premium_tone(self, text: str) -> bool:
        """Check if text has a premium, exclusive tone."""
        premium_words = ["exclusive", "premium", "vip", "elite", "luxury", "exceptional", "valued"]
        return sum(1 for word in premium_words if word in text.lower()) >= 2

    def _has_casual_tone(self, text: str) -> bool:
        """Check if text has a casual, friendly tone."""
        casual_indicators = ["hey", "you", "your", "we've", "let's", "check out", "awesome"]
        return sum(1 for word in casual_indicators if word in text.lower()) >= 2

    def _has_energetic_tone(self, text: str) -> bool:
        """Check if text has an energetic, exciting tone."""
        energetic_words = ["live", "watch", "action", "exciting", "don't miss", "amazing", "!"]
        return sum(1 for word in energetic_words if word in text.lower()) >= 2

    def _has_warm_tone(self, text: str) -> bool:
        """Check if text has a warm, inclusive tone."""
        warm_words = ["family", "together", "everyone", "home", "enjoy", "love", "perfect"]
        return sum(1 for word in warm_words if word in text.lower()) >= 2

    def _has_professional_tone(self, text: str) -> bool:
        """Check if text has a professional, informative tone."""
        professional_words = ["inform", "update", "notice", "please", "ensure", "maintain", "service"]
        return sum(1 for word in professional_words if word in text.lower()) >= 2
