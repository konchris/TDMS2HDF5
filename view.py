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
from PyQt4.QtGui import (QApplication, QDialog, QSizePolicy, QMainWindow,
                         QAction, QIcon, QKeySequence)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (FigureCanvasQTAgg as
                                                FigureCanvas)
from matplotlib.backends.backend_qt4agg import (NavigationToolbar2QT as
                                                NavigationToolbar)

from Ui_MainWindow import Ui_MainWindow as MainWindow
from view_model import (TreeNode, TreeModel)
import resources_rc

class MyMainWindow(QMainWindow, MainWindow):
    """My main window class

    """

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)

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
        self.offsetSpinBox.setDecimals(10)
        self.offsetSpinBox.setRange(-1000000,1000000)

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


def main(argv=None):

    if argv is None:
        argv = sys.argv

    app = QApplication(sys.argv)
    form = MyMainWindow()
    form.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
