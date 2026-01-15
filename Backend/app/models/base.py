"""
Base SQLAlchemy model that all other models inherit from.
This file should be in: app/models/base.py
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass