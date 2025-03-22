from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User
from backend.schemas import UserCreate, Token, LoginResponse, UserLogin
from passlib.hash import bcrypt
import jwt
import datetime
from fastapi.responses import JSONResponse

router = APIRouter()

SECRET_KEY = "your_secret_key"

@router.options("/register")
async def options_handler():
    return {"message": "OK"}
            
# Function to generate JWT token
def create_jwt_token(user_id: int, email: str):
    payload = {
        "sub": str(user_id),
        "email": email,  # Include email in token
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = bcrypt.hash(user.password)
    new_user = User(email=user.email, password=hashed_password,name=user.name)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"access_token": create_jwt_token(new_user.id, new_user.email)}

@router.post("/login", response_model=LoginResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not bcrypt.verify(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    name = db_user.name
    return {"access_token": create_jwt_token(db_user.id, db_user.email),"name":name}

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout():
    # In case you're storing JWT in cookies, you can delete the cookie here.
    response = JSONResponse({"message": "Logged out successfully"})
    response.delete_cookie(key="access_token")
    return response

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

oauth2_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    token = credentials.credentials  # Extract the actual token

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {"user_id": payload["sub"], "email": payload["email"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid toke")