"""
Configuration loader utility for YAML configuration files.

This module provides cached access to YAML configuration files for cohorts,
objectives, products, and channel constraints.
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
import logging

logger = logging.getLogger(__name__)

# Configuration cache
_config_cache: Dict[str, Any] = {}

# Configuration file paths
CONFIG_DIR = Path(__file__).parent.parent / "config"
COHORTS_FILE = CONFIG_DIR / "cohorts.yaml"
OBJECTIVES_FILE = CONFIG_DIR / "objectives.yaml"
PRODUCTS_FILE = CONFIG_DIR / "products.yaml"

# Channel constraints (not in YAML, hardcoded)
CHANNEL_CONSTRAINTS = {
    "sms": {
        "max_length": 160,
        "optimal_min": 140,
        "optimal_max": 160,
        "requires_opt_out": True,
        "opt_out_phrases": ["Reply STOP", "STOP to opt", "Text STOP"],
    },
    "email": {
        "subject_min": 40,
        "subject_max": 60,
        "requires_unsubscribe": True,
        "unsubscribe_phrases": ["unsubscribe", "opt out", "manage preferences"],
    },
    "push": {
        "title_min": 40,
        "title_max": 50,
        "body_min": 100,
        "body_max": 120,
        "supports_emojis": True,
        "requires_cta": True,
    },
}


def load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """
    Load and parse a YAML file.

    Args:
        file_path: Path to the YAML file

    Returns:
        Parsed YAML content as a dictionary

    Raises:
        FileNotFoundError: If the file does not exist
        yaml.YAMLError: If the file cannot be parsed
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {file_path}")
            return content or {}
    except yaml.YAMLError as e:
        logger.error(f"Failed to parse YAML file {file_path}: {e}")
        raise


def get_cached_config(config_name: str, file_path: Path) -> Dict[str, Any]:
    """
    Get cached configuration or load it if not cached.

    Args:
        config_name: Name of the configuration (for cache key)
        file_path: Path to the configuration file

    Returns:
        Configuration dictionary
    """
    if config_name not in _config_cache:
        _config_cache[config_name] = load_yaml_file(file_path)
    return _config_cache[config_name]


def get_cohorts() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get all cohort configurations.

    Returns:
        Dictionary with cohort categories as keys and lists of cohorts as values
    """
    config = get_cached_config("cohorts", COHORTS_FILE)
    return config.get("cohorts", {})


def get_cohort_by_id(cohort_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific cohort by ID.

    Args:
        cohort_id: The cohort ID to retrieve

    Returns:
        Cohort dictionary or None if not found
    """
    cohorts = get_cohorts()
    for category, cohort_list in cohorts.items():
        for cohort in cohort_list:
            if cohort.get("id") == cohort_id:
                return cohort
    return None


