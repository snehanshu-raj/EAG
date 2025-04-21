import redis
import json
import time
import os
from web_extractor import WebContentExtractor
import requests
import hashlib
from search_handler import get_embeddings
import uuid

from transformers import CLIPTokenizer
tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-base-patch32")

from qdrant_helper import QdrantHelper
qdrant_helper = QdrantHelper()
collections = qdrant_helper.list_collections()
if "web_history" not in collections:
    # qdrant_helper.create_collection("web_history", {"clip": 512})
    qdrant_helper.create_collection("web_history", {"ollama": 768, "clip": 512})

REDIS_QUEUE = "url_queue"
JSON_DIR = "url_logs"
IMAGE_DIR = "downloaded_images"
os.makedirs(IMAGE_DIR, exist_ok=True)

redis_client = redis.Redis(host="localhost", port=6379, db=0)
extractor = WebContentExtractor()

def download_image(image_url):
    downloaded_images = []
    # for image_url in image_urls:
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            image_bytes = response.content

            if len(image_bytes) <= 2048:
                print(f"Skipped {image_url} (too small: {len(image_bytes)} bytes)")
                return [None, None]

            md5_hash = hashlib.md5(image_bytes).hexdigest()
            filename = f"{md5_hash}.jpg"
            image_path = os.path.join(IMAGE_DIR, filename)

            with open(image_path, "wb") as f:
                f.write(image_bytes)

            print(f"Downloaded and saved as {filename}")
            return [image_path, image_bytes]
        else:
            print(f"Failed to download {image_url}")
            return [None, None]
    except Exception as e:
        print(f"Error downloading {image_url}: {e}")
        return [None, None]

def chunk_text(text):
    chunks = [sentence.strip() for sentence in text.split('.') if sentence.strip()]   
    return chunks
    
def index(all_indexing_data): 
    points = []
    for item in all_indexing_data:
        if "text" in item.keys():
            try:
                point = {
                    "id": str(uuid.uuid4()),
                    "payload": item,
                    "vectors": {"ollama": get_embeddings(text=item["text"], type="text")["text_embedding"]}
                }
            except Exception as e:
                print(f"Exception in index() for item: {item} as: {str(e)}")
        else:
            try:
                image_bytes = item["image_bytes"]
                del item["image_bytes"]
                point = {
                    "id": str(uuid.uuid4()),
                    "payload": item,
                    "vectors": {"clip": get_embeddings(image_bytes=image_bytes, type="image")["image_embedding"]}
                }
            except Exception as e:
                print(f"Exception in index() for item: {item} as: {str(e)}")

        points.append(point)
    qdrant_helper.upsert_points("web_history", points)

if __name__ == "__main__":
    print("[Consumer] Waiting for messages...")
    while True:
        item = redis_client.brpop(REDIS_QUEUE)

        if item:
            queue_name, filename = item
            filepath = os.path.join(JSON_DIR, filename.decode())

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                extracted_data = extractor.process_html(
                    url=data["url"],
                    html=data["htmlContent"],
                    timestamp=data["timestamp"]
                )
                
                all_chunks = []
                for text_block in extracted_data['text_blocks']:
                    text = text_block['text']
                    chunks = chunk_text(text)
                    for chunk in chunks:
                        all_chunks.append({
                            "url": data["url"],
                            'text': chunk,
                            'xpath': text_block['xpath'],
                            'tag': text_block['tag'],
                            'timestamp': data['timestamp'],
                            "type": "text"
                        })

                for image in extracted_data['images']:
                    image_path, image_bytes = download_image(image['url'])
                    if image_path is not None:
                        all_chunks.append({
                            'image_path': image_path,
                            'xpath': image['xpath'],
                            "url": data["url"],
                            'timestamp': data['timestamp'],
                            "image_bytes": image_bytes,
                            "type": "image"
                        })

                # with open("chunks.json", "w") as f:
                #     json.dump(all_chunks, f)

                index(all_chunks)

                print(f"[Consumer] Processed {filename}:")
            except FileNotFoundError:
                print(f"[Consumer] File not found: {filepath}")
            except Exception as e:
                print(f"[Consumer] Error processing {filepath}: {e}")

        time.sleep(0.1)
