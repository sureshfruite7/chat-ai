from pydantic import BaseModel, Field, validator
from typing import Optional
import re
from datetime import datetime

class CustomerData(BaseModel):
    pan: str = Field(..., description="PAN card number")
    name: str = Field(..., description="Full name")
    date_of_birth: str = Field(..., description="Date of birth in DD-MM-YYYY format")
    address: str = Field(..., description="Full address")
    monthly_income: float = Field(..., description="Monthly income in INR")
    employment_type: str = Field(..., description="Type of employment")
    years_employed: float = Field(..., description="Years employed")
    existing_emis: float = Field(..., description="Existing EMIs in INR")
    credit_score: int = Field(..., description="Credit score")
    loan_amount: Optional[float] = Field(None, description="Requested loan amount")
    loan_purpose: Optional[str] = Field(None, description="Purpose of loan")
    aadhaar: Optional[str] = Field(None, description="Aadhaar number")
    
    @validator('pan')
    def validate_pan_format(cls, v):
        pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        if not re.match(pattern, v.upper()):
            raise ValueError('Invalid PAN format')
        return v.upper()
    
    @validator('date_of_birth')
    def validate_dob_format(cls, v):
        try:
            datetime.strptime(v, '%d-%m-%Y')
        except ValueError:
            raise ValueError('Date of birth must be in DD-MM-YYYY format')
        return v
    
    @validator('credit_score')
    def validate_credit_score(cls, v):
        if not (300 <= v <= 900):
            raise ValueError('Credit score must be between 300 and 900')
        return v

class EligibilityResponse(BaseModel):
    eligible: bool
    reasons: list[str]
    explanation: str
    next_steps: list[str]
    confidence: float

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class VerificationData(BaseModel):
    pan: str
    name: str
    date_of_birth: str
    aadhaar: Optional[str] = None