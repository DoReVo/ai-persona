from pathlib import Path
import click
import yaml

from llm.config import Config
from llm.telegram import process_telegram_exports

SCRIPT_DIR = Path(__file__).parent.resolve()
_DEFAULT_CONFIG_FILENAME = "config.yaml"
DEFAULT_CONFIG_PATH = SCRIPT_DIR / _DEFAULT_CONFIG_FILENAME


def load_config(path):
    with open(path) as f:
        raw_config = yaml.safe_load(f)
    return Config(**raw_config)


@click.group()
@click.option(
    "--config",
    "-c",
    "config_path",
    default=DEFAULT_CONFIG_PATH,
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    help=f"Path to YAML config file (default: '{_DEFAULT_CONFIG_FILENAME}' in script directory)",
)
@click.pass_context
def cli(ctx: click.Context, config_path: str):
    ctx.ensure_object(dict)
    cfg = load_config(config_path)
    ctx.obj["CONFIG"] = cfg
    pass


@click.command("test")
@click.pass_context
def test_function(ctx: click.Context):
    items = tuple(((x * 5, "ok") for x in range(5)))

    print(items)


cli.add_command(process_telegram_exports)
cli.add_command(test_function)

if __name__ == "__main__":
    cli()
