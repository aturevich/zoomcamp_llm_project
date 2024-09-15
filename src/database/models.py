from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
from datetime import datetime

Base = declarative_base()


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, index=True)
    response = Column(String)
    response_time = Column(Float)  # in seconds
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    retrieval_metrics = Column(JSON)
    error = Column(String, nullable=True)

    feedback = relationship("Feedback", back_populates="interaction")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id"))
    rating = Column(Integer)  # e.g., 1-5 star rating
    comment = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    interaction = relationship("Interaction", back_populates="feedback")


class QueryTopic(Base):
    __tablename__ = "query_topics"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id"))
    topic = Column(String)
    confidence = Column(Float)
    interaction = relationship("Interaction")


class Error(Base):
    __tablename__ = "errors"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id"))
    error_type = Column(String)
    error_message = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    interaction = relationship("Interaction")
