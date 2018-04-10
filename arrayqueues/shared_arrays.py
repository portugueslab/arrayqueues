from multiprocessing import Queue, Array
import numpy as np
from datetime import datetime


class ArrayView:
    def __init__(self, array, max_bytes, dtype, el_shape, i_item=0):
        self.dtype = dtype
        self.el_shape = el_shape
        self.nbytes_el = self.dtype.itemsize * np.product(self.el_shape)
        self.n_items = int(np.floor(max_bytes / self.nbytes_el))
        self.total_shape = (self.n_items,) + self.el_shape
        self.i_item = i_item
        self.view = np.frombuffer(array, dtype, np.product(self.total_shape)).reshape(self.total_shape)

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(self, other.__class__):
            return self.el_shape == other.el_shape and self.dtype == other.dtype
        return False

    def push(self, element):
        # TODO warn when overwriting an unread item
        self.view[self.i_item, ...] = element
        i_inserted = self.i_item
        self.i_item = (self.i_item + 1) % self.n_items
        return self.dtype, self.el_shape, i_inserted # a tuple is returned to maximise performance

    def pop(self, i_item):
        return self.view[i_item, ...]

    def fits(self, item):
        if isinstance(item, np.ndarray):
            return item.dtype == self.dtype and item.shape == self.el_shape
        return (item[0] == self.dtype and
                item[1] == self.el_shape and
                item[2] < self.n_items)


class ArrayQueue:
    """ A drop-in replacement for the multiprocessing queue, usable
     only for numpy arrays, which removes the need for pickling and
     should provide higher speeds and lower memory usage

    """
    def __init__(self, max_mbytes=10):
        self.maxbytes = int(max_mbytes*1000000)
        self.array = Array('c', self.maxbytes)
        self.current_view = None
        self.queue = Queue()

    def put(self, element):
        if self.current_view is None or not self.current_view.fits(element):
            self.current_view = ArrayView(self.array.get_obj(), self.maxbytes,
                                          element.dtype, element.shape)
        qitem = self.current_view.push(element)
        self.queue.put(qitem)

    def get(self, **kwargs):
        aritem = self.queue.get(**kwargs)
        if self.current_view is None or not self.current_view.fits(aritem):
            self.current_view = ArrayView(self.array.get_obj(), self.maxbytes,
                                          *aritem)
        return self.current_view.pop(aritem[2])


class TimestampedArrayQueue(ArrayQueue):
    """ A small extension to support timestamps saved alongside arrays

    """
    def put(self, element, timestamp=None):
        if self.current_view is None or not self.current_view.fits(element):
            self.current_view = ArrayView(self.array.get_obj(), self.maxbytes,
                                          element.dtype, element.shape)
        qitem = self.current_view.push(element)
        if timestamp is None:
            timestamp = datetime.now()
        self.queue.put((timestamp, qitem))

    def get(self, **kwargs):
        timestamp, aritem = self.queue.get(**kwargs)
        if self.current_view is None or not self.current_view.fits(aritem):
            self.current_view = ArrayView(self.array.get_obj(), self.maxbytes,
                                          *aritem)
        return timestamp, self.current_view.pop(aritem[2])