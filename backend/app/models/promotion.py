"""
Promotion Upload model for storing promotion details and attachments.
"""

from datetime import datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from database import Base


class PromotionUpload(Base):
    """
    Promotion Upload model for storing uploaded promotion details.

    Attributes:
        promotion_id: Primary key for the promotion
        campaign_id: Foreign key to the parent campaign
        promotion_name: Name of the promotion
        pricing_details: JSON object with pricing information
        features_benefits: JSON array of features and benefits
        terms_conditions: Terms and conditions text
        validity_start: Start date of promotion validity
        validity_end: End date of promotion validity
        created_at: Timestamp when promotion was uploaded
    """

    __tablename__ = "promotion_uploads"

    promotion_id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(
        Integer, ForeignKey("campaigns.campaign_id", ondelete="CASCADE"), nullable=False
    )
    promotion_name = Column(Text, nullable=False)
    pricing_details = Column(Text, nullable=True)  # JSON object
    features_benefits = Column(Text, nullable=True)  # JSON array
    terms_conditions = Column(Text, nullable=True)
    validity_start = Column(Date, nullable=True)
    validity_end = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    campaign = relationship("Campaign", back_populates="promotions")

    def __repr__(self) -> str:
        return (
            f"<PromotionUpload(id={self.promotion_id}, name='{self.promotion_name}', "
            f"campaign_id={self.campaign_id})>"
        )
