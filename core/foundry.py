from server import Server
from datetime import datetime


class Foundry(Server):
    """Main interface Class for foundry."""
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

    def restart(self) -> bool:
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
        self.sftp_connect()
        self.sftp_download(path=remote_local_path)
        self.sftp_connect()
        self.delete_file(remote_local_path["remote"])


class CliHandler(Foundry):
    """CliHandler manages all user inputs."""
    def __init__(self):
        super().__init__()
        self.cli = True
        self.cli_commands = {("help", "h"): self.print_commands,
                             ("quit", "q", "exit", "e"): self.quit_cli,
                             ("status", "info"): self.server_info,
                             ("start", "shutdown", "restart"): self.server_state,
                             ("backup", "download", "backup+download", "bd"): self.file_handling,
                             ("settings", "host", "user", "password", "proxy",
                              "install_location", "vtt_name", "vtt_folder",
                              "data_folder", "download_folder", "last_backup"): self.edit_settings, }

    def print_commands(self, *argv: list[int]):
        print("Commands:\n", ", ".join([", ".join(e) for e in self.cli_commands.keys()]))

    def quit_cli(self, *argv: list[int]):
        self.cli = False

    def server_info(self, *argv: list[int]):
        print("Foundry is ONLINE." if self.status() else "Foundry is OFFLINE.")

    def server_state(self, *argv: list[int]):
        if not argv[0]:
            self.start()
            print("Foundry is started." if self.status() else "Foundry is shutdown.")
        elif argv[0] == 1:
            self.shutdown()
            print("Foundry is started." if self.status() else "Foundry is shutdown.")
        elif argv[0] == 2:
            self.restart()
            print("Foundry is restarted." if self.status() else "Restart failed.")

    def file_handling(self, *argv: list[int]):
        if not argv[0]:
            self.backup()
        elif argv[0] == 1:
            self.download()
        elif argv[0] in [2, 3]:
            self.backup()
            self.download()

    def edit_settings(self, *argv: list[int]):
        if not argv[0]:
            print("Edit settings:", ", ".join(self.settings.keys()))
        elif argv[0] >= 1:
            self.cli = input("Edit settings? y/n?\n>> ")
            if self.cli.lower() in ["yes", "y"]:
                self.settings[list(self.cli_commands.keys())[5][argv[0]]] = input(">> ")
                self.write()


def main():
    print("Foundry-VTT-Server-Tools")
    cli_handler = CliHandler()
    cli_handler.ssh_connect()
    print(f"Connected to... {cli_handler.settings['host']}")
    cli_handler.print_commands()
    while cli_handler.cli:
        cli_handler.cli = input(">> ")
        for commands in cli_handler.cli_commands.keys():
            if cli_handler.cli in commands:
                # cli_handler.cli -> user input ie. "status"
                # commands -> dict key -> (status, info)
                # dict -> {(key0, key1): function,}
                # function is called with index to determine which keyword in tuple is used
                cli_handler.cli_commands[commands](commands.index(cli_handler.cli))
    else:
        cli_handler.ssh_connect()
        print(f"Disconnected from... {cli_handler.settings['host']}")


if __name__ == "__main__":
    main()
