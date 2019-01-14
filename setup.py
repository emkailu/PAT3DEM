#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name = 'pat3dem',
      version = '0.2.0',
      description = 'Personalized Automatic Tools for 3D Electron Microscopy',
      author = 'Kailu Yang',
      author_email = 'emkailu@gmail.com',
      url = 'https://github.com/emkailu/pat3dem',
      license = 'MIT',
      package_dir = {'': 'lib'},
      packages = find_packages('lib'),
      )
