from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.base import Base
from .commons import Timestamp


class Tweet(Base, Timestamp):
    __tablename__ = "tweet"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    updated_at = Column(DateTime, onupdate=datetime.now)
    by_id = Column(Integer, ForeignKey("user.id"))

    by = relationship("User", back_populates="tweets")
