import readline
import os

class BaseTool:
    """A base class for all command-line tools."""

    def __init__(self, config):
        self.config = config
        self.history_file = os.path.expanduser(f"~/.{self.get_tool_name()}_cli_history")
        self.is_connected = False

    def get_tool_name(self):
        """Should return the name of the tool (e.g., 'ssh', 'mysql')."""
        raise NotImplementedError

    def setup_history(self):
        """Loads command history from a file."""
        try:
            readline.read_history_file(self.history_file)
        except FileNotFoundError:
            pass

    def save_history(self):
        """Saves command history to a file."""
        readline.write_history_file(self.history_file)

    def connect(self):
        """Establishes the connection to the server."""
        raise NotImplementedError

    def disconnect(self):
        """Closes the connection to the server."""
        pass # Not all tools may need an explicit disconnect

    def run_loop(self):
        """The main interactive loop for the tool."""
        raise NotImplementedError

    def run(self):
        """The main entry point to run the tool."""
        self.setup_history()
        try:
            if self.connect():
                self.is_connected = True
                self.run_loop()
        except Exception as e:
            print(f"A critical error occurred: {e}")
        finally:
            if self.is_connected:
                self.disconnect()
            self.save_history()
            print("--------------------------------------------------")
            print(f"{self.get_tool_name().capitalize()} session finished.")
