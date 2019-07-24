#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup

PACKAGE_NAME = 'pyroglyph'
VERSION = '0.0.3'

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    python_requires='>=3.6',
    description='A simple library for building real-time text-based UIs',
    long_description=open('README.rst').read(),
    author='Chris Timperley',
    author_email='ctimperley@cmu.edu',
    url='https://github.com/ChrisTimperley/pyroglyph',
    license='Apache License 2.0',
    install_requires=[
        'typing-extensions>=3.7.2',
        'attrs~=19.1.0',
        'blessed~=1.15.0'
    ],
    packages=['pyroglyph'],
    keywords=['cli', 'blessed', 'ui', 'simple'],
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ]
)