def get_cohort_characteristics(cohort_ids: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Get characteristics for multiple cohorts.

    Args:
        cohort_ids: List of cohort IDs

    Returns:
        Dictionary mapping cohort IDs to their full configurations
    """
    characteristics = {}
    for cohort_id in cohort_ids:
        cohort = get_cohort_by_id(cohort_id)
        if cohort:
            characteristics[cohort_id] = cohort
        else:
            logger.warning(f"Cohort not found: {cohort_id}")
    return characteristics


def get_objectives() -> List[Dict[str, Any]]:
    """
    Get all objective configurations.

    Returns:
        List of objective dictionaries
    """
    config = get_cached_config("objectives", OBJECTIVES_FILE)
    return config.get("objectives", [])


def get_objective_by_id(objective_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific objective by ID.

    Args:
        objective_id: The objective ID to retrieve

    Returns:
        Objective dictionary or None if not found
    """
    objectives = get_objectives()
    for objective in objectives:
        if objective.get("id") == objective_id:
            return objective
    return None


def get_objective_guidance(objective_id: str) -> Dict[str, Any]:
    """
    Get guidance for a specific objective.

    Args:
        objective_id: The objective ID

    Returns:
        Dictionary with objective details and guidance
    """
    objective = get_objective_by_id(objective_id)
    if not objective:
        logger.warning(f"Objective not found: {objective_id}")
        return {}

    return {
        "name": objective.get("name", ""),
        "description": objective.get("description", ""),
        "typical_channels": objective.get("typical_channels", []),
    }


def get_products() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get all product configurations.

    Returns:
        Dictionary with product categories as keys and lists of products as values
    """
    config = get_cached_config("products", PRODUCTS_FILE)
    return config.get("products", {})


def get_product_by_id(product_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific product by ID.

    Args:
        product_id: The product ID to retrieve

    Returns:
        Product dictionary or None if not found
    """
    products = get_products()
    for category, product_list in products.items():
        for product in product_list:
            if product.get("id") == product_id:
                return product
    return None


def get_channel_constraints(channel: str) -> Dict[str, Any]:
    """
    Get constraints for a specific communication channel.

    Args:
        channel: The channel name (sms, email, push)

    Returns:
        Dictionary with channel constraints
    """
    return CHANNEL_CONSTRAINTS.get(channel.lower(), {})


def clear_cache() -> None:
    """
    Clear the configuration cache.

    Useful for testing or when configurations are updated.
    """
    global _config_cache
    _config_cache.clear()
    logger.info("Configuration cache cleared")


def get_cohort_keywords(cohort_id: str) -> Dict[str, List[str]]:
    """
    Get recommended keywords for a cohort (for scoring algorithm).

    Args:
        cohort_id: The cohort ID

    Returns:
        Dictionary with 'positive' and 'negative' keyword lists
    """
    # Define cohort-specific keywords for scoring
    cohort_keywords = {
        "high_value": {
            "positive": ["exclusive", "VIP", "premium", "valued", "special", "priority"],
            "negative": ["cheap", "discount", "sale", "budget"],
        },
        "premium_segment": {
            "positive": ["premium", "ultra", "fastest", "10Gbps", "unlimited", "elite"],
            "negative": ["basic", "standard", "limited"],
        },
        "at_risk_churn": {
            "positive": ["save", "deal", "offer", "discount", "limited time", "exclusive"],
            "negative": [],
        },
        "new_customers": {
            "positive": ["welcome", "getting started", "explore", "discover", "new"],
            "negative": ["upgrade", "renew"],
        },
        "loyal_customers": {
            "positive": ["thank you", "loyal", "valued", "appreciation", "exclusive"],
            "negative": [],
        },
        "students": {
            "positive": ["student", "study", "campus", "save", "affordable", "data"],
            "negative": ["expensive", "premium"],
        },
        "families": {
            "positive": ["family", "everyone", "home", "bundle", "together", "kids"],
            "negative": [],
        },
        "seniors": {
            "positive": ["simple", "easy", "support", "help", "assistance"],
            "negative": ["complex", "advanced"],
        },
        "young_professionals": {
            "positive": ["mobile", "fast", "data", "unlimited", "work", "flexible"],
            "negative": [],
        },
        "sports_fans": {
            "positive": ["sports", "match", "league", "cricket", "live", "Premier League", "watch"],
            "negative": [],
        },
        "tech_enthusiasts": {
            "positive": ["new", "latest", "advanced", "technology", "innovation", "5G", "fiber"],
            "negative": ["basic", "old"],
        },
        "high_data_users": {
            "positive": ["unlimited", "data", "GB", "stream", "download", "no limits"],
            "negative": ["limited", "capped"],
        },
    }

    return cohort_keywords.get(cohort_id, {"positive": [], "negative": []})


def get_objective_keywords(objective_id: str) -> Dict[str, List[str]]:
    """
    Get recommended keywords for an objective (for scoring algorithm).

    Args:
        objective_id: The objective ID

    Returns:
        Dictionary with keyword lists for different aspects
    """
    objective_keywords = {
        "promotion": {
            "urgency": ["limited", "expires", "today", "now", "hurry", "don't miss"],
            "value": ["$", "free", "save", "deal", "offer"],
            "cta": ["get", "claim", "sign up", "activate", "start"],
        },
        "retention": {
            "personalization": ["you", "your"],
            "exclusive": ["exclusive", "special", "just for you", "valued"],
            "appreciation": ["thank you", "appreciate", "loyal", "valued"],
            "cta": ["stay", "keep", "continue", "renew"],
        },
        "upsell": {
            "upgrade": ["upgrade", "more", "better", "faster", "premium"],
            "value": ["from just", "only", "for just", "add"],
            "cta": ["upgrade", "move to", "switch to", "get more"],
        },
        "cross_sell": {
            "complementary": ["add", "also", "plus", "with", "bundle"],
            "value": ["complete", "everything", "all-in-one"],
            "cta": ["add", "get", "include", "bundle"],
        },
        "service_update": {
            "clarity": ["update", "maintenance", "notice", "important", "change"],
            "action": ["required", "please", "need to"],
            "cta": ["learn more", "read more", "visit"],
        },
        "billing": {
            "clarity": ["bill", "payment", "due", "amount", "balance"],
            "action": ["pay", "settle", "confirm"],
            "cta": ["pay now", "view bill", "manage payment"],
        },
    }

    return objective_keywords.get(objective_id, {})
