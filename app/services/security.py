import hashlib
import re
from datetime import datetime

class DataSecurity:
    @staticmethod
    def anonymize_pii(text: str) -> str:
        pan_pattern = r'[A-Z]{5}[0-9]{4}[A-Z]{1}'
        aadhaar_pattern = r'\d{4}\s?\d{4}\s?\d{4}'
        
        text = re.sub(pan_pattern, lambda m: hashlib.sha256(m.group().encode()).hexdigest()[:10], text)
        text = re.sub(aadhaar_pattern, lambda m: hashlib.sha256(m.group().encode()).hexdigest()[:12], text)
        
        return text
    
    @staticmethod
    def is_financial_query(query: str) -> bool:
        keywords = ["loan", "credit", "eligibility", "income", "emi", "cibil", "interest",
                   "debt", "repayment", "mortgage", "finance", "bank", "approval", "score"]
        return any(keyword in query.lower() for keyword in keywords)
    
    @staticmethod
    def validate_pan_format(pan: str) -> bool:
        pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        return re.match(pattern, pan.upper()) is not None
    
    @staticmethod
    def validate_aadhaar_format(aadhaar: str) -> bool:
        # Remove any spaces or hyphens
        aadhaar_clean = re.sub(r'[\s-]', '', aadhaar)
        return len(aadhaar_clean) == 12 and aadhaar_clean.isdigit()
    
    @staticmethod
    def validate_date_format(date_str: str) -> bool:
        try:
            datetime.strptime(date_str, '%d-%m-%Y')
            return True
        except ValueError:
            return False