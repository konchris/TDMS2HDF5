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
                         QSpinBox, QFrame, QFileDialog, QListWidget, QCheckBox)
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (FigureCanvasQTAgg as
                                                FigureCanvas)
from matplotlib.backends.backend_qt4agg import (NavigationToolbar2QTAgg as
                                                NavigationToolbar)

from nptdms.tdms import TdmsFile
import h5py

# Import our own modules
#import qrc_resources
from data_structures import Channel, CHAN_DICT, DEFAULTY, AXESLABELS

__author__ = "Christopher Espy"
__copyright__ = "Copyright (C) 2014, Christopher Espy"
__credits__ = ["Christopher Espy"]
__license__ = "GPL"
__version__ = "0.3.1"
__maintainer__ = "Christopher Espy"
__email__ = "christopher.espy@uni-konstanz.de"
__status__ = "Development"

PROGNAME = os.path.basename(sys.argv[0])
PROGVERSION = __version__

class OffsetWidget(QWidget):
    "This widet displays the elements for editing the offset."

    def __init__(self, parent=None):
        super(OffsetWidget, self).__init__(parent)

        offset_label = QLabel("Offset")
        self.offset_entry = QDoubleSpinBox(self)

        preview_chkbx_lbl = QLabel("preview")
        self.preview_chkbx = QCheckBox()

        self.show_btn = QPushButton("Show")
        self.save_btn = QPushButton("Save")
        self.save_btn.setEnabled(False)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.preview_chkbx)
        btn_layout.addWidget(preview_chkbx_lbl)
        btn_layout.addWidget(self.show_btn)
        btn_layout.addWidget(self.save_btn)

        layout = QVBoxLayout()
        layout.addWidget(offset_label)
        layout.addWidget(self.offset_entry)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.preview_chkbx.stateChanged.connect(self.toggle_preview)

    def deactivate(self):
        "A quick function to deactivate all elements."

        pass

    def toggle_preview(self):
        "Toggle previewing offset changes automatically."

        self.show_btn.setEnabled(not self.preview_chkbx.isChecked())
        

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        #1 Create and Initialize data structures
        # The dirty attribute is a boolean flag to indicate whether the
        # file has unsaved changes.
        self.dirty = False
        self.filename = None

        self.tdms_file_object = None
        self.hdf5_file_object = None

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
        sourceFileLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Matplotlib canvas
        self.fig = Figure(dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        mpl_toolbar = NavigationToolbar(self.canvas, self.canvas)

        self.axes = self.fig.add_subplot(111)

        # X selector on bottom
        self.xSelector = QListWidget()
        self.xSelector.addItem("Time")
        self.xSelector.setFlow(0)
        xSelectorLabel = QLabel("x axis channel")
        self.xSelector.setMaximumHeight(self.xSelector.sizeHintForColumn(0))
        #self.xSelector.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)

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
        self.fileMenuActions = (fileOpenAction, fileExportAction,
                                fileQuitAction)
        self.addActions(self.fileMenu, self.fileMenuActions)

        self.ySelector.itemSelectionChanged.connect(self.plotData)
        self.xSelector.itemSelectionChanged.connect(self.plotData)

        #self.offsetThing.preview_chkbx.stateChanged.connect(self.toggle_preview)

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
            action.setIcon(QIcon(":/{icon}.png".format(icon=icon)))
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
        # Process 1.1 Collect file name
        if fname and QFile.exists(fname):
            self.loadFile(fname)

    def loadFile(self, fname): # Process 1.2 Generate TDMS file object
        #TODO self.addRecentFile(fname)  see Rapid GUI ch06.pyw
        self.tdms_file_object = TdmsFile(fname)
        self.filename = fname
        self.dirty = False

         # Process 1.3 Read data into local structure
        if self.tdms_file_object:

            # Process 1.3.0 Generate group list
            group_list = self.tdms_file_object.groups()

            # Processes 1.3.1 through 1.3.3 Sort TDMS data
            for group in group_list:
                self.sortTDMSGroupData(group)

            message = "Loaded {f_name}".format(f_name=os.path.basename(fname))
            self.sourceFileName.setText(os.path.basename(fname))

            print(message)

            # Process 2.1 Populate channl selection lists
            for key in self.channel_registry.keys():
                self.xSelector.addItem(key)
                self.ySelector.addItem(key)
            self.xSelector.sortItems()
            self.ySelector.sortItems()
            zMagnet_item = self.xSelector.findItems('zMagnet', Qt.MatchExactly)
            self.xSelector.setCurrentItem(zMagnet_item[0])
            dR_item = self.ySelector.findItems('dR', Qt.MatchExactly)
            self.ySelector.setCurrentItem(dR_item[0])

        else:
            message = "Failed to load {f_name}".format(f_name=os.path.
                                                       basename(fname))

        self.offsetThing.offset_entry.editingFinished.connect(lambda ch_name = '01-Offset/{0}'.format(self.ySelector.currentItem().text()): self.create_new_channel(ch_name))

        self.xSelector.setMaximumHeight(self.xSelector.sizeHintForColumn(0))
        self.ySelector.setMaximumWidth(self.ySelector.sizeHintForColumn(0))
        #TODO self.updateStatus(message) # see Rapid GUI ch06.pyw


    def sortTDMSGroupData(self, group): # Process 1.3 Sort Group data
        #print("Group:\t{g_name}".format(g_name=group))

        # Process 1.3.1 Get <Group> Channels
        group_props = self.tdms_file_object.object(group).properties

        # Process 1.3.2 Get <Group> Properties
        group_chans = self.tdms_file_object.group_channels(group)

        # Process 1.3.3 Create a new channel in the registry for each channel
        # in the group
        for chan in group_chans:
            chan_name = chan.path.split('/')[-1].strip("'")


            # TODO: update the process numbers, descriptions, and diagrams
            # Process 1.3.3.1 Generate new channel object and fill with data
            new_chan = Channel(chan_name,
                               device=group,
                               meas_array=chan.data)
            # Some of the TDMS channels were created, but never populated with
            # data. The following weeds those out.
            try:
                new_chan.set_start_time(chan.property("wf_start_time"))

                new_chan.set_delta_time(chan.property("wf_increment"))

                new_chan.set_location('raw/{c2_name}'.format(c2_name=chan_name))

                new_chan.set_write()

                # Some of the channel-specific properties were actually
                # saved in the group object's properties list.
                # We retrieve those here.
                # Process 1.3.3.2 Resort the group properties of TDMS ADWin
                if group == "ADWin":
                    for atr_name in CHAN_DICT[chan_name]:
                        try:
                            new_chan.attributes[atr_name] = \
                              group_props[atr_name]
                        except KeyError:
                            print('The key {a_name} was not found.'
                                  .format(a_name=atr_name))
                            print('The keys available are\n')
                            print(group_props)

                # Process 1.3.3.3 Add new channel to the registry
                self.channel_registry[chan_name] = new_chan

                #print('\tChannel name:\t{ch_name}'.format(ch_name=chan_name))

            except KeyError:
                pass
                #print('Error: Was unable to load {c3_name}'
                #      .format(c3_name=chan_name))

    def exprtToHDF5(self): # Process 5 Save to HDF5
        fname = self.filename.split('.')[0] + '.hdf5'

        # Process 5.1 Create HDF5 file object
        self.hdf5_file_object = h5py.File(fname)

        # Process 5.2 Create channels at their locations
        for chan in self.channel_registry:

            chan_obj = self.channel_registry[chan]
            chan_name = chan

            #print(chan, self.channel_registry[chan].location,
            #      self.channel_registry[chan].write_to_file)

            # Process 5.2.1 Write channel data
            if self.channel_registry[chan].write_to_file:

                dset = self.hdf5_file_object.create_dataset(chan_obj.location,
                                                            data=chan_obj.data)

            # Process 5.2.2 Write channel attributes
            for attr_name in self.channel_registry[chan].attributes:
                attr_value = self.channel_registry[chan].attributes[attr_name]

                # Convert the datetime format to a string
                if type(attr_value) is datetime:
                    attr_value = attr_value.isoformat()

                # There's currently a wierd bug when dealing with python3
                # strings.
                # This gets around that
                if type(attr_value) is str:
                    #attr_value = attr_value.encode('utf-8')
                    #attr_value = np.string_(attr_value, dtype="S10")
                    attr_value = np.string_(attr_value)

                dset.attrs.create(attr_name, attr_value)

        # Process 5.3 Write data to file
        self.hdf5_file_object.flush()
        self.hdf5_file_object.close()

    def plotData(self):

        self.axes.cla()

        self.axes.grid(True)

        try:
            ySelection = self.ySelector.currentItem().text()
        except AttributeError:
            ySelection = DEFAULTY
        xSelection = self.xSelector.currentItem().text()

        #print(xSelection, ySelection)

        for axlbl in AXESLABELS.keys():

            for cn in AXESLABELS[axlbl]:
                if xSelection == cn:
                    xLabel = axlbl
                if ySelection == cn:
                    yLabel = axlbl

        self.axes.set_xlabel(xLabel)
        self.axes.set_ylabel(yLabel)

        if xSelection == 'Time':
            xArray = self.channel_registry[ySelection].time
        else:
            xArray = self.channel_registry[xSelection].data

        yArray = self.channel_registry[ySelection].data

        self.axes.plot(xArray, yArray, label=ySelection)

        self.axes.legend(loc=0)

        self.canvas.draw()

    def create_new_channel(self, ch_name):
        "Create a new channel in the registry."

        print(ch_name)

    def toggle_preview(self):
        "Toggle automatic preview on or off."

        if self.offsetThing.preview_chkbx.isChecked():
            self.offsetThing.offset_entry.editingFinished.connect(
                self.subtract_offset)
            self.offsetThing.show_btn.setEnabled(
                not self.offsetThing.preview_chkbx.isChecked())
            try:
                self.offsetThing.show_btn.clicked.disconnect(self.subtract_offset)
            except TypeError:
                pass
        else:
            self.offsetThing.show_btn.clicked.connect(self.subtract_offset)
            self.offsetThing.show_btn.setEnabled(
                not self.offsetThing.preview_chkbx.isChecked())
            try:
                self.offsetThing.offset_entry.editingFinished.disconnect(
                    self.subtract_offset)
            except TypeError:
                    pass


    def subtract_offset(self):
        "Subtract the offset entered from the currently selected y channel."

        offset = self.offsetThing.offset_entry.value()

        print(offset)

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
    # This handles the dispatching of events to various widgets. It controls the
    # GUI's control flow and main settings, the main event loop, etc.
    app = QApplication(argv)
    app.setOrganizationName("tdms2hdf5")
    app.setApplicationName("TDMS 2 HDF5 Converter")

    home = os.path.expanduser("~")

    form = MainWindow()
    form.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
