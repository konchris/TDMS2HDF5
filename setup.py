from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import io
import codecs
import os
import sys

import TDMS2HDF5

here = os.path.abspath(os.path.dirname(__file__))

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md')

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name='TDMS2HDF5',
    version=TDMS2HDF5.__version__,
    url='http://github.com/konchris/TDMS2HDF5/',
    license='GNU GPLv2',
    author='Christopher Espy',
    tests_require=['pytest'],
    install_requires=['numpy>=1.9.0',
                      'npTDMS>=0.6.2',
                      'matplotlib>=1.4.0',
                      'six>=1.5.2',
                      'nose>=1.3.4',
                      'python-dateutil>=2.2',
                      'pyparsing>=2.0.2',
                      'h5py>=2.3.1',
                      'pandas>=0.14.1',
                      'pytz>=2014.7',
                      'Cython>=0.21.1',
                      'numexpr>=2.4',
                      'scipy>=0.14.0',
                      'pep8>=1.5.7',
                      'pylint>=1.3.1',
                      'pytest>=2.6.3',
                      'seaborn>=0.4.0',
                      'tables>=3.1.1',
                      'Sphinx>=1.2.3'
                      ],
    cmdclass={'test': PyTest},
    entry_points={
        'gui_scripts': [
            'tdms2hdf5 = TDMS2HDF5.tdms2hdf5:main'
            ]
        },
    author_email='github@konchris.de',
    description="View National Instruments' TDMS files and export to HDF5",
    long_description=long_description,
    packages=['TDMS2HDF5'],
    include_package_data=True,
    platforms='any',
    test_suite='test.test_tdms2hdf5',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications :: Qt'
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Visualization'
        ],
    extras_require={
        'testing': ['pytest'],
    }
)
