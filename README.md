# ArrayQueues

[![Python Version](https://img.shields.io/pypi/pyversions/arrayqueues.svg)](https://pypi.org/project/arrayqueues)
[![Tests](https://img.shields.io/github/workflow/status/portugueslab/arrayqueues/tests)](
    https://github.com/portugueslab/arrayqueues/actions)
[![Coverage Status](https://coveralls.io/repos/github/portugueslab/arrayqueues/badge.svg?branch=master)](https://coveralls.io/github/portugueslab/arrayqueues?branch=master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/arrayqueues.svg)](https://badge.fury.io/py/arrayqueues)

This package provides a drop-in replacement for the Python multiprocessing Queue class which handles transport of large numpy arrays.
It avoids pickling and uses the multiprocessing Array class in the background.
The major difference between this implementation and the normal queue is that the maximal amount of memory that the queue can have must be specified beforehand.

Attempting to send an array of a different shape or datatype of the previously inserted one resets the queue.
Only passing of numpy arrays is supported, optionally annotated with timestamps if using the TimestampedArrayQueue class,
but other object types can be supported by extending the class.

The package has been tested on Python 3.6/3/7 on Windows and MacOS and Linux with Travis. Python 2.7 is not supported.

# Usage example
```python
from arrayqueues.shared_arrays import ArrayQueue
from multiprocessing import Process
import numpy as np

class ReadProcess(Process):
    def __init__(self, source_queue):
        super().__init__()
        self.source_queue = source_queue
      
    def run(self):
        print(self.source_queue.get())

if __name__ == "__main__":
    q = ArrayQueue(1) # intitialises an ArrayQueue which can hold 1MB of data
    n = np.full((5,5), 5)
    q.put(n)
    r = ReadProcess(q)
    r.start()
    r.join()
    
```

Further examples can be found in tests.
