"""
Authentication & Access Control Endpoints
-----------------------------------------
Protected with rate limiting and audit logging.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.rate_limit import auth_limiter
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, UserResponse, Token
from app.services.audit_service import record_audit_log

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(request: Request, user_in: UserCreate, db: Session = Depends(get_db)):
    auth_limiter.check(request)
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )
        
    user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        role=user_in.role or "SECURITY_ANALYST",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = create_access_token(subject=user.id, role=user.role)
    client_ip = request.client.host if request.client else "127.0.0.1"
    record_audit_log(db, action="USER_REGISTERED", user=user.email, ip_address=client_ip, details={"name": user.name, "role": user.role})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/login", response_model=Token)
def login(request: Request, login_data: UserLogin, db: Session = Depends(get_db)):
    auth_limiter.check(request)
    client_ip = request.client.host if request.client else "127.0.0.1"
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        record_audit_log(db, action="LOGIN_FAILED_BAD_CREDENTIALS", user=login_data.email, ip_address=client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
        
    if not user.is_active:
        record_audit_log(db, action="LOGIN_FAILED_ACCOUNT_SUSPENDED", user=login_data.email, ip_address=client_ip)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your user account is suspended. Contact SOC Administrator."
        )
        
    token = create_access_token(subject=user.id, role=user.role)
    record_audit_log(db, action="USER_LOGIN_SUCCESS", user=user.email, ip_address=client_ip)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user
