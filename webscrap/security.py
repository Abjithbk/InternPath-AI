import os
from fastapi import Header, HTTPException

INGEST_KEY = os.environ["INGEST_KEY"]

def verify_ingest_key(x_api_key: str = Header(...)):
    if x_api_key != INGEST_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
