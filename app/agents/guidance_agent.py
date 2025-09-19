from app.agents.base_agent import BaseAgent
from app.config.prompts import GUIDANCE_PROMPT

class GuidanceAgent(BaseAgent):
    def process(self, eligibility_status: bool, customer_data: dict) -> str:
        prompt = GUIDANCE_PROMPT.format(
            eligibility_status="Eligible" if eligibility_status else "Not Eligible",
            customer_data=str(customer_data)
        )
        
        messages = [
            {"role": "system", "content": "You are a financial guidance expert."},
            {"role": "user", "content": prompt}
        ]
        
        return self.call_genai(messages)