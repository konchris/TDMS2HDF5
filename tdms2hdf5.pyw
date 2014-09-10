#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Testing groud for importing tdms files

"""

__author__ = "Christopher Espy"
__copyright__ = "Copyright (C) 2014, Christopher Espy"
__credits__ = ["Christopher Espy"]
__license__ = "GPL"
__version__ = "0.4.2"
__maintainer__ = "Christopher Espy"
__email__ = "christopher.espy@uni-konstanz.de"
__status__ = "Development"

import sys

# Import thrid-party modules

# PyQt4
from PyQt4.QtGui import (QApplication, QFileDialog, QKeySequence)

# Import our own modules
from view import MyMainWindow
from ChannelModel import  (ChannelRegistry)
from view_model import (TreeNode, TreeModel)

BASEDIR = '/home/chris/Documents/PhD/root/raw-data/sio2al149/CryoMeasurement'

class Main(MyMainWindow):

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)


class Presenter(object):

    def __init__(self):
        super(Presenter, self).__init__()

        self.view = None
        self.yModel = None
        self.xModel = None
        self.channelRegistry = None

        self.fileMenu = None

    def setView(self, view):
        self.view = view
        self._setUpView()

    def setYModel(self, yModel):
        self.yModel = yModel
        self.view.ySelectorView.setModel(self.yModel)

    def setXModel(self, xModel):
        self.xModel = xModel

    def setChanReg(self, chanReg):
        self.channelRegistry = chanReg

    def _setUpView(self):

        # Actions
        fileQuitAction = self.view.createAction("&Quit", self.view.close, "Ctrl+Q",
                                           "exit", "Close the application")
        fileOpenAction = self.view.createAction("&Open TDMS File", self.fileOpen,
                                           QKeySequence.Open, "open",
                                           "Open an existing TDMS file")
        fileExportAction = self.view.createAction("&Export", self.exprtToHDF5,
                                             "Ctrl+E", 'export',
                                             tip="Export the TDMS data to HDF5")

        self.fileMenu = self.view.menuBar().addMenu("&File")
        self.fileMenuActions = (fileOpenAction, fileExportAction,
                                fileQuitAction)
        self.view.addActions(self.fileMenu, self.fileMenuActions)

    def fileOpen(self):
        formats = "TDMS files (*.tdms)"
        fname = QFileDialog.getOpenFileName(self.view, "Open a TDMS File", BASEDIR,
                                            formats)
        self.channelRegistry.loadFromFile(fname)

        self.populateYSelector()

    def populateYSelector(self):
        rootNode0 = TreeNode("")
        raw = 'raw'
        proc = 'proc'
        rawNode = TreeNode(raw, rootNode0)
        procNode = TreeNode(proc, rootNode0)
        for k, v in self.channelRegistry.items():
            if raw in k:
                childNode = TreeNode(v.name, rawNode)
            elif proc in k:
                childNode = TreeNode(v.name, procNode)

        self.setYModel(TreeModel(rootNode0))
        self.view.ySelectorView.update()

    def exprtToHDF5(self):
        pass


def main(argv=None):

    if argv is None:
        argv = sys.argv

    app = QApplication(argv)
    app.setOrganizationName("tdms2hdf5")
    app.setApplicationName("TDMS-2-HDF5 Converter")

    presenter = Presenter()

    presenter.setView(Main())
    presenter.setChanReg(ChannelRegistry())

    presenter.view.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

