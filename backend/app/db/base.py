"""
Database Base Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Provides the declarative base for SQLAlchemy ORM models.
"""

from sqlalchemy.ext.declarative import declarative_base

# Create the declarative base for all models
Base = declarative_base()

