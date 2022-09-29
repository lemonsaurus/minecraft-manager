#!/usr/bin/python3

import re
import textwrap
import time
import math
import os
import pathlib

import typer
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn

from utils.docker import Docker


# Regex expressions for parsing docker container names!
SERVER_CONTAINER_EXPRESSION = r"\s([\w-]+)?-server"
BACKUP_CONTAINER_EXPRESSION = r"\s[\w-]+-backup"

# Crawl the modpacks folder to discover modpack names
MODPACK_SHORT_NAMES = [
    entry.name for entry in pathlib.Path("/opt/minecraft/modpacks").iterdir() if entry.is_dir()
]

# Crawl the docker-compose files to find full modnames
MODPACK_FULL_NAMES = {}
for modpack in MODPACK_SHORT_NAMES:
    with open(f"/opt/minecraft/modpacks/{modpack}/docker-compose.yaml") as compose_file:
        for line in compose_file.readlines():
            if "MODPACK: " in line:
                full_name = line.strip().split('MODPACK: "')[1][:-1]
                MODPACK_FULL_NAMES[modpack] = full_name


# Helper class instances
docker = Docker()
cli = typer.Typer(help="Minecraft Server Loader")
spinner = Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
)

# Exception classes
class ContainerNotFound(Exception):
    """An error raised when a container could not be found."""

# Helper functions
def _validate_modpack(user_input: str):
    """
    When a user provides a modpack name, this function checks whether it's valid.

    If the modpack folder isn't found, returns None.
    """
    if user_input in MODPACK_SHORT_NAMES:
        return user_input
    else:
        return None


def _get_human_modpack(modpack: str = None):
    """Get a nice, human-readable modpack name for display."""
    if not modpack:
        modpack = _get_active_modpack()
    return MODPACK_FULL_NAMES.get(modpack)


def _get_active_modpack():
    """Checks the 'docker ps' output to see which modpack is currently active, if any."""
    modpack = re.search(SERVER_CONTAINER_EXPRESSION, docker.ps())

    if modpack:
        return modpack.group(1)
    else:
        return None

def _server_is_running():
    """Check if the server is currently running or paused."""
    container_name = _get_game_container_name()
    list = docker.exec(f"{container_name} rcon-cli list")
    list = list.split(": ")[0]
    number = int(list.split(" ")[2])

    if number:
        return True
    return False


def _get_game_container_name():
    """Checks the 'docker ps' output to fetch the currently active game container name, if any."""
    container_name = re.search(SERVER_CONTAINER_EXPRESSION, docker.ps())

    if container_name:
        return container_name.group(0)
    else:
        return None

def _get_backup_container_name():
    """Checks the 'docker ps' output to fetch the currently active game container name, if any."""
    container_name = re.search(BACKUP_CONTAINER_EXPRESSION, docker.ps())

    if container_name:
        return container_name.group(0)
    else:
        return None

def _get_compose_file(modpack=None):
    """
    Get the compose file for the provided modpack.

    If no modpack is provided, get for currently running modpack.
    """
    if modpack:
        return f"/opt/minecraft/modpacks/{modpack}/docker-compose.yaml"
    else:
        return f"/opt/minecraft/modpacks/{_get_active_modpack()}/docker-compose.yaml"

def _do_instant_backup():
    """
    Do a backup of whatever is currently running.

    Also, prune so only the 3 latest backups remain.
    """
    backup_container = _get_backup_container_name()

    if backup_container:
        return docker.exec(f"{backup_container} backup now")
    else:
        return None


