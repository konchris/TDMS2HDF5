#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Test the GUI (sort of)

"""

__author__ = "Christopher Espy"
__copyright__ = "Copyright (C) 2014, Christopher Espy"
__credits__ = ["Christopher Espy"]
__license__ = "GPL"
__version__ = "0.5"
__maintainer__ = "Christopher Espy"
__email__ = "christopher.espy@uni-konstanz.de"
__status__ = "Development"

import sys
import unittest

from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from TDMS2HDF5.tdms2hdf5 import Presenter

class TestMyMainWindow(unittest.TestCase):
    pass

if __name__ == "__main__":
    unittest.main()
