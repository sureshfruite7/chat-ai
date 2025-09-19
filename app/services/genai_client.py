import requests
from app.config.settings import settings

class TCSGenAIClient:
    def __init__(self):
        self.api_key = settings.GENAI_API_KEY
        self.base_url = settings.GENAI_BASE_URL
        self.model = settings.GENAI_MODEL
        self.verify_ssl = settings.VERIFY_SSL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def chat_completion(self, messages: list, temperature: float = 0.1) -> dict:
        url = f"{self.base_url}/v1/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(
                url, 
                headers=self.headers, 
                json=payload, 
                timeout=30, 
                verify=self.verify_ssl
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_embeddings(self, text: str) -> list:
        url = f"{self.base_url}/v1/embeddings"
        
        payload = {
            "model": self.model,
            "input": text
        }
        
        try:
            response = requests.post(
                url, 
                headers=self.headers, 
                json=payload, 
                timeout=30, 
                verify=self.verify_ssl
            )
            response.raise_for_status()
            result = response.json()
            return result['data'][0]['embedding']
        except requests.exceptions.RequestException as e:
            return []