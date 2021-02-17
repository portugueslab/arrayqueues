import time
from multiprocessing import Process
from queue import Empty

from arrayqueues.portable_queue import PortableQueue


class SourceProcess(Process):
    def __init__(self, n_elements):
        super().__init__()
        self.n_elements = n_elements
        self.source_queue = PortableQueue()

    def run(self):
        for i in range(self.n_elements):
            self.source_queue.put(1)


class SinkProcess(Process):
    def __init__(self, source_queue):
        super().__init__()
        self.source_queue = source_queue

    def run(self):
        while True:
            try:
                _ = self.source_queue.get(timeout=0.5)
            except Empty:
                break


def test_portable_queue():
    N_ELEMENTS = 5

    p1 = SourceProcess(N_ELEMENTS)
    p2 = SinkProcess(source_queue=p1.source_queue)
    p1.start()
    time.sleep(3)
    assert p1.source_queue.qsize() == N_ELEMENTS
    p2.start()
    time.sleep(3)
    assert p1.source_queue.qsize() == 0
    p2.join()
    p1.join()
