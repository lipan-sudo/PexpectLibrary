#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from setuptools import setup, find_packages
import sys
setup(
    name="PexpectLibrary",
    version="0.2.0",
    author="pan li",
    author_email="lipan.sudo@gmail.com",
    description="An (almost) complete and convenience Pexpect wrapper for Robot Framework, with extra functionalities.",
    license="MIT",
    url="https://github.com/lipan-sudo/PexpectLibrary",
    packages=find_packages(exclude=['tests*', 'examples']),
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        "Topic :: Software Development :: Libraries :: Python Modules",
        'Programming Language :: Python :: 3',
    ],
    zip_safe=False,
    install_requires=[
        'pexpect>=4.6.0',
        'robotframework>=3.2.2',
        'pyserial>=3.5'
    ]
)