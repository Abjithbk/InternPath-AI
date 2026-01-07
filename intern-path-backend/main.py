from fastapi import FastAPI

# Initialize the FastAPI application
app = FastAPI()

# 1. Root Endpoint (Test)
@app.get("/")
def read_root():
    """Returns a simple message to confirm the server is running."""
    return {"message": "Server is UP and running!"}

