from server import Server
from datetime import datetime


class Foundry(Server):
    def status(self) -> bool:
        return True if "online" in self.ssh_command("pm2 list") else False

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
        remote_local_path = {"remote": "{install_location}/backup_{last_backup}.tar.gz".format_map(self.settings),
                             "local": "{download_folder}/backup_{last_backup}.tar.gz".format_map(self.settings)}
        self.sftp_connect(state=True)
        self.sftp_download(path=remote_local_path)
        self.sftp_connect(state=False)
        self.delete_file(remote_local_path["remote"])


def main():
    print("Foundry-VTT-Server-Tools")
    f = Foundry()
    f.ssh_connect(True)
    print("Connected...")
    commands = "Commands: \"status\", \"start\", \"shutdown\", \"restart\", \"backup\", \"download\", \"backup " \
               "download\", \"exit\", \"help\""
    print(commands)
    cli = True
    while cli:
        cli = input()
        if cli.lower() == "exit":
            cli = False
        elif cli.lower() == "status":
            print("Foundry is ONLINE." if f.status() else "Foundry is OFFLINE.")
        elif cli.lower() == "start":
            f.start()
        elif cli.lower() == "shutdown":
            f.shutdown()
        elif cli.lower() == "restart":
            f.restart()
        elif cli.lower() == "backup":
            f.backup()
        elif cli.lower() == "download":
            f.download()
        elif cli.lower() == "backup download":
            f.backup()
            f.download()
        else:
            print(commands)
    else:
        f.ssh_connect(False)
        print("Disconnected...")


if __name__ == "__main__":
    main()
