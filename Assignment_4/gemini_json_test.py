from google import genai
from pydantic import BaseModel
import os
import json
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

class Response(BaseModel):
  function_name: str
  params: list[str]

response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents='List a few popular cookie recipes. Be sure to include the amounts of ingredients.',
    config={
        'response_mime_type': 'application/json',
        'response_schema': Response,
    },
)
print(response.text)
