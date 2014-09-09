#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" The model components

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
from datetime import datetime

import numpy as np

from PyQt4.QtCore import QAbstractItemModel


from ChannelModel import (ADWIN_DICT, Channel, ChannelRegistry)

class ChannelTreeModel(QAbstractItemModel):

    def __init__(self, parent=None):

        super(ChannelTreeModel, self).__init__(parent)
        self.channelRegistry = ChannelRegistry()

        

    def loadFile(self, filename):

        self.channelRegistry.loadFromFile(filename)

    def data(self):
        pass

    def headerData(self):
        pass

    def rowCount(self):
        pass

    def columnCount(self):
        pass

    def index(self):
        pass

    def parent(self):
        pass

def main(argv=None):

    if argv is None:
        argv = sys.argv

    chanReg = ChannelRegistry()
    chanReg.loadFromFile("/home/chris/Espy/MeasData/HelioxTesting/2014-04-09T10-48-33-Cool-Down.tdms")

    for k, v in chanReg.items():
        print(k)
        print(v.name, v.attributes)


if __name__ == "__main__":
    main()
