import os
from paramiko import SSHClient, AutoAddPolicy
from settings import Settings


class Server(Settings):
    """This class manages interaction with remote server."""
    def __init__(self) -> None:
        super().__init__()
        self.ssh: SSHClient = SSHClient()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        self.sftp = None

    def ssh_connect(self) -> None:
        """Connect or disconnect ssh."""
        if not self.ping():
            return
        if not self.ssh_activ():
            self.ssh.connect(self.settings["host"], 22, self.settings["user"], self.settings["password"])
        elif self.ssh_activ():
            self.ssh.close()

    def ssh_activ(self) -> bool:
        """Check if ssh connection is established."""
        if self.ssh.get_transport() is None:
            return False
        elif self.ssh.get_transport().is_active():
            return True
        else:
            return False

    def ssh_command(self, command: str) -> str:
        """Issues bash commands."""
        if self.ssh_activ():
            stdin, stdout, stderr = self.ssh.exec_command(command)
            outlines: list[str] = stdout.readlines()
            output: str = "".join(outlines)
            return output

    def sftp_connect(self) -> None:
        if self.sftp is None:
            self.sftp = self.ssh.open_sftp()
        else:
            self.sftp.close()

    def sftp_download(self, path: dict) -> None:
        try:
            self.sftp.get(path["remote"], path["local"])
        except IOError:
            return False

    def delete_file(self, path: str) -> None:
        self.ssh_command(f"rm {path}")

    def ping(self) -> bool:
        """Check if server is online."""
        if not os.system("ping -c 1 {host} 2>&1 >/dev/null".format_map(self.settings)):
            return True
        else:
            return False
