#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

import sys

# Import thrid-party modules

# PyQt4
from PyQt4.QtGui import QApplication

# Import our own modules
from ChannelModel import (Channel, ChannelRegistry)

def main(argv=None):

    if argv is None:
        argv = sys.argv

    channelRegistry = ChannelRegistry()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

