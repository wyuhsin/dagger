#!/bin/bash

# --- Config Parsing Functions ---

get_config() {
    local server_name="$1"
    local config_file="$2"
    if [ ! -f "${config_file}" ]; then
        printf "Error: Config file not found at %s\n" "${config_file}" >&2
        return 1
    fi
    awk -v server="${server_name}" \
        '$0 == "[" server "]" { in_block=1; next } /^\[/ { in_block=0 } in_block { print }' \
        "${config_file}" | \
        grep '=' | \
        sed 's/\s*=\s*/=/g' | \
        sed 's/"//g'
}

get_config_value() {
    local config_output="$1"
    local key="$2"
    echo "${config_output}" | grep "^${key}=" | cut -d'=' -f2
}

get_server_list() {
    local config_file="$1"
    if [ ! -f "${config_file}" ]; then return 1; fi
    grep -E '^\s*\[.+\]' "${config_file}" | \
        sed 's/^\s*\[//g' | \
        sed 's/\]\s*$//g'
}

# --- UI Functions ---

print_in_columns() {
    local -a items=($@)
    local term_width
    term_width=$(tput cols 2>/dev/null || echo 80)
    local max_len=0
    local item
    for item in "${items[@]}"; do
        (( ${#item} > max_len )) && max_len=${#item}
    done
    local col_width=$((max_len + 4))
    local num_cols=$((term_width / col_width))
    (( num_cols == 0 )) && num_cols=1
    local num_rows=$(( (${#items[@]} + num_cols - 1) / num_cols ))
    local i j index
    for ((i=0; i<num_rows; i++)); do
        for ((j=0; j<num_cols; j++)); do
            index=$((i + j * num_rows))
            if [ -n "${items[index]}" ]; then
                printf "%*s" "${col_width}" "${items[index]}"
            fi
        done
        printf "\n"
    done
}

# --- Tool Functions ---

run_ssh() {
    if ! command -v ssh &> /dev/null; then printf "Error: 'ssh' command not found. Please install the OpenSSH client.\n" >&2; return 1; fi
    local server_name="$1"; shift; local -a tool_args=($@)
    local config_data
    config_data=$(get_config "${server_name}" "./configs/ssh.toml") || return 1
    local host user port key_filename password
    host=$(get_config_value "${config_data}" "host"); user=$(get_config_value "${config_data}" "user"); port=$(get_config_value "${config_data}" "port"); key_filename=$(get_config_value "${config_data}" "key_filename"); password=$(get_config_value "${config_data}" "password")
    local -a cmd=()
    if [ -n "${password}" ]; then
        if ! command -v sshpass &> /dev/null;
        then
            printf "Error: Password detected in config, but 'sshpass' command not found.\n" >&2
            printf "Please install sshpass (e.g., sudo apt-get install sshpass or sudo pacman -S sshpass).\n" >&2
            return 1
        fi
        cmd+=("sshpass" "-p" "${password}")
    fi
    cmd+=("ssh" "-o" "StrictHostKeyChecking=no" "-o" "UserKnownHostsFile=/dev/null")
    [ -n "${port}" ] && cmd+=("-p" "${port}")
    [ -n "${key_filename}" ] && cmd+=("-i" "${key_filename}")
    cmd+=("${user}@${host}")
    [ ${#tool_args[@]} -gt 0 ] && cmd+=("${tool_args[@]}")
    local -a echo_cmd=("${cmd[@]}")
    if [ -n "${password}" ]; then echo_cmd[2]="********"; fi
    printf "Executing: %s\n" "${echo_cmd[*]}"
    printf -- "--------------------------------------------------\n"
    "${cmd[@]}"
}

run_sftp() {
    if ! command -v sftp &> /dev/null; then printf "Error: 'sftp' command not found. Please install the OpenSSH client.\n" >&2; return 1; fi
    local server_name="$1"; shift; local -a tool_args=($@)
    local config_data
    config_data=$(get_config "${server_name}" "./configs/ssh.toml") || return 1
    local host user port key_filename password
    host=$(get_config_value "${config_data}" "host"); user=$(get_config_value "${config_data}" "user"); port=$(get_config_value "${config_data}" "port"); key_filename=$(get_config_value "${config_data}" "key_filename"); password=$(get_config_value "${config_data}" "password")
    local -a cmd=()
    if [ -n "${password}" ]; then
        if ! command -v sshpass &> /dev/null;
        then
            printf "Error: Password detected in config, but 'sshpass' command not found.\n" >&2
            printf "Please install sshpass (e.g., sudo apt-get install sshpass or sudo pacman -S sshpass).\n" >&2
            return 1
        fi
        cmd+=("sshpass" "-p" "${password}")
    fi
    cmd+=("sftp")
    [ -n "${port}" ] && cmd+=("-P" "${port}")
    [ -n "${key_filename}" ] && cmd+=("-i" "${key_filename}")
    cmd+=("${user}@${host}")
    [ ${#tool_args[@]} -gt 0 ] && cmd+=("${tool_args[@]}")

    local -a echo_cmd=("${cmd[@]}")
    if [ -n "${password}" ]; then
        echo_cmd[2]="********"
    fi

    printf "Executing: %s\n" "${echo_cmd[*]}"
    printf -- "--------------------------------------------------\n"
    "${cmd[@]}"
}

run_postgresql() {
    if ! command -v psql &> /dev/null; then printf "Error: 'psql' command not found. Please install the PostgreSQL client.\n" >&2; return 1; fi
    local server_name="$1"; shift; local -a tool_args=($@)
    local config_data
    config_data=$(get_config "${server_name}" "./configs/postgresql.toml") || return 1
    local host port user password dbname
    host=$(get_config_value "${config_data}" "host"); port=$(get_config_value "${config_data}" "port"); user=$(get_config_value "${config_data}" "user"); password=$(get_config_value "${config_data}" "password"); dbname=$(get_config_value "${config_data}" "dbname")
    local -a cmd=()
    local env_vars=""
    if [ -n "${password}" ]; then
        export PGPASSWORD="${password}"
        env_vars="PGPASSWORD=******** "
    fi
    cmd+=("psql")
    [ -n "${host}" ] && cmd+=("-h" "${host}")
    [ -n "${port}" ] && cmd+=("-p" "${port}")
    [ -n "${user}" ] && cmd+=("-U" "${user}")
    [ -n "${dbname}" ] && cmd+=("-d" "${dbname}")
    [ ${#tool_args[@]} -gt 0 ] && cmd+=("${tool_args[@]}")
    printf "Executing: %s%s\n" "${env_vars}" "${cmd[*]}"
    printf -- "--------------------------------------------------\n"
    "${cmd[@]}"
    unset PGPASSWORD
}

run_mysql() {
    if ! command -v mysql &> /dev/null; then printf "Error: 'mysql' command not found. Please install the MySQL/MariaDB client.\n" >&2; return 1; fi
    local server_name="$1"; shift; local -a tool_args=($@)
    local config_data
    config_data=$(get_config "${server_name}" "./configs/mysql.toml") || return 1
    local host port user password database
    host=$(get_config_value "${config_data}" "host"); port=$(get_config_value "${config_data}" "port"); user=$(get_config_value "${config_data}" "user"); password=$(get_config_value "${config_data}" "password"); database=$(get_config_value "${config_data}" "database")
    local -a cmd=("mysql")
    [ -n "${host}" ] && cmd+=("-h" "${host}")
    [ -n "${port}" ] && cmd+=("-P" "${port}")
    [ -n "${user}" ] && cmd+=("-u" "${user}")
    [ -n "${password}" ] && cmd+=("--password=${password}")
    [ -n "${database}" ] && cmd+=("${database}")
    [ ${#tool_args[@]} -gt 0 ] && cmd+=("${tool_args[@]}")
    local echo_cmd_str="${cmd[@]}"
    echo_cmd_str="${echo_cmd_str/--password=*/--password=********}"
    printf "Executing: %s\n" "${echo_cmd_str}"
    printf -- "--------------------------------------------------\n"
    "${cmd[@]}"
}

run_mongo() {
    local mongo_cmd
    if command -v mongosh &> /dev/null;
    then
        mongo_cmd="mongosh"
    elif command -v mongo &> /dev/null;
    then
        mongo_cmd="mongo"
    else
        printf "Error: 'mongosh' or 'mongo' command not found. Please install the MongoDB Shell.\n" >&2
        return 1
    fi
    local server_name="$1"; shift; local -a tool_args=($@)
    local config_data
    config_data=$(get_config "${server_name}" "./configs/mongo.toml") || return 1
    local host port user password database auth_source tls
    host=$(get_config_value "${config_data}" "host"); port=$(get_config_value "${config_data}" "port"); user=$(get_config_value "${config_data}" "user"); password=$(get_config_value "${config_data}" "password"); database=$(get_config_value "${config_data}" "database"); auth_source=$(get_config_value "${config_data}" "auth_source"); tls=$(get_config_value "${config_data}" "tls")
    local conn_str="mongodb://"
    if [ -n "${user}" ]; then
        conn_str+="${user}"
        [ -n "${password}" ] && conn_str+=":${password}"
        conn_str+="@"
    fi
    conn_str+="${host}"
    [ -n "${port}" ] && conn_str+=":${port}"
    conn_str+="/${database}"
    local -a options=()
    [ -n "${auth_source}" ] && options+=("authSource=${auth_source}")
    [ "${tls}" == "true" ] && options+=("tls=true")
    if [ ${#options[@]} -gt 0 ]; then
        local old_ifs="$IFS"
        IFS='&'
        conn_str+="?${options[*]}"
        IFS="$old_ifs"
    fi
    
    local echo_conn_str="${conn_str}"
    if [ -n "${password}" ]; then
        echo_conn_str="${conn_str//:${password}@/:********@}"
    fi

    printf "Executing: %s '%s' %s\n" "${mongo_cmd}" "${echo_conn_str}" "${tool_args[*]}"
    printf -- "--------------------------------------------------\n"
    # Use eval to handle the connection string correctly, especially with special characters
    eval "${mongo_cmd} '${conn_str}' ${tool_args[*]}"
}

run_redis() {
    if ! command -v redis-cli &> /dev/null; then printf "Error: 'redis-cli' command not found. Please install the Redis client.\n" >&2; return 1; fi
    local server_name="$1"; shift; local -a tool_args=($@)
    local config_data
    config_data=$(get_config "${server_name}" "./configs/redis.toml") || return 1
    local host port password db
    host=$(get_config_value "${config_data}" "host"); port=$(get_config_value "${config_data}" "port"); password=$(get_config_value "${config_data}" "password"); db=$(get_config_value "${config_data}" "db")
    local -a cmd=("redis-cli")
    [ -n "${host}" ] && cmd+=("-h" "${host}")
    [ -n "${port}" ] && cmd+=("-p" "${port}")
    [ -n "${password}" ] && cmd+=("-a" "${password}")
    [ -n "${db}" ] && cmd+=("-n" "${db}")
    [ ${#tool_args[@]} -gt 0 ] && cmd+=("${tool_args[@]}")
    local -a echo_cmd=("${cmd[@]}")
    if [ -n "${password}" ]; then
        local pass_idx=-1
        for i in "${!echo_cmd[@]}"; do if [[ "${echo_cmd[$i]}" == "-a" ]]; then pass_idx=$((i+1)); break; fi; done
        [ $pass_idx -ne -1 ] && echo_cmd[$pass_idx]="********"
    fi
    printf "Executing: %s\n" "${echo_cmd[*]}"
    printf -- "--------------------------------------------------\n"
    "${cmd[@]}"
}

run_sqlite() {
    if ! command -v sqlite3 &> /dev/null; then printf "Error: 'sqlite3' command not found. Please install SQLite3.\n" >&2; return 1; fi
    local server_name="$1"; shift; local -a tool_args=($@)
    local config_data
    config_data=$(get_config "${server_name}" "./configs/sqlite.toml") || return 1
    local path
    path=$(get_config_value "${config_data}" "path")
    if [ -z "${path}" ]; then
        printf "Error: Database path not specified for '%s' in sqlite.toml.\n" "${server_name}" >&2
        return 1
    fi
    local -a cmd=("sqlite3" "${path}")
    [ ${#tool_args[@]} -gt 0 ] && cmd+=("${tool_args[@]}")
    printf "Executing: %s\n" "${cmd[*]}"
    printf -- "--------------------------------------------------\n"
    "${cmd[@]}"
}

run_etcd() {
    if ! command -v etcdctl &> /dev/null; then printf "Error: 'etcdctl' command not found. Please install etcdctl.\n" >&2; return 1; fi
    local server_name="$1"; shift; local -a tool_args=($@)
    local config_data
    config_data=$(get_config "${server_name}" "./configs/etcd.toml") || return 1
    local endpoints user password
    endpoints=$(get_config_value "${config_data}" "endpoints"); user=$(get_config_value "${config_data}" "user"); password=$(get_config_value "${config_data}" "password")
    local -a cmd=("etcdctl")
    [ -n "${endpoints}" ] && cmd+=("--endpoints=${endpoints}")
    if [ -n "${user}" ]; then
        local user_pass="${user}"
        [ -n "${password}" ] && user_pass+=":${password}"
        cmd+=("--user=${user_pass}")
    fi
    [ ${#tool_args[@]} -gt 0 ] && cmd+=("${tool_args[@]}")
    local echo_cmd_str="${cmd[@]}"
    echo_cmd_str="${echo_cmd_str/:\$password/}"
    printf "Executing: %s\n" "${echo_cmd_str}"
    printf -- "--------------------------------------------------\n"
    "${cmd[@]}"
}

# --- Interactive Mode ---

interactive_mode() {
    printf "Please select a service:\n"
    local -a services=()
    local f
    for f in ./configs/*.toml.template; do services+=("$(basename "$f" .toml.template)"); done
    services+=("sftp")
    PS3="Enter the service number: "
    local service
    select service in "${services[@]}"; do
        if [ -n "${service}" ]; then break; fi
    done
    local config_name=${service}
    [[ "${service}" == "sftp" ]] && config_name="ssh"
    local config_file="./configs/${config_name}.toml"
    if [ ! -f "${config_file}" ]; then
        printf "\nError: Configuration file not found: %s\n" "${config_file}" >&2
        printf "Please create it first, e.g., cp \"%s.template\" \"%s\"\n" "${config_file}" "${config_file}" >&2
        return 1
    fi
    local -a servers
    servers=($(get_server_list "${config_file}"))
    if [ ${#servers[@]} -eq 0 ]; then
        printf "\nError: No servers found in %s.\n" "${config_file}" >&2
        printf "Please define at least one server in the file (e.g., [my-server]).\n" >&2
        return 1
    fi
    printf "\nSelect a server for %s:\n" "${service}"
    PS3="Enter the server number: "
    local server
    select server in "${servers[@]}"; do
        if [ -n "${server}" ]; then break; fi
    done
    printf "\nStarting interactive session...\n"
    "run_${service}" "${server}"
}

# --- Main Logic ---

interactive_mode
