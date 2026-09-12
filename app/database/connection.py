from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Base de datos SQLite para desarrollo
DATABASE_URL = "sqlite:///./device_systems.db"

# check_same_thread=False es necesario porque SQLite por defecto solo
# permite un hilo; FastAPI puede manejar peticiones en hilos distintos.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()