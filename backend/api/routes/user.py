from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import requests
from auth.dependencies import get_current_user
from database.connection import SessionLocal
from database.schemas import UserResponse
from database.services.user_service import create_user, get_user_by_clerk_id
from app.config import CLERK_SECRET_KEY

router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def fetch_clerk_email(clerk_id: str) -> str:
    """Fetch user email from Clerk API using the user ID."""
    response = requests.get(
        f"https://api.clerk.com/v1/users/{clerk_id}",
        headers={"Authorization": f"Bearer {CLERK_SECRET_KEY}"},
        timeout=10,
    )
    if not response.ok:
        raise HTTPException(status_code=502, detail=f"Clerk API error {response.status_code}: {response.text}")
    data = response.json()
    emails = data.get("email_addresses", [])
    if not emails:
        raise HTTPException(status_code=400, detail="No email address found for user")
    return emails[0]["email_address"]


@router.get("/me", response_model=UserResponse)
def get_me(user=Depends(get_current_user), db: Session = Depends(get_db)):
    clerk_id = user["sub"]
    db_user = get_user_by_clerk_id(db, clerk_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found. Sync sign-up data with backend.")
    return db_user


@router.post("/sync", response_model=UserResponse)
def sync_user(user=Depends(get_current_user), db: Session = Depends(get_db)):
    clerk_id = user["sub"]

    # Try email from token first, fall back to Clerk API
    email = user.get("email") or fetch_clerk_email(clerk_id)

    db_user = get_user_by_clerk_id(db, clerk_id)
    if not db_user:
        db_user = create_user(db, clerk_id, email)

    return db_user