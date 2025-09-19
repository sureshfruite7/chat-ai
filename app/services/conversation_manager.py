import uuid
import re
from datetime import datetime, timedelta
from typing import Dict, Any

class ConversationManager:
    def __init__(self):
        self.sessions = {}
        self.max_attempts = 5
        self.lockout_time = timedelta(minutes=30)
        print("ConversationManager initialized")

    def process_message(self, message: str, session_id: str = None) -> Dict[str, Any]:
        print(f"Processing message: '{message}', session_id: {session_id}")

        # Create new session if needed
        if not session_id or session_id not in self.sessions:
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = {
                "step": "greeting",
                "data": {},
                "attempts": {},
                "created_at": datetime.now(),
                "last_message": ""
            }
            print(f"Created new session: {session_id}")
        else:
            print(f"Using existing session: {session_id}, current step: {self.sessions[session_id]['step']}")

        session = self.sessions[session_id]
        user_input = message.strip().lower()
        response = ""
        current_step = session["step"]

        # Check if session is locked
        if session.get("locked_until") and datetime.now() < session["locked_until"]:
            remaining = session["locked_until"] - datetime.now()
            minutes = int(remaining.total_seconds() // 60)
            return {
                "message": f"Too many failed attempts. Please try again after {minutes} minutes.",
                "session_id": session_id,
                "current_step": "locked",
                "completed": False
            }

        # --- Conversation Steps ---
        if current_step == "greeting":
            response = "Hi 👋 I can help you check your loan eligibility. Please choose: 1️⃣ Personal Loan 2️⃣ Credit Card Loan"
            session["step"] = "loan_type_selection"

        elif current_step == "loan_type_selection":
            if "1" in user_input or "personal" in user_input:
                session["data"]["loan_type"] = "Personal Loan"
                response = "Great! Let's start with your PAN card number."
                session["step"] = "pan_input"
            elif "2" in user_input or "credit card" in user_input:
                session["data"]["loan_type"] = "Credit Card Loan"
                response = "Great! Let's start with your PAN card number."
                session["step"] = "pan_input"
            else:
                response = "Please choose: 1️⃣ Personal Loan 2️⃣ Credit Card Loan"

        elif current_step == "pan_input":
            pan = message.strip().upper()
            if self.validate_pan(pan):
                session["data"]["pan"] = pan
                session["attempts"]["pan"] = 0
                response = f"Thanks. I've converted it to uppercase: {pan} ✅ Please enter your full name."
                session["step"] = "name_input"
            else:
                attempts = session["attempts"].get("pan", 0) + 1
                session["attempts"]["pan"] = attempts
                if attempts >= self.max_attempts:
                    session["locked_until"] = datetime.now() + self.lockout_time
                    response = "Too many failed PAN attempts. Please try again after 30 minutes."
                    session["step"] = "locked"
                else:
                    response = f"Invalid PAN format. Please enter a valid PAN number (e.g., ABCDE1234F). Attempt {attempts}/{self.max_attempts}"

        elif current_step == "name_input":
            name = message.strip().title()
            session["data"]["name"] = name
            session["attempts"]["name"] = 0
            response = f"Registered name: {name} ✅ Please enter your Date of Birth (DD-MM-YYYY)."
            session["step"] = "dob_input"

        elif current_step == "dob_input":
            if self.validate_dob_format(message):
                session["data"]["date_of_birth"] = message.strip()
                session["attempts"]["dob"] = 0
                response = "✅ DOB verified. Enter Aadhaar number (12 digits)."
                session["step"] = "aadhaar_input"
            else:
                attempts = session["attempts"].get("dob", 0) + 1
                session["attempts"]["dob"] = attempts
                if attempts >= self.max_attempts:
                    session["locked_until"] = datetime.now() + self.lockout_time
                    response = "Too many failed DOB attempts. Please try again after 30 minutes."
                    session["step"] = "locked"
                else:
                    response = f"Invalid date format. Please use DD-MM-YYYY. Attempt {attempts}/{self.max_attempts}"

        elif current_step == "aadhaar_input":
            aadhaar = re.sub(r'\D', '', message)
            if len(aadhaar) == 12:
                session["data"]["aadhaar"] = aadhaar
                session["attempts"]["aadhaar"] = 0
                response = "✅ Aadhaar verified. Now, we'll collect financial details. What is your monthly income?"
                session["step"] = "income_input"
            else:
                attempts = session["attempts"].get("aadhaar", 0) + 1
                session["attempts"]["aadhaar"] = attempts
                if attempts >= self.max_attempts:
                    session["locked_until"] = datetime.now() + self.lockout_time
                    response = "Too many failed Aadhaar attempts. Please try again after 30 minutes."
                    session["step"] = "locked"
                else:
                    response = f"Invalid Aadhaar number. Please enter 12 digits. Attempt {attempts}/{self.max_attempts}"

        elif current_step == "income_input":
            try:
                income = float(message)
                session["data"]["monthly_income"] = income
                response = "How much are your total existing EMIs per month?"
                session["step"] = "emis_input"
            except ValueError:
                response = "Please enter a valid number for monthly income."

        elif current_step == "emis_input":
            try:
                emis = float(message)
                session["data"]["existing_emis"] = emis
                response = "What is your latest credit score (CIBIL)?"
                session["step"] = "credit_score_input"
            except ValueError:
                response = "Please enter a valid number for existing EMIs."

        elif current_step == "credit_score_input":
            try:
                credit_score = int(message)
                if 300 <= credit_score <= 900:
                    session["data"]["credit_score"] = credit_score
                    response = "Are you Salaried or Self-Employed?"
                    session["step"] = "employment_type_input"
                else:
                    response = "Please enter a valid credit score between 300 and 900."
            except ValueError:
                response = "Please enter a valid number for credit score."

        elif current_step == "employment_type_input":
            if "salaried" in user_input:
                session["data"]["employment_type"] = "Salaried"
                response = "How many years have you been employed?"
                session["step"] = "employment_years_input"
            elif "self" in user_input:
                session["data"]["employment_type"] = "Self-Employed"
                response = "How many years have you been in business?"
                session["step"] = "employment_years_input"
            else:
                response = "Please specify: Salaried or Self-Employed?"

        elif current_step == "employment_years_input":
            try:
                years = float(message)
                session["data"]["years_employed"] = years
                response = "Please enter your current address."
                session["step"] = "address_input"
            except ValueError:
                response = "Please enter a valid number for years employed."

        elif current_step == "address_input":
            session["data"]["address"] = message.strip()
            age = self.calculate_age(session["data"]["date_of_birth"])
            income = session["data"]["monthly_income"]
            emis = session["data"]["existing_emis"]
            credit_score = session["data"]["credit_score"]
            years_employed = session["data"]["years_employed"]

            eligible = True
            reasons = []

            if age < 21 or age > 58:
                eligible = False
                reasons.append(f"Age {age} is outside acceptable range (21-58)")

            if income < 25000:
                eligible = False
                reasons.append(f"Income ₹{income} is below minimum requirement (₹25,000)")

            debt_ratio = emis / income if income > 0 else 1
            if debt_ratio > 0.5:
                eligible = False
                reasons.append(f"Debt-to-income ratio {debt_ratio:.2f} exceeds maximum allowed (0.5)")

            if credit_score < 750:
                eligible = False
                reasons.append(f"Credit score {credit_score} is below preferred threshold (750)")

            if years_employed < 1:
                eligible = False
                reasons.append(f"Employment duration {years_employed} years is below minimum requirement (1 year)")

            if eligible:
                response = "✅ You are eligible for a Personal Loan\n\nReasons:\n"
                response += f"- Age: {age} (within 21-58 range)\n"
                response += f"- Monthly income: ₹{income} (> ₹25,000)\n"
                response += f"- Existing EMIs: ₹{emis} ({debt_ratio:.0%} of income, < 50%)\n"
                response += f"- Credit score: {credit_score} (> 750)\n"
                response += "\nNext Steps:\n- Upload last 6 months' bank statements\n- Upload latest salary slips\n- Proceed to application form"
            else:
                response = "❌ You are not eligible for a Personal Loan\n\nReasons:\n"
                for reason in reasons:
                    response += f"- {reason}\n"
                response += "\nSuggestions to improve eligibility:\n- Improve your credit score\n- Reduce your existing debt\n- Maintain stable employment"

            session["step"] = "completed"

        return {
            "message": response,
            "session_id": session_id,
            "current_step": session["step"],
            "completed": session["step"] == "completed"
        }

    def validate_pan(self, pan: str) -> bool:
        pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        return re.match(pattern, pan) is not None

    def validate_dob_format(self, dob: str) -> bool:
        try:
            datetime.strptime(dob, '%d-%m-%Y')
            return True
        except ValueError:
            return False

    def calculate_age(self, dob: str) -> int:
        try:
            birth_date = datetime.strptime(dob, '%d-%m-%Y')
            today = datetime.now()
            age = today.year - birth_date.year
            if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
                age -= 1
            return age
        except ValueError:
            return 0
