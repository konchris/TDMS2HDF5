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
        tdmsFileObject = TdmsFile(filename)

        # Generate channels one group at a time
        for group in tdmsFileObject.groups():

            # The ADWin group properties will later need to be mapped to
            # specific channels
            groupProperties = tdmsFileObject.object(group).properties

            groupChannels = tdmsFileObject.group_channels(group)

            for chan in groupChannels:
                # Some channels are empty. This becomes apparent when trying
                # load th properties
                try:
                    channelName = chan.path.split('/')[-1].strip("'")

                    newChannel = Channel(channelName, device=group,
                                         meas_array=chan.data)
                    newChannel.setStartTime(chan.property('wf_start_time'))
                    newChannel.setTimeStep(chan.property("wf_increment"))

                    if group == "ADWin":
                        for attributeName in ADWIN_DICT[channelName]:
                            try:
                                newChannel.attributes[attributeName] = \
                                  groupProperties[attributeName]
                            except KeyError as err:
                                print('Key Error: {0}'.format(err))

                    self.addChannel(newChannel)

                except KeyError:
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
