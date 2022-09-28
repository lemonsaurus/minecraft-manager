import subprocess


class SubProcessor:
    """A class for running commands as subprocesses"""

    @staticmethod
    def run(command: str, cwd: bool = None):
        """Execute the command, and return the output."""
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True,
            executable='/bin/bash',
        )
        return result.stdout
