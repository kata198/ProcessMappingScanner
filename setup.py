#!/usr/bin/env python

from setuptools import setup


if __name__ == '__main__':

    try:
        with open('README.rst', 'r') as f:
            long_description = f.read()
    except:
        long_description = ''

    setup(name='ProcessMappingScanner',
            version='2.0.1',
            author='Tim Savannah',
            author_email='kata198@gmail.com',
            maintainer='Tim Savannah',
            packages=['ProcessMappingScanner'],
            url='https://github.com/kata198/ProcessMappingScanner',
            maintainer_email='kata198@gmail.com',
            description='Python module for scanning information on running processes, including mappings, open file-descriptors, process owner, and other information',
            long_description=long_description,
            license='LGPLv3',
            keywords=['process', 'mapping', 'scanner', 'unix', 'proc', 'mappings', 'lib', 'detect', 'executable', 'shared', 'object', 'fd', 'filename', 'search', 'socket', 'descriptor', 'owner', 'pids'],
            classifiers=['Development Status :: 5 - Production/Stable',
                         'Programming Language :: Python',
                         'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
                         'Programming Language :: Python :: 2',
                          'Programming Language :: Python :: 2',
                          'Programming Language :: Python :: 2.7',
                          'Programming Language :: Python :: 3',
                          'Programming Language :: Python :: 3.3',
                          'Programming Language :: Python :: 3.4',
            ]
    )



