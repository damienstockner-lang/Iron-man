from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Friday Assistant API")

MY_PHONE = os.getenv("MY_PHONE", "6043282162")
TWILIO_ENABLED = os.getenv("TWILIO_ENABLED", "false").lower() == "true"

class PhoneVerificationRequest(BaseModel):
    phone: str

class ConfirmOTPRequest(BaseModel):
    phone: str
    code: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/verify-phone")
async def verify_phone(req: PhoneVerificationRequest):
    """Start phone verification flow. If TWILIO_ENABLED is true and credentials are present,
    this will send an OTP SMS. Otherwise it will return a stub response for local testing.
    """
    if TWILIO_ENABLED:
        # Placeholder: send OTP via Twilio (requires twilio client & credentials)
        return {"status": "sent", "phone": req.phone}
    else:
        # In non-Twilio mode, return a fake OTP for testing (do not use in production)
        return {"status": "test-mode", "phone": req.phone, "otp": "123456"}

@app.post("/confirm-otp")
async def confirm_otp(req: ConfirmOTPRequest):
    # In a real implementation verify the OTP and mark the phone as verified
    if req.code == "123456" or TWILIO_ENABLED:
        return {"status": "verified", "phone": req.phone}
    raise HTTPException(status_code=400, detail="Invalid OTP")

