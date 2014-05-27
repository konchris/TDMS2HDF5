#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Data structures for the tdms2hdf5 program

"""

import sys
import os
import platform
from datetime import datetime

# Import third-party modules
import numpy as np

# Import our own modules

__author__ = "Christopher Espy"
__copyright__ = "Copyright (C) 2014, Christopher Espy"
__credits__ = ["Christopher Espy"]
__license__ = "GPL"
__version__ = "0.0.1"
__maintainer__ = "Christopher Espy"
__email__ = "christopher.espy@uni-konstanz.de"
__status__ = "Development"

PROGNAME = os.path.basename(sys.argv[0])
PROGVERSION = __version__

class Waveform(object):
    """An implementation of the NI LabView Waveform

    """
    
    def __init__(self, t0 = datetime.now(), dt = 0,
                 Y = np.array([]), parent = None):
        super(Waveform, self).__init__(parent)
        self.t0 = 0
        self.dt = 0
        self.Y = np.array([])

    def reset_t0(self):
        """Reset the waveform's start time to now.

        Because the waveform object is not necessarily created when the
        measurement actually starts this makes it easy to syncronize t0
        with the start of the measurement.

        """
        self.t0 = datetime.now()


class Channel(object):
    """An implementation of a measurement channel

    """
    
    def __init__(self, parent = None):
        super(Channel, self).__init__(parent)
        self.attributes = {}
        self.data = Wafeform()
        
