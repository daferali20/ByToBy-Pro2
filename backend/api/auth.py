from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import jwt
from datetime import datetime, timedelta
import bcrypt

from backend.services import UserService
from database.models import User

router = APIRouter()
security = HTTPBearer()

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """Register a new user"""
    user_service = UserService()
    
    # Check if user exists
    existing_user = await user_service.get_user_by_username(request.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Hash password
    hashed_password = bcrypt.hashpw(
        request.password.encode('utf-8'), 
        bcrypt.gensalt()
    )
    
    # Create user
    user = await user_service.create_user(
        username=request.username,
        email=request.email,
        hashed_password=hashed_password.decode('utf-8'),
        full_name=request.full_name
    )
    
    # Generate token
    token = generate_token(user.id, user.username)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=3600
    )

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login user"""
    user_service = UserService()
    user = await user_service.get_user_by_username(request.username)
    
    if not user or not bcrypt.checkpw(
        request.password.encode('utf-8'), 
        user.hashed_password.encode('utf-8')
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = generate_token(user.id, user.username)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=3600
    )

@router.get("/verify")
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"valid": True, "user_id": payload["sub"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def generate_token(user_id: int, username: str) -> str:
    """Generate JWT token"""
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Constants (move to config)
SECRET_KEY = "your-secret-key-here"  # Change in production
ALGORITHM = "HS256"
