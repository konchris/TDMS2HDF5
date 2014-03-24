#!/usr/bin/env python
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
                         QGroupBox, QTextBrowser)
from guiqwt.plot import (PlotManager, CurveWidget, CurveDialog)

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

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        #1 Create and Initialize data structures
        
        self.xSelector = QComboBox()
        self.xSelector.addItems(["x1", "x2", "x3"])
        xSelectorLabel = QLabel("x axis channel")

        self.ySelector = QComboBox()
        self.ySelector.addItems(["y1", "y2", "y3"])
        xSelectorLabel = QLabel("y axis channel")

        self.sourceFileName = QLabel()
        sourceFileLabel = QLabel("current file")

        self.plotDisplay = CurveWidget()

        #2 Create the central widget
        self.centralWidget = QWidget()

        # Left Side
        selectorLayout = QVBoxLayout()
        selectorLayout.addWidget(self.xSelector)
        selectorLayout.addWidget(self.ySelector)
        selectorLayout.addStretch()

        # Center
        centralLayout = QVBoxLayout()
        centralLayout.addWidget(self.sourceFileName)
        centralLayout.addWidget(self.plotDisplay)

        # Right Side
        rightLayout = QVBoxLayout()

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

        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenuActions = (fileQuitAction,)
        self.addActions(self.fileMenu, self.fileMenuActions)

        #5 Read in application's settings
        #settings = QSettings()
        # Restore the geometry and state of the main window from last use
        #self.restoreGeometry(settings.value("MainWindow/Geometry").toByteArray())
        #self.restoreState(settings.value("MainWindow/State").toByteArray())

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
                
    def closeEvent(self, event):
        """Reimplementation of the close even handler.
        
        We have to reimplement this because not all close actions, e.g. clicking
        the X button, call the close() method.  We want to catch this so we can
        give the user the opportunity to save unsaved changes before the program
        exits.

        """
        settings = QSettings()
        settings.setValue("MainWindow/Geometry", QVariant(
            self.saveGeometry()))
        settings.setValue("MainWindow/State", QVariant(
            self.saveState()))
                
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
