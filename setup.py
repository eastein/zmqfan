#!/usr/bin/env python

from setuptools import setup

setup(name='zmqfan',
      version='0.8.0',
      description='ZMQFan zeromq helper wrappers.',
      author='Eric Stein',
      author_email='toba@des.truct.org',
      url='https://github.com/eastein/zmqfan/',
      install_requires=['pyzmq>=14', 'six>=1.8.0'],
      packages=['zmqfan'],
      )
