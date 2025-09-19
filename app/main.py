from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models.schemas import CustomerData, EligibilityResponse, ChatMessage, VerificationData
from app.services.security import DataSecurity
from app.services.conversation_manager import ConversationManager

app = FastAPI(title="Loan Eligibility Chatbot API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize conversation manager
conversation_manager = ConversationManager()

@app.get("/")
async def root():
    return {"message": "Loan Eligibility Chatbot API is running"}

@app.post("/chat")
async def chat_endpoint(message: ChatMessage):
    try:
        print(f"Received message: {message.message}, session_id: {message.session_id}")
        
        # Process the message through conversation manager
        response = conversation_manager.process_message(
            message.message, 
            message.session_id
        )
        
        print(f"Response: {response['message'][:50]}..., step: {response['current_step']}")
        
        return {
            "response": response["message"],
            "session_id": response["session_id"],
            "current_step": response["current_step"],
            "completed": response.get("completed", False)
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/check-eligibility")
async def check_eligibility(customer_data: CustomerData):
    try:
        # This would use the eligibility agent in a real implementation
        # For now, we'll do a simple check
        age = conversation_manager.calculate_age(customer_data.date_of_birth)
        
        # Check eligibility criteria
        eligible = True
        reasons = []
        
        if age < 21 or age > 58:
            eligible = False
            reasons.append(f"Age {age} is outside acceptable range (21-58)")
        
        if customer_data.monthly_income < 25000:
            eligible = False
            reasons.append(f"Income ₹{customer_data.monthly_income} is below minimum requirement (₹25,000)")
        
        debt_ratio = customer_data.existing_emis / customer_data.monthly_income if customer_data.monthly_income > 0 else 1
        if debt_ratio > 0.5:
            eligible = False
            reasons.append(f"Debt-to-income ratio {debt_ratio:.2f} exceeds maximum allowed (0.5)")
        
        if customer_data.credit_score < 750:
            eligible = False
            reasons.append(f"Credit score {customer_data.credit_score} is below preferred threshold (750)")
        
        if customer_data.years_employed < 1:
            eligible = False
            reasons.append(f"Employment duration {customer_data.years_employed} years is below minimum requirement (1 year)")
        
        explanation = "Based on our assessment of your financial profile and eligibility criteria."
        
        next_steps = [
            "Upload last 6 months' bank statements",
            "Upload latest salary slips",
            "Proceed to application form"
        ]
        
        return EligibilityResponse(
            eligible=eligible,
            reasons=reasons,
            explanation=explanation,
            next_steps=next_steps,
            confidence=0.9
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify-user")
async def verify_user(data: VerificationData):
    try:
        # Validate PAN format
        if not DataSecurity.validate_pan_format(data.pan):
            return {"verified": False, "message": "Invalid PAN format"}
        
        # Validate Aadhaar format
        if data.aadhaar and not DataSecurity.validate_aadhaar_format(data.aadhaar):
            return {"verified": False, "message": "Invalid Aadhaar format"}
        
        # Validate date format
        if not DataSecurity.validate_date_format(data.date_of_birth):
            return {"verified": False, "message": "Invalid date format. Use DD-MM-YYYY"}
        
        # In a real application, you would verify against a database
        # For this example, we'll assume verification is successful
        return {"verified": True, "message": "User verified successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)