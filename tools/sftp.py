import os
import stat
from tools.base_tool import BaseTool
import paramiko

class Tool(BaseTool):
    def get_tool_name(self):
        return 'sftp'

    def connect(self):
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(
                hostname=self.config.get('host'),
                port=int(self.config.get('port', 22)),
                username=self.config.get('user'),
                password=self.config.get('password'),
                key_filename=self.config.get('key_filename'),
                timeout=10
            )
            self.sftp = self.client.open_sftp()
            self.remote_cwd = self.sftp.getcwd()
            self.local_cwd = os.getcwd()
            print(f"\nConnected to {self.config.get('user')}@{self.config.get('host')}.")
            print(f"Remote directory: {self.remote_cwd}")
            return True
        except Exception as e:
            print(f"Could not connect to SFTP server: {e}")
            return False

    def disconnect(self):
        if self.sftp:
            self.sftp.close()
        if self.client:
            self.client.close()

    def run_loop(self):
        while self.is_connected:
            try:
                prompt = f"sftp> "
                command_line = input(prompt).strip()
                if not command_line:
                    continue

                parts = command_line.split()
                command = parts[0].lower()

                if command in ['exit', 'quit']:
                    break
                elif command == 'pwd':
                    print(f"Remote directory: {self.remote_cwd}")
                elif command == 'lpwd':
                    print(f"Local directory: {self.local_cwd}")
                elif command == 'cd' and len(parts) > 1:
                    self.sftp.chdir(parts[1])
                    self.remote_cwd = self.sftp.getcwd()
                elif command == 'lcd' and len(parts) > 1:
                    os.chdir(parts[1])
                    self.local_cwd = os.getcwd()
                elif command == 'ls':
                    path = parts[1] if len(parts) > 1 else '.'
                    for attr in self.sftp.listdir_attr(path):
                        print(attr.filename)
                elif command == 'lls':
                    path = parts[1] if len(parts) > 1 else '.'
                    for item in os.listdir(path):
                        print(item)
                elif command == 'get' and len(parts) > 1:
                    remote_path = parts[1]
                    local_path = parts[2] if len(parts) > 2 else os.path.basename(remote_path)
                    self.sftp.get(remote_path, local_path)
                    print(f"Downloaded {remote_path} to {local_path}")
                elif command == 'put' and len(parts) > 1:
                    local_path = parts[1]
                    remote_path = parts[2] if len(parts) > 2 else os.path.basename(local_path)
                    self.sftp.put(local_path, remote_path)
                    print(f"Uploaded {local_path} to {remote_path}")
                elif command == 'help':
                    print("Available commands:\n  ls [path]       - List remote files\n  lls [path]      - List local files\n  cd <path>       - Change remote directory\n  lcd <path>      - Change local directory\n  pwd             - Print remote working directory\n  lpwd            - Print local working directory\n  get <remote> [local] - Download file\n  put <local> [remote]  - Upload file\n  exit, quit      - Disconnect")
                else:
                    print(f"Invalid command: {command}")
            except Exception as e:
                print(f"Error: {e}")

def run(config):
    tool = Tool(config)
    tool.run()
