"""
Campaign model for storing campaign configurations.
"""

from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, Index, Integer, Text
from sqlalchemy.orm import relationship

from database import Base


class Campaign(Base):
    """
    Campaign model representing a customer communication campaign.

    Attributes:
        campaign_id: Primary key for the campaign
        campaign_name: Human-readable name for the campaign
        channel: Communication channel (email, sms, push)
        objective: Campaign objective (promotion, retention, etc.)
        product_lines: JSON array of product line IDs
        cohorts: JSON array of target cohort IDs
        promotion_details: JSON object with promotion information
        customization: JSON object with customization parameters
        created_at: Timestamp when campaign was created
        updated_at: Timestamp when campaign was last updated
    """

    __tablename__ = "campaigns"

    campaign_id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_name = Column(Text, nullable=False)
    channel = Column(
        Text,
        nullable=False,
        # Check constraint for valid channels
    )
    objective = Column(Text, nullable=False)
    product_lines = Column(Text, nullable=False)  # JSON array
    cohorts = Column(Text, nullable=False)  # JSON array
    promotion_details = Column(Text, nullable=True)  # JSON object
    customization = Column(Text, nullable=True)  # JSON object
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    communications = relationship(
        "GeneratedCommunication", back_populates="campaign", cascade="all, delete-orphan"
    )

    creatives = relationship(
        "GeneratedCreative", back_populates="campaign", cascade="all, delete-orphan"
    )

    promotions = relationship(
        "PromotionUpload", back_populates="campaign", cascade="all, delete-orphan"
    )

    error_logs = relationship("ErrorLog", back_populates="campaign", cascade="all, delete-orphan")

    # Table constraints
    __table_args__ = (
        CheckConstraint("channel IN ('email', 'sms', 'push')", name="check_channel_valid"),
        Index("idx_campaigns_created", "created_at"),
        Index("idx_campaigns_channel", "channel"),
    )

    def __repr__(self) -> str:
        return f"<Campaign(id={self.campaign_id}, name='{self.campaign_name}', channel='{self.channel}')>"
