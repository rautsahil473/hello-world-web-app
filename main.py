
from dotenv import load_dotenv

load_dotenv()
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Text,
    DateTime,
    func,
)
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. Read the database connection securely from an environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set.")

# Railway URLs may start with postgres:// or postgresql://.
# Tell SQLAlchemy to use the Psycopg driver.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://", "postgresql+psycopg://", 1
    )
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://", "postgresql+psycopg://", 1
    )

# 2. Connect Python to PostgreSQL
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

# 3. Define the database table
class AnalysisRecord(Base):
    __tablename__ = "text_analyses"

    id = Column(Integer, primary_key=True, index=True)
    original_text = Column(Text, nullable=False)
    word_count = Column(Integer, nullable=False)
    character_count = Column(Integer, nullable=False)
    uppercase_text = Column(Text, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent


# 4. Create the table when the application starts
@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


# Existing homepage — unchanged
@app.get("/")
def hello_world():
    return FileResponse(BASE_DIR / "index.html")


# Existing health endpoint — unchanged
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "message": "API is running smoothly.",
    }


class TextRequest(BaseModel):
    text: str


# 5. Analyze text and save the result in PostgreSQL
@app.post("/api/analyze")
def analyze_text(request: TextRequest):
    text = request.text.strip()

    word_count = len(text.split())
    character_count = len(request.text)
    uppercase_text = request.text.upper()

    with SessionLocal() as db:
        record = AnalysisRecord(
            original_text=request.text,
            word_count=word_count,
            character_count=character_count,
            uppercase_text=uppercase_text,
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return {
            "id": record.id,
            "original_text": record.original_text,
            "word_count": record.word_count,
            "character_count": record.character_count,
            "uppercase_text": record.uppercase_text,
            "created_at": record.created_at.isoformat(),
        }


# 6. Retrieve the latest 20 saved analyses
@app.get("/api/analyses")
def get_analyses():
    with SessionLocal() as db:
        records = (
            db.query(AnalysisRecord)
            .order_by(AnalysisRecord.id.desc())
            .limit(20)
            .all()
        )

        return [
            {
                "id": record.id,
                "original_text": record.original_text,
                "word_count": record.word_count,
                "character_count": record.character_count,
                "uppercase_text": record.uppercase_text,
                "created_at": record.created_at.isoformat(),
            }
            for record in records
        ]
