import os
import mimetypes
import logging
import json
import sys

from google import genai
from dotenv import load_dotenv
from google.genai import types

from Constants import MODEL_NAME
from Constants import OCR_PROMPT

# from ExtractField import extract_fields
load_dotenv()



class GeminiOCRError(Exception):
    """Raised when OCR extraction fails for a reason the caller should handle."""

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
        
    
    def ocr_process(self, file_path) -> dict:
        print("OCR process reached")
        print("OS Path existence",os.path.exists(file_path))
        
        if self.client is None:
            raise ValueError("Client must be created before processing for OCR")

        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            raise ValueError(f"Could not determine mime type for {file_path}")

        try:
            uploaded_file = self.client.files.upload(file=file_path)
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=[OCR_PROMPT, uploaded_file],
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            # print(response)
            parsed = json.loads(response.text)
            required_fields = ["doc_type", "full_name", "date_of_birth", "id_number"]
            validation_errors = [f"{f} could not be extracted" for f in required_fields if not parsed.get(f)]
            parsed["validation_errors"] = validation_errors
            return parsed
          
        except json.JSONDecodeError as e:
            logging.error(f"ERROR: Could not parse Gemini response for {file_path}: {e}")
            # sys.exit()
            raise
        
        except Exception as e:
            logging.error(f"ERROR: Gemini API call failed for {file_path}: {e}")
            # sys.exit()
            raise

        
    
    
            
            
            
                            
        
        