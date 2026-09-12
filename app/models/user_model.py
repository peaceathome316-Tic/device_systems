from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime

from app.database.connection import Base


class User(Base):
    """Modelo SQLAlchemy: representa la tabla 'users' en la base de datos."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    role = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)