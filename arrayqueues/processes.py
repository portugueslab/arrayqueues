from multiprocessing import Process
from datetime import datetime


class FrameProcessor(Process):
    def __init__(self, n_fps_frames=10, check_mem=True, print_framerate=False):
        """ A basic class for a process that deals with frames, provides
        framerate calculation

        :param n_fps_frames:
        :param print_framerate:
        :param check_mem:
        """
        super().__init__()

        # framerate calculation parameters
        self.n_fps_frames = n_fps_frames
        self.i_fps = 0
        self.previous_time_fps = None
        self.current_framerate = None
        self.print_framerate = print_framerate
        self.check_mem = check_mem

        self.current_time = datetime.now()
        self.starting_time = datetime.now()

    def update_framerate(self):
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
        self.i_fps = (self.i_fps + 1) % self.n_fps_frames