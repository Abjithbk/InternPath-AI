from fastapi import FastAPI
from .database import Base, engine
from . import ingest, keywords

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(ingest.router)
app.include_router(keywords.router)

@app.get("/")
def health():
    return {"status": "Backend Running"}
