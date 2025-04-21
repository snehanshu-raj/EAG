import requests
from qdrant_helper import QdrantHelper
import httpx
import asyncio

qdrant_helper = QdrantHelper()

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="logs.log",
    format='%(asctime)s - %(process)d - %(name)s - %(filename)s:%(lineno)d - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO)

async def async_get_embeddings(text=None, image_bytes=None, type=None):
    ollama_text_embed_url = "http://localhost:5000/get-ollama-text-embedding"
    clip_image_embed_url = "http://localhost:5000/get-clip-image-embedding"
    clip_text_embed_url = "http://localhost:5000/get-clip-text-embedding"

    async with httpx.AsyncClient() as client:
        try:
            if text is not None:
                data = {"text": text}
                if type == "text":
                    response = await client.post(ollama_text_embed_url, json=data)
                else:
                    response = await client.post(clip_text_embed_url, json=data)
            else:
                files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
                response = await client.post(clip_image_embed_url, files=files)

            response.raise_for_status()
            logger.info(f"[Embedding API] Success: {response.json()}")
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"[Embedding API Error] {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"[Embedding Request Exception] {e}")
        
        return {}

async def async_search(text=None, image_bytes=None, type=None):
    try:
        if text is not None:
            if type == "text":
                embeddings = (await async_get_embeddings(text=text, type="text"))["text_embedding"]
                logger.info(f"[Embeddings - Text] {embeddings}")
                results = await asyncio.to_thread(
                    qdrant_helper.search,
                    "web_history", embeddings, limit=1, feature_name="ollama", filters={"type": [type]}
                )
            else:
                embeddings = (await async_get_embeddings(text=text, type="image"))["text_embedding"]
                logger.info(f"[Embeddings - Text for Image] {embeddings}")
                results = await asyncio.to_thread(
                    qdrant_helper.search,
                    "web_history", embeddings, limit=1, feature_name="clip", filters={"type": [type]}
                )
        else:
            embeddings = (await async_get_embeddings(image_bytes=image_bytes, type=type))["image_embedding"]
            logger.info(f"[Embeddings - Image] {embeddings}")
            results = await asyncio.to_thread(
                qdrant_helper.search,
                "web_history", embeddings, limit=1, feature_name="clip", filters={"type": [type]}
            )

        logger.info(f"[Qdrant Results] {results}")
        result = results[0].payload
        return result

    except Exception as e:
        logger.error(f"[Search Error] {str(e)}")
        return {"error": str(e)}
    
def get_embeddings(text=None, image_bytes=None, type=None):
    ollama_text_embed_url = "http://localhost:5000/get-ollama-text-embedding"
    clip_image_embed_url = "http://localhost:5000/get-clip-image-embedding"
    clip_text_embed_url = "http://localhost:5000/get-clip-text-embedding"

    if text is not None:
        data = {
            "text": text
        }
        if type == "text":
            response = requests.post(ollama_text_embed_url, json=data)
        else:
            response = requests.post(clip_text_embed_url, json=data)
    else:
        files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}
        response = requests.post(clip_image_embed_url, files=files)

    if response.status_code == 200:
        print(response.json())
        return response.json()
    else:
        print(f"Error in embedding API: {response.text}")
        return {}
    
def search(text=None, image_bytes=None, type=None):
    if text is not None:
        if type == "text":
            embeddings = get_embeddings(text=text, type="text")["text_embedding"]
            logger.info(embeddings)
            results = qdrant_helper.search("web_history", embeddings, limit=1, feature_name="ollama", filters={"type": [type]})
        else:
            embeddings = get_embeddings(text=text, type="image")["text_embedding"]
            results = qdrant_helper.search("web_history", embeddings, limit=1, feature_name="clip", filters={"type": [type]})
    else:
        embeddings = get_embeddings(image_bytes=image_bytes, type=type)["image_embedding"]
        results = qdrant_helper.search("web_history", embeddings, limit=1, feature_name="clip", filters={"type": [type]})

    logger.info(results)
    result = results[0].payload
    return result