import json
import os

class FileHandler:
    def __init__(self, save_dir="data"):
        self.save_dir = save_dir
        print("FileHandler called")
        print(save_dir)
        os.makedirs(self.save_dir, exist_ok=True)

    def get_file_path(self, filename: str, extension: str) -> str:
        """
        Generates the full path for the file to be saved, adding the appropriate extension.
        """
        return os.path.join(self.save_dir, f"{filename}{extension}")

    def save_json(self, filename: str, data: dict):
        """
        Saves data as a JSON file.
        """
        file_path = self.get_file_path(filename, ".json")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"JSON data saved to: {file_path}")
        except Exception as e:
            print(f"Failed to save JSON file: {e}")

    def save_html(self, filename: str, content: str):
        """
        Saves content as an HTML file.
        """
        file_path = self.get_file_path(filename, ".html")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"HTML content saved to: {file_path}")
        except Exception as e:
            print(f"Failed to save HTML file: {e}")

    def save_txt(self, filename: str, content: str):
        """
        Saves content as a plain text (.txt) file.
        """
        file_path = self._get_file_path(filename, ".txt")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Text content saved to: {file_path}")
        except Exception as e:
            print(f"Failed to save text file: {e}")

    def save_content(self, filename: str, content: str, file_type: str):
        """
        Determines the file type and saves the content accordingly.
        """
        if file_type == "json":
            try:
                data = json.loads(content)  # Assuming content is JSON string
                self.save_json(filename, data)
            except json.JSONDecodeError:
                print("Error: The content is not valid JSON format.")
        elif file_type == "html":
            self.save_html(filename, content)
        elif file_type == "txt":
            self.save_txt(filename, content)
        else:
            print("Unsupported file type. Supported types: json, html, txt.")
