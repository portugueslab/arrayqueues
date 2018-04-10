from arrayqueues.shared_arrays import SharedArrayQueue, TimestampedArrayQueue
from multiprocessing import Process
import numpy as np
from queue import Empty
import unittest


class SourceProcess(Process):
    def __init__(self, n_items=100, timestamped = False):
        super().__init__()
        self.source_array = TimestampedArrayQueue() if timestamped else SharedArrayQueue()
        self.n_items = n_items

    def run(self):
        for i in range(self.n_items):
            self.source_array.put(np.full((100, 500), 5))


class SinkProcess(Process):
    def __init__(self, source_array):
        super().__init__()
        self.source_array = source_array

    def run(self):
        while True:
            try:
                item = self.source_array.get(timeout=0.5)
                assert item[0, 0] == 5
            except Empty:
                break


class TimestampedSinkProcess(Process):
    def __init__(self, source_array):
        super().__init__()
        self.source_array = source_array

    def run(self):
        previous_time = None
        while True:
            try:
                time, item = self.source_array.get(timeout=0.5)
                assert item[0, 0] == 5
                if previous_time is not None:
                    assert time>=previous_time
                previous_time = time
            except Empty:
                break


class TestSample(unittest.TestCase):
    def test_shared_queues(self):
        p1 = SourceProcess(100)
        p2 = SinkProcess(source_array=p1.source_array)
        p1.start()
        p2.start()
        p1.join()
        p2.join()

    def test_shared_timestamped_queues(self):
        p1 = SourceProcess(100, timestamped=True)
        p2 = TimestampedSinkProcess(source_array=p1.source_array)
        p1.start()
        p2.start()
        p1.join()
        p2.join()

