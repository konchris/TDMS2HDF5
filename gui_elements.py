#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Testing ground for importing tdms files

"""

import sys
import os
import platform

# Import thrid-party modules
from PyQt4.QtCore import (PYQT_VERSION_STR, QSettings, QT_VERSION_STR,
                          QVariant, Qt, SIGNAL, QModelIndex, QSize, QFile)
from PyQt4.QtGui import (QAction, QApplication, QIcon, QKeySequence, QLabel,
                         QMainWindow, QMessageBox, QTableView, QComboBox,
                         QVBoxLayout, QHBoxLayout, QWidget, QGridLayout,
                         QPushButton, QDialog, QLineEdit, QDialogButtonBox,
                         QGroupBox, QTextBrowser, QSizePolicy, QDoubleSpinBox,
                         QSpinBox, QFrame, QFileDialog)
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

from nptdms.tdms import TdmsFile

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

class OffsetWidget(QWidget):

    def __init__(self, parent = None):
        super(OffsetWidget, self).__init__(parent)

        offsetLabel = QLabel("Offset")
        self.offsetEntry = QDoubleSpinBox(self)

        layout = QVBoxLayout()
        layout.addWidget(offsetLabel)
        layout.addWidget(self.offsetEntry)

        self.setLayout(layout)

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        #1 Create and Initialize data structures
        # The dirty attribute is a boolean flag to indicate whether the
        # file has unsaved changes.
        self.dirty = False
        self.filename = None

        self.channel_registry = {}

        # Selectors on Left
        self.xSelector = QComboBox()
        self.xSelector.addItems(["None"])
        xSelectorLabel = QLabel("x axis channel")

        self.ySelector = QComboBox()
        self.ySelector.addItems(["None"])
        ySelectorLabel = QLabel("y axis channel")

        # File name and plot in the middle
        self.sourceFileName = QLabel("None")
        self.sourceFileName.setSizePolicy(QSizePolicy.Expanding,
                                          QSizePolicy.Fixed)
        sourceFileLabel = QLabel("current file")
        sourceFileLabel.setSizePolicy(QSizePolicy.Expanding,
                                          QSizePolicy.Fixed)

        # Matplotlib canvas
        self.fig = Figure(dpi = 100)
        self.canvas = FigureCanvas(self.fig)
        mpl_toolbar = NavigationToolbar(self.canvas, self.canvas)

        self.axes = self.fig.add_subplot(111)
        self.axes.grid(True)

        # Offset and parameter widgets on the right
        self.offsetThing = OffsetWidget()
        

        #2 Create the central widget
        self.centralWidget = QWidget()

        # Left Side
        selectorLayout = QVBoxLayout()
        selectorLayout.addWidget(xSelectorLabel)
        selectorLayout.addWidget(self.xSelector)
        selectorLayout.addWidget(ySelectorLabel)
        selectorLayout.addWidget(self.ySelector)
        selectorLayout.addStretch()

        # Center
        centralLayout = QVBoxLayout()
        fileNameLayout = QHBoxLayout()
        fileNameLayout.addWidget(sourceFileLabel)
        fileNameLayout.addWidget(self.sourceFileName)
        centralLayout.addLayout(fileNameLayout)
        centralLayout.addWidget(self.canvas)
        centralLayout.addWidget(mpl_toolbar)

        # Right Side
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(self.offsetThing)
        rightLayout.addStretch()

        layout = QHBoxLayout()
        layout.addLayout(selectorLayout)
        layout.addLayout(centralLayout)
        layout.addLayout(rightLayout)

        self.centralWidget.setLayout(layout)
        self.setCentralWidget(self.centralWidget)

        #3 Create and set up any dock windows

        #4 Create actions and insert them into menus and toolbars
        fileQuitAction = self.createAction("&Quit", self.close, "Ctrl+Q",
                                           "exit", "Close the application")
        fileOpenAction = self.createAction("&Open TDMS File", self.fileOpen,
                                           QKeySequence.Open, "fileopen",
                                           "Open an existing TDMS file")

        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenuActions = (fileOpenAction, fileQuitAction)
        self.addActions(self.fileMenu, self.fileMenuActions)

        #5 Read in application's settings
        settings = QSettings()
        
        # Restore the geometry and state of the main window from last use
        #self.restoreGeometry(settings.value("MainWindow/Geometry"))
        #self.restoreState(settings.value("MainWindow/State"))

        self.setWindowTitle("TDMS to HDF5 Converter")
        
    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
        # Create the action
        action = QAction(text, self)
        # Give it its icon
        if icon is not None:
            action.setIcon(QIcon(":/{0}.png".format(icon)))
        # Give it its shortcut
        if shortcut is not None:
            action.setShortcut(shortcut)
        # Set up its help/tip text
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        # Connect it to a signal
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        # Make it checkable
        if checkable:
            action.setCheckable(True)
        return action
        
    def addActions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def fileOpen(self):
        basedir = "~/Espy/MeasData"
        formats = "TDMS files (*.tdms)"
        fname = QFileDialog.getOpenFileName(self, "Open a TDMS File",
                                            basedir, formats)
        if fname and QFile.exists(fname):
            self.loadFile(fname)

    def loadFile(self, fname):
        #TODO self.addRecentFile(fname) # see Rapid GUI ch06.pyw
        self.tdms_file_object = TdmsFile(fname)
        self.filename = fname
        self.dirty = False
        # Get the ADWin data
        self.sortADWinData()
        message = "Loaded {0}".format(os.path.basename(fname))
        print(message)
        #TODO self.updateStatus(message) # see Rapid GUI ch06.pyw

    def sortADWinData(self):
        device = "ADWin"
        if self.tdms_file_object:
            #print(self.tdms_file_object.object("ADWin").properties.keys())
            
            for chan in self.tdms_file_object.group_channels("ADWin"):
                chan_name = chan.path.split('/')[-1].strip("'")

                # Get the generic stuff for each channel

                self.channel_registry[chan_name] = {}
                self.channel_registry[chan_name]["Device"] = "ADWin"
                self.channel_registry[chan_name]["TimeInterval"] = chan.property("wf_increment")
                self.channel_registry[chan_name]["Length"] = chan.data.size
                self.channel_registry[chan_name]["StartTime"] = chan.property("wf_start_time")

                # Get the channel-specific stuff
                CHAN_DICT = {}
                CHAN_DICT["ISample"] = ["IAmp"]
                CHAN_DICT["VSample"] = ["VAmp"]
                CHAN_DICT["dISample"] = ["IAmp", "LISens"]
                CHAN_DICT["dVSample"] = ["VAmp", "LVSens"]
                if chan_name == "ISample":
                    print(chan_name)

                
                
    def closeEvent(self, event):
        """Reimplementation of the close even handler.
        
        We have to reimplement this because not all close actions, e.g. clicking
        the X button, call the close() method.  We want to catch this so we can
        give the user the opportunity to save unsaved changes before the program
        exits.

        """
        #settings = QSettings()
        #settings.setValue("MainWindow/Geometry", QVariant(
        #    self.saveGeometry()))
        #settings.setValue("MainWindow/State", QVariant(
        #    self.saveState()))
        pass
                
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

    home = os.path.expanduser("~")

    form = MainWindow()
    form.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
