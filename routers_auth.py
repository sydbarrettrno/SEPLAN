from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from schemas import RegisterRequest, LoginRequest, TokenResponse
from models import User
from database import get_session
from security import hash_password, verify_password, create_access_token, get_user_by_email
from settings import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, session: Session = Depends(get_session)):
    if get_user_by_email(session, payload.email):
        raise HTTPException(status_code=409, detail="E-mail jÃ¡ cadastrado")
    user = User(email=payload.email, name=payload.name, password_hash=hash_password(payload.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    token = create_access_token(user.email, get_settings().ACCESS_TOKEN_EXPIRE_MINUTES)
    return TokenResponse(access_token=token)

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, session: Session = Depends(get_session)):
    user = get_user_by_email(session, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais invÃ¡lidas")
    token = create_access_token(user.email, get_settings().ACCESS_TOKEN_EXPIRE_MINUTES)
    return TokenResponse(access_token=token)
