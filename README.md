# Dagger

Dagger is a shell script that provides a unified, interactive interface for managing connections to various backend services. It simplifies connecting to databases and remote servers by using a menu-driven system based on TOML configuration files.

## Features

- **Unified Interface**: Connect to services like SSH, SFTP, MySQL, PostgreSQL, MongoDB, Redis, SQLite, and etcd from a single script.
- **Interactive Mode**: An intuitive, menu-driven interface guides you to select the service and server you want to connect to.
- **Simple Configuration**: Easy-to-use TOML files for managing all your server connection configurations.
- **Secure Password Handling**: Uses `sshpass` for password-based authentication for SSH and SFTP, and environment variables for other services, avoiding plain-text passwords in commands.

## Requirements

- The command-line client for each service you intend to use (e.g., `psql`, `mysql`, `mongosh`, `redis-cli`, `ssh`, `sftp`, `sqlite3`, `etcdctl`).
- `sshpass`: Required for password authentication with SSH and SFTP.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd dagger
    ```

2.  **Make the script executable:**
    ```bash
    chmod +x dagger.sh
    ```

## Configuration

Dagger uses `.toml` files for configuration, located in the `configs/` directory. Template files (`.toml.template`) are provided for each supported service.

1.  **Create a configuration file:**
    To configure a new server, copy the corresponding template file. For example, to add a new PostgreSQL server:
    ```bash
    cp configs/postgresql.toml.template configs/postgresql.toml
    ```

2.  **Edit the configuration file:**
    Open the `.toml` file and add your server details. You can define multiple servers within the same file using unique headers.

    **Example for `configs/postgresql.toml`:**
    ```toml
    [my_dev_db]
    host = "127.0.0.1"
    port = 5432
    user = "dev_user"
    password = "your_password"
    dbname = "development_db"

    [my_prod_db]
    host = "prod.db.example.com"
    port = 5432
    user = "prod_user"
    password = "your_secret_password"
    dbname = "production_db"
    ```

## Usage

To use Dagger, simply run the script from your terminal:

```bash
./dagger.sh
```

The script will launch in interactive mode, prompting you to select a service and then a configured server to connect to.

## Acknowledgments

This project was developed with the assistance of Gemini, a large language model from Google.