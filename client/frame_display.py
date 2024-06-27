import numpy as np
import cv2


class FrameDisplay:
    """
    FrameDisplay is responsible for displaying frames using OpenCV.

    Attributes:
        frame_width (int): The width of the frame.
        frame_height (int): The height of the frame.
        display_width (int): The width of the display window.
        display_height (int): The height of the display window.
    """

    def __init__(self, frame_width, frame_height, display_width=None, display_height=None):
        """
        Initializes the FrameDisplay with the given frame width, frame height, display width, and display height.

        Args:
            frame_width (int): The width of the frames to be displayed.
            frame_height (int): The height of the frames to be displayed.
            display_width (int, optional): The width of the display window. Defaults to frame_width.
            display_height (int, optional): The height of the display window. Defaults to frame_height.
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.display_width = display_width if display_width is not None else frame_width
        self.display_height = display_height if display_height is not None else frame_height

    def display_frame(self, frame):
        """
        Display the frame using OpenCV.

        Args:
            frame (np.ndarray): The frame to display. The frame should be in a format
                                that can be reshaped into (frame_height, frame_width, 4).
        """
        display_frame = frame.astype(np.uint32)  # Ensure the frame is in the correct data type
        # Reshape the frame to have the correct dimensions and 4 channels (e.g., RGBA).
        reshaped_frame = display_frame.view(np.uint8).reshape((self.frame_height, self.frame_width, 4))
        # Resize the frame to the display resolution.
        resized_frame = cv2.resize(reshaped_frame, (self.display_width, self.display_height), interpolation=cv2.INTER_LINEAR)
        # Display the resized frame.
        cv2.imshow("Screen", resized_frame)

    def wait_for_quit(self):
        """
        Wait for the 'q' key to be pressed to quit the display.

        Returns:
            bool: True if 'q' was pressed, False otherwise.
        """
        return cv2.waitKey(1) == ord('q')  # Check if 'q' key is pressed

    def close(self):
        """
        Close all OpenCV windows.
        """
        cv2.destroyAllWindows()
