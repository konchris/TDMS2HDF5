#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103
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

import os
import sys

# Import thrid-party modules

# PyQt4
from PyQt4.QtGui import (QApplication, QFileDialog, QKeySequence, QMessageBox)
from PyQt4.QtCore import (QModelIndex)

# Import our own modules
from view import (MyMainWindow, AXESLABELS)
from ChannelModel import  (ChannelRegistry)
from view_model import (TreeNode, TreeModel, MyListModel)

BASEDIR = '/home/chris/Documents/PhD/root/raw-data/'

class Main(MyMainWindow):
    """ The main window of the program.

    """

    def __init__(self, parent=None):
        super(Main, self).__init__(parent)


class Presenter(object):
    """The presenter coordinates between the PyQt models and channel registry

    """

    def __init__(self):
        super(Presenter, self).__init__()

        self.baseDir = BASEDIR

        self.view = None
        self.yModel = None
        self.xModel = None
        self.channelRegistry = None

        self.ySelected = None
        self.ySelected_old = None
        self.xSelected = None
        self.xSelected_old = None

        self.fileMenu = None

    def setView(self, view):
        """Set the view to which the information is pushed.

        Parameters
        ----------
        view : PyQt.QtGui
            The main window, dialog, etc through with the information is
            displayed.

        """

        self.view = view
        self._setUpView()

    def setYModel(self, yModel):
        """Set the model for the y Selector Tree View.

        Parameters
        ----------
        yModel : PyQt type model
            The model that will display information in the tree view.

        """
        self.yModel = yModel
        self.view.ySelectorView.setModel(self.yModel)

    def setXModel(self, xModel):
        """Set the model for the x Selector List View.

        Parameters
        ----------
        xModel : PyQt type model
            The model that will display information in the list view.

        """
        self.xModel = xModel
        self.view.xSelectorView.setModel(self.xModel)

    def setChanReg(self, chanReg):
        """Set the presenter's channel registry, i.e. the lower model.

        Parameters
        ----------
        chanReg : Channel Registry type object
            This is the underlying model that deals with communicating with
            TDMS and HDF5 files.

        """
        self.channelRegistry = chanReg

    def _setUpView(self):
        """Once the view and underlying model have added, setup the view.

        """

        self.view.xSelectorView.setFlow(0)

        # Actions
        fileQuitAction = self.view.createAction("&Quit", self.view.close,
                                                "Ctrl+Q", "exit",
                                                "Close the application")
        fileOpenAction = self.view.createAction("&Open TDMS File",
                                                self.fileOpen,
                                                QKeySequence.Open, "open",
                                                "Open an existing TDMS file")
        fileExportAction = self.view.createAction("&Export", self.exprtToHDF5,
                                             "Ctrl+E", 'export',
                                             tip="Export the TDMS data to HDF5")

        self.fileMenu = self.view.menuBar().addMenu("&File")
        self.fileMenuActions = (fileOpenAction, fileExportAction,
                                fileQuitAction)
        self.view.addActions(self.fileMenu, self.fileMenuActions)

        # Connections
        self.view.ySelectorView.clicked.connect(self.newYSelection)
        self.view.xSelectorView.clicked.connect(self.newXSelection)

    def fileOpen(self):
        """Open a file."""
        formats = "TDMS files (*.tdms)"
        fname = QFileDialog.getOpenFileName(self.view, "Open a TDMS File",
                                            self.baseDir, formats)
        self.channelRegistry.loadFromFile(fname)

        self.baseDir = os.path.dirname(fname)

        self.populateSelectors()

    def populateSelectors(self):
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
        self.setXModel(MyListModel(['Time'] + list(self.channelRegistry.keys())))
        self.view.ySelectorView.expandAll()
        self.view.ySelectorView.setHeaderHidden(True)
        self.view.ySelectorView.setMaximumWidth(self.view.ySelectorView.sizeHintForColumn(0) + 10)

        self.view.xSelectorView.setMaximumHeight(self.view.xSelectorView.sizeHintForColumn(0) - 50)

    def newYSelection(self, ySelection):
        self.ySelected_old = self.ySelected
        if not ySelection.data() in ['proc', 'raw']:
            parentName = ySelection.parent().data()
            channelName = ySelection.data()
            self.ySelected = "{0}/{1}".format(parentName, channelName)
            # print('The Y-Channel {0} was selected.'.format(self.ySelected))

            self.populateOffsetEditor()
            self.populateAttributeViewer()
            self.plotSelection()

    def newXSelection(self, xSelection):
        self.xSelected_old = self.xSelected
        self.xSelected = xSelection.data()
        # print('The X-Channel {0} was selected.'.format(self.xSelected))

        self.plotSelection()

    def populateOffsetEditor(self):
        pass

    def populateAttributeViewer(self):
        pass

    def plotSelection(self):
        if self.xSelected and self.ySelected:

            # Clear the plot
            self.view.axes.cla()

            # Turn on the grid
            self.view.axes.grid(True)

            # Set the labels
            xLabel = self.generateAxisLabel(self.xSelected)
            yLabel = self.generateAxisLabel(self.ySelected)
            self.view.axes.set_xlabel(xLabel)
            self.view.axes.set_ylabel(yLabel)

            # Generate the data arrays
            if self.xSelected == 'Time':
                # print('Time was indeed selected')
                xArray = self.channelRegistry[self.ySelected].getTimeTrack()
            else:
                xArray = self.channelRegistry[self.xSelected].data
            yArray = self.channelRegistry[self.ySelected].data

            # Plot the data
            try:
                self.view.axes.plot(xArray, yArray, label=self.ySelected)
            except ValueError as err:
                dialog = QMessageBox()
                dialog.setText("Value Error: {0}".format(err))
                dialog.exec_()

            # Show the legend
            self.view.axes.legend(loc=0)

            # Draw everything
            self.view.canvas.draw()

    def generateTimeTrack(self, yChannel):
        pass
        

    def populateXSelector(self):
        pass

    def generateAxisLabel(self, chan_name):

        chan_name = chan_name.split('/')[-1]

        # Generate the axis labels based on the selected channels
        # Cycle through the labes in the AXESLABELS dictionary
        for axlbl in AXESLABELS.keys():

            # Cycle through the channel names in each label's dictionary entry
            for cn in AXESLABELS[axlbl]:

                # If a channel equals one of the selections, save the label 
                if chan_name == cn:
                    label = axlbl

        return label

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

