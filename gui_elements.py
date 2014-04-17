#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Testing groud for importing tdms files


"""

import sys
import os
import platform

# Import thrid-party modules
from PyQt4.QtCore import (PYQT_VERSION_STR, QSettings, QT_VERSION_STR,
                          QVariant, Qt, SIGNAL, QModelIndex, QSize)
from PyQt4.QtGui import (QAction, QApplication, QIcon, QKeySequence, QLabel,
                         QMainWindow, QMessageBox, QTableView, QComboBox,
                         QVBoxLayout, QHBoxLayout, QWidget, QGridLayout,
                         QPushButton, QDialog, QLineEdit, QDialogButtonBox,
                         QGroupBox)
import numpy as np
# Import our own modules
#import qrc_resources

__author__ = "Christopher Espy"
__copyright__ = "Copyright (C) 2014, Christopher Espy"
__credits__ = ["Christopher Espy"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Christopher Espy"
__email__ = "christopher.espy@uni-konstanz.de"
__status__ = "Development"

PROGNAME = os.path.basename(sys.argv[0])
PROGVERSION = __version__

def fuck_this(test=None):
    """Test this shit
    
    Arguments:
    - `test`:
    """
    if test:
        print(test)
    else:
        print("Hello World!")

fuck_this()
test_var = np.float16(2**15 + 2)
