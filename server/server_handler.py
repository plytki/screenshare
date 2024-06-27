import socket
import pickle
import threading
import time
import lz4.frame
import numpy as np
import cv2

from camera_handler import CameraHandler
from frame_processor import FrameProcessor


class ServerHandler:
    """
    ServerHandler is responsible for handling the server-side operations, including capturing,
    processing, and sending frames to clients.

    Attributes:
        host (str): The host address to bind the server.
        port (int): The port number to bind the server.
        frame_width (int): The width of the frames.
        frame_height (int): The height of the frames.
        camera_handler (CameraHandler): The handler for capturing frames from the camera.
        frame_processor (FrameProcessor): The handler for processing frames.
    """

    def __init__(self, host, port, frame_width, frame_height):
        """
        Initializes the ServerHandler with the given host, port, frame width, and frame height.

        Args:
            host (str): The host address to bind the server.
            port (int): The port number to bind the server.
            frame_width (int): The width of the frames to be processed.
            frame_height (int): The height of the frames to be processed.
        """
        self.host = host
        self.port = port
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.camera_handler = CameraHandler(frame_width, frame_height)
        self.frame_processor = FrameProcessor(frame_width, frame_height)
        self.server_socket = None
        self.running = False
        self.client_threads = []

    def send_frame(self, client_socket, frame):
        """
        Compress and send a frame to the client.

        Args:
            client_socket (socket.socket): The client socket to send the frame to.
            frame (np.ndarray): The frame to send.
        """
        data_to_send = pickle.dumps(frame)  # Serialize the frame
        compressed_data = lz4.frame.compress(data_to_send)  # Compress the serialized frame
        client_socket.sendall(len(compressed_data).to_bytes(4, 'big') + compressed_data)  # Send the size and data

    def send_resolution(self, client_socket):
        width = self.frame_width
        height = self.frame_height
        resolution_message = f"{width}x{height}"
        client_socket.sendall(resolution_message.encode())
        print("resolution sent")

    def handle_client(self, client_socket):
        """
        Handle the client connection, capturing and sending frames.

        Args:
            client_socket (socket.socket): The client socket.
        """
        try:
            self.send_resolution(client_socket)
            back_buffer = np.zeros((self.frame_height * self.frame_width,), dtype=np.uint32)
            first_frame_sent = False
            frame_count = 0
            start_time = time.time()

            while self.running:
                frame = self.camera_handler.grab_frame()  # Capture a frame from the camera
                if frame is None:
                    continue

                frame = self.frame_processor.draw_overlay(frame)  # Draw overlay on the frame
                frame = np.array(frame)
                frame = cv2.resize(frame, (self.frame_width, self.frame_height))  # Resize the frame
                frame = frame.view(np.uint32).reshape((self.frame_height * self.frame_width,))

                if not first_frame_sent:
                    self.send_frame(client_socket, frame)  # Send the first frame
                    first_frame_sent = True
                    back_buffer = frame.copy()
                    continue

                diff_buffer = self.frame_processor.calculate_diff(back_buffer, frame)  # Calculate the difference
                self.send_frame(client_socket, diff_buffer)  # Send the difference frame

                frame_count += 1
                elapsed_time = time.time() - start_time
                if elapsed_time > 1.0:
                    fps = frame_count / elapsed_time  # Calculate FPS
                    print(f"FPS: {fps:.2f}")
                    frame_count = 0
                    start_time = time.time()

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.camera_handler.stop_camera()  # Stop the camera
            client_socket.close()
            cv2.destroyAllWindows()

    def start_server(self):
        """
        Start the server to listen for incoming client connections.
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        print(f"Server is listening on port {self.port}...")

        self.running = True

        try:
            while self.running:
                client_socket, client_address = self.server_socket.accept()  # Accept a new client connection
                print(f"Connection from {client_address} established.")
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                self.client_threads.append(client_thread)
                client_thread.start()  # Handle client in a new thread
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.server_socket.close()
            self.running = False

    def stop_server(self):
        """
        Stop the server and close all connections.
        """
        self.running = False
        if self.server_socket:
            self.server_socket.close()

        # Wait for all client threads to finish
        for thread in self.client_threads:
            thread.join()

        print("Server has been stopped.")
