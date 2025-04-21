from pydantic import BaseModel
import asyncio
from google import genai
from concurrent.futures import TimeoutError
import config
import json
from ast import literal_eval
from typing import Optional

class Params(BaseModel):
    text: Optional[str] = None
    image_bytes: Optional[str] = None
    type: Optional[str] = None

class Response(BaseModel):
    function_name: str
    params: Params
    final_ans: str
    reasoning_type: str

client = genai.Client(api_key=config.GEMINI_API_KEY)

async def generate_with_timeout(prompt, timeout=10):
    try:
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: client.models.generate_content(
                    # model="gemini-1.5-flash",
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config={
                        'response_mime_type': 'application/json',
                        'response_schema': Response,
                    },
                )
            ),
            timeout=timeout
        )
        print("LLM generation completed")
        return response
    except TimeoutError:
        print("LLM generation timed out!")
        raise
    except Exception as e:
        print(f"Error in LLM generation: {e}")
        raise

def validate_response(response_text):
    try:
        parsed = literal_eval(json.loads(json.dumps(response_text.strip())))
        Response(**parsed)
        return parsed
    except Exception as e:
        raise ValueError(f"Invalid response format: {e}")

