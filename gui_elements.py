#!/usr/bin/env ipython3
# -*- coding: utf-8 -*-
""" Testing ground for importing tdms files

"""

import sys
import os
import platform
from datetime import datetime

# Import thrid-party modules
from PyQt4.QtCore import (QSettings, Qt, SIGNAL, QFile, pyqtSignal, QFileInfo)
from PyQt4.QtGui import (QAction, QApplication, QIcon, QKeySequence, QLabel,
                         QMainWindow, QMessageBox, QVBoxLayout, QHBoxLayout,
                         QWidget, QPushButton, QLineEdit, QSizePolicy,
                         QDoubleSpinBox, QSpinBox, QFrame, QFileDialog,
                         QListWidget, QCheckBox, QDateTimeEdit)
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (FigureCanvasQTAgg as
                                                FigureCanvas)
from matplotlib.backends.backend_qt4agg import (NavigationToolbar2QT as
                                                NavigationToolbar)

from nptdms.tdms import TdmsFile
import h5py

# Import our own modules
from data_structures import (Channel, ADWIN_DICT, DEFAULTY, AXESLABELS,
                             SENSVECTOR, DEFAULTX)

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

    This widget deals with the logic of when the new offset should be
    taken into account internally. When it determines that the new
    offset should be used, it emits the 'new_offset' signal.

    Parameters
    ----------
    parent : ?

    Attributes
    ----------
    offset_entry : QDoubleSpinBox
        The numerical element where the user can enter the offset. The units
        are determined by the currently displayed channel.

    Methods
    -------
    toggle_preview
        Determine how the new_offset signal should be emitted and connect the
        proper element to the emit_new_offset method.
    emit_new_offset
        Wrapper function for connecting one of the widget's element's signals
        to the new_offset signal.

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
    """This widget displays an attribute and label.

    The widget displays an HDF5 attribute: the name is in a label, and the value
    is in an edit element depending on what it's data type is.

    Parameters
    ----------
    attr_name : str
        The name of the attribute, which is also its key in the channel's
        attributes dictionary.
    attr_val : int or float or datetime or string
        The value of the attribute, i.e. the key's value in the channel's
        attributes dictionary.

    Returns
    -------
    Attribute
        The Attribute is then the combination of a QLabel and whatever editing
        element cooresponds to the value. These are arranged in a QHBoxLayout.

    """

    def __init__(self, attr_name, attr_val, parent=None):
        super(Attribute, self).__init__(parent)

        # The label with the attribute's name
        label = QLabel(attr_name)

        # Now create the editing element, initialized with the attribute's
        # value.
        # First, if the value is an integer, use a spinbox
        if type(attr_val) is int:
            value = QSpinBox()
            value.setMaximum(1E9)
            value.setValue(attr_val)
        # Second, if the value is a float, use a doublespinbox, with some
        # customizations for certain attributes.
        elif type(attr_val) is float:
            # We want to display the sensitivities in useful units, which should
            # simulate scientific notation. The attribute value is the
            # sensitivity's index in the SENSVECTOR.
            if "Sens" in attr_name:
                value = QSpinBox()
                value.setMaximum(1E10)
                value.setMinimum(1)
                attr_val = SENSVECTOR[int(attr_val)]
                # Figure out which units to use
                for ex in [(1E-3, 'mV'), (1E-6, 'uV'), (1E-9, 'nV')]:
                    if attr_val / ex[0] > 1 and attr_val / ex[0] < 1000:
                        value.setValue(attr_val / ex[0])
                        value.setSuffix(' {units}'.format(units=ex[1]))
            # If the value is a float, but not a sensitivity, just use a normal
            # doublespinbox
            else:
                value = QDoubleSpinBox()
                value.setMaximum(1E9)
                value.setMinimum(-1E9)
                value.setValue(attr_val)
        # Third, if the value is a datetime, dispaly it in a datetimeedit
        # element.
        elif type(attr_val) is datetime:
            value = QDateTimeEdit()
            value.setDateTime(attr_val)
        # Finally, for everything else just display it in a lineedit element.
        else:
            value = QLineEdit()
            value.setText(str(attr_val))

        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(value)

        self.setLayout(layout)

