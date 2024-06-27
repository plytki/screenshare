import tkinter as tk
from tkinter import messagebox
from client_handler import ClientHandler


class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Client Config")

        self.create_widgets()

    def create_widgets(self):
        # Host
        tk.Label(self.root, text="Host:").grid(row=0, column=0, padx=10, pady=5)
        self.host_entry = tk.Entry(self.root)
        self.host_entry.grid(row=0, column=1, padx=10, pady=5)
        self.host_entry.insert(0, "host1.plytki.cc")

        # Port
        tk.Label(self.root, text="Port:").grid(row=1, column=0, padx=10, pady=5)
        self.port_entry = tk.Entry(self.root)
        self.port_entry.grid(row=1, column=1, padx=10, pady=5)
        self.port_entry.insert(0, "9998")

        # Frame Width
        tk.Label(self.root, text="Display Width:").grid(row=2, column=0, padx=10, pady=5)
        self.width_entry = tk.Entry(self.root)
        self.width_entry.grid(row=2, column=1, padx=10, pady=5)
        self.width_entry.insert(0, "1920")

        # Frame Height
        tk.Label(self.root, text="Display Height:").grid(row=3, column=0, padx=10, pady=5)
        self.height_entry = tk.Entry(self.root)
        self.height_entry.grid(row=3, column=1, padx=10, pady=5)
        self.height_entry.insert(0, "1080")

        # Connect Button
        self.connect_button = tk.Button(self.root, text="Connect", command=self.connect_to_server)
        self.connect_button.grid(row=4, column=0, columnspan=2, pady=10)

    def connect_to_server(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        frame_width = int(self.width_entry.get())
        frame_height = int(self.height_entry.get())

        try:
            client_handler = ClientHandler(host, port, frame_width, frame_height)
            client_handler.start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to server: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ClientGUI(root)
    root.mainloop()
