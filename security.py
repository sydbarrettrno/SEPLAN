# security.py
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from settings import get_settings
from models import User

# Prioriza Argon2 (sem limite de 72 bytes); mantém compatibilidade com bcrypt se existir hash legado.
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt_sha256", "bcrypt"],
    deprecated="auto",
)

def hash_password(password: str) -> str:
    """Gera hash de senha (argon2 por padrão)."""
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    """Verifica senha contra o hash salvo (auto-detecta o esquema)."""
    return pwd_context.verify(password, password_hash)

def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    """Cria JWT (HS256) com expiração configurável."""
    settings = get_settings()
    exp_minutes = expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    payload = {
        "sub": subject,
        "exp": datetime.utcnow() + timedelta(minutes=exp_minutes),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

def decode_token(token: str) -> Optional[str]:
    """Decodifica o JWT e retorna o 'sub' (email) se válido; caso contrário, None."""
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload.get("sub")
    except Exception:
        return None

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """Helper para buscar usuário por e-mail."""
    stmt = select(User).where(User.email == email)
    return session.exec(stmt).first()
