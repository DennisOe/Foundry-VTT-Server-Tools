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
        self.shutdown()
        self.ssh_command(f"tar -czf backup_{date}.tar.gz {backup_folders}")
        self.start()
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
    foundry = Foundry()
    foundry.ssh_connect(True)
    print(f"Connected to... {foundry.settings['host']}")
    commands = "Commands: status, start, shutdown, restart, backup+download, backup, download, settings, quit, help"
    print(commands)
    cli = True
    while cli:
        cli = input(">> ")
        if cli.lower() in ["quit", "q", "exit", "e"]:
            cli = False
        elif cli.lower() in ["status", ]:
            print("Foundry is ONLINE." if foundry.status() else "Foundry is OFFLINE.")
        elif cli.lower() in ["start", ]:
            foundry.start()
            print("Foundry is started." if foundry.status() else "Foundry is shutdown.")
        elif cli.lower() in ["shutdown", ]:
            foundry.shutdown()
            print("Foundry is started." if foundry.status() else "Foundry is shutdown.")
        elif cli.lower() in ["restart", "re"]:
            foundry.restart()
            print("Foundry is restarted." if foundry.status() else "Restart failed.")
        elif cli.lower() in ["backup", ]:
            foundry.backup()
        elif cli.lower() in ["download", ]:
            foundry.download()
        elif cli.lower() in ["backup+download", "bd"]:
            foundry.backup()
            foundry.download()
        elif cli.lower() in ["settings", ]:
            print("Edit settings:", ", ".join(foundry.settings.keys()))
        elif cli.lower() in ["host", "user", "password", "proxy", "install_location", "vtt_name", "vtt_folder",
                             "data_folder", "download_folder", "last_backup"]:
            if cli.lower() in foundry.settings.keys():
                setting_key = cli.lower()
                print(foundry.settings[setting_key])
                cli = input("Edit settings? y/n?\n>> ")
                if cli.lower() in ["yes", "y"]:
                    foundry.settings[setting_key] = input(">> ")
                    foundry.write()
        elif cli == "":
            cli = True
            print(commands)
        else:
            print(commands)
    else:
        foundry.ssh_connect(False)
        print(f"Disconnected from... {foundry.settings['host']}")


if __name__ == "__main__":
    main()
