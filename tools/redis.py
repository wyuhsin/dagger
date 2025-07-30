from tools.base_tool import BaseTool
import redis
from redis.exceptions import ConnectionError, RedisError

class Tool(BaseTool):
    def get_tool_name(self):
        return 'redis'

    def connect(self):
        try:
            db = int(self.config.get('db', 0))
            self.r = redis.Redis(host=self.config['host'], port=self.config['port'], password=self.config.get('password'), db=db, decode_responses=True)
            self.r.ping()
            print(f"\nConnected to Redis server: {self.config['host']}.")
            return True
        except ConnectionError as err:
            print(f"Could not connect to Redis server: {err}")
            return False

    def run_loop(self):
        while True:
            try:
                prompt = f"{self.config['host']}:{self.config['port']}> "
                command_string = input(prompt)
                if command_string.strip().lower() in ['exit', 'quit']:
                    break
                if not command_string.strip():
                    continue
                
                result = self.r.execute_command(command_string)
                
                # Check if the result is a list and print each item on a new line
                if isinstance(result, list):
                    for i, item in enumerate(result):
                        print(f"{i+1}) \"{item}\"")
                else:
                    print(result)

            except RedisError as err:
                print(f"Redis Error: {err}")

def run(config):
    tool = Tool(config)
    tool.run()
