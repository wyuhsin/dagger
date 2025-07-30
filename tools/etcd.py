from tools.base_tool import BaseTool
import etcd3
from etcd3.exceptions import Etcd3Exception

class Tool(BaseTool):
    def get_tool_name(self):
        return 'etcd'

    def connect(self):
        try:
            self.client = etcd3.client(host=self.config.get('host', 'localhost'), port=int(self.config.get('port', 2379)))
            self.client.status()
            print(f"\nConnected to etcd server: {self.config.get('host')}.")
            return True
        except Etcd3Exception as e:
            print(f"Could not connect to etcd: {e}")
            return False

    def run_loop(self):
        while True:
            prompt = f"etcd://{self.config.get('host')}:{self.config.get('port')}> "
            command_string = input(prompt).strip()
            if command_string.lower() in ['exit', 'quit']:
                break
            parts = command_string.split(maxsplit=2)
            command = parts[0].lower()
            try:
                if command == 'get' and len(parts) == 2:
                    value, _ = self.client.get(parts[1])
                    print(value.decode('utf-8') if value else "(nil)")
                elif command == 'put' and len(parts) == 3:
                    self.client.put(parts[1], parts[2])
                    print("OK")
                elif command == 'delete' and len(parts) == 2:
                    print("1" if self.client.delete(parts[1]) else "0")
            except Etcd3Exception as e:
                print(f"Error: {e}")

def run(config):
    tool = Tool(config)
    tool.run()
