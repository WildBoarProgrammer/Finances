import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# Configurazione database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:ciaociao@localhost:5432/finances_db"
)

# Creazione del motore SQLAlchemy
engine = create_engine(DATABASE_URL)

# Creazione della sessione
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base per i modelli ORM
Base = declarative_base()

def get_db():
    """Generatore per ottenere una sessione database."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Crea tutte le tabelle nel database."""
    Base.metadata.create_all(bind=engine)