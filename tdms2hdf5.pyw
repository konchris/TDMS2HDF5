#!/usr/bin/env ipython
""" Testing groud for importing tdms files

"""

__author__ = "Christopher Espy"
__copyright__ = "Copyright (C) 2014, Christopher Espy"
__credits__ = ["Christopher Espy"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Christopher Espy"
__email__ = "christopher.espy@uni-konstanz.de"
__status__ = "Development"

import sys
import os

# Import numpy
import numpy as np

# Import guiqwt stuff

import platform

# Import thrid-party modules
# PyQt4
from PyQt4.QtGui import QApplication, QFileDialog
# npTDMS
from nptdms import TdmsFile

# Import our own modules
from gui_elements import MainWindow

#app = QApplication(sys.argv)

#qtFormat = "TDMS files (*.tdms)"

#File_in = QFileDialog.getOpenFileName(None, 'Open a TDMS File',
#                                             "~/Espy/MeasData", qtFormat)

#Tdms_file_object = TdmsFile(File_in)

#ADWin_Group_Object = tdms_file.object("ADWin")

class Main(MainWindow):

    def __init__(self, parent = None):
        super(Main, self).__init__(parent)

def main(argv=None):

    if argv is None:
        argv = sys.argv

    #### Create the QApplication object
    # This handles the dispatching of events to various widgets. It
    # controls the GUI's control flow and main settings, the main event
    # loop, etc.
    app = QApplication(argv)
    app.setOrganizationName("tdms2hdf5")
    app.setApplicationName("TDMS 2 HDF5 Converter")

    form = Main()
    form.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

