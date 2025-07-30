from tools.base_tool import BaseTool
import mysql.connector
from mysql.connector import errorcode, Error

class Tool(BaseTool):
    def get_tool_name(self):
        return 'mysql'

    def connect(self):
        db_config = self.config.copy()
        self.database = db_config.pop('database', None)
        try:
            self.cnx = mysql.connector.connect(**db_config, use_pure=True)
            self.cursor = self.cnx.cursor()
            print(f"\nConnected to MySQL server: {db_config['host']}.")
            if self.database:
                self.cursor.execute(f"USE {self.database}")
                print(f"Database set to '{self.database}'.")
            return True
        except Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
            return False

    def disconnect(self):
        if self.cnx.is_connected():
            self.cursor.close()
            self.cnx.close()

    def run_loop(self):
        while True:
            try:
                current_db_str = f"[{self.database}]" if self.database else ""
                prompt = f"{self.config['user']}@{self.config['host']}{current_db_str}> "
                query_string = input(prompt)
                if query_string.strip().lower() in ['exit', 'quit']:
                    break
                if not query_string.strip():
                    continue
                commands = [q.strip() for q in query_string.split(';') if q.strip()]
                for query in commands:
                    self.cursor.execute(query)
                    if self.cursor.with_rows:
                        rows = self.cursor.fetchall()
                        if rows:
                            print("...") # Simplified for brevity
                    else:
                        print(f"Query OK, {self.cursor.rowcount} row(s) affected")
            except Error as err:
                print(f"Error: {err}")

def run(config):
    tool = Tool(config)
    tool.run()