# Typer commands
@cli.command()
def load(new_modpack: str):
    """Back up and shut down the current modpack, and load a new one."""
    if new_modpack == _get_active_modpack():
        print(f"❌  [red]Aborted:[/red]Requested modpack is already running!")
        return
    elif not _validate_modpack(new_modpack):
        print(f"❌  [red]Aborted:[/red]Could not resolve modpack name {new_modpack}!")
        return

    human_current_modpack = _get_human_modpack()
    human_new_modpack = _get_human_modpack(new_modpack)

    with spinner as progress:
        if _get_active_modpack() and _server_is_running():
            progress.add_task(f"Backing up current modpack ([blue]{human_current_modpack}[/blue]")
            _do_instant_backup()

        if _get_active_modpack():
            progress.add_task(f"Shutting down currently running modpack ([blue]{human_current_modpack}[/blue])")
            docker.compose_down(_get_compose_file())

        progress.add_task(f"Starting up the new modpack ([green]{human_new_modpack}[/green])")
        new_compose_file = _get_compose_file(new_modpack)
        docker.compose_up(new_compose_file)
        time.sleep(20)


    print(f"✅  Active modpack is now [blue]{human_new_modpack}[/blue]! It may take up to a few minutes before the server is fully available.")


@cli.command()
def backup():
    """Do a backup of the currently running modpack."""
    if not _server_is_running():
        print(f"❌  [red]Aborted:[/red] Server is currently [blue]paused[/blue] and cannot be backed up.")
        return

    with spinner as progress:
        progress.add_task(f"Backing up [blue]{_get_active_modpack()}[/blue]...")
        result = _do_instant_backup()

        if result:
            print(result)
        else:
            raise ContainerNotFound("Could not find an active backup container!")

    print(f"✅  Backup complete!")


@cli.command()
def status():
    """Check the current status of the currently running modpack."""
    container_name = _get_game_container_name()

    if container_name:
        _list = docker.exec(f"{container_name} rcon-cli list")
        current_day = docker.exec(f"{container_name} rcon-cli time query day").split("\n")[0].split(" ")[-1]
        current_time = docker.exec(f"{container_name} rcon-cli time query daytime").split("\n")[0].split(" ")[-1]
        server_running = _server_is_running()

        # Sanitize output
        players_online, player_list = _list.split(": ")
        player_list = player_list.split("\n")[0]
        ingame_hours = math.floor(int(current_time) / 1000 + 8) % 24
        ingame_minutes = int((int(current_time) % 1000) / 1000.0 * 60)
        ingame_time = f"{ingame_hours:02}:{ingame_minutes:02}"

        status = textwrap.dedent(f"""\
            [bold magenta]{_get_human_modpack()}[/bold magenta]

            Current status:      {"[green bold]Running[/green bold]" if server_running else "[red bold]Paused[/red bold]"}
            Ingame days passed:  [bold blue]{current_day} days[/bold blue]
            Current ingame time: [bold yellow]{ingame_time}[/bold yellow]

            {players_online}{":" if player_list else ""}
            {player_list if player_list else ""}
            """
        )
        print(status)
    else:
        raise ContainerNotFound("Could not find an active game container!")

@cli.command()
def stop():
    """Stop the currently running server."""
    human_current_modpack = _get_human_modpack()
    with spinner as progress:
        progress.add_task(f"Shutting down currently running modpack ([blue]{human_current_modpack}[/blue])")
        docker.compose_down(_get_compose_file())


@cli.command()
def logs(service: str = "server", tail: str = "100", follow: bool = False):
    """Show the log tail for the server or backup service, up to 2000 lines."""
    if service.lower() == "server":
        container_name = _get_game_container_name()
    elif service.lower() == "backup":
        container_name = _get_backup_container_name()

    if not tail.isnumeric() or int(tail) > 2000:
        print(f"❌ [red] Request too large:[/red] Please select a tail of [blue]less than 2000 lines[/blue].")
        return

    if follow:
        os.system(f"docker logs {container_name} --tail {tail} --follow")
        return

    print(f"[cyan]{docker.logs(container_name, tail)}[/cyan]")


@cli.command(name="list")
def _list():
    """List all the available modpacks to switch between."""
    print(f"[cyan bold]Available modpacks:[/cyan bold]")
    for shortname, fullname in MODPACK_FULL_NAMES.items():
        print(f"• [green bold]{fullname}[/green bold] ([yellow]{shortname}[/yellow])")


# Entry point for this application
if __name__ == "__main__":
    cli()
