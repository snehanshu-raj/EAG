from fastapi import FastAPI
from pydantic import BaseModel  
from get_embeddings import CLIPEmbedder, get_ollama_embedding  
from fastapi import UploadFile, File

embedder = CLIPEmbedder()
app = FastAPI()

class EmbedRequest(BaseModel):
    text: str = None
    image_path: str = None

@app.post("/get-ollama-text-embedding")
async def get_text_embedding(request: EmbedRequest):
    return get_ollama_embedding(request.text)

@app.post("/get-clip-text-embedding")
async def get_text_embedding(request: EmbedRequest):
    return embedder.embed(text=request.text)

@app.post("/get-clip-image-embedding")
async def get_image_embedding(file: UploadFile = File(...)):
    image_bytes = await file.read()
    with open("zzzz.jpg", "wb") as f:
        f.write(image_bytes)

    return embedder.embed(image_bytes=image_bytes)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=5000)
