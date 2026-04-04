import resend
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from app.config import settings

router = APIRouter()


class SubscribeRequest(BaseModel):
    email: EmailStr


@router.post("", status_code=201)
async def subscribe(body: SubscribeRequest):
    if not settings.resend_api_key or not settings.resend_audience_id:
        raise HTTPException(status_code=503, detail="Email service not configured")

    resend.api_key = settings.resend_api_key
    try:
        resend.Contacts.create(  # type: ignore[call-arg]
            params={
                "audience_id": settings.resend_audience_id,
                "email": body.email,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"message": "Subscribed"}
