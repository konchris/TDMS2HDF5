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
import pytz

import numpy as np
import pandas as pd
import csv
from scipy import stats

from nptdms.tdms import TdmsFile

from TDMS2HDF5.Calculations import new_interpolate_bfield

ADWIN_DICT = {"ISample": ["IAmp"], "VSample": ["VAmp"],
              "dISample": ["IAmp", "LISens"], "dVSample": ["VAmp", "LVSens"],
              "xMagnet": [], "TCap": [], "zMagnet": [], "Cap": [],
              "VRuO": ["r max", "r min"], "I": [], "V": [], "R": [], "dI": [],
              "dV": [], "dR": [], "Res_RuO": ["p0", "p1", "r0"],
              "Temp_RuO": []}

CHANNEL_DICT = {"T1K": "1k - Pot",
                "THe3": "He3",
                "TSorp": "Sorption",
                "TSorp": "TSorb",
                "TSample_LK": "Temperature",
                "TSample_AD": "Temp_RuO",
                "Time_s": "measTime"
                }

DEVICE_NAMES = {"ITC503": "ITC 503"}

LOCAL_TZ = pytz.timezone("Europe/Berlin")


def replace_name(name, dict=CHANNEL_DICT):
    """Replace a non-pythonic name with a pythonic one.

    The goal is to be able to utilize pandas' method of accessing parts of a
    dataframe as though it were an attribute of the dataframe. Some of the
    device and channel names in the TDMS files are not conducive to being used
    as a python identifier like this.

    Parameters
    ----------
    name : str
        The string to be checks for replacement.

    Returns
    -------
    str
        A string where the invalid python identifiers are replaced with valid
        strings.

    """
    for replString, origString in dict.items():
        if (origString in name) and (replString not in name):
            name = name.replace(origString, replString)
    return name


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
       TimeInterval : numpy.timedelta64
           The time interval between data points.
       Length : int
           The number of data points in the mesurement array.
       StartTime : numpy.datetime64
           The starting time (of recording) of the channel.
    name : string
       The channel's name.
    data : numpy.ndarray
       The measurement data array.
    time : numpy.ndarray
       The absolute time array of the measurement.
    elapsed_time : numpy.ndarray
       The elapsed time array of the measurement.
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
    setStartTime(newStartTime : numpy.datetime64)
        Set the starting time of the channel measurement
    getStartTime()
        Return the start time of the channel measurement (numpy.datetime64)
    setTimeStep(newDelTime : numpy.timedelta64)
        Set the time step of the channel measurement
    getTimeStep()
        Return the time step of the measurement (numpy.timedelta64)
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
                           "TimeInterval": np.timedelta64(1, 'ms'),
                           "Length": len(meas_array),
                           "StartTime": np.datetime64(datetime.now())}

        self.setName(name)
        self.data = meas_array
        self.time = np.array([])
        self.elapsed_time = np.array([])
        self.parent = None
        self.unit = 'n.a.'
        self.write_to_file = True

        self._recalculateTimeArray()

    def _recalculateTimeArray(self):
        """Recalculate the time track based on start time and time step"""

        dt = self.attributes['TimeInterval']

        length = self.attributes['Length']

        startTime = np.datetime64(self.attributes['StartTime'])

        stopTime = startTime + dt * length

        absolute_time_track = np.arange(startTime, stopTime, dt)

        elapsed_time_track = ((absolute_time_track - startTime) /
                              np.timedelta64(1, 'm'))

        self.time = absolute_time_track
        self.elapsed_time = elapsed_time_track

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
        str
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
            self.name = replace_name(newName)
        else:
            raise TypeError('Channel name can only be a string')

    def getName(self):
        """Return the name of the  channel

        Returns
        -------
        str
            The name of the channel

        """
        return self.name

    def setStartTime(self, newStartTime):
        """Set the starting time of the channel measurement

        Parameters
        ----------
        newStartTime : numpy.datetime64
            The new datetime at which the measurement started.

        """
        if isinstance(newStartTime, np.datetime64):
            self.attributes['StartTime'] = newStartTime
            self._recalculateTimeArray()
        # else:
        #     raise TypeError('The start time has to be of numpy.datetime64'
        #                     'type')

    def getStartTime(self):
        """Returns the channel's measurement starting time in numpy.datetime64
            format

        Returns
        -------
        numpy.datetime64
            The datetime at which the measurement started.

        """
        return self.attributes['StartTime']

    def setTimeStep(self, newDelTime):
        """Set the time between two measurement points.

        Parameters
        ----------
        int, float
            The new time interval between measurement points

        """

        if isinstance(newDelTime, np.timedelta64):
            self.attributes['TimeInterval'] = newDelTime
            self._recalculateTimeArray()
        else:
            message = 'The time interval can only be a numpy.timedelta64'
            raise TypeError(message)

    def getTimeStep(self):
        """Return the time interval of the measurement

        Returns
        -------
        int, float
            The new time interval between measurement points

        """
        return self.attributes['TimeInterval']

    def getElapsedTimeTrack(self):
        """Return the elapsed time of the measurement in a numpy.ndarray

        Returns
        -------
        numpy.ndarray
            The time array of the measurement

        """
        return self.elapsed_time

    def getTimeTrack(self):
        """Return the absolute time track of the measurement

        Returns
        -------
        numpy.ndarray
           This is an array of the elapsed time from the start of the
           measurement in seconds.

        """
        return self.time

    def toggleWrite(self):
        """Toggle whether to write the channel to the HDF5 file

        """
        self.write_to_file = not self.write_to_file

    def getDevice(self):
        """Return the name of the device that recorded the channel.

        """
        return self.attributes['Device']


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
    file_start_time : numpy.datetime64
        The start time recorded in the TDMS file's properties
    file_end_time :  numpy.datetime64
        The end time recorded in the TDMS file's properties

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
    addTimeTracks():
        Add the time tracks for each device.

    """

    def __init__(self):
        super(ChannelRegistry, self).__init__()

        self.parents = []
        self.file_start_time = None
        self.file_end_time = None
        self.devices = []
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

        parent = newChan.getParent()

        if parent not in self.parents:
            self.parents.append(parent)

        device = newChan.getName().split('/')[0]

        if device not in self.devices:
            self.devices.append(device)

        time_name = '{r}/{d}/{t}'.format(r=parent, d=device, t='Time_m')

        for key in self.keys():
            if '{r}/{d}/time'.format(r=parent, d=device) in key:
                time_name = key
            elif '{r}/{d}/Time'.format(r=parent, d=device) in key:
                time_name = key

        if time_name not in self.keys():
            self.addTimeTracks(device, newChan.getElapsedTimeTrack())

    def loadFromFile(self, filename):
        """Load the data from a file

        Parameters
        ----------
        filename : str
            The absolute path of the file to be loaded

        """
        self.clear()

        if os.path.exists(filename):
            extention = filename.split('.')[-1]
            if extention in ('tdms'):
                self._loadFromTDMS(filename)
            elif extention in ('csv', 'dat'):
                self._loadFromCSV(filename)
        else:
            print('The file {fn} does not exist!'.format(fn=filename))
            return

    def _loadFromCSV(self, filename):
        """Load the data from a CSV file into the channel registry

        Parameters
        ----------
        filename : str
            The absolute path of the file to be loaded


        """
        ext = filename.split('.')[-1]

        if ext in ['dat']:
            start_time, col_names = self._get_dat_column_names(filename)
            sr = None
        elif ext in ['csv']:
            start_time, col_names = self._get_csv_column_names(filename)
            sr = 1

        # col_names = ('measTime', 'RSample', 'TSorb', 'T1K', 'THe3')
        # csvDataFrame = pd.read_csv(filename, header=None, comment='#',
        #                            names=col_names)
        # print(csvDataFrame.describe())
        device = 'all'

        for i, chan in enumerate(col_names):
            chan_df = pd.read_csv(filename, header=None, comment='#',
                                  names=[chan], usecols=[i], skiprows=sr)

            data = chan_df[chan].values

            chan_name = '/'.join([device, chan])

            device = replace_name(device, DEVICE_NAMES)

            newChannel = Channel(chan_name, device=device, meas_array=data)

            newChannel.setParent('proc01')

            newChannel.setStartTime(start_time)

            if 'Milli' not in chan:
                self.addChannel(newChannel)

        self.add_dISample()
        self.add_dVSample()
        self.add_dRSample()

    def _get_dat_column_names(self, filename):
        """Get the column names of a dat file.

        Assuming that the last commented line, i.e. a line that starts with
        '#', contains the header or names of the file, grab that list and
        return it.

        Parameters
        ----------
        filename : str
            The absolute path of the file to be loaded

        Returns
        -------
        datetimestamp : numpy.datetime64
            The starting date and time stamp of the file
        headerline : list
            The list of strings to use as the column headers

        """

        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile, skipinitialspace=True)
            dateline = next(reader, None)
            line = dateline
            while line[0][0] == '#':
                headerline = line
                line = next(reader, None)

        datetimestamp = np.datetime64('T'.join(dateline[0].split(' ')[-2:]))

        headerline[0] = headerline[0].lstrip('#').strip()

        return (datetimestamp, headerline)

    def _get_csv_column_names(self, filename):
        """Get the column names of a csv file produced by ADWin

        Assuming that the last commented line, i.e. a line that starts with
        '#', contains the header or names of the file, grab that list and
        return it.

        Parameters
        ----------
        filename : str
            The absolute path of the file to be loaded

        Returns
        -------
        headerline : list
            The list of strings to use as the column headers

        """

        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile, skipinitialspace=True)
            headerline = next(reader, None)

        headerline[0] = headerline[0].lstrip('#').strip()

        datetimestamp = np.datetime64(datetime.fromtimestamp(
            os.path.getmtime(filename)).isoformat())

        return (datetimestamp, headerline)

    def _loadFromTDMS(self, filename):
        """Load the data from a TDMS file into the channel registry

        Parameters
        ----------
        filename : str
            The absolute path of the file to be loaded

        """

        tdmsFileObject = TdmsFile(filename)

        try:
            self.file_start_time = np.datetime64(tdmsFileObject.object()
                                                 .properties['StartTime'])
            self.file_end_time = np.datetime64(tdmsFileObject.object()
                                               .properties['EndTime'])

        except KeyError:
            print('File {f} does not have StartTime or EndTime key.'
                  .format(f=filename))

        # Generate channels one device at a time
        for device in tdmsFileObject.groups():

            # The ADWin device properties will later need to be mapped to
            # specific channels
            deviceProperties = tdmsFileObject.object(device).properties

            # Get a list of the device's channels
            deviceChannels = tdmsFileObject.group_channels(device)
            device = replace_name(device, DEVICE_NAMES)

            # Setup a channel object for each channel.
            # Sort the ADWin device properites to the proper channels if
            # necessary.
            for chan in deviceChannels:
                channelName = chan.path.replace("'", "").lstrip("/")
                # Some channels are empty. This becomes apparent when trying
                # load the properties.
                # try:
                channelName = replace_name(channelName, DEVICE_NAMES)

                if 'wf_start_time' in chan.properties:
                    newChannel = Channel(channelName, device=device,
                                         meas_array=chan.data)
                    newChannel.setParent('proc01')

                    # startTime = np.datetime64(chan.property('wf_start_time')
                    #                           .astimezone(LOCAL_TZ))

                    newChannel.setStartTime(self.file_start_time)

                    # Sometimes the wf_increment is saved in seconds. Convert
                    # to milliseconds for easier use with numpy timedeltas.

                    timeStep = chan.property("wf_increment")
                    # if channelName == 'IPS/Magnetfield':
                    #     #print(timeStep)
                    #     new_dt = ((self.file_end_time - self.file_start_time)
                    #       / len(chan.data)) / np.timedelta64(1, 's')
                    #     timeStep = new_dt

                    if timeStep < 1:
                        timeStep = timeStep * 1000

                    if device == 'ADWin' and timeStep != 100:
                        # print('Old ADWin timeStep is {}'.format(timeStep))
                        timeStep = 100

                    newChannel.setTimeStep(np.timedelta64(int(timeStep), 'ms'))

                    if device == "ADWin":
                        try:
                            for attributeName in ADWIN_DICT[channelName
                                                            .lstrip('ADWin/')]:
                                # If LISens or LVSens is not present a key
                                # error is thrown here!  This is where to catch
                                # the missing data and allow the user to enter
                                # it.
                                newChannel.attributes[attributeName] = \
                                    deviceProperties[attributeName]
                        except KeyError:
                            # print('1\tKey Error: {0} on channel {1}'
                            #       .format(err, channelName))
                            pass

                    self.addChannel(newChannel)

                # except TypeError as err:
                #     print('3\tType Error: {0} on channel {1}'
                #          .format(err, channelName))
                #    pass

        # self.addTransportChannels()
        try:
            self.removeADWinTempOffset()
        except KeyError as err:
            print('KeyError when trying to remove ADWin temp offset')
            print(err)

    def add_V(self):
        """Add the processed channel 'V' derived from 'VSample'.

        """
        if 'proc01/VSample' in self.keys() and 'proc01/V' not in self.keys():
            chanVSample = self['proc01/VSample']
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
        if (('proc01/dVSample' in self.keys() and 'LVSens' in self['proc01/dVSample']
             .attributes.keys()) and ('proc01/dV' not in self.keys())):
            chandVSample = self['proc01/dVSample']
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
        if 'proc01/ISample' in self.keys() and 'proc01/I' not in self.keys():
            chanISample = self['proc01/ISample']
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
        if (('proc01/dISample' in self.keys() and 'LISens' in self['proc01/dISample']
             .attributes.keys()) and ('proc01/dI' not in self.keys())):
            chandISample = self['proc01/dISample']
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
        # R depends on V and I try and get the proc01 (calculated by ADWin) data
        # and fall back on the processed data
        if ('proc01/I' and 'proc01/V') in self.keys() and 'proc01/R' not in self.keys():
            chanI = self['proc01/I']
            chanV = self['proc01/V']
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
        # the proc01 data. Fall back to the processed data
        if (('proc01/ADWin/ISample' and 'proc01/ADWin/VSample') in self.keys() and
           (('proc01/ADWin/RSample'and 'proc01/ADWin/R') not in self.keys())):
            chanISample = self['proc01/ADWin/ISample']
            chanVSample = self['proc01/ADWin/VSample']
        elif ('proc/ISample' and 'proc/VSample') in self.keys():
            chanISample = self['proc/ISample']
            chanVSample = self['proc/VSample']
        else:
            return

        # Calculate the data
        rMeasArray = chanVSample.data/chanISample.data
        # Create the channel
        chanRSample = Channel('ADWin/RSample', device='ADWin', meas_array=rMeasArray)
        # Set the parent
        chanRSample.setParent('proc01')
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
        if (('proc01/ADWin/dISample' in self.keys()) and
            ('proc01/ADWin/dVSample' in self.keys()) and
            ('proc01/ADWin/dRSample' not in self.keys())):
            print('Condition 01 met')
            chandISample = self['proc01/ADWin/dISample']
            chandVSample = self['proc01/ADWin/dVSample']
        elif ('proc/dISample' and 'proc/dVSample') in self.keys():
            chandISample = self['proc/dISample']
            chandVSample = self['proc/dVSample']
        else:
            print('No conditions met')
            return

        # Calculate the data
        dRMeasArray = chandVSample.data/chandISample.data
        # Create the channel
        chandRSample = Channel('ADWin/dRSample', device='ADWin',
                               meas_array=dRMeasArray)
        # Set the parent
        chandRSample.setParent('proc01')
        # Set the start time and time interval based on dISample's values
        chandRSample.setStartTime(chandISample.getStartTime())
        chandRSample.setTimeStep(chandISample.getTimeStep())
        # Add the channel to the registry
        self.addChannel(chandRSample)

    def add_dISample(self):
        """Add the processed channel 'dRSample' derived from 'dVSample' and
        'dISample'

        """
        # dRSample depends on dISample and dVSample. Try to use the raw data.
        # Fall back on the processed data.
        print('Going to try to add dISample')

        if (('proc01/all/dISamplex' and 'proc01/all/dISampley') in self.keys()
            and
           ('proc01/all/dISample' not in self.keys())):
            chandISamplex = self['proc01/all/dISamplex']
            chandISampley = self['proc01/all/dISampley']
        else:
            print('Failed')
            return

        # Calculate the data
        dIMeasArray = np.sqrt(chandISamplex.data**2 + chandISampley.data**2)
        # Create the channel
        chandISample = Channel('all/dISample', device='all',
                               meas_array=dIMeasArray)

        # Set the parent
        chandISample.setParent('proc01')
        # Set the start time and time interval based on dISample's values
        chandISample.setStartTime(chandISamplex.getStartTime())
        chandISample.setTimeStep(chandISamplex.getTimeStep())
        # Add the channel to the registry
        self.addChannel(chandISample)

    def add_dVSample(self):
        """Add the processed channel 'dRSample' derived from 'dVSample' and
        'dVSample'

        """
        # dRSample depends on dISample and dVSample. Try to use the proc01 data.
        # Fall back on the processed data.
        print('Going to try to add dVSample')

        if (('proc01/all/dVSamplex' and 'proc01/all/dVSampley') in self.keys()
            and
           ('proc01/all/dVSample' not in self.keys())):
            chandVSamplex = self['proc01/all/dVSamplex']
            chandVSampley = self['proc01/all/dVSampley']
        else:
            print('Failed')
            return

        # Calculate the data
        dVMeasArray = np.sqrt(chandVSamplex.data**2 + chandVSampley.data**2)
        # Create the channel
        chandVSample = Channel('all/dVSample', device='all',
                               meas_array=dVMeasArray)

        # Set the parent
        chandVSample.setParent('proc01')
        # Set the start time and time interval based on dVSample's values
        chandVSample.setStartTime(chandVSamplex.getStartTime())
        chandVSample.setTimeStep(chandVSamplex.getTimeStep())
        # Add the channel to the registry
        self.addChannel(chandVSample)

    def add_dR(self):
        """Add the processed channel 'dR' derived from 'dV' and 'dI'

        """
        # dR depends on dI and dV. Try to get the proc01 data. Fall back on the
        # processed data.
        if (('proc01/dI' and 'proc01/dV') in self.keys() and
           ('proc01/dR' not in self.keys())):
            chandI = self['proc01/dI']
            chandV = self['proc01/dV']
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

    def addTimeTracks(self, device, time_track):
        """Add the time track for a device

        Parameters
        ----------
        device : str
            The name of the device for which the time track will be added.
        time_track : numpy.ndarray
            The time data

        """

        if not isinstance(device, str):
            raise TypeError('The device parameter must be a string.')

        if not isinstance(time_track, np.ndarray):
            raise TypeError('The time_track parameter must be a numpy array')

        newChan = Channel('{}/Time_m'.format(device), device, time_track)
        newChan.setParent('proc01')
        newChan.setStartTime(self.file_start_time)

        # channelKey = "{parent}/{cName}".format(parent=newChan.getParent(),
        #                                            cName=newChan.getName())

        self.addChannel(newChan)

    def addInterpolatedB(self):
        """Add the interpolated BField data to ADWin device.

        This assumes that the data from the IPS and ADWin devices are already
        loaded.

        """
        for key in ['proc01/IPS/Magnetfield', 'proc01/ADWin/Time_m']:
            if key not in self.keys():
                print('{k} data is not present. Cannot add B.'.format(k=key))
                return

        magnetfield_array = self['proc01/IPS/Magnetfield'].data
        adwin_time = self['proc01/ADWin/Time_m'].data
        ips_time = self['proc01/IPS/Time_m'].data
        b_ts = new_interpolate_bfield(magnetfield_array, ips_time, adwin_time)

        newChan = Channel('ADWin/B', 'ADWin', b_ts)
        newChan.setParent('proc01')
        newChan.setStartTime(self.file_start_time)

        # channelKey = "{parent}/{cName}".format(parent=newChan.getParent(),
        #                                            cName=newChan.getName())

        self.addChannel(newChan)

    def addTemperatureMode(self):
        """Add the mode of the temperature during the measurement to ADWin device.

        """

        t_mode = stats.mode(self['proc01/ADWin/TSample_AD'].data)[0][0]
        t_adjust = self['proc01/ADWin/TSample_AD'].data - t_mode

        newChan = Channel('ADWin/Tm', 'ADWin', t_adjust)
        newChan.setParent('proc01')

        # channelKey = "{parent}/{cName}".format(parent=newChan.getParent(),
        #                                            cName=newChan.getName())

        self.addChannel(newChan)

    def removeADWinTempOffset(self):
        """Remove the small offset in ADWin's recorded temperature."""
        print("Remove the offset on ADWin's temperature reading")

        if 'proc01/ADWin/TSample_AD' in self.keys():
            TADkey = 'proc01/ADWin/TSample_AD'
        elif 'proc01/ADWin/TSample' in self.keys():
            TADkey = 'proc01/ADWin/TSample'
        else:
            TADkey = None

        if 'proc01/Lakeshore/TSample_LK' in self.keys():
            TLKkey = 'proc01/Lakeshore/TSample_LK'
        elif 'proc01/Lakeshore/Temperature' in self.keys():
            TLKkey = 'proc01/Lakeshore/Temperature'
        else:
            TLKkey = None

        ad_mean = self[TADkey].data.mean()
        lk_mean = self[TLKkey].data.mean()

        offset = ad_mean - lk_mean
        print("The offset is: {0:.2f} - {1:.2f} = {2:.2f}".format(ad_mean*1000,
                                                                  lk_mean*1000,
                                                                  offset*1000))
        self[TADkey].data -= offset


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
        print(v.name)
        print(v.getTimeTrack())
        print(v.getElapsedTimeTrack())

if __name__ == "__main__":
    main()
