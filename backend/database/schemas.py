from datetime import datetime

from pydantic import BaseModel


class UserResponse(BaseModel):
    clerk_id: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}