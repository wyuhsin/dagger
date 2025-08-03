import paramiko
import socket
import sys
import termios
import tty
import select
from tools.base_tool import BaseTool

def posix_shell(chan):
    """Starts a fully interactive shell session using select to multiplex I/O."""
    # Get the original terminal attributes to restore them on exit
    old_tty = termios.tcgetattr(sys.stdin)
    try:
        # Set the terminal to raw mode, allowing character-by-character input
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        chan.settimeout(0.0)

        while True:
            # Wait until either the SSH channel or stdin has data to be read
            readable, _, _ = select.select([chan, sys.stdin], [], [])

            # Handle data from the remote server
            if chan in readable:
                try:
                    data = chan.recv(1024)
                    if not data: # An empty read indicates the session has closed
                        break
                    # Write the server's output directly to the user's screen
                    sys.stdout.write(data.decode('utf-8', 'ignore'))
                    sys.stdout.flush()
                except socket.timeout:
                    pass
                except Exception:
                    break # Exit on other channel errors

            # Handle data from the user's keyboard
            if sys.stdin in readable:
                try:
                    char = sys.stdin.read(1)
                    if not char: # An empty read indicates EOF (e.g., Ctrl+D)
                        break
                    # Send the user's input directly to the server
                    chan.send(char)
                except EOFError:
                    break

    finally:
        # Always restore the original terminal settings
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)

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
            # Request a PTY (pseudo-terminal) for a true interactive session
            self.channel = self.client.invoke_shell(term='xterm')
            print(f"\nConnected to {self.config.get('user')}@{self.config.get('host')}. Session started.")
            return True
        except Exception as e:
            print(f"Could not connect to SSH server: {e}")
            return False

    def disconnect(self):
        if self.client:
            self.client.close()

    def run_loop(self):
        # Hand over terminal control to the interactive shell function
        posix_shell(self.channel)

    def run(self):
        # We bypass the base tool's run() as we don't need its history management.
        # The remote shell handles its own history.
        try:
            if self.connect():
                self.is_connected = True
                self.run_loop()
        except Exception as e:
            print(f"A critical error occurred: {e}")
        finally:
            if self.is_connected:
                self.disconnect()
            print("\n--------------------------------------------------")
            print(f"{self.get_tool_name().capitalize()} session finished.")

def run(config):
    tool = Tool(config)
    tool.run()