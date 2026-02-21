from dotenv import load_dotenv


load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# Local imports (Works when Root Directory = backend)
from database.database import engine
from database import models
from routers import auth ,internship,user_profile,automation,chatbot,fake_detector,resume_analyzer


# Create Tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS so Frontend can talk to Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://localhost:3000","https://intern-path-ai-teal.vercel.app"],  # Change this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def health_check():
    return {"status": "ok", "message": "Backend is running"}
app.include_router(auth.router)
app.include_router(internship.router)
app.include_router(user_profile.router)
app.include_router(automation.router)
app.include_router(chatbot.router)
app.include_router(fake_detector.router)
app.include_router(resume_analyzer.router)


