"""
Auth routes: register, login, me.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from auth.dependencies import get_current_user
from auth.security import create_access_token, hash_password, verify_password
from database import users

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------- Schemas ----------
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    name: str = Field(..., min_length=1, max_length=80)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


# ---------- Routes ----------
@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(req: RegisterRequest):
    """Create a new user and return a JWT."""
    existing = await users.get_user_by_email(req.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    hashed = hash_password(req.password)
    user = await users.create_user(req.email, hashed, req.name)
    token = create_access_token(user["_id"], user["email"])
    return {"access_token": token, "user": user}


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    """Authenticate and return a JWT."""
    user = await users.get_user_by_email(req.email)
    if not user or not verify_password(req.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    user_out = {
        "_id": str(user["_id"]),
        "email": user["email"],
        "name": user["name"],
    }
    token = create_access_token(user_out["_id"], user_out["email"])
    return {"access_token": token, "user": user_out}


@router.get("/me")
async def me(current_user: dict = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    return {"user": current_user}