import socket
import threading
import tkinter as tk
import json
from tkinter import ttk, simpledialog, scrolledtext
from colorama import init, Fore, Style
import argparse

init(autoreset=True)

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR"]
current_log_level = "INFO"


def log(level, msg):
    if LOG_LEVELS.index(level) < LOG_LEVELS.index(current_log_level):
        return
    color = {
        "DEBUG": Fore.CYAN, "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW, "ERROR": Fore.RED
    }.get(level, "")
    print(f"{color}[{level}]{Style.RESET_ALL} {msg}")


def log_debug(msg): log("DEBUG", msg)


class ChatClientGUI:
    def __init__(self, master, ip, port):
        self.master = master
        self.sock = socket.socket()
        self.sock.connect((ip, port))

        self.username = simpledialog.askstring("Login", "Enter username:", parent=master)
        self.sock.sendall(f"{self.username}\n".encode())
        self.master.title(f"Chat Client – {self.username}")

        self.tabs = {}
        self.clients_or_groups = {}

        self.tab_control = ttk.Notebook(master)
        self.tab_control.pack(expand=1, fill='both')
        self.add_tab("System")

        self.entry = tk.Entry(master)
        self.entry.pack(fill='x')
        self.entry.bind("<Return>", self.send_message)

        threading.Thread(target=self.receive_messages, daemon=True).start()

    def add_tab(self, name, tab_type="user"):
        if name in self.tabs:
            return
        frame = ttk.Frame(self.tab_control)
        text_area = scrolledtext.ScrolledText(frame, state='disabled', font=("Courier", 10))
        text_area.pack(expand=1, fill='both')
        self.tabs[name] = text_area
        self.clients_or_groups[name] = tab_type
        self.tab_control.add(frame, text=name)
        self.tab_control.select(len(self.tabs) - 1)
        log_debug(f"Added tab: {name}")

    def display_message(self, sender, msg, tab="System"):
        if tab not in self.tabs:
            self.add_tab(tab)
        widget = self.tabs[tab]
        widget.config(state='normal')
        widget.insert('end', f"{sender}: {msg}\n")
        widget.see('end')
        widget.config(state='disabled')

    def send_message(self, event=None):
        msg = self.entry.get().strip()
        self.entry.delete(0, 'end')
        if not msg:
            return

        current_tab = self.tab_control.tab(self.tab_control.select(), "text")

        if msg == "/exit":
            self.sock.close()
            self.master.quit()
            return
        elif msg == "/whoami":
            self.display_message("System", f"You are {self.username}")
            return
        elif msg == "/users":
            users = [n for n, t in self.clients_or_groups.items() if t == "user"]
            self.display_message("System", f"Users: {', '.join(users)}")
            return
        elif msg == "/groups":
            groups = [n for n, t in self.clients_or_groups.items() if t == "group"]
            self.display_message("System", f"Groups: {', '.join(groups)}")
            return

        if msg.startswith("/send "):
            parts = msg.split()
            if len(parts) >= 3:
                target = parts[1]
                message = " ".join(parts[2:])
                self.add_tab(target, tab_type="user")
                self.display_message("You", message, tab=target)
        elif msg.startswith("/sendgroup "):
            parts = msg.split()
            if len(parts) >= 3:
                group = parts[1]
                message = " ".join(parts[2:])
                self.add_tab(group, tab_type="group")
                self.display_message("You", message, tab=group)

        if msg.startswith("/"):
            try:
                self.sock.sendall((msg + "\n").encode())
            except Exception as e:
                log_debug(f"Send error: {e}")
                self.display_message("System", f"Send failed: {e}")
            return

        if current_tab == "System":
            self.display_message("System", "Cannot send from System tab.")
            return

        if self.clients_or_groups.get(current_tab) == "group":
            cmd = f"/sendgroup {current_tab} {msg}"
        else:
            cmd = f"/send {current_tab} {msg}"

        try:
            self.sock.sendall((cmd + "\n").encode())
            self.display_message("You", msg, tab=current_tab)
        except Exception as e:
            log_debug(f"Send error: {e}")
            self.display_message("System", f"Send failed: {e}")

    def receive_messages(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(1024).decode()
                if not chunk:
                    break
                buffer += chunk
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    self.route_message(line.strip())
            except Exception as e:
                log_debug(f"Receive error: {e}")
                self.display_message("System", f"Receive failed: {e}")
                break
        self.sock.close()

    def route_message(self, msg):
        log_debug(f"Received: {msg}")

        if msg.startswith("[ERROR]") or msg.startswith("[INFO]") or msg.startswith("[WARNING]"):
            self.display_message("System", msg)
            return

        if msg.startswith("[HISTORY]"):
            try:
                json_part = msg[len("[HISTORY]"):].strip()
                if not json_part.startswith("{") or not json_part.endswith("}"):
                    self.display_message("System", f"Invalid history: {json_part}")
                    return
                entry = json.loads(json_part)
                ts = entry["timestamp"]
                sender = entry["sender"]
                recipient = entry.get("recipient")
                group = entry.get("group")
                content = entry["content"]

                label = f"[{ts}] {sender}"

                if group:
                    self.add_tab(group, tab_type="group")
                    self.display_message(label, content, tab=group)
                elif recipient == self.username:
                    self.add_tab(sender, tab_type="user")
                    self.display_message(label, content, tab=sender)
                elif sender == self.username and recipient:
                    self.add_tab(recipient, tab_type="user")
                    self.display_message(label, content, tab=recipient)
            except Exception as e:
                self.display_message("System", f"Parse error: {e}")
            return

        if msg.startswith("[") and "]" in msg:
            bracket = msg.find("]")
            source = msg[1:bracket]
            body = msg[bracket + 1:].strip()
            if " to " in source:
                sender, group = source.split(" to ")
                self.add_tab(group, tab_type="group")
                self.display_message(sender, body, tab=group)
            else:
                self.add_tab(source, tab_type="user")
                self.display_message(source, body, tab=source)
        else:
            self.display_message("System", msg)

if __name__ == "__main__":
    root = tk.Tk()
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9000)
    parser.add_argument("--loglevel", choices=LOG_LEVELS, default="INFO")
    args = parser.parse_args()
    current_log_level = args.loglevel
    ChatClientGUI(root, args.ip, args.port)
    root.mainloop()
