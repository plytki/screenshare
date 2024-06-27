import numpy as np
import pyopencl as cl


class OpenCLHandler:
    """
    OpenCLHandler is responsible for processing frames using OpenCL.

    Attributes:
        frame_width (int): The width of the frame.
        frame_height (int): The height of the frame.
        context (cl.Context): The OpenCL context.
        queue (cl.CommandQueue): The OpenCL command queue.
        program_add_diff (cl.Program): The compiled OpenCL program for processing image differences.
        back_buffer (np.ndarray): The back buffer for storing processed frames.
        back_buffer_cl (cl.Buffer): The OpenCL buffer for the back buffer.
        diff_buffer_cl (cl.Buffer): The OpenCL buffer for the difference buffer.
    """

    def __init__(self, frame_width, frame_height):
        """
        Initializes the OpenCLHandler with the given frame width and frame height.

        Args:
            frame_width (int): The width of the frames to be processed.
            frame_height (int): The height of the frames to be processed.
        """
        self.frame_width = frame_width
        self.frame_height = frame_height

        # OpenCL setup
        platform = cl.get_platforms()[0]  # Select the first platform
        device = platform.get_devices()[0]  # Select the first device
        self.context = cl.Context([device])
        self.queue = cl.CommandQueue(self.context, device)

        # OpenCL kernel code for processing image differences
        kernel_code = """
        __kernel void AddDiffKernel(__global unsigned int *BackBuffer, __global unsigned int *DiffBuffer, 
                                    unsigned int BufferWidth, unsigned int BufferHeight) {
            unsigned int LinearIndex = get_global_id(0);

            if(LinearIndex >= (BufferWidth * BufferHeight)) return;

            unsigned char Alpha = (DiffBuffer[LinearIndex] >> 24) & 0xFF;

            if(Alpha) {
                BackBuffer[LinearIndex] = DiffBuffer[LinearIndex];
            }
        }
        """
        self.program_add_diff = cl.Program(self.context, kernel_code).build()

        # OpenCL buffers initialization
        mf = cl.mem_flags
        self.back_buffer = np.zeros((frame_height * frame_width,), dtype=np.uint32)
        self.back_buffer_cl = cl.Buffer(self.context, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=self.back_buffer)
        self.diff_buffer_cl = cl.Buffer(self.context, mf.READ_ONLY, self.back_buffer.nbytes)

    def process_frame(self, received_frame):
        """
        Process the received frame using OpenCL.

        Args:
            received_frame (np.ndarray): The frame to process.
        """
        # Copy the received frame to the OpenCL buffer
        cl.enqueue_copy(self.queue, self.diff_buffer_cl, received_frame).wait()

        # Set kernel arguments
        add_diff_kernel = self.program_add_diff.AddDiffKernel
        add_diff_kernel.set_arg(0, self.back_buffer_cl)
        add_diff_kernel.set_arg(1, self.diff_buffer_cl)
        add_diff_kernel.set_arg(2, np.uint32(self.frame_width))
        add_diff_kernel.set_arg(3, np.uint32(self.frame_height))

        # Execute the kernel
        cl.enqueue_nd_range_kernel(self.queue, add_diff_kernel, (self.frame_width * self.frame_height,), None)
        cl.enqueue_copy(self.queue, self.back_buffer, self.back_buffer_cl).wait()

    def get_processed_frame(self):
        """
        Get the processed frame.

        Returns:
            np.ndarray: The processed frame.
        """
        return self.back_buffer
