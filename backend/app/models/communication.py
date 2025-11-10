"""
Generated Communication model for AI-generated communication variations.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Text, Boolean, DateTime, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from database import Base


class GeneratedCommunication(Base):
    """
    Generated Communication model representing AI-generated communication variations.

    Attributes:
        communication_id: Primary key for the communication
        campaign_id: Foreign key to the parent campaign
        variation_number: Variation number (1-5)
        communication_text: The generated communication text
        recommendation_score: AI recommendation score (0-100)
        score_breakdown: JSON object with score component breakdown
        recommendation_reasoning: Explanation for the recommendation score
        compliance_notes: Any compliance-related notes or warnings
        is_selected: Whether this variation was selected by the user
        edited_text: User-edited version of the communication text
        created_at: Timestamp when communication was generated
    """

    __tablename__ = "generated_communications"

    communication_id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.campaign_id", ondelete="CASCADE"), nullable=False)
    variation_number = Column(Integer, nullable=False)
    communication_text = Column(Text, nullable=False)
    recommendation_score = Column(Integer, nullable=False)
    score_breakdown = Column(Text, nullable=False)  # JSON object
    recommendation_reasoning = Column(Text, nullable=True)
    compliance_notes = Column(Text, nullable=True)
    is_selected = Column(Boolean, default=False, nullable=False)
    edited_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    campaign = relationship("Campaign", back_populates="communications")

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "variation_number >= 1 AND variation_number <= 5",
            name="check_variation_number_range"
        ),
        Index("idx_gencomm_campaign", "campaign_id"),
        Index("idx_gencomm_score", "recommendation_score", postgresql_using="btree"),
    )

    def __repr__(self) -> str:
        return (
            f"<GeneratedCommunication(id={self.communication_id}, "
            f"campaign_id={self.campaign_id}, variation={self.variation_number}, "
            f"score={self.recommendation_score})>"
        )
