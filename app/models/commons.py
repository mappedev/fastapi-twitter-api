from datetime import datetime

from sqlalchemy import Column, DateTime


class Timestamp:
    created_at = Column(DateTime, default=datetime.now)
