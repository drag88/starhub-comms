"""
Error Log model for tracking system errors and failures.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from database import Base


class ErrorLog(Base):
    """
    Error Log model for tracking system errors and failures.

    Attributes:
        error_id: Primary key for the error log
        campaign_id: Foreign key to the related campaign (nullable)
        error_type: Type/category of the error
        error_message: Detailed error message
        stack_trace: Full stack trace for debugging
        request_params: JSON object with request parameters that caused the error
        created_at: Timestamp when error occurred
    """

    __tablename__ = "error_logs"

    error_id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(
        Integer,
        ForeignKey("campaigns.campaign_id", ondelete="CASCADE"),
        nullable=True
    )
    error_type = Column(Text, nullable=False)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    request_params = Column(Text, nullable=True)  # JSON object
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    campaign = relationship("Campaign", back_populates="error_logs")

    # Table constraints
    __table_args__ = (
        Index("idx_errors_created", "created_at"),
        Index("idx_errors_type", "error_type"),
    )

    def __repr__(self) -> str:
        return (
            f"<ErrorLog(id={self.error_id}, type='{self.error_type}', "
            f"campaign_id={self.campaign_id})>"
        )
