"""
Multiprocessing queues for numpy arrays using shared memory

"""

__author__ = "Vilim Stih @portugueslab"

__version__ = "1.2.0"

from arrayqueues.portable_queue import PortableQueue
from arrayqueues.shared_arrays import (
    ArrayQueue,
    IndexedArrayQueue,
    TimestampedArrayQueue,
)
