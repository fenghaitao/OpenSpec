"""Main CLI entry point for OpenSpec."""

import click
from rich.console import Console

from .commands import change, init, show, spec, validate, view, archive, update, list_cmd

console = Console()


@click.group()
@click.version_option(version="0.14.0", prog_name="openspec")
@click.help_option("-h", "--help")
def main():
    """OpenSpec - AI-native system for spec-driven development."""
    pass


# Add all command groups
main.add_command(change.change)
main.add_command(init.init)
main.add_command(show.show)
main.add_command(spec.spec)
main.add_command(validate.validate)
main.add_command(view.view)
main.add_command(archive.archive)
main.add_command(update.update)
main.add_command(list_cmd.list_changes)


if __name__ == "__main__":
    main()