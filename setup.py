#!/usr/bin/env python

from distutils.core import setup

setup(name = 'thebigpicture',
      version = 'v1-alpha1',
      packages = ['TBP'],
      description = 'Read and write metadata in Jpeg and Tiff files',
      author = 'Pieter Edelman',
      author_email = 'p.edelman@gmx.net',
      url = 'http://code.google.com/p/thebigpicture/',
      classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License ::	OSI Approved :: GNU Lesse General Public License (LGPL)',
        'Operating System :: POSIX :: Linux',
        'Operating System :: OS Independant',
        'Programming Language :: Python',
        'Topic ::	Multimedia :: Graphics'
      ],
      provides = ["The Big Picture"]
     )