class AttributesWidget(QWidget):
    """This widget displays the attributes of a channel.

    This widget displays all attributes of a HDF5 channel.

    Parameters
    ----------
    chan : Channel, optional
        A channel whose attributes should be displayed at instantiation.

    Attributes
    ----------
    label : QLabel
        The label of this widget, which is "Attributes".
    lbl_layout : QHBoxLayout
        The layout for the label
    layout : QVBoxLayout
        The layout for all elements of the widget

    Methods
    -------
    clear_attributes
        Delete all of the Attribute widgets contained by this widget
    select_chan
        Select the channel whose attributes are to be shown
    emit_new_attributes
        Wrapper function for connecting the editing of a widget to the
        new_attribute signal.

    Signals
    -------
    new_attribute
        Indicates that a new attributes has been entered and is ready to be
        incorporated into the channel's data.

    """

    # Define the new signal 'new_attributes'
    new_attributes = pyqtSignal()

    def __init__(self, chan=None, parent=None):
        super(AttributesWidget, self).__init__(parent)

        self.label = QLabel("Attributes")

        self.lbl_layout = QHBoxLayout()
        self.lbl_layout.addWidget(self.label)
        self.lbl_layout.addStretch()

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.lbl_layout)

        # Generate some temporary filler attributes when the program initially
        # starts.
        if not chan:
            for i in range(3):
                new_attr = Attribute("Attribute {n}".format(n=i), i)
                self.layout.addWidget(new_attr)
        else:
            self.select_chan(chan)

        self.setLayout(self.layout)

        self.setMaximumWidth(self.sizeHint().width())

    def clear_attributes(self):
        """Delete the attribute widgets from the display."""

        for i in range(self.layout.count()):
            try:
                self.layout.itemAt(i).widget().close()
            except AttributeError:
                pass

    def select_chan(self, chan):
        """Select the channel whose attributes are to be displayed.

        Pass the channel so its attributes can be collected and displayed.

        Parameters
        ----------
        chan : Channel
            The channel whose attributes are to be displayed.

        """

        for attr_name in sorted(chan.attributes.keys()):
            attr_val = chan.attributes[attr_name]
            self.layout.insertWidget(self.layout.count()-1,
                                     Attribute(attr_name, attr_val))

    def emit_new_attributes(self):
        """Emit the 'new_attributes' signal.

        The function just provides an easy way to connect other signals to
        emitting the widget's new_attributes signal.

        """

        self.new_attributes.emit()

