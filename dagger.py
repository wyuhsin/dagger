import os
import sys
import toml
import importlib
import argparse
from ui import print_in_columns

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def get_config(service_name):
    """Loads the config file for a given service."""
    # Map sftp to use ssh's config
    config_service = 'ssh' if service_name == 'sftp' else service_name
    config_path = os.path.join(project_root, "configs", f"{config_service}.toml")
    try:
        with open(config_path, "r", encoding='utf-8') as f:
            return toml.load(f)
    except (FileNotFoundError, toml.TomlDecodeError) as e:
        print(f"Error loading config for {config_service}: {e}")
        return None

def run_service(service, server_name):
    """Loads the correct tool and runs it for the given server."""
    config = get_config(service)
    if not config or server_name not in config:
        print(f"Server '{server_name}' not found in {service} config.")
        return

    try:
        tool_module = importlib.import_module(f"tools.{service}")
        tool_module.run(config[server_name])
    except ImportError as e:
        print(f"Could not find or load tool for '{service}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(description="A multi-tool CLI for various services.")
    parser.add_argument("service", nargs='?', help="The service to connect to (e.g., ssh, mysql, sftp).")
    parser.add_argument("server", nargs='?', help="The name of the server to connect to.")
    args = parser.parse_args()

    if args.service and args.server:
        run_service(args.service, args.server)
    else:
        interactive_mode()

def interactive_mode():
    """Runs the tool in interactive selection mode."""
    # 1. Select a service
    configs_path = os.path.join(project_root, "configs")
    services = sorted([f.replace(".toml", "") for f in os.listdir(configs_path) if f.endswith(".toml")])
    # Manually add sftp to the list of services
    if 'ssh' in services and 'sftp' not in services:
        services.append('sftp')
        services.sort()
        
    print("Select a service:")
    for i, service in enumerate(services):
        print(f"{i + 1}. {service}")

    try:
        choice = int(input("Enter the number of the service: ")) - 1
        selected_service = services[choice]
    except (ValueError, IndexError):
        print("Invalid input.")
        return

    # 2. Select a server
    config = get_config(selected_service)
    if not config:
        return

    servers = list(config.keys())
    print(f"\nSelect a server for {selected_service}:")
    print_in_columns(servers)

    try:
        choice = int(input("Enter the number of the server: ")) - 1
        selected_server = servers[choice]
    except (ValueError, IndexError):
        print("Invalid input.")
        return

    # 3. Run the tool
    run_service(selected_service, selected_server)

if __name__ == "__main__":
    main()
