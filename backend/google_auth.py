from google.oauth2 import id_token
from google.auth.transport.requests import Request
from fastapi import HTTPException
from models import User
from security import create_access_token
import os

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

if not GOOGLE_CLIENT_ID:
    # We log a warning but don't crash, allowing manual signup to work even if Google config is missing
    print("WARNING: GOOGLE_CLIENT_ID not set. Google Auth will fail.")

def handle_google_signup_or_login(token: str, db):
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Server misconfiguration: missing Google Client ID")

    try:
        # Verification of token
        info = id_token.verify_oauth2_token(token, Request(), GOOGLE_CLIENT_ID)

        email = info["email"]
        first_name = info.get("given_name", "User")
        second_name = info.get("family_name", "")

        user = db.query(User).filter(User.email == email).first()

        if not user:
            # new user creation 
            user = User(
                first_name=first_name,
                second_name=second_name,
                email=email,
                password=None,
                is_google_user=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        #Jwt token gen
        jwt_token = create_access_token(user.email)
        return {"access_token": jwt_token}

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Google token")
    except Exception as e:
        print(f"Google Auth Error: {str(e)}")
        raise HTTPException(status_code=400, detail="Google authentication failed")