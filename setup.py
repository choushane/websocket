#!/usr/bin/env python2.7
from setuptools import setup, find_packages

setup(
    name='websocket',
    version='0.1',
    packages=find_packages("."),
    description='Python websocket ...',
    author='Shane Chou',
    author_email='choukuangs@gmail.com',
    install_requires=[
	"pycrypto",
    ],
)
