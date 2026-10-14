
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent

@app.get("/")
def hello_world():
    return FileResponse(BASE_DIR/"index.html") 

@app.get("/api/health")
def health_check():
    return {"status": "healthy",
            "message": "API is running smoothly."}

class TextRequest(BaseModel):
    text: str


@app.post("/api/analyze")
def analyze_text(request: TextRequest):
    text = request.text.strip()

    return {
        "original_text": request.text,
        "word_count": len(text.split()),
        "character_count": len(request.text),
        "uppercase_text": request.text.upper()
    }

