"""
Generated Creative model for AI-generated campaign creative images.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from database import Base


class GeneratedCreative(Base):
    """
    Generated Creative model representing AI-generated campaign creative images.

    Attributes:
        creative_id: Primary key for the creative
        campaign_id: Foreign key to the parent campaign
        variant_number: Variant number (1-3)
        channel_type: Creative channel type (email_header, push_header)
        image_filename: Filename of the generated image
        image_url: URL or path to the generated image file
        prompt_used: The complete prompt used for image generation
        generation_params: JSON object with generation parameters (model, style, etc.)
        model_used: AI model used for generation (e.g., "gemini-nano-banana")
        recommendation_score: AI recommendation score (0-100)
        score_reasoning: Explanation for the recommendation score
        is_selected: Whether this creative was selected by the user
        created_at: Timestamp when creative was generated
    """

    __tablename__ = "generated_creatives"

    creative_id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(
        Integer, ForeignKey("campaigns.campaign_id", ondelete="CASCADE"), nullable=False
    )
    variant_number = Column(Integer, nullable=False)
    channel_type = Column(String(50), nullable=False)
    image_filename = Column(Text, nullable=False)
    image_url = Column(Text, nullable=False)
    prompt_used = Column(Text, nullable=False)
    generation_params = Column(Text, nullable=False)  # JSON object
    model_used = Column(String(100), nullable=False)
    recommendation_score = Column(Integer, nullable=False)
    score_reasoning = Column(Text, nullable=True)
    is_selected = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    campaign = relationship("Campaign", back_populates="creatives")

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "variant_number >= 1 AND variant_number <= 3", name="check_variant_number_range"
        ),
        CheckConstraint(
            "channel_type IN ('email_header', 'push_header')", name="check_channel_type_valid"
        ),
        CheckConstraint(
            "recommendation_score >= 0 AND recommendation_score <= 100",
            name="check_recommendation_score_range",
        ),
        Index("idx_creative_campaign", "campaign_id"),
        Index("idx_creative_created", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<GeneratedCreative(id={self.creative_id}, "
            f"campaign_id={self.campaign_id}, variant={self.variant_number}, "
            f"channel={self.channel_type}, score={self.recommendation_score})>"
        )
