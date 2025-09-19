from app.agents.base_agent import BaseAgent
from app.services.knowledge_base import LoanEligibilityKnowledgeBase
from app.config.prompts import ELIGIBILITY_PROMPT
from app.models.schemas import CustomerData, EligibilityResponse

class EligibilityAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.knowledge_base = LoanEligibilityKnowledgeBase()
    
    def process(self, customer_data: dict) -> EligibilityResponse:
        validated_data = CustomerData(**customer_data)
        
        # Retrieve relevant rules
        query = f"Eligibility for {validated_data.employment_type} with income {validated_data.monthly_income}"
        relevant_rules = self.knowledge_base.retrieve_relevant_rules(query)
        
        # Prepare prompt
        context = "\n".join(relevant_rules)
        prompt = ELIGIBILITY_PROMPT.format(
            context=context,
            customer_data=validated_data.json()
        )
        
        messages = [
            {"role": "system", "content": "You are a financial eligibility assessment expert."},
            {"role": "user", "content": prompt}
        ]
        
        # Get AI response
        response = self.call_genai(messages)
        
        return self._parse_response(response, validated_data)
    
    def _parse_response(self, response: str, customer_data: CustomerData) -> EligibilityResponse:
        # Simple parsing logic - in production, you'd want more sophisticated parsing
        lines = response.split('\n')
        eligible = any('eligible' in line.lower() for line in lines if 'not eligible' not in line.lower())
        
        reasons = []
        explanation = ""
        next_steps = []
        
        for line in lines:
            if 'reason' in line.lower() or 'criteria' in line.lower():
                reasons.append(line.strip())
            elif 'step' in line.lower() or 'document' in line.lower():
                next_steps.append(line.strip())
            else:
                explanation += line + "\n"
        
        return EligibilityResponse(
            eligible=eligible,
            reasons=reasons,
            explanation=explanation,
            next_steps=next_steps,
            confidence=0.8  # Placeholder
        )