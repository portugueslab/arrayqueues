from multiprocessing import Process
from datetime import datetime


class FrameProcessor(Process):
    """ A basic class for a process that deals with frames. It provides
    framerate calculation and ?
    # TODO documentation: what is check_mem here?
    # TODO do we realy need this class here?
    """
    def __init__(self, n_fps_frames=10, check_mem=True, print_framerate=False):
        """ Initialize the class.
        :param n_fps_frames: number of frames after which framerate is updated.
        :param check_mem: # TODO unused in this class
        :param print_framerate: flag for printing framerate
        """
        super().__init__()

        # Set framerate calculation parameters
        self.n_fps_frames = n_fps_frames
        self.i_fps = 0
        self.previous_time_fps = None
        self.current_framerate = None
        self.print_framerate = print_framerate
        self.check_mem = check_mem

        # Store current time timestamp:
        self.current_time = datetime.now()
        self.starting_time = datetime.now()

    def update_framerate(self):
        """ Calculate the framerate every n_fps_frames frames.
        """
        # If number of frames for updating is reached:
        if self.i_fps == self.n_fps_frames - 1:
            self.current_time = datetime.now()
            if self.previous_time_fps is not None:
                try:
                    self.current_framerate = self.n_fps_frames / (
                        self.current_time - self.previous_time_fps).total_seconds()
                except ZeroDivisionError:
                    self.current_framerate = 0
                if self.print_framerate:
                    print('FPS: ' + str(self.current_framerate))

            self.previous_time_fps = self.current_time
        # Reset i after every n frames
        self.i_fps = (self.i_fps + 1) % self.n_fps_frames
