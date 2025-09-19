from app.agents.base_agent import BaseAgent
from app.config.prompts import DATA_COLLECTION_PROMPT

class DataCollectionAgent(BaseAgent):
    def process(self, current_data: dict, missing_fields: list) -> str:
        prompt = DATA_COLLECTION_PROMPT.format(
            current_data=str(current_data),
            missing_fields=", ".join(missing_fields)
        )
        
        messages = [
            {"role": "system", "content": "You are a helpful data collection assistant."},
            {"role": "user", "content": prompt}
        ]
        
        return self.call_genai(messages)