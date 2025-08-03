# Dagger

Dagger is a unified command-line interface (CLI) tool designed to simplify interactions with various backend services. It provides a single, consistent entry point for connecting to and managing databases and remote servers, either through direct commands or an interactive selection mode.

## Features

- **Unified Interface**: Connect to multiple services like SSH, SFTP, MySQL, PostgreSQL, MongoDB, Redis, and more using a single tool.
- **Interactive Mode**: An intuitive, menu-driven interface guides you to select the service and server you want to connect to.
- **Direct Connection**: Quickly connect to a service by providing the service and server name as command-line arguments.
- **Simple Configuration**: Easy-to-use TOML files for managing all your server connection configurations.
- **Command History**: Maintains a separate command history for each service, just like your standard shell.
- **Full TTY Support for SSH**: Provides a true interactive terminal experience for SSH, with support for programs like `vim` and `top`.

## Requirements

- Python 3.6+
- The required Python packages are listed in `requirements.txt`.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd dagger
    ```

2.  **Install the dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

## Configuration

Dagger uses `.toml` files for configuration, located in the `configs/` directory. Template files (`.toml.template`) are provided for each supported service.

1.  **Create a configuration file:**
    To configure a new server, copy the corresponding template file. For example, to add a new MySQL server:
    ```bash
    cp configs/mysql.toml.template configs/mysql.toml
    ```

2.  **Edit the configuration file:**
    Open the `.toml` file and add your server details. You can define multiple servers within the same file.

    **Example for `configs/mysql.toml`:**
    ```toml
    [my_dev_db]
    host = "127.0.0.1"
    port = 3306
    user = "dev_user"
    password = "your_password"
    database = "development_db"

    [my_prod_db]
    host = "prod.db.example.com"
    port = 3306
    user = "prod_user"
    password = "your_secret_password"
    database = "production_db"
    ```

## Usage

Dagger can be run in two modes:

### 1. Interactive Mode

Simply run the `dagger.py` script without any arguments to enter the interactive mode.

```bash
python dagger.py
```

You will be prompted to select a service first, and then a server from the ones you have configured.

### 2. Direct Connection Mode

You can also connect directly to a server by providing the service and server name as arguments.

```bash
python dagger.py <service_name> <server_name>
```

**Example:**
To connect to the `my_dev_db` MySQL server defined in the example above:
```bash
python dagger.py mysql my_dev_db
```

## Acknowledgments

This project was developed with the assistance of Gemini, a large language model from Google.
