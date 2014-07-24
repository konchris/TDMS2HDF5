#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Data structures for the tdms2hdf5 program

"""

import sys
import os
#import platform
from datetime import datetime

# Import third-party modules
import numpy as np

# Import our own modules

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

CHAN_DICT = {"ISample": ["IAmp"],
             "VSample": ["VAmp"],
             "dISample": ["IAmp", "LISens"],
             "dVSample": ["VAmp", "LVSens"],
             "xMagnet": [],
             "TCap": [],
             "zMagnet": [],
             "VRuO": ["r max", "r min"],
             "I": [],
             "V": [],
             "R": [],
             "dI": [],
             "dV": [],
             "dR": [],
             "Res_RuO": ["p0", "p1", "r0"],
             "Temp_RuO": []}

OFFSET_CHANS = ["VSample", "ISample", "VRuO", "I", "V", "R", "Res_RuO",
                "zMagnet", "xMagnet", "Temp_RuO"]

CHAN_PARAMETERS = {"Res_RuO" : ["p0", "p1", "r0"],
                   "VRuO" : ["r max", "r min"],
                   "zMagnet" : ["V2T"],
                   "ISample" : ["IAmp"],
                   "VSample" : ["VAmp"],
                   "dISample" : ["IAmp", "LISens"],
                   "dVSample" : ["VAmp", "LVSens"]}

DEFAULTX = "zMagnet"
DEFAULTY = "dR"

AXESLABELS = {r"Resistance [$\Omega$]" : ["dR", "dRSample", "R", "RSample",
                                          "Res_RuO"],
              r"Current [$\mu$A]" : ["I", "dI", "ISample", "dRSample"],
              "Voltage [mV]" : ["V", "dV", "VSample", "dVSample", "VRuO"],
              "Magnetfield [B]" : ["zMagnet", "xMagnet"],
              "Time [s]" : ["Time"],
              "Temperature [K]" : ["Temp_RuO"],
              "Capacitance [nF]" : ["Cap"]}

RDEPENDENCIES = {}
DESCRIPTIONS = {}

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
    name : string
       The channel's name.
    data : numpy.array
       The measurement data array.
    time : numpy.array
       The time array of the measurement.
    location : string
       The absolute path of the channel in the HDF5 file.
    write_to_file : boolean
       Whether the channel should be written into the HDF5 file or discarded.

    Methods
    -------

    See Also
    --------
    numpy.array

    """

    def __init__(self, name, device='', meas_array=np.array([])):
        super(Channel, self).__init__()
        self.attributes = {"Device" : device,
                           "TimeInterval" : 0,
                           "Length" : len(meas_array),
                           "StartTime" : datetime.now(),
                           "Description" : "",
                           "RDepends" : []}

        self.name = name
        self.data = meas_array
        self.time = np.array([])
        self.location = ""
        self.write_to_file = False

    def _calculate_time_array(self):
        "If the time or measurment data updated, recalculate the time array."

        delta_time = self.attributes['TimeInterval']
        length = self.attributes['Length']

        self.time = np.linspace(0, length*delta_time, length)

    def set_delta_time(self, delta_time):
        "Reset the time interval (in seconds) of the measurement."

        self.attributes['TimeInterval'] = delta_time

        self._calculate_time_array()

    def set_location(self, location):
        "Set the absolute path of the channel in the HDF5 file."

        self.location = location

    def set_start_time(self, init_time):
        "Reset the start time (datetimestamp) of the measurement"

        self.attributes['StartTime'] = init_time

    def set_write(self):
        "Turn on writing this channel to the HDF5 file."

        self.write_to_file = True

    def unset_write(self):
        "Turn off writing this channel to the HDF5 file."

        self.write_to_file = False

def main(argv=None):
    "The main loop, for testing purposes only"

    if argv is None:
        argv = sys.argv

    chan_list = ['TestSine', 'TestCosine']
    chan_registry = {}

    test = Channel('none')
    test.attributes["Device"] = "ADWin"
    print(test.attributes)

    for chan in chan_list:
        chan_registry[chan] = 0


if __name__ == "__main__":
    main()
