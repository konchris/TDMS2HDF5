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
    """A waveform object similar to those in LabView.
    
    Returns a waveform object which was inspired by LabView's waveforms.
    A waveform is a specialized time-dependant array that includes a starting
    time and an interval time between each data point.

    Parameters
    ----------
    t0 : datetime_like or float
       The starting time of the data series.
    dt : float
       The time interval between each data point in the time series.
    Y : array_like
       The time series data.

    Attributes
    ----------
    t0 : datetime_like or float
       The starting time of the data series.
    dt : float
       The time interval between each data point in the time series.
    Y : array_like
       The time series data.

    Methods
    -------
    reset_t0()
       Reset the waveform's starting time to now.

    See Also
    --------
    numpy.array

    """
    
    def __init__(self, t0 = datetime.now(), dt = 0,
                 Y = np.array([]), parent = None):
        """Initiate the waveform object.

        Parameters
        ----------
        t0 : datetime_like or float
           The starting time of the data series.
        dt : float
           The time interval between each data point in the time series.
        Y : array_like
           The time series data.
        
        
        """
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
    """A measurement channel containing a waveform and meta data.

    Returns a channel object which contains a waveform object plus any
    meta-data relevant to the measurement data. Examples of this include
    amplification factors or parameters used for calculations.

    Parameters
    ----------

    Attributes
    ----------
    attributes : dictionary_like
       The channel's attributes correspond to the attributes found with
       a channel in a HDF5 file. Here they are stored as key-value pairs.
    data : waveform
       The waveform object containing the measurement data.

    Methods
    -------

    See Also
    --------
    Waveform, numpy.array

    """
    
    def __init__(self, parent = None):
        super(Channel, self).__init__(parent)
        self.attributes = {}
        self.data = Wafeform()
        
