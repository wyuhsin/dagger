from tools.base_tool import BaseTool
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, PyMongoError

class Tool(BaseTool):
    def get_tool_name(self):
        return 'mongo'

    def connect(self):
        try:
            uri = f"mongodb://{self.config.get('user')}:{self.config.get('password')}@{self.config.get('host')}:{self.config.get('port', 27017)}/"
            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ismaster')
            self.db = self.client[self.config.get('database', 'admin')]
            print(f"\nConnected to MongoDB server: {self.config.get('host')}.")
            return True
        except (ConnectionFailure, OperationFailure) as err:
            print(f"Could not connect to MongoDB: {err}")
            return False

    def disconnect(self):
        if self.client:
            self.client.close()

    def run_loop(self):
        while True:
            try:
                prompt = f"mongodb://{self.config.get('host')}/{self.db.name}> "
                command_string = input(prompt)
                if command_string.strip().lower() in ['exit', 'quit']:
                    break
                if command_string.startswith("db."):
                    result = eval(command_string, {"db": self.db})
                    if hasattr(result, '__iter__') and not isinstance(result, (dict, str)):
                        for doc in result:
                            print(doc)
                    else:
                        print(result)
                elif command_string.lower().startswith("use "):
                    self.db = self.client[command_string.split()[1]]
                    print(f"Switched to db '{self.db.name}'")
            except PyMongoError as e:
                print(f"Execution Error: {e}")

def run(config):
    tool = Tool(config)
    tool.run()
