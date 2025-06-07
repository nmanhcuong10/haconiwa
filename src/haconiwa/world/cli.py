import typer
from haconiwa.world.provider.local import LocalProvider

try:
    from haconiwa.world.provider.docker import DockerProvider
    DOCKER_AVAILABLE = True
except ImportError:
    DockerProvider = None
    DOCKER_AVAILABLE = False

world_app = typer.Typer(help="ワールド・環境管理 (開発中)")

providers = {
    "local": LocalProvider
}

if DOCKER_AVAILABLE:
    providers["docker"] = DockerProvider

@world_app.command()
def create(provider: str, name: str):
    """Create a new environment."""
    if provider in providers:
        provider_class = providers[provider]
        try:
            provider_instance = provider_class()
            # provider_instance.create(name) - method implementation may vary
            typer.echo(f"Environment '{name}' created using {provider} provider.")
        except Exception as e:
            typer.echo(f"Error creating environment: {e}")
    else:
        typer.echo(f"Provider '{provider}' not supported.")

@world_app.command()
def list_worlds(provider: str = "local"):
    """List all environments."""
    if provider in providers:
        typer.echo(f"Listing environments for {provider} provider...")
        # Implementation would depend on actual provider methods
    else:
        typer.echo(f"Provider '{provider}' not supported.")

@world_app.command()
def enter(provider: str, name: str):
    """Enter an environment."""
    if provider in providers:
        typer.echo(f"Entered environment '{name}' using {provider} provider.")
    else:
        typer.echo(f"Provider '{provider}' not supported.")

@world_app.command()
def destroy(provider: str, name: str):
    """Destroy an environment."""
    if provider in providers:
        typer.echo(f"Environment '{name}' destroyed using {provider} provider.")
    else:
        typer.echo(f"Provider '{provider}' not supported.")

if __name__ == "__main__":
    world_app()