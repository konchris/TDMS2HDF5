#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" The components for dealing with channel data.

The Channel object is an easy wrapper for channel data.
The ChannelRegistry is a sub-classed dictionary that stores the channels and
deals with writing them to a file.

"""

__author__ = "Christopher Espy"
__copyright__ = "Copyright (C) 2014, Christopher Espy"
__credits__ = ["Christopher Espy"]
__license__ = "GPL"
__version__ = "0.5"
__maintainer__ = "Christopher Espy"
__email__ = "christopher.espy@uni-konstanz.de"
__status__ = "Development"

import os
import sys
from datetime import datetime

import numpy as np

from nptdms.tdms import TdmsFile

ADWIN_DICT = {"ISample": ["IAmp"], "VSample": ["VAmp"],
              "dISample": ["IAmp", "LISens"], "dVSample": ["VAmp", "LVSens"],
              "xMagnet": [], "TCap": [], "zMagnet": [],
              "VRuO": ["r max", "r min"], "I": [], "V": [], "R": [], "dI": [],
              "dV": [], "dR": [], "Res_RuO": ["p0", "p1", "r0"],
              "Temp_RuO": []}


class Channel(object):
    """A measurement channel containing a waveform and meta data.

    Returns a channel object which contains a waveform object plus any
    meta-data relevant to the measurement data. Examples of this include
    amplification factors or parameters used for calculations.

    Parameters
    ----------
    name : string
        The channel's name.
    device : string
        The name of the recording device used to record this data.
    meas_array : numpy.ndarray
        The measurement data corresponding to this channel.

    Attributes
    ----------
    attributes : dictionary_like
       The channel's attributes correspond to the attributes found with
       a channel in a HDF5 file. Here they are stored as key-value pairs.
       Device : string
           The recording device for the channel.
       TimeInterval : int, float
           The time interval between data points.
       Length : int
           The number of data points in the mesurement array.
       StartTime : datetime.datetime
           The starting time (of recording) of the channel.
    name : string
       The channel's name.
    data : numpy.ndarray
       The measurement data array.
    time : numpy.ndarray
       The time array of the measurement.
    parent : string
       The name of the parent group of the channel in the HDF5 file.
    write_to_file : boolean
       Whether the channel should be written into the HDF5 file or discarded.

    Methods
    -------
    setParent(newParent : str)
        Set the parent group of the channel
    getParent()
        Return the parent group of the channel (str)
    setName(newName : str)
        Set the name of the channel
    getName()
        Return the name of the channel (str)
    setStartTime(newStartTime : datetime.datetime)
        Set the starting time of the channel measurement
    getStartTime()
        Return the start time of the channel measurement (datetime.datetime)
    setTimeStep(newDelTime : int, float)
        Set the time step of the channel measurement
    getTimeStep()
        Return the time step of the measurement (int, float)
    getTimeTrack()
        Return the time track of the channel measurement (numpy.ndarray)
    getElapsedTime()
        Return the elapsed time track of the measurement (numpy.ndarry)
    toggleWrite()
        Toggle's the channels write_to_file value

    See Also
    --------
    numpy.ndarray

    """

    def __init__(self, name, device='', meas_array=np.array([])):
        super(Channel, self).__init__()
        self.attributes = {"Device": device,
                           "TimeInterval": 0,
                           "Length": len(meas_array),
                           "StartTime": datetime.now()}

        self.name = name
        self.data = meas_array
        self.time = np.array([])
        self.parent = 'raw'
        self.unit = 'n.a.'
        self.write_to_file = True

        self._recalculateTimeArray()

    def _recalculateTimeArray(self):
        """Recalculate the time track based on start time and time step"""
        dt = self.getTimeStep()

        length = self.attributes['Length']

        timeArray = np.linspace(0, length*dt, length)

        self.time = timeArray

    def setParent(self, newParent):
        """Set the parent group of the channel in the HDF5 file.

        Parameters
        ----------
        newParent : string
            The name of the parent group of the channel in the HDF5 file.

        """

        if isinstance(newParent, str):
            self.parent = newParent
        else:
            raise TypeError('Channel parent can only be a string')

    def getParent(self):
        """Return the name of the parent group of the channel

        Returns
        -------
        parent : str
            The name of the parent group of the channel in the HDF5 file.

        """
        return self.parent

    def setName(self, newName):
        """Set the name of the channel

        Parameters
        ----------
        newName : str
            The name of the channel

        """

        if isinstance(newName, str):
            self.name = newName
        else:
            raise TypeError('Channel name can only be a string')

    def getName(self):
        """Return the name of the  channel

        Returns
        -------
        name : str
            The name of the channel

        """
        return self.name

    def setStartTime(self, newStartTime):
        """Set the starting time of the channel measurement

        Parameters
        ----------
        newStartTime : datetime.datetime
            The new datetime at which the measurement started.

        """
        if isinstance(newStartTime, datetime):
            self.attributes['StartTime'] = newStartTime
        else:
            raise TypeError('The start time has to be of datetime type')

    def getStartTime(self):
        """Returns the channel's measurement starting time in datetime format

        Returns
        -------
        StartTime : datetime.datetime
            The datetime at which the measurement started.

        """
        return self.attributes['StartTime']

    def setTimeStep(self, newDelTime):
        """Set the time between two measurement points.

        Parameters
        ----------
        newDelTime : int, float
            The new time interval between measurement points

        """
        if isinstance(newDelTime, (int, float)):
            self.attributes['TimeInterval'] = newDelTime
            self._recalculateTimeArray()
        else:
            message = 'The time interval can only be an int or a float'
            raise TypeError(message)

    def getTimeStep(self):
        """Return the time interval of the measurement

        Returns
        -------
        TimeInterval : int, float
            The new time interval between measurement points

        """
        return self.attributes['TimeInterval']

    def getTimeTrack(self):
        """Return the time array of the measurement

        Returns
        -------
        timeTrack : numpy.ndarray
            The time array of the measurement

        """
        return self.time

    def getElapsedTime(self):
        """Return the elapsed time track of the measurement

        Returns
        -------
        elapsedTime : numpy.ndarray
           This is an array of the elapsed time from the start of the
           measurement in seconds.

        """
        dt = self.attributes['TimeInterval']

        length = self.attributes['Length']

        elapsed_time = np.linspace(0, length * dt, length)

        return elapsed_time

    def toggleWrite(self):
        """Toggle whether to write the channel to the HDF5 file

        """
        self.write_to_file = not self.write_to_file


class ChannelRegistry(dict):
    """Container for holding all of the channels

    This is just a basic dictionary with a few added changes.
    Channels are saved under the key <parent>/<channel name>.
    The dictionary also provides a list of the parents present in the registry
    as well as the names. It is also respondisble for importing the channels
    from a file and finally exporting them to the HDF5 file.

    Attributes
    ----------
    parents : list
        A list of the parent groups of all of the channels

    Methods
    -------
    addChannel(newChan : Channel)
        Add a new, unique channel to the registry
    loadFromFile(filename : str)
        Load data from a file with the absolute path filename
    add_V():
        Add the processed channel 'V' derived from 'VSample'
    add_dV():
        Add the processed channel 'dV' derived from 'dVSample'
    add_I():
        Add the processed channel 'I' derived from 'ISample'
    add_dI():
        Add the processed channel 'dI' derived from 'dISample'
    add_R():
        Add the processed channel 'R' derived from 'V' and 'I'
    add_RSample():
        Add the processed channel 'RSample' derived from 'VSample' and
        'ISample'
    add_dRSample():
        Add the processed channel 'dRSample' derived from 'dVSample' and
        'dISample'
    add_dR():
        Add the processed channel 'dR' derived from 'dV' and 'dI'
    addTransportChannels():
        Add all of the transport channels

    """

    def __init__(self):
        super(ChannelRegistry, self).__init__()

        self.parents = []

    def addChannel(self, newChan):
        """Add a new, unique channel to the registry

        Parameters
        ----------
        newChan : Channel
            The channel object to add to the channel registry

        """
        if isinstance(newChan, Channel):
            channelKey = "{parent}/{cName}".format(parent=newChan.getParent(),
                                                   cName=newChan.getName())
            self[channelKey] = newChan
        else:
            raise TypeError('Only an object of the Channel type can be added')

    def loadFromFile(self, filename):
        """Load the data from a file

        Parameters
        ----------
        filename : str
            The absolute path of the file to be loaded

        """
        self.clear()

        if os.path.exists(filename):
            tdmsFileObject = TdmsFile(filename)
        else:
            print('The file {fn} does not exist!'.format(fn=filename))
            return

        # Generate channels one device at a time
        for device in tdmsFileObject.groups():

            # The ADWin device properties will later need to be mapped to
            # specific channels
            deviceProperties = tdmsFileObject.object(device).properties

            # Get a list of the device's channels
            deviceChannels = tdmsFileObject.group_channels(device)

            # Setup a channel object for each channel.
            # Sort the ADWin device properites to the proper channels if
            # necessary.
            for chan in deviceChannels:
                channelName = chan.path.split('/')[-1].strip("'")
                # Some channels are empty. This becomes apparent when trying
                # load the properties.
                try:

                    newChannel = Channel(channelName, device=device,
                                         meas_array=chan.data)

                    startTime = chan.property('wf_start_time')
                    newChannel.setStartTime(startTime)

                    # Sometimes the wf_increment is not saved in seconds, but
                    # in milliseconds.
                    # Convert is back into seconds

                    timeStep = chan.property("wf_increment")

                    if timeStep > 1:
                        timeStep = timeStep / 1000

                    newChannel.setTimeStep(timeStep)

                    if device == "ADWin":
                        for attributeName in ADWIN_DICT[channelName]:
                            # If LISens or LVSens is not present a key error is
                            # thrown here!
                            # This is where to catch the missing data and allow
                            # the user to enter it.
                            try:
                                newChannel.attributes[attributeName] = \
                                    deviceProperties[attributeName]
                            except KeyError as err:
                                # print('1\tKey Error: {0} on channel {1}'
                                #       .format(err, channelName))
                                pass

                    self.addChannel(newChannel)

                except KeyError as err:
                    # print('2\tKey Error: {0} on channel {1}'
                    #       .format(err, channelName))
                    pass
                except TypeError as err:
                    # print('3\tType Error: {0} on channel {1}'
                    #       .format(err, channelName))
                    pass

        self.addTransportChannels()

    def add_V(self):
        """Add the processed channel 'V' derived from 'VSample'.

        """
        if 'raw/VSample' in self.keys() and 'raw/V' not in self.keys():
            chanVSample = self['raw/VSample']
        else:
            return

        # Calculate the data
        vMeasArray = (chanVSample.data / chanVSample.attributes['VAmp']) * 1E3
        # Create the channel
        chanV = Channel('V', device='ADWin', meas_array=vMeasArray)
        # Set the parent
        chanV.setParent('proc')
        # Set the start time and time interval based on VSample's values
        chanV.setStartTime(chanVSample.getStartTime())
        chanV.setTimeStep(chanVSample.getTimeStep())
        # Add the channel to the registry
        self.addChannel(chanV)

    def add_dV(self):
        """Add the processed channel 'dV' derived from 'dVSample'

        """
        # dV depends on dVSample and LVSens
        if ('raw/dVSample' in self.keys() and 'LVSens' in self['raw/dVSample'] \
            .attributes.keys()) and ('raw/dV' not in self.keys()):
            chandVSample = self['raw/dVSample']
        else:
            return

        # Calculate the data
        dVMeasArray = ((chandVSample.data / chandVSample.attributes['VAmp']) /
                       10) * chandVSample.attributes['LVSens'] * 1E3
        # Create the channel
        chandV = Channel('dV', device='ADWin', meas_array=dVMeasArray)
        # Set the parent
        chandV.setParent('proc')
        # Set the start time and time interval based on dVSample's values
        chandV.setStartTime(chandVSample.getStartTime())
        chandV.setTimeStep(chandVSample.getTimeStep())
        # Add the channel to the registry
        self.addChannel(chandV)

    def add_I(self):
        """Add the processed channel 'I' derived from 'ISample'

        """
        if 'raw/ISample' in self.keys() and 'raw/I' not in self.keys():
            chanISample = self['raw/ISample']
        else:
            return

        # Calculate the data
        iMeasArray = (chanISample.data / chanISample.attributes['IAmp']) * 1E6
        # Create the channel
        chanI = Channel('I', device='ADWin', meas_array=iMeasArray)
        # Set the parent
        chanI.setParent('proc')
        # Set the start time and time interval based on ISample's values
        chanI.setStartTime(chanISample.getStartTime())
        chanI.setTimeStep(chanISample.getTimeStep())
        # Add the channel to the registry
        self.addChannel(chanI)

    def add_dI(self):
        """Add the processed channel 'dI' derived from 'dISample'

        """
        # dI depends on dISample and LISens
        if ('raw/dISample' in self.keys() and 'LISens' in self['raw/dISample'] \
            .attributes.keys()) and ('raw/dI' not in self.keys()):
            chandISample = self['raw/dISample']
        else:
            return

        # Calculate the data
        dIMeasArray = ((chandISample.data / chandISample.attributes['IAmp']) /
                       10) * chandISample.attributes['LISens'] * 1E6
        # Create the channel
        chandI = Channel('dI', device='ADWin', meas_array=dIMeasArray)
        # Set the parent
        chandI.setParent('proc')
        # Set the start time and time interval from dISample's values
        chandI.setStartTime(chandISample.getStartTime())
        chandI.setTimeStep(chandISample.getTimeStep())
        # Add the channel to the registry
        self.addChannel(chandI)

    def add_R(self):
        """Add the processed channel 'R' derived from 'V' and 'I'

        """
        # R depends on V and I try and get the raw (calculated by ADWin) data
        # and fall back on the processed data
        if ('raw/I' and 'raw/V') in self.keys() and 'raw/R' not in self.keys():
            chanI = self['raw/I']
            chanV = self['raw/V']
        elif ('proc/I' and 'proc/V') in self.keys():
            chanI = self['proc/I']
            chanV = self['proc/V']
        else:
            return

        # Calculate the data
        rMeasArray = chanV.data/chanI.data
        # Create the channel
        chanR = Channel('R', device='ADWin', meas_array=rMeasArray)
        # Set the parent
        chanR.setParent('proc')
        # Set the start time and time interval based on I's values'
        chanR.setStartTime(chanI.getStartTime())
        chanR.setTimeStep(chanI.getTimeStep())
        # Add the channel to the registry
        self.addChannel(chanR)

    def add_RSample(self):
        """Add the processed channel 'RSample' derived from 'VSample' and
        'ISample'

        """
        # RSample depends on ISample and VSample. Try to get the values from
        # the raw data. Fall back to the processed data
        if ('raw/ISample' and 'raw/VSample') in self.keys() and \
            (('raw/RSample'and 'raw/R') not in self.keys()):
            chanISample = self['raw/ISample']
            chanVSample = self['raw/VSample']
        elif ('proc/ISample' and 'proc/VSample') in self.keys():
            chanISample = self['proc/ISample']
            chanVSample = self['proc/VSample']
        else:
            return

        # Calculate the data
        rMeasArray = chanVSample.data/chanISample.data
        # Create the channel
        chanRSample = Channel('RSample', device='ADWin', meas_array=rMeasArray)
        # Set the parent
        chanRSample.setParent('proc')
        # Set the start time and time interval based on ISample's values
        chanRSample.setStartTime(chanISample.getStartTime())
        chanRSample.setTimeStep(chanISample.getTimeStep())
        # Add the channel to the registry
        self.addChannel(chanRSample)

    def add_dRSample(self):
        """Add the processed channel 'dRSample' derived from 'dVSample' and
        'dISample'

        """
        # dRSample depends on dISample and dVSample. Try to use the raw data.
        # Fall back on the processed data.
        if ('raw/dISample' and 'raw/dVSample') in self.keys() and \
          (('raw/dRSample' and 'raw/dR') not in self.keys()):
            chandISample = self['raw/dISample']
            chandVSample = self['raw/dVSample']
        elif ('proc/dISample' and 'proc/dVSample') in self.keys():
            chandISample = self['proc/dISample']
            chandVSample = self['proc/dVSample']
        else:
            return

        # Calculate the data
        dRMeasArray = chandVSample.data/chandISample.data
        # Create the channel
        chandRSample = Channel('dRSample', device='ADWin',
                               meas_array=dRMeasArray)
        # Set the parent
        chandRSample.setParent('proc')
        # Set the start time and time interval based on dISample's values
        chandRSample.setStartTime(chandISample.getStartTime())
        chandRSample.setTimeStep(chandISample.getTimeStep())
        # Add the channel to the registry
        self.addChannel(chandRSample)

    def add_dR(self):
        """Add the processed channel 'dR' derived from 'dV' and 'dI'

        """
        # dR depends on dI and dV. Try to get the raw data. Fall back on the
        # processed data.
        if ('raw/dI' and 'raw/dV') in self.keys() and \
          ('raw/dR' not in self.keys()):
            chandI = self['raw/dI']
            chandV = self['raw/dV']
        elif ('proc/dI' and 'proc/dV') in self.keys():
            chandI = self['proc/dI']
            chandV = self['proc/dV']
        else:
            return

        # Calculate the data
        dRMeasArray = chandV.data/chandI.data
        # Create the channel
        chandR = Channel('dR', device='ADWin', meas_array=dRMeasArray)
        # Set the parent
        chandR.setParent('proc')
        # Set the start time and time interval based on dI's values
        chandR.setStartTime(chandI.getStartTime())
        chandR.setTimeStep(chandI.getTimeStep())
        # Add the channel to the registry
        self.addChannel(chandR)

    def addTransportChannels(self):
        """Add all of the transport channels

        """
        self.add_V()
        self.add_dV()
        self.add_I()
        self.add_dI()
        self.add_RSample()
        self.add_dRSample()
        self.add_R()
        self.add_dR()


def main(argv=None):
    """The main loop when running this module as a standalone script."""

    if argv is None:
        argv = sys.argv

    DATADIR = '/home/chris/Documents/PhD/root/raw-data/'

    TESTFILE01 = os.path.join(DATADIR, "sio2al149", "cryo_measurement",
                              "2014-02-14",
                              "2014-02-14T14-39-08-First-Cooldown.tdms")
    TESTFILE02 = os.path.join(DATADIR, "fonin_heliox",
                              "2014-09-22-Testing-Run",
                              "2014-09-23T09-05-59-Pump-to-1.6K.tdms")

    chanReg = ChannelRegistry()
    chanReg.loadFromFile(TESTFILE02)

    for k, v in chanReg.items():
        # print(v.name, v.attributes['Device'], v.getTimeStep(),
        #       v.attributes['Length'])
        print(k, v.name)

if __name__ == "__main__":
    main()
