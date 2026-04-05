from jose import jwt, JWTError
import requests
from fastapi import HTTPException
from app.config import CLERK_JWKS_URL


def get_jwks():
    if not CLERK_JWKS_URL:
        raise HTTPException(status_code=500, detail="CLERK_JWKS_URL is not configured")
    try:
        response = requests.get(CLERK_JWKS_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Unable to fetch Clerk JWKS: {exc}")


def verify_clerk_token(token: str):
    try:
        jwks = get_jwks()
        header = jwt.get_unverified_header(token)
        key = next((k for k in jwks["keys"] if k["kid"] == header["kid"]), None)

        if key is None:
            raise HTTPException(status_code=401, detail="Token signing key not found")

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
        return payload

    except JWTError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}")
