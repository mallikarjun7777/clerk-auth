from fastapi import Depends
from fastapi.security import HTTPBearer
from .clerk_auth import verify_clerk_token

security = HTTPBearer()

def get_current_user(credentials=Depends(security)):
    token = credentials.credentials
    return verify_clerk_token(token)