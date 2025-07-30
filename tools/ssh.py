import paramiko
import time
from tools.base_tool import BaseTool

class Tool(BaseTool):
    def get_tool_name(self):
        return 'ssh'

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
            self.channel = self.client.invoke_shell()
            time.sleep(0.5)
            while self.channel.recv_ready():
                self.channel.recv(4096)
            print(f"\nConnected to {self.config.get('user')}@{self.config.get('host')}. Type 'exit' or 'quit' to leave.")
            return True
        except Exception as e:
            print(f"Could not connect to SSH server: {e}")
            return False

    def disconnect(self):
        if self.client:
            self.client.close()

    def run_loop(self):
        while self.is_connected:
            prompt = f"[{self.config.get('user')}@{self.config.get('host')}]$ "
            command = input(prompt).strip()

            if command.lower() in ['exit', 'quit']:
                break
            if not command:
                continue

            self.channel.send(command + '\n')
            time.sleep(0.2)
            output = ""
            while self.channel.recv_ready():
                output += self.channel.recv(4096).decode('utf-8', errors='ignore')
            
            lines = output.replace('\r\n', '\n').split('\n')
            if lines and lines[0].strip() == command:
                lines = lines[1:]
            if lines and (']#' in lines[-1] or ']$' in lines[-1]):
                lines = lines[:-1]

            cleaned_output = "\n".join(lines).strip()
            if cleaned_output:
                print(cleaned_output)

def run(config):
    tool = Tool(config)
    tool.run()