class MainWindow(QMainWindow):
    """The main window widget for the program.

    """

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        #### 1 CREATE AND INITIALIZE DATA STRUCTURES ####

        self.xLabel = None
        self.xSelection = DEFAULTX
        self.xSelection_old = None
        self.xArray = None

        self.yLabel = None
        self.ySelection = DEFAULTY
        self.ySelection_old = None

        self.yArray = None

        self.filename = None

        self.tdms_file_object = None

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
        fig = Figure(dpi=100)
        self.canvas = FigureCanvas(fig)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        mpl_toolbar = NavigationToolbar(self.canvas, self.canvas)

        self.axes = fig.add_subplot(111)

        # X selector on bottom
        self.xSelector = QListWidget()
        self.xSelector.addItem("Time")
        self.xSelector.setFlow(0)
        xSelectorLabel = QLabel("x axis channel")
        self.xSelector.setMaximumHeight(self.xSelector.sizeHintForColumn(0))

        # Offset and parameter widgets on the right top
        self.offsetThing = OffsetWidget()
        self.attributesThing = AttributesWidget()

        # Save channel on right bottom
        self.save_chan_chkbx = QCheckBox()
        save_chan_label = QLabel("Save Channel")

        # Status bar at the bottom

        self.fileSizeLabel = QLabel("File Size: {f_size:0>7.3f} MB".format(f_size=0.0))
        self.fileSizeLabel.setFixedWidth(self.fileSizeLabel.sizeHint().width()+10)
        self.fileSizeLabel.setFrameStyle(QFrame.Panel|QFrame.Sunken)

        self.yChanLength = QLabel("Y Channel Length: {y_len:0>7.0f}".format(y_len=0.0))
        self.yChanLength.setFixedWidth(self.yChanLength.sizeHint().width()+10)
        self.yChanLength.setFrameStyle(QFrame.Panel|QFrame.Sunken)
        
        self.xChanLength = QLabel("X Channel Length: {x_len:0>7.0f}".format(x_len=0.0))
        self.xChanLength.setFixedWidth(self.xChanLength.sizeHint().width()+10)
        self.xChanLength.setFrameStyle(QFrame.Panel|QFrame.Sunken)

        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.addPermanentWidget(self.fileSizeLabel)
        status.addPermanentWidget(self.yChanLength)
        status.addPermanentWidget(self.xChanLength)

        status.showMessage("Ready", 5000)
        
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

        self.resize(self.sizeHint())

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
        #self.addActions(self.fileMenu, self.fileMenuActions)

        self.xSelector.itemSelectionChanged.connect(self.make_x_selection)
        self.ySelector.itemSelectionChanged.connect(self.make_y_selection)
        self.offsetThing.new_offset.connect(self.subtract_offset)
        self.fileMenu.triggered.connect(self.update_file_menu)

        self.save_chan_chkbx.stateChanged.connect(self.toggle_save)

        #5 Read in application's settings
        settings = QSettings()

        # Restore the geometry and state of the main window from last use
        #self.restoreGeometry(settings.value("MainWindow/Geometry"))
        #self.restoreState(settings.value("MainWindow/State"))

        self.setWindowTitle("TDMS to HDF5 Converter")
        self.recentFiles = settings.value("RecentFiles")
        if not self.recentFiles:
            self.recentFiles = []

        self.update_file_menu()

    def update_ui(self):
        pass

    def initVariables(self):
        self.xLabel = None
        self.xSelection = DEFAULTX
        self.xSelection_old = None
        self.xArray = None

        self.yLabel = None
        self.ySelection = DEFAULTY
        self.ySelection_old = None

        self.yArray = None

        self.filename = None

        self.tdms_file_object = None

        self.channel_registry = {}

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

    def update_file_menu(self):
        self.fileMenu.clear()
        self.addActions(self.fileMenu, self.fileMenuActions[:-1])
        current = self.filename if self.filename is not None else None
        recentFiles = []
        for fname in self.recentFiles:
            if fname != current and QFile.exists(fname):
                recentFiles.append(fname)
        if recentFiles:
            self.fileMenu.addSeparator()
            for i, fname in enumerate(recentFiles):
                action = QAction("&{num} {name}".format(num=i+1, name=QFileInfo(fname).fileName()), self)
                action.setData(fname)
                action.triggered.connect(lambda: self.loadFile(fname))
                self.fileMenu.addAction(action)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.fileMenuActions[-1])

    def fileOpen(self): # Process 1
        self.initVariables()
        basedir = os.path.dirname(self.filename) if self.filename is not None \
          else "~/Documents/PhD/root/raw-data/sio2al149/CryoMeasurement"
        formats = "TDMS files (*.tdms)"
        fname = QFileDialog.getOpenFileName(self, "Open a TDMS File",
                                            basedir, formats)

        # Process 1.1 Collect file name
        if fname and QFile.exists(fname):
            self.loadFile(fname)

    def loadFile(self, fname): # Process 1.2 Generate TDMS file object
        self.add_recent_file(fname)
        self.tdms_file_object = TdmsFile(fname)
        self.filename = fname

         # Process 1.3 Read data into local structure
        if self.tdms_file_object:

            # Process 1.3.0 Generate group list
            group_list = self.tdms_file_object.groups()

            # Processes 1.3.1 through 1.3.3 Sort TDMS data
            for group in group_list:
                self.sortTDMSGroupData(group)

            message = "Loaded {f_name}".format(f_name=os.path.basename(fname))
            self.sourceFileName.setText(os.path.basename(fname))

            # Process 2.1 Populate channel selection lists
            self.update_selectors()

        else:
            message = "Failed to load {f_name}".format(f_name=os.path.
                                                       basename(fname))

        self.statusBar().showMessage(message, 5000)

        fsize = os.path.getsize(self.filename)
        self.fileSizeLabel.setText("File Size: {file_size:>7.3f} MB".format(file_size=fsize/1E6))
        #TODO self.updateStatus(message) # see Rapid GUI ch06.pyw

    def add_recent_file(self, fname):
        if fname is None:
            return
        if not fname in self.recentFiles:
            self.recentFiles.insert(0, fname)
            while len(self.recentFiles) > 9:
                self.recentFiles.pop()

    def sortTDMSGroupData(self, group): # Process 1.3 Sort Group data

        # Process 1.3.1 Get <Group> Channels
        group_props = self.tdms_file_object.object(group).properties

        # Process 1.3.2 Get <Group> Properties
        group_chans = self.tdms_file_object.group_channels(group)

        # Process 1.3.3 Create a new channel in the registry for each channel
        # in the group
        for chan in group_chans:
            chan_name = chan.path.split('/')[-1].strip("'")

            # Process 1.3.3.1 Generate new channel object and fill with data
            # Some of the TDMS channels were created, but never populated with
            # data. The following weeds those out.
            try:
                new_chan = Channel(chan_name,
                                device=group,
                                meas_array=chan.data)
            except TypeError:
                self.statusBar().showMessage("Channel {chan} in {dev} has no data"
                                             .format(chan=chan_name, dev=group),
                                             5000)

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
                    for atr_name in ADWIN_DICT[chan_name]:
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

    def update_selectors(self):

        # Clear the selectors
        self.xSelector.clear()
        self.ySelector.clear()

        # Add the names of the channels in the registry to both selectors
        for key in self.channel_registry.keys():
            self.xSelector.addItem(key)
            self.ySelector.addItem(key)

        # Add the time "channel" to the x selector
        self.xSelector.addItem('Time')

        # Sort the lists (alphabetically) otherwise the order constantly changes
        self.xSelector.sortItems()
        self.ySelector.sortItems()

        # Set the current x selector default
        default_x_item = self.xSelector.findItems(DEFAULTX, Qt.MatchExactly)
        self.xSelector.setCurrentItem(default_x_item[0])

        # Set the current y selector default
        try:
            default_y_item = self.ySelector.findItems(DEFAULTY,
                                                      Qt.MatchExactly)
            self.ySelector.setCurrentItem(default_y_item[0])
        except IndexError:
            self.ySelector.setCurrentRow(0)

        self.xSelector.setMinimumHeight(self.xSelector.sizeHintForRow(0)*3)
        self.ySelector.setMinimumWidth(self.ySelector.sizeHintForColumn(0)+10)

    def exprtToHDF5(self): # Process 5 Save to HDF5
        fname = self.filename.split('.')[0] + '.hdf5'
        basedir = "/home/chris/Documents/PhD/root/data/sio2al149/cryo_measurement"

        if not os.path.exists(basedir):
            os.makedirs(basedir)

        formats = "TDMS files (*.hdf5 *.h5 *.he5 *.hdf)"
    
        dialog = QFileDialog()
        dialog.setFilter(formats)
        dialog.setDefaultSuffix("*.hdf5")
        dialog.selectFile(os.path.join(basedir, fname))
        dialog.setDirectory(basedir)
        if dialog.exec_():
            fname = dialog.selectedFiles()
        else:
            return

        # Process 5.1 Create HDF5 file object
        hdf5_file_object = h5py.File(fname[0])

        # Process 5.2 Create channels at their locations
        for chan in self.channel_registry:

            chan_obj = self.channel_registry[chan]
            chan_name = chan

            #print(chan, self.channel_registry[chan].location,
            #      self.channel_registry[chan].write_to_file)

            # Process 5.2.1 Write channel data
            if self.channel_registry[chan].write_to_file:

                dset = hdf5_file_object.create_dataset(chan_obj.location,
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
        hdf5_file_object.flush()
        hdf5_file_object.close()

    def make_x_selection(self):

        self.x_change = True

        # Get the name of the newly selected channel
        self.xSelection = self.xSelector.currentItem().text()

        # Get the axis label
        self.xLabel = self.gen_axis_label(self.xSelection)

        # If the xSelection is time, use the time data instead of measurement
        # data
        if self.xSelection == 'Time':
            try:
                self.xArray = self.channel_registry[self.ySelection].time
            except KeyError:
                self.xArray = np.array([])
        else:
            self.xArray = self.channel_registry[self.xSelection].data

        if self.yLabel:
            self.plotData()

        self.xSelection_old = self.xSelector.currentItem()

        self.x_change = False

        self.xChanLength.setText("X Channel Length: {x_len:>7.0f}".format(x_len=len(self.xArray)))

    def make_y_selection(self, offset=0.0):

        self.y_change = True

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
        self.attributesThing.clear_attributes()

        self.attributesThing.select_chan(self.channel_registry[self.ySelection])

        if self.xSelection == 'Time':
            self.make_x_selection()
        else:
            self.plotData()

        self.ySelection_old = self.ySelector.currentItem()

        self.y_change = False

        self.yChanLength.setText("Y Channel Length: {y_len:>7.0f}".format(y_len=len(self.yArray)))

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
            self.statusBar().showMessage("Could not generate an axis label for {chan}"
                                         .format(chan=self.xSelection), 5000)
        try:
            self.axes.set_ylabel(self.yLabel)
        except UnboundLocalError:
            self.statusBar().showMessage("Could not generate an axis label for {chan}"
                                         .format(chan=self.ySelection), 5000)

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

            if self.x_change:
                self.xSelector.setCurrentItem(self.xSelection_old)
            elif self.y_change:
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

        #print(ch_name)
        pass

    def closeEvent(self, event):
        """Reimplementation of the close even handler.

        We have to reimplement this because not all close actions, e.g. clicking
        the X button, call the close() method.  We want to catch this so we can
        give the user the opportunity to save unsaved changes before the program
        exits.

        """
        settings = QSettings()
        #settings.setValue("MainWindow/Geometry", QVariant(
        #    self.saveGeometry()))
        #settings.setValue("MainWindow/State", QVariant(
        #    self.saveState()))
        if self.recentFiles:
            recentFiles = self.recentFiles
        else:
            recentFiles = []
        settings.setValue("RecentFiles", recentFiles)

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
