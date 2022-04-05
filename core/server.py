import os
import paramiko
from settings import Settings


class Server(Settings):
    """This class manages interaction with remote server."""
    def __init__(self):
        super().__init__()
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def ssh_connect(self, state: bool):
        """Connect or disconnect ssh."""
        if state:
            if self.ping():
                if not self.ssh_activ():
                    self.ssh.connect(self.settings["host"], 22, self.settings["user"], self.settings["password"])
        else:
            if self.ssh_activ():
                self.ssh.close()

    def ssh_activ(self) -> bool:
        """Check if ssh connection is established."""
        if self.ssh.get_transport() is not None:
            if self.ssh.get_transport().is_active():
                return True
            else:
                return False
        else:
            return False

    def ssh_command(self, command: str) -> str:
        """Issues bash commands."""
        if self.ssh_activ():
            stdin, stdout, stderr = self.ssh.exec_command(command)
            outlines = stdout.readlines()
            output = "".join(outlines)
            return output

    def ping(self) -> bool:
        """Check if server is online."""
        if not os.system("ping -c 1 {host} 2>&1 >/dev/null".format_map(self.settings)):
            return True
        else:
            return False
