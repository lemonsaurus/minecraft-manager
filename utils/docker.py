from .subprocessor import SubProcessor


class Docker(SubProcessor):
    """An interface for running docker commands."""

    def compose_pull(self, compose_file: str):
        """Do a docker compose pull on the file."""
        return self.run(f"docker compose -f {compose_file} pull")

    def compose_up(self, compose_file: str):
        """Do a docker compose up -d on the file."""
        return self.run(f"docker compose -f {compose_file} up -d --remove-orphans")

    def compose_down(self, compose_file: str):
        """Do a docker compose down on the file."""
        return self.run(f"docker compose -f {compose_file} down")

    def logs(self, container_name: str, tail):
        """Show the latest 100 items in the logs for the specified container name"""
        return self.run(f"docker logs {container_name} -n {tail}")

    def ps(self):
        """A docker ps, so we can see what's running."""
        return self.run("docker ps")

    def exec(self, command):
        """A docker exec, so we can execute commands inside the containers."""
        return self.run(f"docker exec {command}")
