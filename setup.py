from distutils.core import setup

from setuptools import find_packages

with open("requirements_dev.txt") as f:
    requirements_dev = f.read().splitlines()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="arrayqueues",
    version="1.3.0",
    author="Vilim Stih @portugueslab",
    author_email="vilim@neuro.mpg.de",
    license="MIT",
    packages=find_packages(),
    install_requires=requirements,
    extras_require=dict(dev=requirements_dev),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video",
        "Topic :: Software Development :: Libraries",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    keywords="multiprocessing queues arrays",
    description="Multiprocessing queues for numpy arrays using shared memory",
    project_urls={
        "Source": "https://github.com/portugueslab/arrayqueues",
        "Tracker": "https://github.com/portugueslab/arrayqueues/issues",
    },
)
