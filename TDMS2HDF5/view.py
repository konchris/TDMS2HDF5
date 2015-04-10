#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" The veiw components

"""

__author__ = "Christopher Espy"
__copyright__ = "Copyright (C) 2014, Christopher Espy"
__credits__ = ["Christopher Espy"]
__license__ = "GPL"
__version__ = "0.5"
__maintainer__ = "Christopher Espy"
__email__ = "christopher.espy@uni-konstanz.de"
__status__ = "Development"

import sys

from PyQt4.QtCore import (SIGNAL)
from PyQt4.QtGui import (QApplication, QSizePolicy, QMainWindow,
                         QAction, QIcon)
import matplotlib as mpl
from tzlocal import get_localzone
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (FigureCanvasQTAgg as
                                                FigureCanvas)
from matplotlib.backends.backend_qt4agg import (NavigationToolbar2QT as
                                                NavigationToolbar)
import seaborn as sns

from TDMS2HDF5.Ui_MainWindow import Ui_MainWindow as MainWindow
from TDMS2HDF5.view_model import (TreeNode, TreeModel)

AXESLABELS = {r"Resistance [$\Omega$]": ["dR", "dRSample", "R", "RSample",
                                         "Res_RuO"],
              r"Current [$\mu$A]": ["I", "dI", "ISample", "dISample"],
              "Voltage [mV]": ["V", "dV", "VSample", "dVSample", "VRuO"],
              "Magnetfield [B]": ["zMagnet", "xMagnet", "Magnetfield", "B"],
              "Temperature [K]": ["Temp_RuO", "Temperature", "1k - Pot",
                                  "He3", "Sorption", "1k-Pot", "T1K", "THe3",
                                  "TSorp", "TSample_LK", "TSample_AD", "Tm"],
              "Capacitance [nF]": ["Cap", "TCap"],
              "Time [m]": ["Time_m"],
              }

sns.set_context("talk", font_scale=1.25, rc={'lines.linewidth': 3})
sns.set_style('whitegrid')


class MyMainWindow(QMainWindow, MainWindow):
    """The main window of the program.

    Attributes
    ----------
    ySelectorModel : view_mode.TreeModel
        The model driving how the channels are displayed in the ySelectorView.
    ySelectorView : PyQt.QtGui.QTreeView
        The view in which the y channel(s) of the plot is listed.
    xSelectorView : PyQt.QtGui.QListView
        The horizontal list view in which the plot's x channel is selected.
    saveChannelsCheckBox : PyQt.QtGui.QCheckBox
        Toggle whether the displayed y channel should be included in the
        export.
    noChannels : PyQt.QtGui.QPushButton
        Deselect all of the channels so that none are exported.
    allChannels : PyQt.QtGui.QPushButton
        Select all of the channels so that all are exported.
    menubar : PyQt.QtGui.QMenuBar
        The main window's menu bar.
    statusbar : PyQt.QtGui.QStatusBar
        The main window's status bar.
    canvas : matplotlib.backends.backend_qt4agg.FigureCanvasQTAgg
        The matplotlib canvas
    axes : matplotlib.axes.Axes
        The axes instance shown in the plot

    Layouts
    -------
    mainLayout : PyQt.QtGui.QHBoxLayout
        parent : centralwidget
        The main layout of the window. This contains two (three) sections:
        1. Left: The area for the ySelector
        2. Central: The area for the plotting canvas, xSelector, and export
            selector.
        (3. ) Right: The area for the offset and channel properties editors.
    centralLayout : PyQt.QtGui.QVBoxLayout
        parent : mainLayout
        The central layout displays the plotting canvas in the main, upper
        portion and the bottom stip has the xSelector on the left side and the
        export selector on the right side.
    xSelectorLayout : PyQt.QtGui.QHBoxLayout
        parent : centralLayout
        The layout for the xSelector. This contains a label on the left and the
        selector list view on the right.
    horizontalLayout : PyQt.QtGui.QHBoxLayout
        parent : xSelectorLayout
        The channel export selector layout. On the left is the selection
        checkbox. In the middle is the "All" button, which marks all channels
        to be export. On the right is the "None" button, which unmarks all
        channels from exporting.
    ySelectorLayout : PyQt.QtGui.QVBoxLayout
        parent : mainLayout
        The layout for the ySelector. This contains a label at the extreme top
        and the tree view below that.

    Methods
    -------
    createAction(text : str, slot=None, shortcut=None, icon=None, tip=None,
                 checkable=False, signal="triggered()")
        Create an action to be added to the menu bar.
    addAction(target : PyQt.QtGui.QMenuBar, action : PyQt.QtGui.QAction)
        Add an action to a menu bar.

    """

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)

        mpl.rcParams['timezone'] = get_localzone().zone

        self.setupUi(self)

        # Set models
        self.ySelectorModel = TreeModel(TreeNode(""))
        self.ySelectorView.setModel(self.ySelectorModel)

        # Matplotlib canvas
        fig = Figure(dpi=100)

        self.canvas = FigureCanvas(fig)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        mpl_toolbar = NavigationToolbar(self.canvas, self.canvas)

        self.axes = fig.add_subplot(111)

        self.centralLayout.insertWidget(0, self.canvas)
        self.centralLayout.insertWidget(1, mpl_toolbar)

        # Adjust the offset spinbox range and significant digits
        # self.offsetSpinBox.setDecimals(10)
        # self.offsetSpinBox.setRange(-1000000,1000000)

    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
        """Do something.

        This was take from 'Rapid Gui Programming with Python and Qt' by Mark
        Summerfield. This code automates the tasks associated with creating new
        actions.

        Parameters
        ----------
        text : str
            The text of the action.
        slot : , optional
            The slot to which the action will be connected.
        shortcut: str or PyQt.QtGui.QKeySequence, optional
            The shortcut keyboard sequence for the action.
        icon : str, optional
            The base filename of image to use as the icon.
        tip : str, optional
            The string that should appear in the tool tip and status tip.
        checkable : boolean, optional
            Whether the action in the menu bar is checkable.
        signal : str, optional
            The the text of the PyQt.QtCore.SIGNAL to use for the action.

        Returns
        -------
        PyQt.QtGui.QAction


        """
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
        """Add an action to the target object.

        Parameters
        ----------
        target : PyQt.QtGui.QObject
            The object, usually a QFileMenu, to which the action should be
            added.
        actions : list
            A list of the actions to add to target.

        """
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)


def main(argv=None):
    "The main function"

    if argv is None:
        argv = sys.argv

    app = QApplication(sys.argv)
    form = MyMainWindow()
    form.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
