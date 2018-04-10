from distutils.core import setup
from setuptools import find_packages

setup(name='arrayqueues',
      version='0.1',
      author='Vilim Stih @portugueslab',
      author_email='vilim@neuro.mpg.de',
      packages=find_packages(),
      install_requires=['numpy'])

