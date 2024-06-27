import tkinter as tk
from tkinter import messagebox
import threading
from server_handler import ServerHandler


class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Server Config")
        self.server_handler = None
        self.server_thread = None
        self.is_running = False

        self.create_widgets()

    def create_widgets(self):
        # Host
        tk.Label(self.root, text="Host:").grid(row=0, column=0, padx=10, pady=5)
        self.host_entry = tk.Entry(self.root)
        self.host_entry.grid(row=0, column=1, padx=10, pady=5)
        self.host_entry.insert(0, "0.0.0.0")

        # Port
        tk.Label(self.root, text="Port:").grid(row=1, column=0, padx=10, pady=5)
        self.port_entry = tk.Entry(self.root)
        self.port_entry.grid(row=1, column=1, padx=10, pady=5)
        self.port_entry.insert(0, "9998")

        # Frame Width
        tk.Label(self.root, text="Frame Width:").grid(row=2, column=0, padx=10, pady=5)
        self.width_entry = tk.Entry(self.root)
        self.width_entry.grid(row=2, column=1, padx=10, pady=5)
        self.width_entry.insert(0, "1920")

        # Frame Height
        tk.Label(self.root, text="Frame Height:").grid(row=3, column=0, padx=10, pady=5)
        self.height_entry = tk.Entry(self.root)
        self.height_entry.grid(row=3, column=1, padx=10, pady=5)
        self.height_entry.insert(0, "1080")

        # Start Button
        self.start_button = tk.Button(self.root, text="Start Server", command=self.start_server)
        self.start_button.grid(row=4, column=0, pady=10)

        # Stop Button
        self.stop_button = tk.Button(self.root, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.grid(row=4, column=1, pady=10)

    def start_server(self):
        if self.is_running:
            messagebox.showwarning("Warning", "Server is already running")
            return

        host = self.host_entry.get()
        port = int(self.port_entry.get())
        frame_width = int(self.width_entry.get())
        frame_height = int(self.height_entry.get())

        try:
            self.server_handler = ServerHandler(host, port, frame_width, frame_height)
            self.server_thread = threading.Thread(target=self.run_server)
            self.server_thread.start()
            self.is_running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            messagebox.showinfo("Success", "Server started successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start server: {e}")

    def run_server(self):
        try:
            self.server_handler.start_server()
        except Exception as e:
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            messagebox.showerror("Error", f"Server encountered an error: {e}")

    def stop_server(self):
        if not self.is_running:
            messagebox.showwarning("Warning", "Server is not running")
            return

        try:
            self.server_handler.stop_server()
            self.server_thread.join()
            self.is_running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            messagebox.showinfo("Success", "Server stopped successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop server: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ServerGUI(root)
    root.mainloop()
