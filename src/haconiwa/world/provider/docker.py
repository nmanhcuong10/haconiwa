try:
    import docker
    from docker.models.containers import Container
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    Container = None

from haconiwa.core.config import Config

class DockerProvider:
    def __init__(self):
        if not DOCKER_AVAILABLE:
            raise ImportError("Docker is not available. Install docker with: pip install docker")
        self.client = docker.from_env()
        self.config = Config()

    def create_container(self, image: str, name: str, **kwargs) -> Container:
        return self.client.containers.run(image, name=name, detach=True, **kwargs)

    def start_container(self, container_id: str):
        container = self.client.containers.get(container_id)
        container.start()

    def stop_container(self, container_id: str):
        container = self.client.containers.get(container_id)
        container.stop()

    def remove_container(self, container_id: str):
        container = self.client.containers.get(container_id)
        container.remove()

    def build_image(self, path: str, tag: str):
        self.client.images.build(path=path, tag=tag)

    def manage_volumes(self, name: str, **kwargs):
        return self.client.volumes.create(name=name, **kwargs)

    def configure_network(self, name: str, **kwargs):
        return self.client.networks.create(name=name, **kwargs)

    def connect_containers(self, network_name: str, container_id: str):
        network = self.client.networks.get(network_name)
        network.connect(container_id)

    def set_resource_limits(self, container_id: str, cpu_quota: int, mem_limit: str):
        container = self.client.containers.get(container_id)
        container.update(cpu_quota=cpu_quota, mem_limit=mem_limit)

    def health_check(self, container_id: str):
        container = self.client.containers.get(container_id)
        return container.attrs['State']['Health']

    def log_container(self, container_id: str):
        container = self.client.containers.get(container_id)
        return container.logs()

    def debug_container(self, container_id: str):
        container = self.client.containers.get(container_id)
        return container.exec_run('sh', tty=True);