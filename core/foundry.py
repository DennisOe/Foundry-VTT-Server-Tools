from server import Server
from datetime import datetime


class Foundry(Server):
    def status(self) -> str:
        return self.ssh_command("pm2 list")

    def start(self) -> bool:
        self.ssh_command("pm2 start "
                         "\"node {install_location}/{vtt_folder}/resources/app/main.js "
                         "--dataPath={install_location}/{data_folder}\" "
                         "--name \"{vtt_name}\"".format_map(self.settings))
        return True

    def shutdown(self) -> bool:
        self.ssh_command("pm2 delete foundry-server")
        return False

    def restart(self) -> True:
        self.ssh_command("pm2 restart foundry-server")
        return True

    def backup(self):
        date = datetime.today().strftime("%Y-%m-%d")
        backup_folders = " ".join([self.settings["vtt_folder"], self.settings["data_folder"]])
        self.ssh_command(f"tar -czf backup_{date}.tar.gz {backup_folders}")
        self.settings["last_backup"] = date
        self.write()

    def download(self):
        pass


f = Foundry()
f.ssh_connect(True)
f.backup()
