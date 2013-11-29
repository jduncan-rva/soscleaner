#!/usr/bin/env python
from distutils.core import setup

version = '0.1'

setup(
    name='SOSCleaner',
    license = 'GPLv2',
    version=version,
    description='To clean and filter sensitive data from a standard sosreport',
    author='Jamie Duncan',
    author_email='jduncan@redhat.com',
    url='https://github.com/jduncan-rva/SOSCleaner',
    platform=['Linux'],
    maintainer='Jamie Duncan',
    maintainer_email = 'jduncan@redhat.com',
    long_description='SOSCleaner is an application to filer out sensitive and un-scan-able data from a standard sosreport',
    packages=['python-magic'],
    py_modules=['SOSCleaner'],
    scripts = ['soscleaner'],
    data_files=[
            ('/usr/share/doc/SOSCleaner-%s'% version, ['README','README.md','LICENSE']),
        ],
    )

