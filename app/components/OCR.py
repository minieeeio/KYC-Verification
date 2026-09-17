import os

from google import genai
from dotenv import load_dotenv
load_dotenv()


class GeminiOCR(object):
    def __init__(self):
        print("Initialization of Gemini OCR")
        print(os.getenv("GEMINI_API_KEY"))
        self.API_KEY=os.getenv("GEMINI_API_KEY")
        self.client=None
        
    
    def create_client(self):
        if not self.API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
        self.client=genai.Client(api_key=self.API_KEY)
    
    
        
        