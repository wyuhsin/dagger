from tools.base_tool import BaseTool
import psycopg2
from psycopg2 import OperationalError, Error

class Tool(BaseTool):
    def get_tool_name(self):
        return 'postgresql'

    def connect(self):
        try:
            self.conn = psycopg2.connect(**self.config)
            self.conn.autocommit = True
            self.cursor = self.conn.cursor()
            print(f"\nConnected to PostgreSQL server: {self.config['host']}.")
            return True
        except OperationalError as e:
            print(f"Could not connect to PostgreSQL: {e}")
            return False

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def run_loop(self):
        while True:
            try:
                prompt = f"{self.config.get('user')}@{self.config.get('dbname')}> "
                query = input(prompt).strip()
                if query.lower() in ['exit', 'quit']:
                    break
                self.cursor.execute(query)
                if self.cursor.description:
                    rows = self.cursor.fetchall()
                    print(f"{len(rows)} row(s) in set")
                else:
                    print(f"Query OK, {self.cursor.statusmessage}")
            except Error as e:
                print(f"PostgreSQL Error: {e}")

def run(config):
    tool = Tool(config)
    tool.run()
