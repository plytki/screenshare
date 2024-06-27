import numpy as np
import bettercam as dxcam


class CameraHandler:
    """
    CameraHandler is responsible for interfacing with the camera to grab frames.

    Attributes:
        frame_width (int): The width of the frame.
        frame_height (int): The height of the frame.
        camera (dxcam.Camera): The camera object from the dxcam library.
    """

    def __init__(self, frame_width, frame_height):
        """
        Initializes the CameraHandler with the given frame width and frame height.

        Args:
            frame_width (int): The width of the frames to be grabbed.
            frame_height (int): The height of the frames to be grabbed.
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.camera = dxcam.create(output_color="BGRA")  # Initialize the camera with BGRA color format

    def grab_frame(self):
        """
        Grab a frame from the camera.

        Returns:
            np.ndarray: The grabbed frame.
        """
        return self.camera.grab()  # Grab a frame from the camera

    def stop_camera(self):
        """
        Stop the camera.
        """
        self.camera.stop()  # Stop the camera