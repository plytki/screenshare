from opencl_handler import OpenCLHandler
from frame_receiver import FrameReceiver
from frame_display import FrameDisplay


class ClientHandler:
    """
    ClientHandler is responsible for receiving, processing, and displaying frames.

    Attributes:
        receiver (FrameReceiver): The frame receiver object.
        processor (OpenCLHandler): The OpenCL processor object.
        display (FrameDisplay): The frame display object.
    """

    def __init__(self, host, port, display_width=None, display_height=None):
        """
        Initializes the ClientHandler with the given host, port, and optional display width and height.

        Args:
            host (str): The host address to connect to.
            port (int): The port number to connect to.
            display_width (int, optional): The width of the display window. Defaults to None.
            display_height (int, optional): The height of the display window. Defaults to None.
        """
        self.receiver = FrameReceiver(host, port)
        self.processor = OpenCLHandler(self.receiver.frame_width, self.receiver.frame_height)
        self.display = FrameDisplay(self.receiver.frame_width, self.receiver.frame_height, display_width, display_height)

    def start(self):
        """
        Starts the client to receive, process, and display frames.

        Continuously receives frames from the receiver, processes them using the OpenCL processor,
        and displays them using the frame display. The loop terminates if no more frames are received
        or if the user chooses to quit.

        Raises:
            Exception: If an error occurs during the frame handling process.
        """
        try:
            while True:
                received_frame = self.receiver.receive_data()
                if received_frame is None:
                    break

                self.processor.process_frame(received_frame)
                processed_frame = self.processor.get_processed_frame()
                self.display.display_frame(processed_frame)

                if self.display.wait_for_quit():
                    break

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            self.receiver.close()
            self.display.close()
