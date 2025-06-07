import os

__all__ = ['LocalProvider', 'DockerProvider']

class BaseProvider:
    def __init__(self):
        self.name = self.__class__.__name__

class LocalProvider(BaseProvider):
    def __init__(self):
        super().__init__()
        # Local provider specific initialization

class DockerProvider(BaseProvider):
    def __init__(self):
        super().__init__()
        # Docker provider specific initialization

def register_providers():
    providers = {
        'local': LocalProvider,
        'docker': DockerProvider,
    }
    return providers

providers = register_providers()