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
                          QVariant, Qt, SIGNAL, QModelIndex, QSize, QFile,
                          pyqtSignal)
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
__version__ = "0.4.2"
__maintainer__ = "Christopher Espy"
__email__ = "christopher.espy@uni-konstanz.de"
__status__ = "Development"

PROGNAME = os.path.basename(sys.argv[0])
PROGVERSION = __version__

class OffsetWidget(QWidget):
    """This widet displays the elements for editing the offset.

    This widget deals with the logic of when the new offset should be taken into
    account internally. When it determines that the new offset should be used,
    it emits the 'new_offset' signal.

    Parameters
    ----------
    parent : ?

    Attributes
    ----------
    offset_entry : QDoubleSpinBox
        The numerical element where the user can enter the offset. The units are
        determined by the currently displayed channel.

    Methods
    -------
    toggle_preview
        Determine how the new_offset signal should be emitted and connect the
        proper element to the emit_new_offset method.
    emit_new_offset
        Wrapper function for connected one of the widget's element's signals to
        the new_offset signal.

    Signals
    -------
    new_offset
        Indicates that a new offset has been entered and is ready to be used in
        calculations.

    """

    # Define a new signal called 'new_offset'
    new_offset = pyqtSignal()

    def __init__(self, parent=None):
        super(OffsetWidget, self).__init__(parent)

        ### CREATE GRAPHICAL ELEMENTS ###

        # Create the numerical entry spinbox and its label
        offset_label = QLabel("Offset")
        self.offset_entry = QDoubleSpinBox(self)
        self.offset_entry.setDecimals(10)
        self.offset_entry.setRange(-1000000,1000000)

        # Create the preview checkbox and its label
        preview_chkbx_lbl = QLabel("preview")
        self.preview_chkbx = QCheckBox()

        # Create the 'Show' and 'Save' push buttons
        self.show_btn = QPushButton("Show")
        self.save_btn = QPushButton("Save")
        # The save feature is planned for later, so the button is disabled for
        # now
        self.save_btn.setEnabled(False)

        ### CREATE LAYOUTS ###

        # Create the layout for the checkbox/button strip at the bottom of the
        # widget's layout:
        # | checkbox | checkbox label | show button | save button |
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.preview_chkbx)
        btn_layout.addWidget(preview_chkbx_lbl)
        btn_layout.addWidget(self.show_btn)
        btn_layout.addWidget(self.save_btn)

        # Create the main layout of the widget:
        # |      spinbox label     |
        # |         spinbox        |
        # | checkbox/button layout |
        layout = QVBoxLayout()
        layout.addWidget(offset_label)
        layout.addWidget(self.offset_entry)
        layout.addLayout(btn_layout)

        # Set the layout
        self.setLayout(layout)

        ### CONNECT SIGNALS ###

        # Connect the checkbox's 'stateChanged' signal to the toggle_preview
        # method
        self.preview_chkbx.stateChanged.connect(self.toggle_preview)
        # Connect the show button's 'clicked' signal to the emit_new_offset
        # method.
        # By default the checkbox is not selected, thus the default is that the
        # show button is how the user indicates that there is a new offset.
        self.show_btn.clicked.connect(self.emit_new_offset)

    def toggle_preview(self):
        """Toggle previewing offset changes automatically.

        This function checks the state of the preview checkbox and establishes
        the Offset_Widget's method of emitting the new_offset signal.

        """

        # Connect and disconnect the spinbox's and show button's signals to the
        # widget's new_offset signal.
        if self.preview_chkbx.isChecked():
            # Preview is selected:
            #  show button is disconnected from new_offset
            #  spinbox is connected to new_offset
            self.show_btn.clicked.disconnect(self.emit_new_offset)
            self.offset_entry.editingFinished.connect(self.emit_new_offset)
        elif not self.preview_chkbx.isChecked():
            # Preview is not selected:
            #  spinbox is disconnected from new_offset
            #  show button is connected to new_offset
            self.offset_entry.editingFinished.disconnect(self.emit_new_offset)
            self.show_btn.clicked.connect(self.emit_new_offset)

        # Enable or disable the show button depending on checkbox's state
        self.show_btn.setEnabled(not self.preview_chkbx.isChecked())

    def emit_new_offset(self):
        """Emit the 'new_offset' signal.

        The function just provides an easy way to connect other signals to
        emitting the widget's new_offset signal.

        """

        self.new_offset.emit()

