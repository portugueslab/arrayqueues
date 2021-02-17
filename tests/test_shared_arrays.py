import time
from multiprocessing import Process
from queue import Empty, Full

import numpy as np

from arrayqueues.shared_arrays import (
    ArrayQueue,
    IndexedArrayQueue,
    TimestampedArrayQueue,
)


class SourceProcess(Process):
    def __init__(
        self,
        n_items=100,
        timestamped=False,
        indexed=False,
        n_mbytes=2,
        wait=0,
        test_full=False,
    ):
        super().__init__()
        self.source_array = (
            IndexedArrayQueue(max_mbytes=n_mbytes)
            if indexed
            else (
                TimestampedArrayQueue(max_mbytes=n_mbytes)
                if timestamped
                else ArrayQueue(max_mbytes=n_mbytes)
            )
        )
        self.n_items = n_items
        self.wait = wait
        self.test_full = test_full

    def run(self):
        full = False
        for i in range(self.n_items):
            try:
                self.source_array.put(np.full((100, 100), 5, np.uint8))
                print("I inserted ", self.source_array.view.i_item)
                print("Last item read was ", self.source_array.last_item)
            except Full:
                full = True
                if not self.test_full:
                    assert False
            if self.wait > 0:
                time.sleep(self.wait)
        if self.test_full and not full:
            assert False
        else:
            assert True
        print(self.source_array.view.total_shape)


class SinkProcess(Process):
    def __init__(self, source_array, limit=None):
        super().__init__()
        self.source_array = source_array
        self.limit = limit

    def run(self):
        while True:
            try:
                item = self.source_array.get(timeout=0.5)
                print("Got item")
                assert item[0, 0] == 5
            except Empty:
                break
            if self.limit is not None:
                self.limit -= 1
                if self.limit == 0:
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
                    assert time >= previous_time
                previous_time = time
            except Empty:
                break


def test_sample():
    p1 = SourceProcess(100)
    p2 = SinkProcess(source_array=p1.source_array)
    p1.start()
    p2.start()
    p1.join()
    p2.join()


def test_shared_timestamped_queues():
    p1 = SourceProcess(100, timestamped=True)
    p2 = TimestampedSinkProcess(source_array=p1.source_array)
    p1.start()
    p2.start()
    p1.join()
    p2.join()


def test_full_queue():
    # Here we intentionally overfill the queue to test if the right
    # exception is raised
    # TODO is this actually completed?
    p1 = SourceProcess(40, n_mbytes=0.2, wait=0.1, test_full=True)
    p2 = SinkProcess(source_array=p1.source_array, limit=4)
    p1.start()
    p2.start()
    p2.join()
    p1.join()


def test_clearing_queue():
    p1 = SourceProcess(5, n_mbytes=10)
    p1.start()
    p1.join()
    p1.source_array.clear()
    time.sleep(1.0)
    assert p1.source_array.empty()
