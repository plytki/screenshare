import socket
import numpy as np
import cv2
import imutils
import time
import pyautogui


class FrameProcessor:
    """
    FrameProcessor is responsible for processing frames by calculating differences and drawing overlays.

    Attributes:
        frame_width (int): The width of the frame.
        frame_height (int): The height of the frame.
        cursor_image (np.ndarray): The image of the cursor to overlay on the frames.
        host_name (str): The hostname of the machine.
    """

    def __init__(self, frame_width, frame_height):
        """
        Initializes the FrameProcessor with the given frame width and frame height.

        Args:
            frame_width (int): The width of the frames to be processed.
            frame_height (int): The height of the frames to be processed.
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.cursor_image = cv2.imread('assets/cursor.png', cv2.IMREAD_UNCHANGED)  # Load the cursor image with alpha channel
        self.cursor_image = imutils.resize(self.cursor_image, width=12)  # Resize the cursor image to a smaller size
        self.host_name = socket.gethostname()  # Get the hostname of the machine

    def draw_overlay(self, frame):
        """
        Draw an overlay on the frame, including the cursor image, hostname, current time, and status message.

        Args:
            frame (np.ndarray): The frame to draw the overlay on.

        Returns:
            np.ndarray: The frame with the overlay.
        """
        cursor_x, cursor_y = pyautogui.position()  # Get the current cursor position
        # Calculate the cursor position relative to the frame dimensions
        cursor_pos = (int(cursor_x * self.frame_width / pyautogui.size().width),
                      int(cursor_y * self.frame_height / pyautogui.size().height))
        cursor_h, cursor_w, cursor_c = self.cursor_image.shape
        x, y = cursor_pos

        # Check if the cursor fits within the frame dimensions
        if x + cursor_w <= frame.shape[1] and y + cursor_h <= frame.shape[0]:
            alpha_cursor = self.cursor_image[:, :, 3] / 255.0  # Extract the alpha channel
            alpha_inv = 1.0 - alpha_cursor  # Calculate the inverse alpha channel

            # Overlay the cursor image on the frame
            for c in range(0, 3):
                frame[y:y + cursor_h, x:x + cursor_w, c] = (alpha_cursor * self.cursor_image[:, :, c] +
                                                            alpha_inv * frame[y:y + cursor_h, x:x + cursor_w, c])

        # Draw the hostname on the frame
        cv2.putText(frame, self.host_name, (10, 30), cv2.QT_FONT_NORMAL, 0.75, (255, 255, 255), 1, cv2.LINE_AA)
        current_time = time.strftime("%H:%M:%S")  # Get the current time
        # Draw the current time on the frame
        cv2.putText(frame, current_time, (10, 60), cv2.QT_FONT_NORMAL, 0.75, (255, 255, 255), 1, cv2.LINE_AA)
        status_message = "Live"  # Define the status message
        # Draw the status message on the frame
        cv2.putText(frame, status_message, (10, 90), cv2.QT_FONT_NORMAL, 0.75, (0, 255, 0), 1, cv2.LINE_AA)

        return frame

    @classmethod
    def calculate_diff(cls, old_image, new_image):
        """
        Calculate the difference between two images.

        Args:
            old_image (np.ndarray): The previous frame.
            new_image (np.ndarray): The current frame.

        Returns:
            np.ndarray: The difference image with alpha channel for changed pixels.
        """
        diff_image = np.zeros_like(old_image)
        differences = old_image != new_image  # Find differences between the old and new images
        diff_image[differences] = (0xFF000000 |
                                   (new_image[differences] & 0x00FFFFFF))  # Mark differences with alpha channel
        old_image[:] = new_image  # Update the old image with the new image
        return diff_image
