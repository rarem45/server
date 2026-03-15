import socket
import threading
import subprocess
import platform
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import os

class Server:
    def __init__(self, host='0.0.0.0', port=12345):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.clients = []
        self.client_list = None  # Will be set by GUI
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"Server listening on {self.host}:{self.port} (local IP: {local_ip})")

    def start(self):
        print(f"Server listening on {self.host}:{self.port}")
        threading.Thread(target=self.accept_clients, daemon=True).start()

    def accept_clients(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Client connected: {addr}")
            self.clients.append((client_socket, addr))
            threading.Thread(target=self.handle_client, args=(client_socket, addr), daemon=True).start()
            self.update_client_list()

    def handle_client(self, client_socket, addr):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                message = data.decode('utf-8')
                if message.startswith('OUTPUT:'):
                    output = message[7:]
                    self.display_output(f"From {addr}: {output}")
        except:
            pass
        finally:
            self.clients.remove((client_socket, addr))
            client_socket.close()
            self.update_client_list()

    def send_command(self, command):
        for client_socket, addr in self.clients:
            try:
                client_socket.send(f"COMMAND:{command}".encode('utf-8'))
            except:
                pass

    def update_client_list(self):
        if self.client_list:
            self.client_list.delete(0, tk.END)
            for _, addr in self.clients:
                self.client_list.insert(tk.END, f"{addr[0]}:{addr[1]}")

    def display_output(self, output):
        if self.output_text:
            self.output_text.insert(tk.END, output + '\n')
            self.output_text.see(tk.END)

class GUI:
    def __init__(self, server):
        self.server = server
        self.root = tk.Tk()
        self.root.title("Computer Control Network")
        self.root.configure(bg='#2e2e2e')
        self.root.geometry("800x600")

        # Style for dark mode
        self.style = {
            'bg': '#2e2e2e',
            'fg': '#ffffff',
            'button_bg': '#4a4a4a',
            'button_fg': '#ffffff',
            'entry_bg': '#4a4a4a',
            'entry_fg': '#ffffff',
            'listbox_bg': '#4a4a4a',
            'listbox_fg': '#ffffff'
        }

        # Clients list
        tk.Label(self.root, text="Connected Clients:", bg=self.style['bg'], fg=self.style['fg']).pack(pady=5)
        self.client_list = tk.Listbox(self.root, height=5, bg=self.style['listbox_bg'], fg=self.style['listbox_fg'])
        self.client_list.pack(pady=5, fill=tk.X)
        server.client_list = self.client_list

        # Command section
        tk.Label(self.root, text="Quick Command:", bg=self.style['bg'], fg=self.style['fg']).pack(pady=5)
        self.command_entry = tk.Entry(self.root, width=50, bg=self.style['entry_bg'], fg=self.style['entry_fg'], insertbackground='white')
        self.command_entry.pack(pady=5)
        self.run_button = tk.Button(self.root, text="Run on All", command=self.run_command, bg=self.style['button_bg'], fg=self.style['button_fg'])
        self.run_button.pack(pady=5)

        # Scripts section
        tk.Label(self.root, text="Scripts:", bg=self.style['bg'], fg=self.style['fg']).pack(pady=5)
        self.script_list = tk.Listbox(self.root, height=5, bg=self.style['listbox_bg'], fg=self.style['listbox_fg'])
        self.script_list.pack(pady=5, fill=tk.X)
        self.load_scripts()

        button_frame = tk.Frame(self.root, bg=self.style['bg'])
        button_frame.pack(pady=5)
        tk.Button(button_frame, text="Load Script", command=self.load_script, bg=self.style['button_bg'], fg=self.style['button_fg']).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Save Script", command=self.save_script, bg=self.style['button_bg'], fg=self.style['button_fg']).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Execute Script", command=self.execute_script, bg=self.style['button_bg'], fg=self.style['button_fg']).pack(side=tk.LEFT, padx=5)

        tk.Label(self.root, text="Script Editor:", bg=self.style['bg'], fg=self.style['fg']).pack(pady=5)
        self.script_text = scrolledtext.ScrolledText(self.root, height=10, bg=self.style['entry_bg'], fg=self.style['entry_fg'], insertbackground='white')
        self.script_text.pack(pady=5, fill=tk.BOTH, expand=True)

        # Output
        tk.Label(self.root, text="Output:", bg=self.style['bg'], fg=self.style['fg']).pack(pady=5)
        self.output_text = scrolledtext.ScrolledText(self.root, height=10, bg=self.style['listbox_bg'], fg=self.style['listbox_fg'])
        self.output_text.pack(pady=5, fill=tk.BOTH, expand=True)
        server.output_text = self.output_text

    def load_scripts(self):
        self.script_list.delete(0, tk.END)
        if os.path.exists('scripts'):
            for file in os.listdir('scripts'):
                if file.endswith('.py'):
                    self.script_list.insert(tk.END, file)

    def load_script(self):
        selection = self.script_list.curselection()
        if selection:
            script_name = self.script_list.get(selection[0])
            with open(f'scripts/{script_name}', 'r') as f:
                self.script_text.delete(1.0, tk.END)
                self.script_text.insert(tk.END, f.read())

    def save_script(self):
        script_name = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python files", "*.py")], initialdir='scripts')
        if script_name:
            with open(script_name, 'w') as f:
                f.write(self.script_text.get(1.0, tk.END))
            self.load_scripts()

    def execute_script(self):
        code = self.script_text.get(1.0, tk.END).strip()
        if code:
            command = f'python -c "{code.replace(chr(34), chr(92) + chr(34))}"'  # Escape quotes
            self.server.send_command(command)

    def run_command(self):
        command = self.command_entry.get()
        if command:
            self.server.send_command(command)
            self.command_entry.delete(0, tk.END)

    def start(self):
        self.root.mainloop()

if __name__ == "__main__":
    server = Server()
    server.start()
    gui = GUI(server)
    gui.start()