class Attribute(QWidget):
    """This class is displays an attribute and label."""

    def __init__(self, attr_name, attr_val, parent=None):
        super(Attribute, self).__init__(parent)

        ### CREATE GRAPHICAL ELEMENTS ###
        label = QLabel(attr_name)
        value = QLineEdit()
        value.setText(str(attr_val))

        ### CREATE LAYOUTS ###
        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(value)

        self.setLayout(layout)

class AttributesWidget(QWidget):
    """This widget displays the attributes of a channel for editing."""

    new_attributes = pyqtSignal()

    def __init__(self, chan = None, parent=None):
        super(AttributesWidget, self).__init__(parent)

        ### CREATE GRAPHICAL ELEMENTS ###
        self.apply_btn = QPushButton("Apply")
        self.label = QLabel("Attributes")

        ### CREATE LAYOUTS ###
        self.lbl_layout = QHBoxLayout()
        self.lbl_layout.addWidget(self.label)
        self.lbl_layout.addStretch()
        
        self.btn_layout = QHBoxLayout()
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.apply_btn)

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.lbl_layout)

        if not chan:
            for i in np.arange(3):
                new_attr = Attribute("Parameter {n}".format(n=i), i)
                self.layout.addWidget(new_attr)

        self.layout.addLayout(self.btn_layout)

        self.setLayout(self.layout)

        ### CONNECT SIGNALS ###
        self.apply_btn.clicked.connect(self.emit_new_attributes)

    def clear_widgets(self):

        for i in range(self.layout.count()):
            try:
                self.layout.itemAt(i).widget().close()
            except AttributeError:
                pass

    def add_chan(self, chan):

        
        for i in range(self.layout.count()):
            print(type(self.layout.itemAt(i)))

        for attr_name in chan.attributes:
            attr_val = chan.attributes[attr_name]
            self.layout.addWidget(Attribute(attr_name, attr_val))
            

    def emit_new_attributes(self):
        """Emit the 'new_attributes' signal.

        The function just provides an easy way to connect other signals to
        emitting the widget's new_attributes signal.

        """

        print("Come and get 'em! New attributes!")
        self.new_attributes.emit()

    ## def update_ui(self, chan):

    ##     layout = QVBoxLayout()
    ##     label = QLabel("Attributes")
    ##     layout.addWidget(label)

    ##     for attr_name in chan.attributes:
    ##         attr_val = chan.attributes[attr_name]
    ##         layout.addWidget(Attribute(attr_name, attr_val))

    ##     layout.addLayout(btn_layout)

    ##     self.setLayout(layout)

