from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pi_rtvp",
    version="0.0.1",
    description="Real-Time Video Processing with the Raspberry Pi",
    long_description=long_description,
    url="https://github.com/circuitfox/csc2300-pi-project",
    author="Chris Stankus",
    author_email="cdstankus@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(exclude=['docs', 'tests']),
    install_requires=["RPi.GPIO", "picamera"],
    entry_points={
        "console_scripts": [
            "pi_rtvp=pi_rtvp:main"
        ],
    },
)

