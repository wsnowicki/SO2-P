#!/usr/bin/env python
import socket
import threading
import json
import os
import sqlite3
from datetime import datetime
from colorama import init, Fore, Style
import argparse

init(autoreset=True)

clients = {}
groups = {}
lock = threading.Lock()

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR"]
log_level = "INFO"

def log(level, msg):
    if LOG_LEVELS.index(level) < LOG_LEVELS.index(log_level):
        return
    color = {
        "DEBUG": Fore.CYAN, "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW, "ERROR": Fore.RED
    }.get(level, "")
    print(f"{color}[{level}]{Style.RESET_ALL} {msg}")

def log_debug(msg): log("DEBUG", msg)
def log_info(msg): log("INFO", msg)
def log_warning(msg): log("WARNING", msg)
def log_error(msg): log("ERROR", msg)

def load_user_history(username):
    file = f"chat_history/{username}.json"
    if os.path.exists(file):
        with open(file, 'r') as f:
            return json.load(f)
    return []

def save_message(username, sender, content, recipient=None, group=None):
    os.makedirs("chat_history", exist_ok=True)
    file = f"chat_history/{username}.json"
    history = load_user_history(username)
    history.append({
        "timestamp": datetime.now().isoformat(),
        "sender": sender,
        "recipient": recipient,
        "group": group,
        "content": content
    })
    with open(file, 'w') as f:
        json.dump(history, f, indent=2)
    log_debug(f"Saved message for {username} from {sender} → {recipient or group or 'self'}")

def save_group_to_db(db_path, group_name, members):
    with lock:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS groups (group_name TEXT, username TEXT)")
        cur.execute("DELETE FROM groups WHERE group_name = ?", (group_name,))
        for user in members:
            cur.execute("INSERT INTO groups (group_name, username) VALUES (?, ?)", (group_name, user))
        conn.commit()
        conn.close()
    log_info(f"Group '{group_name}' saved with: {', '.join(members)}")

def load_groups_from_db(db_path):
    loaded = {}
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS groups (group_name TEXT, username TEXT)")
        rows = cursor.execute("SELECT group_name, username FROM groups").fetchall()
        for group_name, username in rows:
            if group_name not in loaded:
                loaded[group_name] = []
            loaded[group_name].append(username)
        conn.close()
    except Exception as e:
        log_error(f"Failed to load groups from DB: {e}")
    return loaded

def handle_client(conn, addr, db_path):
    username = None
    try:
        username = conn.recv(1024).decode().strip().lower()
        with lock:
            clients[username] = conn
        log_info(f"{username} connected from {addr}")

        # Send chat history
        for entry in load_user_history(username):
            conn.sendall(f"[HISTORY] {json.dumps(entry)}\n".encode())
        conn.sendall("Welcome to the chat server!\n".encode())

        while True:
            msg = conn.recv(1024)
            if not msg:
                break
            msg = msg.decode().strip()
            log_debug(f"{username} → {msg}")

            if msg.startswith("/group"):
                parts = msg.split()
                group, members = parts[1], [m.lower() for m in parts[2:]]
                with lock:
                    groups[group] = members
                save_group_to_db(db_path, group, members)
                conn.sendall(f"[INFO] Group '{group}' created with: {', '.join(members)}\n".encode())

            elif msg.startswith("/send "):
                parts = msg.split()
                if len(parts) < 3:
                    conn.sendall("[ERROR] Invalid /send usage\n".encode())
                    continue
                target, content = parts[1], " ".join(parts[2:])
                full = f"[{username}] {content}\n"
                with lock:
                    if target in clients:
                        clients[target].sendall(full.encode())
                    save_message(username, username, content, recipient=target)
                    if target != username:
                        save_message(target, username, content, recipient=target)

            elif msg.startswith("/sendgroup "):
                parts = msg.split()
                if len(parts) < 3:
                    conn.sendall("[ERROR] Invalid /sendgroup usage\n".encode())
                    continue
                group = parts[1]
                content = " ".join(parts[2:])
                full = f"[{username} to {group}] {content}\n"
                with lock:
                    if group not in groups:
                        conn.sendall("[ERROR] Group doesn't exist\n".encode())
                        continue
                    if username not in groups[group]:
                        conn.sendall("[ERROR] You are not a member of this group\n".encode())
                        continue
                    for member in groups[group]:
                        try:
                            if member in clients:
                                clients[member].sendall(full.encode())
                            save_message(member, username, content, group=group)
                        except Exception as e:
                            log_warning(f"{member} send failed: {e}")
                    save_message(username, username, content, group=group)

            elif msg == "/exit":
                break
            else:
                conn.sendall("[ERROR] Unknown command\n".encode())

    except ConnectionResetError:
        log_info(f"{username} disconnected abruptly")
    except Exception as e:
        log_error(f"{addr} error: {e}")
    finally:
        with lock:
            if username in clients:
                del clients[username]
                log_info(f"{username} disconnected")
        conn.close()

def start_server(ip, port, db_path):
    sock = socket.socket()
    sock.bind((ip, port))
    sock.listen()
    log_info(f"Server listening on {ip}:{port}")
    while True:
        conn, addr = sock.accept()
        threading.Thread(target=handle_client, args=(conn, addr, db_path)).start()

def main():
    global log_level
    parser = argparse.ArgumentParser(description="Multi-threaded Chat Server")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads to handle clients (default: 4)")
    parser.add_argument("--ip", type=str, default="0.0.0.0", help="IP address to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=9000, help="Port to bind (default: 9000)")
    parser.add_argument("--db", type=str, default="chat.db", help="Path to SQLite3 database (default: chat.db)")
    parser.add_argument("--loglevel", type=str, choices=LOG_LEVELS, default="INFO", help="Log level (default: INFO)")
    args = parser.parse_args()
    log_level = args.loglevel

    os.makedirs("chat_history", exist_ok=True)
    groups.update(load_groups_from_db(args.db))
    log_info(f"Loaded groups: {list(groups.keys())}")
    start_server(args.ip, args.port, args.db)

if __name__ == "__main__":
    main()
