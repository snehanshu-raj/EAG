import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import numpy as np
import os
from io import BytesIO
import numpy as np
import requests
import json

class CLIPEmbedder:
    def __init__(self, model_name="openai/clip-vit-base-patch32", device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = CLIPModel.from_pretrained(model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(model_name)

    def embed_text(self, text: str) -> np.ndarray:
        inputs = self.processor(text=[text], return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            embeddings = self.model.get_text_features(**inputs)
        return embeddings.cpu().numpy().squeeze()

    def embed_image(self, image_bytes: bytes) -> np.ndarray:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            embeddings = self.model.get_image_features(**inputs)
        return embeddings.cpu().numpy().squeeze()

    def embed(self, text: str = None, image_bytes: str = None) -> dict:
        result = {}
        if text:
            result["text_embedding"] = self.embed_text(text).tolist()
        if image_bytes:
            result["image_embedding"] = self.embed_image(image_bytes).tolist()
        return result

def get_ollama_embedding(text: str):
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={
            "model": "nomic-embed-text",
            "prompt": text
        }
    )
    response.raise_for_status()
    return {"text_embedding": response.json()["embedding"]}

if __name__ == "__main__":
    # embedder = CLIPEmbedder()

    # text = "a photo of a cat"
    # text_emb = embedder.embed(text=text)["text_embedding"]
    # print("Text Embedding Shape:", text_emb)

    # img_path = "Cat.jpg"
    # img_emb = embedder.embed(image_path=img_path)["image_embedding"]
    # print("Image Embedding Shape:", img_emb)

    # both = embedder.embed(text=text, image_path=img_path)
    # print("Cosine Similarity (Image vs Text):",
    #       np.dot(both["text_embedding"], both["image_embedding"]) / (
    #           np.linalg.norm(both["text_embedding"]) * np.linalg.norm(both["image_embedding"])
    #       ))

    embedding = get_ollama_embedding("hello")
    print(len(embedding))