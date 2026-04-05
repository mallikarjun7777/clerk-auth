import json

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session
from svix.webhooks import Webhook, WebhookVerificationError
from app.config import CLERK_WEBHOOK_SECRET
from database.connection import SessionLocal
from database.services.user_service import create_user, get_user_by_clerk_id

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/clerk")
async def clerk_webhook(
    request: Request,
    svix_id: str | None = Header(None, alias="svix-id"),
    svix_timestamp: str | None = Header(None, alias="svix-timestamp"),
    svix_signature: str | None = Header(None, alias="svix-signature"),
    db: Session = Depends(get_db),
):
    if not CLERK_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Webhook secret is not configured")

    body = await request.body()

    try:
        wh = Webhook(CLERK_WEBHOOK_SECRET)
        headers = {
            "svix-id": svix_id,
            "svix-timestamp": svix_timestamp,
            "svix-signature": svix_signature,
        }
        event = wh.verify(body, headers)
    except WebhookVerificationError:
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    if event.get("type") != "user.created":
        return {"status": "ignored"}

    data = event.get("data") or {}
    clerk_id = data.get("id")
    email_addresses = data.get("email_addresses", [])
    email = email_addresses[0].get("email_address") if email_addresses else None

    if not clerk_id or not email:
        raise HTTPException(status_code=400, detail="Invalid webhook payload")

    if not get_user_by_clerk_id(db, clerk_id):
        create_user(db, clerk_id, email)

    return {"status": "ok"}
