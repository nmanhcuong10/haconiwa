import os

__all__ = ["ResourceManager"]

class ResourceManager:
    def __init__(self):
        self.resources = {}

    def load_file(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = file.read()
                self.resources[file_path] = data
        else:
            raise FileNotFoundError(f"{file_path} not found.")

    def get_resource(self, file_path):
        return self.resources.get(file_path, None)

    def clear_resources(self):
        self.resources.clear()