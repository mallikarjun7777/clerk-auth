import os
from dotenv import load_dotenv

load_dotenv()

CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL")
CLERK_WEBHOOK_SECRET = os.getenv("CLERK_WEBHOOK_SECRET")
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
