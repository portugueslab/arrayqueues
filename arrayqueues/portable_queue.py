"""The code below has been entirely taken from the following GitHub gist:
https://gist.github.com/FanchenBao/d8577599c46eab1238a81857bb7277c9
"""

import sys
from multiprocessing import Value, get_context, queues


class SharedCounter(object):
    """A synchronized shared counter.

    The locking done by multiprocessing.Value ensures that only a single
    process or thread may read or write the in-memory ctypes object. However,
    in order to do n += 1, Python performs a read followed by a write, so a
    second process may read the old value before the new one is written by the
    first process. The solution is to use a multiprocessing.Lock to guarantee
    the atomicity of the modifications to Value.

    This class comes almost entirely from Eli Bendersky's blog:
    http://eli.thegreenplace.net/2012/01/04/shared-counter-with-pythons-multiprocessing/

    """

    def __init__(self, n=0):
        self.count = Value("i", n)

    def increment(self, n=1):
        """Increment the counter by n (default = 1)"""
        with self.count.get_lock():
            self.count.value += n

    @property
    def value(self):
        """Return the value of the counter"""
        return self.count.value


class PortableQueue(queues.Queue):
    """A portable implementation of multiprocessing.Queue.

    Because of multithreading / multiprocessing semantics, Queue.qsize() may
    raise the NotImplementedError exception on Unix platforms like Mac OS X
    where sem_getvalue() is not implemented. This subclass addresses this
    problem by using a synchronized shared counter (initialized to zero) and
    increasing / decreasing its value every time the put() and get() methods
    are called, respectively. This not only prevents NotImplementedError from
    being raised, but also allows us to implement a reliable version of both
    qsize() and empty().

    """

    def __init__(self, *args, **kwargs):
        self.size = SharedCounter(0)
        super(PortableQueue, self).__init__(*args, ctx=get_context(), **kwargs)

    def __getstate__(self):
        state = super(PortableQueue, self).__getstate__()
        return state + (self.size,)

    def __setstate__(self, state):
        (
            self._ignore_epipe,
            self._maxsize,
            self._reader,
            self._writer,
            self._rlock,
            self._wlock,
            self._sem,
            self._opid,
            self.size,
        ) = state
        if sys.version_info >= (3, 9):
            super(PortableQueue, self)._reset()
        else:
            super(PortableQueue, self)._after_fork()

    def put(self, *args, **kwargs):
        super(PortableQueue, self).put(*args, **kwargs)
        self.size.increment(1)

    def get(self, *args, **kwargs):
        retrived_val = super(PortableQueue, self).get(*args, **kwargs)
        self.size.increment(-1)
        return retrived_val

    def qsize(self):
        """Reliable implementation of multiprocessing.Queue.qsize()"""
        return self.size.value

    def empty(self):
        """Reliable implementation of multiprocessing.Queue.empty()"""
        return not self.qsize()
