import os


class FileHandler:
    @staticmethod
    def save_content(content, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)

    @staticmethod
    def save_image(image_bytes, path):
        with open(path, 'wb') as file:
            file.write(image_bytes)
