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

from PyQt4.QtGui import (QApplication, QDialog, QSizePolicy)
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (FigureCanvasQTAgg as
                                                FigureCanvas)
from matplotlib.backends.backend_qt4agg import (NavigationToolbar2QT as
                                                NavigationToolbar)

from Ui_MainWindow import MainWindow


class MyMainWindow(MainWindow):
    """My main window class

    """

    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)

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


def main(argv=None):

    if argv is None:
        argv = sys.argv

    app = QApplication(sys.argv)
    form = MyMainWindow()
    form.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
