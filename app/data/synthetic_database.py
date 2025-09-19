import json
from typing import Dict, Optional

# Synthetic customer database
SYNTHETIC_CUSTOMERS = [
    {
        "pan": "ZDPSW7555R",
        "name": "Anthony Ramachandran",
        "father_name": "Warjas Ratta",
        "date_of_birth": "16-02-1975",
        "address": "21, Chauhan Circle, Nanded 928939",
        "aadhaar": "348426963552",
        "monthly_income": 80000,
        "employment_type": "Self-Employed",
        "years_employed": 10,
        "existing_emis": 0,
        "credit_score": 681
    },
    {
        "pan": "ABCDE1234F",
        "name": "Rahul Sharma",
        "father_name": "Rajesh Sharma",
        "date_of_birth": "15-06-1985",
        "address": "123 Main Street, Mumbai 400001",
        "aadhaar": "123456789012",
        "monthly_income": 75000,
        "employment_type": "Salaried",
        "years_employed": 5,
        "existing_emis": 15000,
        "credit_score": 780
    },
    {
        "pan": "XYZAB1234C",
        "name": "Priya Singh",
        "father_name": "Vikram Singh",
        "date_of_birth": "22-11-1990",
        "address": "45, Gandhi Road, Delhi 110001",
        "aadhaar": "987654321098",
        "monthly_income": 22000,
        "employment_type": "Salaried",
        "years_employed": 2,
        "existing_emis": 5000,
        "credit_score": 750
    }
]

class SyntheticDatabase:
    def __init__(self):
        self.customers = {customer["pan"]: customer for customer in SYNTHETIC_CUSTOMERS}
    
    def find_by_pan(self, pan: str) -> Optional[Dict]:
        """Find customer by PAN number (case-insensitive)"""
        pan_upper = pan.upper()
        return self.customers.get(pan_upper)
    
    def verify_customer(self, pan: str, name: str, dob: str, aadhaar: str = None) -> Dict:
        """Verify customer information against synthetic database"""
        customer = self.find_by_pan(pan)
        
        if not customer:
            return {"verified": False, "message": "PAN not found in records"}
        
        # Check name similarity (handle different name orders)
        name_parts = set(name.upper().split())
        customer_name_parts = set(customer["name"].upper().split())
        name_match = name_parts.issubset(customer_name_parts) or customer_name_parts.issubset(name_parts)
        
        # Check DOB match
        dob_match = dob == customer["date_of_birth"]
        
        # Check Aadhaar if provided
        aadhaar_match = True
        if aadhaar and customer.get("aadhaar"):
            aadhaar_clean = ''.join(filter(str.isdigit, aadhaar))
            customer_aadhaar_clean = ''.join(filter(str.isdigit, customer["aadhaar"]))
            aadhaar_match = aadhaar_clean == customer_aadhaar_clean
        
        verified = name_match and dob_match and (aadhaar_match if aadhaar else True)
        
        return {
            "verified": verified,
            "customer": customer if verified else None,
            "details": {
                "name_match": name_match,
                "dob_match": dob_match,
                "aadhaar_match": aadhaar_match
            }
        }
    
    def get_financial_data(self, pan: str) -> Optional[Dict]:
        """Get financial data for a customer"""
        customer = self.find_by_pan(pan)
        if customer:
            return {
                "monthly_income": customer["monthly_income"],
                "employment_type": customer["employment_type"],
                "years_employed": customer["years_employed"],
                "existing_emis": customer["existing_emis"],
                "credit_score": customer["credit_score"]
            }
        return None

# Global instance
synthetic_db = SyntheticDatabase()