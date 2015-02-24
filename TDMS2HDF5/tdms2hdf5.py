#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=C0103
""" The main script.

"""

__author__ = "Christopher Espy"
__copyright__ = "Copyright (C) 2014, Christopher Espy"
__credits__ = ["Christopher Espy"]
__license__ = "GPLv2"
__version__ = "0.5"
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

# Import our own modules
from .view import (MyMainWindow, AXESLABELS)
from .ChannelModel import (ChannelRegistry)
from .view_model import (TreeNode, TreeModel, MyListModel)

BASEDIR = '/home/chris/Documents/PhD/root/raw-data/'

MEAS_TYPES = {'BSweep': 'bsweep_files.csv',
              'BRamp': 'bramp_files.csv'}

class Main(MyMainWindow):
    """ The main window of the program.

    """

    def __init__(self, parent=None):

        super(Main, self).__init__(parent)


class Presenter(object):
    """The presenter coordinates between the PyQt models and channel registry

    Attributes
    ----------
    baseDir : str
        The location where the raw data are stored.
    fileName : str
        The name of the current file being viewed.
    view : MyMainWindow
        The view of the program.
    yModel : PyQt type model
        The model for the behavior of the y selector.
    xModel : PyQt type model
        The model for the behavior of the x selector.
    channelRegistry : Channel Registry type object
        The main channel registry where channel objects are stored.
    ySelected : str
        The currently selected channel displayed on the y-axis in the plot.
    ySelected_old : str
        The previously selected y channel.
    xSelected : str
        The currently selected x channel.
    xSelected_old : str
        The previously selected x channel.
    fileMenu : PyQt.QtGui.QFileMenu
        The file menu of the main window.
    fileMenuActions : tuple
        The actions added to the file menu.

    Methods
    -------
    setView(view : MyMainWindow)
        Set the view to which the information is pushed.
    setYModel(yModel : PyQt type model)
        The model for the y selector tree view
    setXModel(xModel : PyQt type model)
        The model for the x selector list view.
    setChanReg(chanReg : channel registry type object)
        The presenter's channel registry.
    fileOpen()
        Open a data file to view.
    populateSelectors()
        Populate the x and y selectors with the names of the available
        channels.
    newYSelection(ySelection : str)
        Redraw the plot with the newly selected channel's data
    newXSelection(xSelection : str)
        Redraw the plot with the newly selected channel's data
    plotSelection()
        Plot the selected data
    generateAxisLabel(chan_name : str)
        Return the axes label for the channel.
    toggleWriteToFile()
        Toggle the currently plotted y channel's write to file property.
    saveAllChannels()
        Select all channels to be exported.
    saveNoChannels()
        Deselect all channels from exporting.
    exprtToFile()
        Export the selected channels to a file.
    exprtToPandasHDF5()
        Export the channels to HDF5 type file using pandas.
    exprtToCSV()
        Export the channels to a csv file.
    exprtToHDF5()
        Export the channels to a HDF5 file using h5py.

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
        self.fileMenuActions = None

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
                                                  tip=("Export the TDMS data"
                                                       " to HDF5"))
        channelAddBAction = self.view.createAction("Add B to ADWin [&B]",
                                                   self.addB,
                                                   "Ctrl+B", tip='Add B')

        # Add the 'File' menu to the menu bar
        self.fileMenu = self.view.menuBar().addMenu("&File")
        self.fileMenuActions = (fileOpenAction, fileExportAction,
                                fileQuitAction)
        self.view.addActions(self.fileMenu, self.fileMenuActions)

        # Add the 'Channels'
        self.channelAddMenu = self.view.menuBar().addMenu("&Add Channel")
        self.view.addActions(self.channelAddMenu, (channelAddBAction,))

        # Connections
        self.view.ySelectorView.clicked.connect(self.newYSelection)
        self.view.xSelectorView.clicked.connect(self.newXSelection)
        self.view.saveChannelCheckBox.stateChanged.connect(self
                                                           .toggleWriteToFile)
        self.view.allChannels.clicked.connect(self.saveAllChannels)
        self.view.noChannels.clicked.connect(self.saveNoChannels)

    def fileOpen(self):
        """Open a data file to view file.

        """
        formats = "TDMS files (*.tdms)"
        fname = QFileDialog.getOpenFileName(self.view, "Open a TDMS File",
                                            self.baseDir, formats)
        if fname:
            self.channelRegistry.loadFromFile(fname)

            self.baseDir = os.path.dirname(fname)

            self.fileName = fname

            windowTitle = self.view.windowTitle().split(':')[0]
            baseName = os.path.basename(self.fileName)
            self.view.setWindowTitle('{0}: {1}'.format(windowTitle, baseName))

            self.populateSelectors()
            self.plotSelection()
        else:
            return

    def populateSelectors(self):
        """Populate the x and y selectors with the names of the channels.

        """
        # Setup the root node of the tree
        rootNode0 = TreeNode("")

        procDeviceNodes = {}

        for chanTDMSPath in sorted(self.channelRegistry.keys()):

            (root, device, chan) = chanTDMSPath.split('/')

            if root not in procDeviceNodes:

                procDeviceNodes[root] = {'node': TreeNode(root, rootNode0)}

            if device not in procDeviceNodes[root]:

                procDeviceNodes[root][device] = \
                  {'node': TreeNode(device, procDeviceNodes[root]['node'])}

            procDeviceNodes[root][device][chan] = \
              TreeNode(chan, procDeviceNodes[root][device]['node'])

        self.setYModel(TreeModel(rootNode0))
        self.setXModel(None)

        self.ySelected = None
        self.xSelected = None

        self.view.ySelectorView.expandAll()
        self.view.ySelectorView.setHeaderHidden(True)
        self.view.ySelectorView.setMaximumWidth(self.view.ySelectorView
                                                .sizeHintForColumn(0) + 10)

        self.view.xSelectorView.setMaximumHeight(42)
        # self.view.xSelectorView.sizeHintForColumn(0) - 50)

    def newYSelection(self, ySelection):
        """Get the newly selected y channel's data

        When a new y channel is selected, redraw the plot with the new
        channel's data.

        """
        self.ySelected_old = self.ySelected
        if not ySelection.data() in ['proc01'] + self.channelRegistry.devices:
            parentName = ySelection.parent().data()
            grandParentName = ySelection.parent().parent().data()
            channelName = ySelection.data()
            if grandParentName == '01':
                grandParentName = 'proc/' + grandParentName
            self.ySelected = "{0}/{1}/{2}".format(grandParentName, parentName,
                                                  channelName)
            self.ySelected_root = "{0}/{1}".format(grandParentName, parentName)
            # print('The Y-Channel {0} was selected.'.format(self.ySelected))

            self.populateOffsetEditor()
            self.populateAttributeViewer()
            self.plotSelection()
            channelObj = self.channelRegistry[self.ySelected]
            self.view.saveChannelCheckBox.setChecked(channelObj.write_to_file)

        newXList = [k.split('/')[-1] for k in self.channelRegistry.keys()
                    if self.ySelected_root in k]

        self.setXModel(MyListModel(sorted(newXList)))

    def newXSelection(self, xSelection):
        """Get the newly selected y channel's data

        When a new y channel is selected, redraw the plot with the new
        channel's data.

        """
        self.xSelected_old = self.xSelected
        self.xSelected = "{0}/{1}".format(self.ySelected_root,
                                          xSelection.data())
        # print('The X-Channel {0} was selected.'.format(self.xSelected))

        self.plotSelection()

    def populateOffsetEditor(self):
        """(Coming soon!)Display the offset in the offset editor.

        """
        pass

    def populateAttributeViewer(self):
        """(Coming soon!)Display the channel's attributes in the attribute
        viewer.

        """
        pass

    def plotSelection(self):
        """Plot the data channels indicated by xSelected and ySelected.

        """
        if self.xSelected and self.ySelected:

            # Clear the plot
            self.view.axes.cla()

            # Turn on the grid
            self.view.axes.grid(True)

            # Generate the data arrays
            yArray = self.channelRegistry[self.ySelected].data
            # print('y array is:', yArray)

            xArray = self.channelRegistry[self.xSelected].data
            # print('x array is:', xArray)

            # Set the labels
            xLabel = self.generateAxisLabel(self.xSelected)
            yLabel = self.generateAxisLabel(self.ySelected)

            self.view.axes.set_xlabel(xLabel)
            self.view.axes.set_ylabel(yLabel)

            # Do the plotting
            try:
                self.view.axes.plot(xArray, yArray, label=self.ySelected,
                                    color=sns.xkcd_rgb['pale red'])
            except ValueError as err:
                dialog = QMessageBox()
                dialog.setText("Value Error: {0}".format(err))
                dialog.exec_()

            # Show the legend
            self.view.axes.legend(loc=0)

            # Draw everything
            self.view.canvas.draw()

    def generateAxisLabel(self, chan_name):
        """Return the axes label for the channel.

        Based on the axes label and channel combinations in AXESLABELS
        (imported from view), return the channel's axes label.

        Parameters
        ----------
        chan_name : str
            The channel name for which the axes label needs to be generated.

        Returns
        -------
        label
            chan_name's axes label.
        """

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
        """Toggle the currently plotted y channel's write to file property.

        This toggles whether the currently plotted channel will be included in
        the export.

        """
        try:
            self.channelRegistry[self.ySelected].write_to_file = \
              self.view.saveChannelCheckBox.isChecked()
        except KeyError:
            pass

    def saveAllChannels(self):
        """Select all channels to be exported.

        """

        for v in self.channelRegistry.values():
            v.write_to_file = True

        self.view.saveChannelCheckBox.setChecked(True)

    def saveNoChannels(self):
        """Deselect all channels from exporting.

        """

        for v in self.channelRegistry.values():
            v.write_to_file = False

        self.view.saveChannelCheckBox.setChecked(False)

    def exprtToFile(self):
        """Export the selected channels to a file.

        Based on the file extension that is chosen here, a futher export parser
        is called.

        """
        fname = self.fileName.split('.')[0] + '.h5'

        meas_type = os.path.basename(fname).split('_')[1]

        baseDir = self.baseDir.replace('raw-data', 'data')

        if not os.path.exists(baseDir):
            os.makedirs(baseDir)

        formats = ("Pandas HDF files (*.h5);;"
                   "HDF5 files (*.hdf5 *.he5 *.hdf);;"
                   "CSV files (*.csv *.txt *.dat)")

        dialog = QFileDialog()
        dialog.setFilter(formats)
        dialog.setDefaultSuffix("*.h5")
        dialog.selectFile(os.path.join(baseDir, fname))
        dialog.setDirectory(baseDir)
        if dialog.exec_():
            fname = dialog.selectedFiles()[0]
        else:
            return

        ext = fname.split('.')[1]

        if ext in ['hdf5', 'he5', 'hdf']:
            self.exprtToHDF5(fname)
        elif ext in ['h5']:
            self.exprtToPandasHDF5(fname)
        elif ext in ['csv', 'txt', 'dat']:
            self.exprtToCSV(fname)

        self.addFileToGoodList(fname, meas_type)

    def exprtToPandasHDF5(self, fname):
        """Export the channels to HDF5 type file using pandas.

        The channels to be exported are grouped by device and merged into a
        pandas time series data frame where the index is one of the channels'
        time series data.

        """
        # Process 5.1 Create HDF5 file object
        hdfStore = pd.HDFStore(fname, 'w')

        df_register = {}

        # Process 5.2 Create channels at their locations
        for chan in sorted(self.channelRegistry.keys()):

            chan_obj = self.channelRegistry[chan]
            chan_device = chan_obj.attributes['Device']

            # Remove whitespace and minus signs from the channel name
            chan_name = chan.replace(" ", "")

            device_df_key = "/".join(chan_name.split("/")[:-1])

            if device_df_key not in df_register.keys():
                df_register[device_df_key] = pd.DataFrame(index=chan_obj
                                                          .getTimeTrack())

            chan_name = chan_name.split("/")[-1]

            # Process 5.2.1 Write channel data
            if chan_obj.write_to_file:

                # print('Adding channel {0} to data fram {1}'
                #       .format(chan_name, device_df_key))

                df_register[device_df_key][chan_name] = chan_obj.data

        for k, v in df_register.items():
            # print('put({}, df)'.format(k))
            hdfStore.put(k, v, format='table')

        # Process 5.3 Write data to file
        hdfStore.close()

        # Write start and end times to file

        f = h5py.File(fname, 'a')

        try:
            start_time = self.channelRegistry.file_start_time.astype('<i8')
            end_time = self.channelRegistry.file_end_time.astype('<i8')

            f.attrs.create('StartTime', start_time)
            f.attrs.create('EndTime', end_time)
        except AttributeError:
            pass

        f.flush()

        f.close()

    def exprtToCSV(self, fname):
        """Export the channels to a csv file.

        """
        pass

    def exprtToHDF5(self, fname):
        """Export the channels to a HDF5 file using h5py.

        """

        # Process 5.1 Create HDF5 file object
        hdf5FileObject = h5py.File(fname, 'w')

        # Process 5.2 Create channels at their locations
        for chan in sorted(self.channelRegistry.keys()):

            chan_obj = self.channelRegistry[chan]

            # Process 5.2.1 Write channel data
            if self.channelRegistry[chan].write_to_file:

                dset = hdf5FileObject.require_dataset(chan,
                                                      shape=(chan_obj.data
                                                             .shape),
                                                      dtype=(chan_obj.data
                                                             .dtype),
                                                      data=chan_obj.data)

                # Process 5.2.2 Write channel attributes
                for attr_name in self.channelRegistry[chan].attributes:
                    attr_value = (self.channelRegistry[chan]
                                  .attributes[attr_name])

                    # Convert the datetime format to a string
                    if type(attr_value) is datetime:
                        attr_value = attr_value.isoformat()

                    # There's currently a wierd bug when dealing with python3
                    # strings.
                    # This gets around that
                    if type(attr_value) is str:
                        attr_value = np.string_(attr_value)
                    print(attr_name, attr_value.astype('float64') / 1e3,
                          type(attr_value))
                    dset.attrs.create(attr_name, attr_value)

        # Process 5.3 Write data to file
        hdf5FileObject.flush()
        hdf5FileObject.close()

    def addFileToGoodList(self, fname, meas_type):
        """

        """
        base_dir = os.path.dirname(fname)
        original_file = os.path.basename(fname)

        try:
            base_name = MEAS_TYPES[meas_type]
        except KeyError:
            return

        full_path = os.path.join(base_dir, base_name)

        df_files = pd.DataFrame.from_csv(full_path)

        new_df = pd.DataFrame()

        if not np.any(df_files['0'].str.contains(original_file)):
            new_df['0'] = df_files['0'].append(pd.Series(original_file,
                                            index=[len(df_files['0'])]))

            new_df.to_csv(full_path)

    def addB(self):
        """Add BField Data to ADWin."""

        self.channelRegistry.addInterpolatedB()

        self.populateSelectors()


def main(argv=None):
    """The main function."""

    if argv is None:
        argv = sys.argv

    app = QApplication(argv)
    app.setOrganizationName("TDMS2HDF5")
    app.setApplicationName("TDMS-2-HDF5 Converter")

    presenter = Presenter()

    presenter.setView(Main())
    presenter.setChanReg(ChannelRegistry())
    presenter.view.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
