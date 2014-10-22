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
from datetime import datetime

# Import thrid-party modules
import h5py
import numpy as np
import pandas as pd
import seaborn as sns

# PyQt4
from PyQt4.QtGui import (QApplication, QFileDialog, QKeySequence, QMessageBox)
from PyQt4.QtCore import (QModelIndex)

from matplotlib import dates

# Import our own modules
from .view import (MyMainWindow, AXESLABELS)
from .ChannelModel import  (ChannelRegistry)
from .view_model import (TreeNode, TreeModel, MyListModel)

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
        self.fileName = None

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
        fileExportAction = self.view.createAction("&Export", self.exprtToFile,
                                             "Ctrl+E", 'export',
                                             tip="Export the TDMS data to HDF5")

        self.fileMenu = self.view.menuBar().addMenu("&File")
        self.fileMenuActions = (fileOpenAction, fileExportAction,
                                fileQuitAction)
        self.view.addActions(self.fileMenu, self.fileMenuActions)

        # Connections
        self.view.ySelectorView.clicked.connect(self.newYSelection)
        self.view.xSelectorView.clicked.connect(self.newXSelection)
        self.view.saveChannelCheckBox.stateChanged.connect(self.toggleWriteToFile)
        self.view.allChannels.clicked.connect(self.saveAllChannels)
        self.view.noChannels.clicked.connect(self.saveNoChannels)

    def fileOpen(self):
        """Open a file."""
        formats = "TDMS files (*.tdms)"
        fname = QFileDialog.getOpenFileName(self.view, "Open a TDMS File",
                                            self.baseDir, formats)
        self.channelRegistry.loadFromFile(fname)

        self.baseDir = os.path.dirname(fname)

        self.fileName = fname

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
            channelObj = self.channelRegistry[self.ySelected]
            self.view.saveChannelCheckBox.setChecked(channelObj.write_to_file)

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
            yArray = self.channelRegistry[self.ySelected].data
            ## if self.xSelected == 'Time':
            ##     xArray = self.channelRegistry[self.ySelected].getTimeTrack().astype(datetime)
            ##     xArray = dates.date2num(xArray)
            ##     try:
            ##         self.view.axes.plot_date(xArray, yArray, '-', label=self.ySelected)
            ##     except ValueError as err:
            ##         dialog = QMessageBox()
            ##         dialog.setText("Value Error: {0}".format(err))
            ##         dialog.exec_()
            ## else:
            ##     xArray = self.channelRegistry[self.xSelected].data
            ##     try:
            ##         self.view.axes.plot(xArray, yArray, label=self.ySelected)
            ##     except ValueError as err:
            ##         dialog = QMessageBox()
            ##         dialog.setText("Value Error: {0}".format(err))
            ##         dialog.exec_()

            if self.xSelected == 'Time':
                xArray = self.channelRegistry[self.ySelected].getTimeTrack() / 3600
            else:
                xArray = self.channelRegistry[self.xSelected].data

            try:
                self.view.axes.plot(xArray, yArray, label=self.ySelected, color=sns.xkcd_rgb['pale red'])
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

    def toggleWriteToFile(self):
        self.channelRegistry[self.ySelected].write_to_file = \
          self.view.saveChannelCheckBox.isChecked()

    def saveAllChannels(self):

        for k, v in self.channelRegistry.items():
            v.write_to_file = True

        self.view.saveChannelCheckBox.setChecked(True)

    def saveNoChannels(self):

        for k, v in self.channelRegistry.items():
            v.write_to_file = False

        self.view.saveChannelCheckBox.setChecked(False)

    def exprtToFile(self):
        fname = self.fileName.split('.')[0] + '.h5'

        baseDir = self.baseDir.replace('raw-data', 'data')

        if not os.path.exists(baseDir):
            os.makedirs(baseDir)

        formats = "Pandas HDF files (*.h5);;" + \
          "HDF5 files (*.hdf5 *.he5 *.hdf);;" + \
          "CSV files (*.csv *.txt *.dat)"

        dialog = QFileDialog()
        dialog.setFilter(formats)
        dialog.setDefaultSuffix("*.hdf5")
        dialog.selectFile(os.path.join(baseDir, fname))
        dialog.setDirectory(baseDir)
        if dialog.exec_():
            fname = dialog.selectedFiles()[0]
        else:
            return

        basename, ext = fname.split('.')

        if ext in ['hdf5', 'he5', 'hdf']:
            self.exprtToHDF5(fname)
        elif ext in ['h5']:
            self.exprtToPandasHDF5(fname)
        elif ext in ['csv', 'txt', 'dat']:
            self.exprtToCSV(fname)

    def exprtToPandasHDF5(self, fname):

        # Process 5.1 Create HDF5 file object
        hdfStore = pd.HDFStore(fname, 'w')

        df_register = {}

        # Process 5.2 Create channels at their locations
        for chan in self.channelRegistry:

            chan_obj = self.channelRegistry[chan]
            chan_device = chan_obj.attributes['Device']

            # Remove whitespace and minus signs from the channel name
            chan_name = chan.replace(" ", "")

            chan_name = chan_name.replace("/", "/{}/".format(chan_device))

            chan_device = "/".join(chan_name.split("/")[:2])

            chan_name = chan_name.split("/")[-1]

            # Get the start time
            start_time = chan_obj.getStartTime()

            # Get time
            #chan_obj.time = pd.to_datetime(chan_obj.time, unit='s')

            if chan_obj.time[-1] > 3600:
                # Then it means we have hours worth of data
                chan_obj.time = chan_obj.time / 3600
                chan_obj.unit = '[h]'
            elif chan_obj.time[-1] > 60:
                # Then it means we have minutes worth of data
                chan_obj.time = chan_obj.time / 60
                chan_obj.unit = '[m]'
            else:
                chan_obj.unit = '[s]'

            if chan_device not in df_register.keys():
                df_register[chan_device] = pd.DataFrame()

            # Process 5.2.1 Write channel data
            if self.channelRegistry[chan].write_to_file:

                s = pd.Series(data=chan_obj.data,
                              index=chan_obj.getTimeTrack())

                df_register[chan_device][chan_name] = s
                #df_register2[chan_device].append(s, ignore_index=True)

                #dset = hdf5FileObject.require_dataset(chan,
                #                                      shape=chan_obj.data.shape,
                #                                      dtype=chan_obj.data.dtype,
                #                                      data=chan_obj.data)

                # Process 5.2.2 Write channel attributes
                #for attr_name in self.channelRegistry[chan].attributes:
                #    attr_value = self.channelRegistry[chan].attributes[attr_name]

                    # Convert the datetime format to a string
                    #if type(attr_value) is datetime:
                    #    attr_value = attr_value.isoformat()

                    # There's currently a wierd bug when dealing with python3
                    # strings.
                    # This gets around that
                    #if type(attr_value) is str:
                    #    attr_value = np.string_(attr_value)

                    #dset.attrs.create(attr_name, attr_value)

        for k, v in df_register.items():
            hdfStore[k] = v

        # Process 5.3 Write data to file
        hdfStore.close()

    def exprtToCSV(self, fname):
        pass

    def exprtToHDF5(self, fname):

        # Process 5.1 Create HDF5 file object
        hdf5FileObject = h5py.File(fname, 'w')

        # Process 5.2 Create channels at their locations
        for chan in self.channelRegistry:

            chan_obj = self.channelRegistry[chan]
            chan_name = chan

            # Process 5.2.1 Write channel data
            if self.channelRegistry[chan].write_to_file:

                dset = hdf5FileObject.require_dataset(chan,
                                                      shape=chan_obj.data.shape,
                                                      dtype=chan_obj.data.dtype,
                                                      data=chan_obj.data)

                # Process 5.2.2 Write channel attributes
                for attr_name in self.channelRegistry[chan].attributes:
                    attr_value = self.channelRegistry[chan].attributes[attr_name]

                    # Convert the datetime format to a string
                    if type(attr_value) is datetime:
                        attr_value = attr_value.isoformat()

                    # There's currently a wierd bug when dealing with python3
                    # strings.
                    # This gets around that
                    if type(attr_value) is str:
                        attr_value = np.string_(attr_value)
                    print(attr_name, attr_value.astype('float64') / 1e3, type(attr_value))
                    dset.attrs.create(attr_name, attr_value)

        # Process 5.3 Write data to file
        hdf5FileObject.flush()
        hdf5FileObject.close()


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