class MainWindow(QMainWindow):
    """The main window widget for the program.

    """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        #1 Create and Initialize data structures

        self.xLabel = None
        self.xSelection = None
        self.xArray = None

        self.yLabel = None
        self.ySelection = None
        self.ySelection_old = None
        self.yArray = None

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
        #self.xSelector.addItem("Time")
        self.xSelector.setFlow(0)
        xSelectorLabel = QLabel("x axis channel")
        self.xSelector.setMaximumHeight(self.xSelector.sizeHintForColumn(0))
        #self.xSelector.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)

        # Offset and parameter widgets on the right top
        self.offsetThing = OffsetWidget()
        self.attributesThing = AttributesWidget()

        # Save channel on right bottom
        self.save_chan_chkbx = QCheckBox()
        save_chan_label = QLabel("Save Channel")

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

        # Right bottom
        save_chan_layout = QHBoxLayout()
        save_chan_layout.addWidget(self.save_chan_chkbx)
        save_chan_layout.addWidget(save_chan_label)

        # Right Side
        rightLayout = QVBoxLayout()
        rightLayout.addWidget(self.offsetThing)
        rightLayout.addWidget(self.attributesThing)
        rightLayout.addStretch()
        rightLayout.addLayout(save_chan_layout)

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

        #self.xSelector.itemSelectionChanged.connect(self.plotData)
        self.xSelector.itemSelectionChanged.connect(self.make_x_selection)
        #self.ySelector.itemSelectionChanged.connect(self.plotData)
        self.ySelector.itemSelectionChanged.connect(self.make_y_selection)
        self.offsetThing.new_offset.connect(self.subtract_offset)

        self.save_chan_chkbx.stateChanged.connect(self.toggle_save)

        #self.offsetThing.preview_chkbx.stateChanged.connect(self.toggle_preview)

        #5 Read in application's settings
        settings = QSettings()

        # Restore the geometry and state of the main window from last use
        #self.restoreGeometry(settings.value("MainWindow/Geometry"))
        #self.restoreState(settings.value("MainWindow/State"))

        self.setWindowTitle("TDMS to HDF5 Converter")

    def update_ui(self):
        pass

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
            try:
                dR_item = self.ySelector.findItems('dR', Qt.MatchExactly)
                self.ySelector.setCurrentItem(dR_item[0])
            except IndexError:
                self.ySelector.setCurrentRow(0)

        else:
            message = "Failed to load {f_name}".format(f_name=os.path.
                                                       basename(fname))

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
            try:
                new_chan = Channel(chan_name,
                                device=group,
                                meas_array=chan.data)
            except TypeError:
                print("Channel {chan} in {dev} has no data"
                      .format(chan=chan_name, dev=group))
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
                            #print('The key {a_name} was not found.'
                            #      .format(a_name=atr_name))
                            #print('The keys available are\n')
                            #print(group_props)
                            pass

                # Process 1.3.3.3 Add new channel to the registry
                self.channel_registry[chan_name] = new_chan

                #print('\tChannel name:\t{ch_name}'.format(ch_name=chan_name))

            except (KeyError, UnboundLocalError):
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

    def make_x_selection(self):

        # Get the name of the newly selected channel
        self.xSelection = self.xSelector.currentItem().text()

        # Get the axis label
        self.xLabel = self.gen_axis_label(self.xSelection)

        # If the xSelection is time, use the time data instead of measurement
        # data
        if self.xSelection == 'Time':
            self.xArray = self.channel_registry[self.ySelection].time
        else:
            self.xArray = self.channel_registry[self.xSelection].data

        if self.yLabel:
            self.plotData()

    def make_y_selection(self, offset=0.0):

        # Get the names of the selected channels from the selectors
        try:
            self.ySelection = self.ySelector.currentItem().text()
        except AttributeError:
            self.ySelection = DEFAULTY

        # Set save channel checkbox state
        self.save_chan_chkbx.setChecked(self.channel_registry[self.ySelection]
                                        .write_to_file)

        # Get the axis label
        self.yLabel = self.gen_axis_label(self.ySelection)

        # Generate the y-channel array to be plotted
        self.yArray = self.channel_registry[self.ySelection].data - offset

        # Update the attributes view
        self.attributesThing.clear_widgets()
        print('cleared')
        self.attributesThing.add_chan(self.channel_registry[self.ySelection])

        if self.xSelection == 'Time':
            self.make_x_selection()
        else:
            self.plotData()

        self.ySelection_old = self.ySelector.currentItem()


    def gen_axis_label(self, chan_name):

        # Generate the axis labels based on the selected channels
        # Cycle through the labes in the AXESLABELS dictionary
        for axlbl in AXESLABELS.keys():

            # Cycle through the channel names in each label's dictionary entry
            for cn in AXESLABELS[axlbl]:

                # If a channel equals one of the selections, save the label 
                if chan_name == cn:
                    label = axlbl

        return label

    def plotData(self):

        # Clear the plot
        self.axes.cla()

        # Turn on the grid
        self.axes.grid(True)

        # Set the labels
        try: 
            self.axes.set_xlabel(self.xLabel)
        except UnboundLocalError:
            print("Could not generate an axis label for {chan}"
                  .format(chan=self.xSelection))
        try:
            self.axes.set_ylabel(self.yLabel)
        except UnboundLocalError:
            print("Could not generate an axis label for {chan}"
                  .format(chan=self.ySelection))

        # Try plotting the data. There are still no checks in place to make sure
        # the arrays are of the same length.
        try:
            # Plot the data and label it
            self.axes.plot(self.xArray, self.yArray, label=self.ySelection)

            # Show the legend
            self.axes.legend(loc=0)

            # Draw everything
            self.canvas.draw()
        except ValueError:

            QMessageBox.warning(self, "Unequal Arrays", "{y_chan} and {x_chan} "
                                .format(y_chan=self.ySelection,
                                        x_chan=self.xSelection) + \
                                        "are not the same length!")

            self.ySelector.setCurrentItem(self.ySelection_old)

    def subtract_offset(self):
        "Subtract the offset entered from the currently selected y channel."

        offset = self.offsetThing.offset_entry.value()

        self.make_y_selection(offset=offset)

    def toggle_save(self):

        self.channel_registry[self.ySelection].write_to_file = \
          self.save_chan_chkbx.isChecked()

    def create_new_channel(self, ch_name):
        "Create a new channel in the registry."

        print(ch_name)

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
