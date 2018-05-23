from distutils.core import setup
from setuptools import find_packages

setup(name='arrayqueues',
      version='1.0.0b0',
      author='Vilim Stih @portugueslab',
      author_email='vilim@neuro.mpg.de',
      license='MIT',
      packages=find_packages(),
      install_requires=['numpy'],
      classifiers=[
            'Development Status :: 4 - Beta',

            'Intended Audience :: Developers',
            'Topic :: Multimedia :: Video',
            'Topic :: Software Development :: Libraries',

            # Pick your license as you wish (should match "license" above)
            'License :: OSI Approved :: MIT License',

            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
      ],
      keywords='multiprocessing queues arrays',
      description='Multiprocessing queues for numpy arrays using shared memory',
      project_urls={
    'Source': 'https://github.com/portugueslab/arrayqueues',
    'Tracker': 'https://github.com/portugueslab/arrayqueues/issues',
      },
      )

