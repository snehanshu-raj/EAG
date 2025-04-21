from bs4 import BeautifulSoup, NavigableString
from markitdown import MarkItDown
from urllib.parse import urlparse
from datetime import datetime
from file_handler import FileHandler

class WebContentExtractor:
    def __init__(self, save_dir="extracted_data"):
        self.save_dir = save_dir
        self.file_handler = FileHandler(save_dir)

    def tag_to_xpath(self, tag):
        if tag is None or not hasattr(tag, 'name'):
            return None
        path = []
        while tag and tag.name:
            siblings = tag.find_previous_siblings(tag.name)
            index = len(siblings) + 1
            path.insert(0, f"{tag.name}[{index}]")
            tag = tag.parent
        return '/' + '/'.join(path)

    def get_visible_text_blocks(self, soup):
        content_blocks = []
        tags_to_extract = ['p', 'span', 'div', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']

        for tag in soup.find_all(tags_to_extract):
            text = tag.get_text(separator=" ")
            if text:
                xpath = self.tag_to_xpath(tag)
                if xpath:
                    content_blocks.append({
                        "text": text,
                        "tag": tag.name,
                        "attrs": dict(tag.attrs),
                        "xpath": xpath
                    })
        return content_blocks

    def get_image_urls(self, soup: BeautifulSoup):
        image_data = []
        valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.webp')

        all_img_tags = soup.find_all('img', src=True)
        for tag in all_img_tags:
            try:
                src = tag.get("src", "")
                if src.lower().endswith(valid_extensions):
                    xpath = self.tag_to_xpath(tag)
                    if xpath:
                        image_data.append({
                            "url": src,
                            "tag": tag.name,
                            "attrs": dict(tag.attrs),
                            "xpath": xpath
                        })
            except Exception as e:
                print(f"Error extracting image info: {e}")
                continue

        return image_data

    def extract_content_from_html(self, html: str, base_url: str) -> dict:
        soup = BeautifulSoup(html, "html.parser")
        cleaned_html_str = str(soup)

        html_file_name = urlparse(base_url).netloc.replace(".", "_")
        html_file_path = self.file_handler.get_file_path(html_file_name, ".html")
        self.file_handler.save_html(html_file_name, cleaned_html_str)

        text_blocks = self.get_visible_text_blocks(soup)
        image_data = self.get_image_urls(soup)

        return {
            "text_blocks": text_blocks,
            "images": image_data
        }

    def structure_payload(self, url: str, timestamp: str, extracted: dict) -> dict:
        return {
            "url": url,
            "title": urlparse(url).netloc,
            "timestamp": timestamp,
            "text_blocks": extracted["text_blocks"],
            "images": extracted["images"]
        }

    def save_to_json(self, payload: dict):
        domain = urlparse(payload["url"]).netloc.replace(".", "_")
        timestamp = payload["timestamp"].replace(":", "_").replace(" ", "_")
        filename = f"{domain}_{timestamp}"
        return self.file_handler.save_json(filename, payload)

    def process_html(self, url: str, html: str, timestamp: str) -> dict:
        print(f"Processing HTML for: {url}")
        try:
            extracted = self.extract_content_from_html(html, url)
            payload = self.structure_payload(url, timestamp, extracted)
            self.save_to_json(payload)
            return payload
        except Exception as e:
            print(f"Failed to process HTML: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

if __name__ == "__main__":
    url = "https://example.com"
    timestamp = "2025-04-19T11:42:17.697157"

    with open("extracted_data/temp.html", "r", encoding="utf-8") as f:
        html = f.read()

    extractor = WebContentExtractor()
    result = extractor.process_html(url, html, timestamp)

    print("Result:", result)
