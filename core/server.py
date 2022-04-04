import paramiko
import os
from settings import Settings


class Server(Settings):
    def __init__(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def ssh_connect(self, state):
        if state:
            if self.ping():
                if self.ssh.get_transport() is None:
                    self.ssh.connect(Settings.host, 22, Settings.user, Settings.password)
        else:
            if self.ssh.get_transport() is not None:
                if self.ssh.get_transport().is_active():
                    self.ssh.close()

    def ssh_command(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        outlines = stdout.readlines()
        output = "".join(outlines)
        return output

    @staticmethod
    def ping():
        """Check if server is online."""
        if not os.system("ping -c 1 " + Settings.host + " 2>&1 >/dev/null"):
            return True
        else:
            return False
