from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from app.services.genai_client import TCSGenAIClient

class LoanEligibilityKnowledgeBase:
    def __init__(self):
        self.genai_client = TCSGenAIClient()
        self.rules = self._load_eligibility_rules()
        self.vectorstore = None
    
    def _load_eligibility_rules(self) -> list:
        rules = [
            Document(page_content="""
            Personal Loan Eligibility Criteria:
            - Age: 21 to 58 years
            - Minimum Income: ₹25,000 per month
            - Employment: Minimum 2 years in current job/business
            - Credit Score: Minimum 750 preferred
            - Debt-to-Income Ratio: Existing EMIs should not exceed 50% of income
            - Documents Required: PAN, Aadhaar, Address Proof, Income Proof
            """),
            Document(page_content="""
            Credit Card Eligibility Criteria:
            - Age: 21 to 60 years
            - Minimum Income: ₹15,000 per month
            - Employment: Minimum 1 year in current job
            - Credit Score: Minimum 700
            - Documents Required: PAN, Aadhaar, Address Proof
            """),
            Document(page_content="""
            Home Loan Eligibility Criteria:
            - Age: 21 to 65 years
            - Minimum Income: ₹30,000 per month
            - Employment: Minimum 3 years in current job/business
            - Credit Score: Minimum 750
            - Property Valuation: Required
            - Documents Required: PAN, Aadhaar, Address Proof, Income Proof, Property Documents
            """),
            Document(page_content="""
            General Eligibility Rules:
            - No active defaults or serious delinquencies
            - Stable employment/income history
            - Valid KYC documents
            - Indian residency required
            """)
        ]
        return rules
    
    def setup_vectorstore(self):
        texts = [doc.page_content for doc in self.rules]
        embeddings = [self.genai_client.get_embeddings(text) for text in texts]
        
        self.vectorstore = FAISS.from_embeddings(
            list(zip(texts, embeddings)),
            embedding=TCSGenAIEmbeddings(self.genai_client)
        )
    
    def retrieve_relevant_rules(self, query: str, k: int = 3) -> list:
        if not self.vectorstore:
            self.setup_vectorstore()
        
        docs = self.vectorstore.similarity_search(query, k=k)
        return [doc.page_content for doc in docs]

class TCSGenAIEmbeddings:
    def __init__(self, genai_client):
        self.genai_client = genai_client
    
    def embed_documents(self, texts):
        return [self.genai_client.get_embeddings(text) for text in texts]
    
    def embed_query(self, text):
        return self.genai_client.get_embeddings(text)