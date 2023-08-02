from datetime import datetime
from multiprocessing import Array
from queue import Empty, Full

# except AttributeError:
# from multiprocessing import Queue
import numpy as np

# try:
from arrayqueues.portable_queue import PortableQueue  # as Queue


class ArrayView:
    def __init__(self, array, max_bytes, dtype, el_shape, i_item=0):
        self.dtype = dtype
        self.el_shape = el_shape
        self.nbytes_el = self.dtype.itemsize * np.product(self.el_shape)
        self.n_items = int(np.floor(max_bytes / self.nbytes_el))
        self.total_shape = (self.n_items,) + self.el_shape
        self.i_item = i_item
        self.view = np.frombuffer(array, dtype, np.product(self.total_shape)).reshape(
            self.total_shape
        )

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(self, other.__class__):
            return self.el_shape == other.el_shape and self.dtype == other.dtype
        return False

    def push(self, element):
        self.view[self.i_item, ...] = element
        i_inserted = self.i_item
        self.i_item = (self.i_item + 1) % self.n_items
        # a tuple is returned to maximise performance
        return self.dtype, self.el_shape, i_inserted

    def pop(self, i_item):
        return self.view[i_item, ...]

    def fits(self, item):
        if isinstance(item, np.ndarray):
            return item.dtype == self.dtype and item.shape == self.el_shape
        return (
            item[0] == self.dtype
            and item[1] == self.el_shape
            and item[2] < self.n_items
        )


class ArrayQueue:
    """A drop-in replacement for the multiprocessing queue, usable
    only for numpy arrays, which removes the need for pickling and
    should provide higher speeds and lower memory usage

    """

    def __init__(self, max_mbytes=10):
        self.maxbytes = int(max_mbytes * 1000000)
        self.array = Array("c", self.maxbytes)
        self.view = None
        self.queue = PortableQueue()
        self.read_queue = PortableQueue()
        self.last_item = 0

    def check_full(self):
        while True:
            try:
                self.last_item = self.read_queue.get(timeout=0.00001)
            except Empty:
                break
        if self.view.i_item == self.last_item:
            raise Full(
                "Queue of length {} full when trying to insert {},"
                " last item read was {}".format(
                    self.view.n_items, self.view.i_item, self.last_item
                )
            )

    def put(self, element):
        if self.view is None or not self.view.fits(element):
            self.view = ArrayView(
                self.array.get_obj(), self.maxbytes, element.dtype, element.shape
            )
            self.last_item = 0
        else:
            self.check_full()
        qitem = self.view.push(element)

        self.queue.put(qitem)

    def get(self, **kwargs):
        aritem = self.queue.get(**kwargs)
        if self.view is None or not self.view.fits(aritem):
            self.view = ArrayView(self.array.get_obj(), self.maxbytes, *aritem)
        self.read_queue.put(aritem[2])
        return self.view.pop(aritem[2])

    def clear(self):
        """Empties the queue without the need to read all the existing
        elements

        :return: nothing
        """
        self.view = None
        while True:
            try:
                _ = self.queue.get_nowait()
            except Empty:
                break
        while True:
            try:
                _ = self.read_queue.get_nowait()
            except Empty:
                break

        self.last_item = 0

    def empty(self):
        return self.queue.empty()

    def qsize(self):
        return self.queue.qsize()


class TimestampedArrayQueue(ArrayQueue):
    """A small extension to support timestamps saved alongside arrays"""

    def put(self, element, timestamp=None):
        if self.view is None or not self.view.fits(element):
            self.view = ArrayView(
                self.array.get_obj(), self.maxbytes, element.dtype, element.shape
            )
        else:
            self.check_full()

        qitem = self.view.push(element)
        if timestamp is None:
            timestamp = datetime.now()

        self.queue.put((timestamp, qitem))

    def get(self, **kwargs):
        timestamp, aritem = self.queue.get(**kwargs)
        if self.view is None or not self.view.fits(aritem):
            self.view = ArrayView(self.array.get_obj(), self.maxbytes, *aritem)
        self.read_queue.put(aritem[2])
        return timestamp, self.view.pop(aritem[2])


class IndexedArrayQueue(ArrayQueue):
    """A small extension to support timestamps saved alongside arrays"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = 0

    def put(self, element, timestamp=None):
        if self.view is None or not self.view.fits(element):
            self.view = ArrayView(
                self.array.get_obj(), self.maxbytes, element.dtype, element.shape
            )
        else:
            self.check_full()

        qitem = self.view.push(element)
        if timestamp is None:
            timestamp = datetime.now()

        self.queue.put((timestamp, self.counter, qitem))
        self.counter += 1

    def get(self, **kwargs):
        timestamp, index, aritem = self.queue.get(**kwargs)
        if self.view is None or not self.view.fits(aritem):
            self.view = ArrayView(self.array.get_obj(), self.maxbytes, *aritem)
        self.read_queue.put(aritem[2])
        return timestamp, index, self.view.pop(aritem[2])
