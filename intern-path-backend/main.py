from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# Local imports (Works when Root Directory = backend)
from database.database import engine
from database import models
from routers import auth


# Create Tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS so Frontend can talk to Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://localhost:3000"],  # Change this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def health_check():
    return {"status": "ok", "message": "Backend is running"}

app.include_router(auth.router)