"""
dbmodels/base.py — the declarative base every ORM model inherits from.

Rookie note: the actual database tables are created by `database/init/*.sql`
(run once at setup). These ORM classes are how Python *reads and writes* those
tables — we do NOT use `Base.metadata.create_all()`. So the models must MIRROR
the SQL exactly (same table names, columns, types). The SQL is the source of truth.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Parent class for all IDRM ORM models."""
    pass
