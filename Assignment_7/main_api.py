from fastapi import FastAPI
from pydantic import BaseModel
import redis  
import hashlib
from file_handler import FileHandler
from fastapi import UploadFile, File, Form
from search_handler import search
from client import main

app = FastAPI()
redis_client = redis.Redis(host="localhost", port=6379, db=0)

class VisitedURLData(BaseModel):
    url: str
    title: str
    timestamp: str
    htmlContent: str

def generate_md5(url: str) -> str:
    return hashlib.md5(url.encode('utf-8')).hexdigest()

@app.post("/api/visited-url-logger")
async def log_visit(data: VisitedURLData):
    data = data.model_dump()
    timestamp = data["timestamp"].split(".")[0].replace(":", "-")

    url_md5 = generate_md5(data["url"])

    if redis_client.exists(url_md5):
        print(f"skipping url: {data['url']}")
        return {
            "status": "skipped",
            "message": f"URL: {data['url']} already logged."
        }
    
    redis_client.set(url_md5, "exists")
    
    file_hander = FileHandler("url_logs")
    file_hander.save_json(timestamp, data)

    redis_client.rpush("url_queue", f"{timestamp}.json")

    return  {
                "status": "success", 
                "message": f"URL: {data["url"]} logged successfully", 
            }

@app.post("/api/search")
async def search_query(text: str = Form(None), file: UploadFile = File(None), type: str = Form(None)):
    if text:
        results = search(text=text, type=type)
    elif file:
        image_bytes = await file.read()
        results = search(image_bytes=image_bytes, type=type)
    else:
        return {"error": "No input provided"}
    
    print(results)
    return {"results": results}

@app.post("/api/agent-search")
async def search_query(text: str = Form(None), file: UploadFile = File(None), type: str = Form(None)):
    if text:
        results = await main(query_text=text, image_bytes=None, type=type)
    elif file:
        image_bytes = await file.read()
        results = await main(query_text=None, image_bytes=image_bytes, type=type)
    else:
        return {"error": "No input provided"}
    
    print(results)
    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
