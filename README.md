# ArrayQueues

[![Build Status](https://travis-ci.org/portugueslab/arrayqueues.svg?branch=master)](https://travis-ci.org/portugueslab/arrayqueues)

This package provides a replacement for the Python multiprocessing Queue class which handles transport of large arrays.
It avoids pickling and uses the multiprocessing Array class in the background.
The major difference is that the maximal amount of memory that the queue can have has to be specified beforehand.

Attempting to send an array of a different shape or datatype of the previously inserted one resets the queue.
Only passing of numpy arrays is supported, optionally annotated with timestamps if using the TimestampedArrayQueue class,
but more complicated structures can be constructed by extending the class.

The package has been tested on Python 3.6 on Windows and MacOS, but should work for other versions of
Python and operating systems.





