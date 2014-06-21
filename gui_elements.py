#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Testing ground for importing tdms files

"""

import sys
import os
import platform
from datetime import datetime

# Import thrid-party modules
from PyQt4.QtCore import (PYQT_VERSION_STR, QSettings, QT_VERSION_STR,
                          QVariant, Qt, SIGNAL, QModelIndex, QSize, QFile)
from PyQt4.QtGui import (QAction, QApplication, QIcon, QKeySequence, QLabel,
                         QMainWindow, QMessageBox, QTableView, QComboBox,
                         QVBoxLayout, QHBoxLayout, QWidget, QGridLayout,
                         QPushButton, QDialog, QLineEdit, QDialogButtonBox,
                         QGroupBox, QTextBrowser, QSizePolicy, QDoubleSpinBox,
                         QSpinBox, QFrame, QFileDialog, QListWidget)
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

from nptdms.tdms import TdmsFile
import h5py

# Import our own modules
#import qrc_resources
from data_structures import Waveform, Channel, CHAN_DICT

__author__ = "Christopher Espy"
__copyright__ = "Copyright (C) 2014, Christopher Espy"
__credits__ = ["Christopher Espy"]
__license__ = "GPL"
__version__ = "0.2"
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

        # Y selector on Left
        self.ySelector = QListWidget()
        ySelectorLabel = QLabel("y axis channel")
        self.ySelector.setMaximumWidth(ySelectorLabel.sizeHint().width())

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

        # X selector on bottom
        self.xSelector = QListWidget()
        self.xSelector.addItem("Time")
        self.xSelector.setFlow(0)
        xSelectorLabel = QLabel("x axis channel")
        self.xSelector.setMaximumHeight(self.xSelector.sizeHintForColumn(0))

        # Offset and parameter widgets on the right
        self.offsetThing = OffsetWidget()
        

        #2 Create the central widget
        self.centralWidget = QWidget()

        # Left Side
        selectorLayout = QVBoxLayout()
        #selectorLayout.addWidget(xSelectorLabel)
        #selectorLayout.addWidget(self.xSelector)
        selectorLayout.addWidget(ySelectorLabel)
        selectorLayout.addWidget(self.ySelector)
        selectorLayout.addStretch()

        # Center
        centralLayout = QVBoxLayout()
        fileNameLayout = QHBoxLayout()
        xSelectorLayout = QHBoxLayout()
        fileNameLayout.addWidget(sourceFileLabel)
        fileNameLayout.addWidget(self.sourceFileName)
        xSelectorLayout.addWidget(xSelectorLabel)
        xSelectorLayout.addWidget(self.xSelector)
        centralLayout.addLayout(fileNameLayout)
        centralLayout.addWidget(self.canvas)
        centralLayout.addWidget(mpl_toolbar)
        centralLayout.addLayout(xSelectorLayout)

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
        fileExportAction = self.createAction("&Export", self.exprtToHDF5,
                                             "Ctrl+E",
                                             tip="Export the TDMS data to HDF5")
        
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenuActions = (fileOpenAction, fileExportAction, fileQuitAction)
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

    def fileOpen(self): # Process 1
        basedir = "~/Espy/MeasData"
        formats = "TDMS files (*.tdms)"
        fname = QFileDialog.getOpenFileName(self, "Open a TDMS File",
                                            basedir, formats)
        # Process 1.1
        if fname and QFile.exists(fname): 
            self.loadFile(fname)

    def loadFile(self, fname): # Process 1.2
        #TODO self.addRecentFile(fname)  see Rapid GUI ch06.pyw
        self.tdms_file_object = TdmsFile(fname)
        self.filename = fname
        self.dirty = False

         # Process 1.3
        if self.tdms_file_object:

            # Get the ADWin data Process 1.3.1
            self.sortADWinData()

            message = "Loaded {0}".format(os.path.basename(fname))

            print(message)
        else:
            message = "Failed to load {0}".format(os.path.basename(fname))

        #TODO self.updateStatus(message) # see Rapid GUI ch06.pyw

    def sortADWinData(self): # Process 1.3.1
        device = "ADWin"
        # Process 1.3.1.1
        adwin_group_chans = self.tdms_file_object.group_channels(device)
        # Process 1.3.1.2
        adwin_group_props = self.tdms_file_object.object(device).properties 

        # Go through all of the channels in the adwin group and generate
        # the channel data and place it into the channel registry
        # Process 1.3.1.3
        for chan in adwin_group_chans:
            chan_name = chan.path.split('/')[-1].strip("'")

            # Process 1.3.1.3.1
            new_chan = Channel(chan_name,
                               t0 = chan.property("wf_start_time"),
                               dt = chan.property("wf_increment"),
                               Y = chan.data,
                               device = device)

            # Some of the channel-specific properties were actually
            # saved in the group object's properties list.
            # We retrieve those here.
            # Process 1.3.1.3.2
            for atr_name in CHAN_DICT[chan_name]:
                new_chan.attributes[atr_name] = \
                  adwin_group_props[atr_name]

            # Process 1.3.1.3.3
            self.channel_registry[chan_name] = new_chan

    def exprtToHDF5(self): # Process 5
        fname = self.filename.split('.')[0] + '.hdf5'

        # Process 5.1
        self.hdf5_file_object = h5py.File(fname)

        # Process 5.2
        raw = self.hdf5_file_object.create_group('raw')

        # Process 5.3
        for chan in self.channel_registry:

            # Process 5.3.1
            HDF5_data = raw.create_dataset(chan,
                                           data = self.channel_registry[chan].data)
            # Process 5.3.2
            for attr_name in self.channel_registry[chan].attributes:
                attr_value = self.channel_registry[chan].attributes[attr_name]

                # Convert the datetime format to a string
                if type(attr_value) is datetime:
                    attr_value = attr_value.isoformat()

                # There's currently a wierd bug when dealing with python3 strings.
                # This gets around that
                if type(attr_value) is str:
                    #attr_value = attr_value.encode('utf-8')
                    #attr_value = np.string_(attr_value, dtype="S10")
                    attr_value = np.string_(attr_value)

                HDF5_data.attrs.create(attr_name, attr_value)

        # Process 5.4
        self.hdf5_file_object.flush()
        self.hdf5_file_object.close()
                
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
