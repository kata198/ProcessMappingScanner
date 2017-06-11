#!/usr/bin/env python

from setuptools import setup


if __name__ == '__main__':

    summary = 'Python module for scanning information on running processes, including mappings, open file-descriptors, process owner, and other information'
    try:
        with open('README.rst', 'rt') as f:
            long_description = f.read()
    except Exception as e:
        sys.stderr.write('Got exception reading long description: %s\n' %(str(e),))
        long_description = summary

    setup(name='ProcessMappingScanner',
            version='2.3.2',
            author='Tim Savannah',
            author_email='kata198@gmail.com',
            maintainer='Tim Savannah',
            packages=['ProcessMappingScanner'],
            url='https://github.com/kata198/ProcessMappingScanner',
            maintainer_email='kata198@gmail.com',
            description=summary,
            long_description=long_description,
            license='LGPLv3',
            keywords=['process', 'mapping', 'scanner', 'unix', 'proc', 'mappings', 'lib', 'detect', 'executable', 'shared', 'object', 'fd', 'filename', 'search', 'socket', 'descriptor', 'owner', 'pids', 'cwd'],
            classifiers=['Development Status :: 5 - Production/Stable',
                         'Programming Language :: Python',
                         'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
                         'Programming Language :: Python :: 2',
                          'Programming Language :: Python :: 2',
                          'Programming Language :: Python :: 2.7',
                          'Programming Language :: Python :: 3',
                          'Programming Language :: Python :: 3.3',
                          'Programming Language :: Python :: 3.4',
                          'Programming Language :: Python :: 3.5',
                          'Programming Language :: Python :: 3.6',
            ]
    )



