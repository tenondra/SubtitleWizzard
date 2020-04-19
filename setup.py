import fnmatch
import os
from setuptools import setup, find_packages
import sys

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name='subwiz',
    version='1.0',
    # version=subwiz.__version__,
    license="GNU GPL3",
    description="A subtitle wizzard for your media",
    long_description=long_description,
    author='Ondřej Malaník',
    author_email='onmalanik@gmail.com',
    url='https://github.com/tenondra/SubtitleWizzard',
    packages=['src'],
    entry_points={
            "console_scripts": [
                "subwiz=src.subwiz:entry_point"
            ]
    }
)
