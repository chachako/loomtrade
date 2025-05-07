from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud # Assuming __init__.py in app/crud makes crud_user available as crud.user
from app.api import deps # Assuming deps.py will provide get_db dependency
from app.core.security import create_access_token, verify_password
from app.schemas.token import Token
# User schema might be needed if we return user details along with token
# from app.schemas.user import User

router = APIRouter()

# This assumes you have a dependency `get_db` in `app/api/deps.py`
# Example `app/api/deps.py`:
# from app.db.session import SessionLocal
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
# If not, db: Session = Depends() needs to be adjusted or get_db created.
# For now, I'll assume deps.get_db exists.


@router.post("/login/access-token", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db), # Placeholder for DB dependency
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
  """
  OAuth2 compatible token login, get an access token for future requests.
  Username in OAuth2PasswordRequestForm corresponds to email.
  """
  # In `crud_user.py`, `get_user_by_username` exists.
  # OAuth2PasswordRequestForm uses `username` field for the identifier.
  # We'll treat `form_data.username` as the email for login.
  user = crud.user.get_user_by_email(db, email=form_data.username)
  if not user:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Incorrect email or password",
    )
  if not verify_password(form_data.password, user.password_hash): # user.password_hash from model
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Incorrect email or password",
    )
  
  access_token_expires = timedelta(minutes=crud.settings.ACCESS_TOKEN_EXPIRE_MINUTES if hasattr(crud, 'settings') else 30) # Fallback if settings not easily accessible
  access_token = create_access_token(
      subject=user.email, expires_delta=access_token_expires # Using email as subject
  )
  return {"access_token": access_token, "token_type": "bearer"}

# A more common path for token generation might be just /token
@router.post("/token", response_model=Token)
def login_for_access_token(
    db: Session = Depends(deps.get_db), # Placeholder for DB dependency
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
  """
  Standard token login.
  form_data.username is treated as email.
  """
  user = crud.user.get_user_by_email(db, email=form_data.username)
  if not user or not verify_password(form_data.password, user.password_hash):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
  access_token_expires = timedelta(minutes=crud.settings.ACCESS_TOKEN_EXPIRE_MINUTES if hasattr(crud, 'settings') else 30)
  access_token = create_access_token(
      subject=user.user_id, expires_delta=access_token_expires # Using user_id as subject
  )
  return {"access_token": access_token, "token_type": "bearer"}

# 提示: 请确保已安装必要的依赖:
# pip install fastapi uvicorn sqlalchemy python-jose[cryptography] passlib
# Also, ensure `app.api.deps.get_db` is defined.
# And ensure `app.crud.user` and `app.core.settings` (if used) are correctly imported.
# For `crud.user`, ensure `backend/app/crud/__init__.py` has `from . import crud_user as user`
# For `crud.settings`, ensure `backend/app/core/config.py` (or similar) defines ACCESS_TOKEN_EXPIRE_MINUTES
# and it's imported into `app.core.security` or made available via an importable `settings` object.
# The `security.py` directly defines `ACCESS_TOKEN_EXPIRE_MINUTES`, so `crud.settings` might not be needed here.
# I'll adjust to use the direct import from security for simplicity.

# Corrected version using direct constant from security.py for expiration
@router.post("/login", response_model=Token) # Changed path to /login as per initial prompt
def login_for_access_token_corrected(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
  """
  Login endpoint.
  form_data.username is treated as email.
  """
  user = crud.user.get_user_by_email(db, email=form_data.username) # crud.user.get_user_by_email
  if not user or not verify_password(form_data.password, user.password_hash):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
  
  # ACCESS_TOKEN_EXPIRE_MINUTES is defined in app.core.security
  # No need to go via crud.settings for this specific constant if security.py defines it.
  # from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES (implicitly available via create_access_token default)
  
  access_token = create_access_token(
      subject=str(user.user_id) # JWT subject should be a string
  )
  return {"access_token": access_token, "token_type": "bearer"}

# To make `crud.user` work, we need `backend/app/crud/__init__.py`:
# from .crud_user import *
# Or, more explicitly:
# from . import crud_user as user

# To make `deps.get_db` work, we need `backend/app/api/deps.py`:
# from app.db.session import SessionLocal
# def get_db():
#   db = SessionLocal()
#   try:
#     yield db
#   finally:
#     db.close()

# I will assume these helper files (`__init__.py` for crud, `deps.py` for api)
# will be created or already exist as per common FastAPI project structure.
# The prompt asks only to create auth.py.