from tools.base_tool import BaseTool
import sqlite3

class Tool(BaseTool):
    def get_tool_name(self):
        return 'sqlite'

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.config.get('path'))
            self.cursor = self.conn.cursor()
            print(f"\nConnected to SQLite database: {self.config.get('path')}.")
            return True
        except sqlite3.Error as e:
            print(f"Could not connect to SQLite: {e}")
            return False

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def run_loop(self):
        while True:
            try:
                query = input("sqlite> ").strip()
                if query.lower() in ['exit', 'quit']:
                    break
                self.cursor.execute(query)
                if query.lower().startswith('select'):
                    rows = self.cursor.fetchall()
                    # ... (printing logic omitted for brevity)
                    print(f"{len(rows)} row(s) in set")
                else:
                    self.conn.commit()
                    print(f"Query OK, {self.cursor.rowcount} row(s) affected")
            except sqlite3.Error as e:
                print(f"SQLite Error: {e}")

def run(config):
    tool = Tool(config)
    tool.run()
