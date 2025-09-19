from abc import ABC, abstractmethod
from ..services.genai_client import TCSGenAIClient

class BaseAgent(ABC):
    def __init__(self):
        self.genai_client = TCSGenAIClient()
    
    @abstractmethod
    def process(self, input_data: dict) -> dict:
        pass
    
    def call_genai(self, messages: list, temperature: float = 0.1) -> str:
        response = self.genai_client.chat_completion(messages, temperature)
        
        if "error" in response:
            return f"Sorry, I encountered an error: {response['error']}"
        
        return response['choices'][0]['message']['content']