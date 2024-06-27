import socket
import pickle
import lz4.frame
import numpy as np


class FrameReceiver:
    """
    FrameReceiver is responsible for receiving and decompressing frames from a socket connection.

    Attributes:
        host (str): The host address to connect to.
        port (int): The port number to connect to.
        client_socket (socket.socket): The socket used for the connection.
        frame_width (int): The width of the frame.
        frame_height (int): The height of the frame.
    """

    def __init__(self, host, port):
        """
        Initializes the FrameReceiver with the given host and port.

        Args:
            host (str): The host address to connect to.
            port (int): The port number to connect to.
        """
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        self.frame_width, self.frame_height = self._receive_resolution()

    def _receive_resolution(self):
        """
        Receive the initial resolution message from the server.

        Returns:
            tuple: A tuple containing the width and height of the frame.
        """
        resolution_data = self.client_socket.recv(1024).decode('utf-8')
        width, height = map(int, resolution_data.split('x'))
        return width, height

    def receive_data(self):
        """
        Receive and decompress data from the socket.

        Returns:
            np.ndarray: The decompressed and deserialized frame.
        """
        size_data = self.client_socket.recv(4)
        if not size_data:
            return None

        size = int.from_bytes(size_data, 'big')  # Convert the size from bytes to an integer
        data = b""

        # Receive the complete data based on the size
        while len(data) < size:
            packet = self.client_socket.recv(size - len(data))
            if not packet:
                return None
            data += packet

        # Decompress and deserialize the received data
        data = lz4.frame.decompress(data)
        return pickle.loads(data).astype(np.uint32)

    def close(self):
        """
        Close the socket connection.
        """
        self.client_socket.close()
