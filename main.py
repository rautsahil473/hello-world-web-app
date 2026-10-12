
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent

@app.get("/")
def hello_world():
    return FileResponse(BASE_DIR/"index.html") 