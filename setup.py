#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function
from setuptools import setup
import io

import ixload


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.txt')

with open('requirements.txt') as f:
    required = f.read().splitlines()
install_requires = [r for r in required if r and r[0] != '#' and not r.startswith('git')]

setup(
    name='ixlooapi',
    version=ixload.__version__,
    url='https://github.com/shmir/PyIxLoad/',
    license='Apache Software License',
    author='Yoram Shamir',
    install_requires=install_requires,
    tests_require=['pytest'],
    author_email='yoram@ignissoft.com',
    description='Python OO API package to automate Ixia IxLoad traffic generator',
    long_description=long_description,
    packages=['ixload', 'ixload.test', 'ixload.api'],
    include_package_data=True,
    platforms='any',
    test_suite='ixload.test',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Testing :: Traffic Generation'],
)
