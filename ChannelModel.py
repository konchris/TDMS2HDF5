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

from nptdms.tdms import TdmsFile

ADWIN_DICT = {"ISample": ["IAmp"], "VSample": ["VAmp"],
              "dISample": ["IAmp", "LISens"], "dVSample": ["VAmp", "LVSens"],
              "xMagnet": [], "TCap": [], "zMagnet": [],
              "VRuO": ["r max", "r min"], "I": [], "V": [], "R": [], "dI": [],
             "dV": [], "dR": [], "Res_RuO": ["p0", "p1", "r0"], "Temp_RuO": []}


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
    parent : string
       The name of the parent group of the channel in the HDF5 file.
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
        self.attributes = {"Device": device,
                           "TimeInterval": 0,
                           "Length": len(meas_array),
                           "StartTime": datetime.now()}

        self.name = name
        self.data = meas_array
        self.time = np.array([])
        self.parent = 'raw'
        self.write_to_file = False

        self._recalculateTimeArray()

    def _recalculateTimeArray(self):
        """Recalculate the time track based on start time and time step"""
        dt = self.attributes['TimeInterval']
        length = self.attributes['Length']

        self.time = np.linspace(0, length*dt, length)

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
        newStartTime : datetime
            The new datetime at which the measurement started.

        """
        if isinstance(newStartTime, datetime):
            self.attributes['StartTime'] = newStartTime
        else:
            raise TypeError('The start time has to be of the datetime type')

    def getStartTime(self):
        """Returns the channel's measurement starting time in datetime format

        Returns
        -------
        StartTime : datetime
            The datetime at which the measurement started.

        """
        return self.attributes['StartTime']

    def setTimeStep(self, newDelTime):
        """Set the time between two measurement points.

        Parameters
        ----------
        newDelTime : int,float
            The new time interval between measurement points

        """
        if isinstance(newDelTime, (int, float)):
            self.attributes['TimeInterval'] = newDelTime
            self._recalculateTimeArray()
        else:
            message = 'The time interval can only be an integer or a float'
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

    """

    def __init__(self):
        super(ChannelRegistry, self).__init__()

        self.parents = []

    def addChannel(self, newChan):
        """Add a new, unique channel to the registry"""
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
            The name of the file to be loaded

        """
        self.clear()
        tdmsFileObject = TdmsFile(filename)

        # Generate channels one group at a time
        for group in tdmsFileObject.groups():

            # The ADWin group properties will later need to be mapped to
            # specific channels
            groupProperties = tdmsFileObject.object(group).properties

            groupChannels = tdmsFileObject.group_channels(group)

            for chan in groupChannels:
                channelName = chan.path.split('/')[-1].strip("'")
                # Some channels are empty. This becomes apparent when trying
                # load th properties
                try:

                    newChannel = Channel(channelName, device=group,
                                         meas_array=chan.data)
                    newChannel.setStartTime(chan.property('wf_start_time'))

                    # Sometimes the wf_increment is not saved in seconds, but in
                    # milliseconds

                    timeStep = chan.property("wf_increment")

                    if timeStep > 1:
                        timeStep = timeStep / 1000

                    newChannel.setTimeStep(timeStep)

                    if group == "ADWin":
                        for attributeName in ADWIN_DICT[channelName]:
                            try:
                                newChannel.attributes[attributeName] = \
                                  groupProperties[attributeName]
                            # If LISens or LVSens is not present a key error is
                            # thrown here!
                            # This is where to catch the missing data and allow
                            # the user to enter it.
                            except KeyError as err:
                                #print('Key Error: {0} on channel {1}'.format(err, channelName))
                                pass

                    self.addChannel(newChannel)

                except KeyError as err:
                    # print('Key Error: {0} on channel {1}'.format(err, channelName))
                    pass
                except TypeError as err:
                    # print('Type Error: {0} on channel {1}'.format(err, channelName))
                    pass

        self.addTransportChannels()

    def addV(self):
        if 'raw/VSample' in self.keys():
            # print('We can calculate V')
            chanVSample = self['raw/VSample']
        else:
            # print('We cannot caluculate V')
            return
        vMeasArray = (chanVSample.data / chanVSample.attributes['VAmp']) * 1E3
        chanV = Channel('V', meas_array=vMeasArray)
        chanV.setParent('proc')
        chanV.setStartTime(chanVSample.getStartTime())
        chanV.setTimeStep(chanVSample.getTimeStep())
        self.addChannel(chanV)

    def adddV(self):
        if 'raw/dVSample' in self.keys() and \
          'LVSens' in self['raw/dVSample'].attributes.keys():
            # print('We can calculate dV')
            chandVSample = self['raw/dVSample']
        else:
            # print('We cannot caluculate dV')
            return
        dVMeasArray = ((chandVSample.data / chandVSample.attributes['VAmp']) /
                       10) * chandVSample.attributes['LVSens'] * 1E3
        chandV = Channel('dV', meas_array=dVMeasArray)
        chandV.setParent('proc')
        chandV.setStartTime(chandVSample.getStartTime())
        chandV.setTimeStep(chandVSample.getTimeStep())
        self.addChannel(chandV)

    def addI(self):
        if 'raw/ISample' in self.keys():
            # print('We can calculate I')
            chanISample = self['raw/ISample']
        else:
            # print('We cannot caluculate I')
            return
        iMeasArray = (chanISample.data / chanISample.attributes['IAmp']) * 1E6
        chanI = Channel('I', meas_array=iMeasArray)
        chanI.setParent('proc')
        chanI.setStartTime(chanISample.getStartTime())
        chanI.setTimeStep(chanISample.getTimeStep())
        self.addChannel(chanI)

    def adddI(self):
        if 'raw/dISample' in self.keys() and \
          'LISens' in self['raw/dISample'].attributes.keys():
            # print('We can calculate dI')
            chandISample = self['raw/dISample']
        else:
            # print('We cannot caluculate dI')
            return
        dIMeasArray = ((chandISample.data / chandISample.attributes['IAmp']) /
                       10) * chandISample.attributes['LISens'] * 1E6
        chandI = Channel('dI', meas_array=dIMeasArray)
        chandI.setParent('proc')
        chandI.setStartTime(chandISample.getStartTime())
        chandI.setTimeStep(chandISample.getTimeStep())
        self.addChannel(chandI)

    def addR(self):
        if ('raw/I' and 'raw/V') in self.keys():
            # print('We can calculate R')
            chanI = self['raw/I']
            chanV = self['raw/V']
        elif ('proc/I' and 'proc/V') in self.keys():
            # print('We can calculate R')
            chanI = self['proc/I']
            chanV = self['proc/V']
        else:
            # print('We cannot caluculate R')
            return
        rMeasArray = chanV.data/chanI.data
        chanR = Channel('R', meas_array=rMeasArray)
        chanR.setParent('proc')
        chanR.setStartTime(chanI.getStartTime())
        chanR.setTimeStep(chanI.getTimeStep())
        self.addChannel(chanR)

    def addRSample(self):
        if ('raw/ISample' and 'raw/VSample') in self.keys():
            # print('We can calculate RSample')
            chanISample = self['raw/ISample']
            chanVSample = self['raw/VSample']
        elif ('proc/ISample' and 'proc/VSample') in self.keys():
            # print('We can calculate RSample')
            chanISample = self['proc/ISample']
            chanVSample = self['proc/VSample']
        else:
            # print('We cannot calculate RSample')
            return
        rMeasArray = chanVSample.data/chanISample.data
        chanRSample = Channel('RSample', meas_array=rMeasArray)
        chanRSample.setParent('proc')
        chanRSample.setStartTime(chanISample.getStartTime())
        chanRSample.setTimeStep(chanISample.getTimeStep())
        self.addChannel(chanRSample)

    def adddRSample(self):
        if ('raw/dISample' and 'raw/dVSample') in self.keys():
            # print('We can calculate dRSample')
            chandISample = self['raw/dISample']
            chandVSample = self['raw/dVSample']
        elif ('proc/dISample' and 'proc/dVSample') in self.keys():
            # print('We can calculate dRSample')
            chandISample = self['proc/dISample']
            chandVSample = self['proc/dVSample']
        else:
            # print('We cannot calculate dRSample')
            return
        dRMeasArray = chandVSample.data/chandISample.data
        chandRSample = Channel('dRSample', meas_array=dRMeasArray)
        chandRSample.setParent('proc')
        chandRSample.setStartTime(chandISample.getStartTime())
        chandRSample.setTimeStep(chandISample.getTimeStep())
        self.addChannel(chandRSample)

    def adddR(self):
        if ('raw/dI' and 'raw/dV') in self.keys():
            # print('We can calculate dR')
            chandI = self['raw/dI']
            chandV = self['raw/dV']
        elif ('proc/dI' and 'proc/dV') in self.keys():
            # print('We can calculate dR')
            chandI = self['proc/dI']
            chandV = self['proc/dV']
        else:
            # print('We cannot caluculate dR')
            return
        dRMeasArray = chandV.data/chandI.data
        chandR = Channel('dR', meas_array=dRMeasArray)
        chandR.setParent('proc')
        chandR.setStartTime(chandI.getStartTime())
        chandR.setTimeStep(chandI.getTimeStep())
        self.addChannel(chandR)

    def addTransportChannels(self):
        self.addV()
        self.adddV()
        self.addI()
        self.adddI()
        self.addRSample()
        self.adddRSample()
        self.addR()
        self.adddR()


def main(argv=None):

    if argv is None:
        argv = sys.argv

    testfile01 = "/home/chris/Documents/PhD/root/raw-data/sio2al149/CryoMeasurement/2014-02-14T14-39-08-First-Cooldown.tdms"
    testfile02 = "/home/chris/Espy/MeasData/HelioxTesting/2014-04-09T10-48-33-Cool-Down.tdms"

    chanReg = ChannelRegistry()
    chanReg.loadFromFile(testfile01)

    for k, v in chanReg.items():
        print(k)
        print(v.name, v.attributes)


if __name__ == "__main__":
    main()
