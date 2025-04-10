# TCP Chat Server – SO2 Project

## Project Description

This project implements a **multi-threaded TCP chat server** and a **GUI client**, written in Python.  
It is the second project for the Operating Systems 2 course, focused on concurrency and critical section management using `threading`.

---

## Goals

- Handle multiple client connections using threads.
- Support private and group chat functionality.
- Ensure message delivery and synchronization between threads.
- Preserve message history across sessions.
- Provide a GUI client interface for messaging.

---

## How to Run

### Requirements

- Python 3.10+
- Modules: `colorama`, `sqlite3`, `tkinter`, `argparse`
- Optional: `flake8` for code style checking

Install dependencies:

```bash
pip install colorama flake8
```

### Server

```bash
python chat/server.py --ip 0.0.0.0 --port 9000 --db chat.db --loglevel INFO
```

### Client (GUI)

```bash
python chat/client.py --ip 127.0.0.1 --port 9000 --loglevel INFO
```

---

## Threads

- **Each connected client** is handled by a **separate thread**.
- These threads are responsible for:
  - Receiving and parsing client commands
  - Broadcasting messages to other users
  - Saving history to disk

---

## Critical Sections

- **Shared data:**
  - `clients` dictionary
  - `groups` dictionary
  - Access to SQLite group membership
- **Synchronization:**
  - A global `threading.Lock()` protects concurrent access to shared state.
  - Used during:
    - Registering/removing clients
    - Sending messages
    - Modifying group membership

---

## Features

- Private chat (`/send <user> <message>`)
- Group chat (`/group <name> users...` + `/sendgroup <group> <msg>`)
- JSON-based per-user message history
- SQLite-based group persistence
- Session restoration after reconnecting
- GUI client:
  - Separate tabs for each user or group
  - System tab for commands and logs
  - Auto tab switching
- Commands:
  - `/exit`, `/whoami`, `/users`, `/groups`

---

## Bonus – Advanced Features

- Graphical client instead of CLI
- Colored console logging with `--loglevel`
- GitHub Actions workflow (PEP8/flake8)

---

## Sample Output

### Server

```
[INFO] user1 connected
[DEBUG] user1 → /send user2 Hello!
[INFO] user1 disconnected
```

### Client (GUI)

```
System: Welcome to the chat server!
[user2]: Hi user1!
You: Hello!
```

---

## Repo Structure

```
chat/
├── client.py       # GUI client (tkinter)
├── server.py       # TCP multithreaded server
├── README.md       # This file
├── chat_history/   # Auto-generated per-user logs
└── chat.db         # Sqlite3 database
```

---

## Author

- Project for Operating Systems 2 – 2025  
- Instructor: Damian Raczkowski  
- Author: Wiktor Nowicki

[Go to repo's README](../README.md)
