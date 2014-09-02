#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Test the model

"""

__author__ = "Christopher Espy"
__copyright__ = "Copyright (C) 2014, Christopher Espy"
__credits__ = ["Christopher Espy"]
__license__ = "GPL"
__version__ = "0.5"
__maintainer__ = "Christopher Espy"
__email__ = "christopher.espy@uni-konstanz.de"
__status__ = "Development"

import unittest
from datetime import datetime

import numpy as np

from model import Channel, ChannelRegistry

class TestChannel(unittest.TestCase):
    """Tests the channel object used by the model."""

    def setUp(self):
        self.channel = Channel('TestChannel01', device='Virtual',
                               meas_array=np.random.random(100))

    def test_channel_has_string_name(self):
        self.assertIsInstance(self.channel.name, str)

    def test_channel_has_parent_group(self):
        self.assertEqual(self.channel.parent, 'raw', 'Parent group is not raw')

    def test_set_get_parent_group(self):
        current_parent = self.channel.getParent()
        self.channel.setParent('proc')
        self.assertNotEqual(self.channel.getParent(), current_parent, 'Parent group is unchanged')

    def test_set_get_name(self):
        current_name = self.channel.getName()
        self.channel.setName('TestChannel02')
        self.assertNotEqual(self.channel.getName(), current_name, 'Name is unchanged')

    def test_set_get_starttime_now(self):
        now = datetime.now()
        self.channel.setStartTime(now)
        self.assertEqual(self.channel.getStartTime(), now)

    def test_set_get_dt_changes_timetrack(self):
        current_time_track = self.channel.getTimeTrack()
        current_dt = self.channel.getTimeStep()
        self.channel.setTimeStep(current_dt + 1)
        self.assertFalse(np.array_equal(self.channel.getTimeTrack(),
                                        current_time_track))

    def test_toggle_write_to_file(self):
        current_write_state = self.channel.write_to_file
        self.channel.toggleWrite()
        self.assertNotEqual(self.channel.write_to_file, current_write_state)

class TestChannelRegistry(unittest.TestCase):

    def setUp(self):
        self.channel_registry = ChannelRegistry()
        self.test_channel = Channel('TestChannel1', device='Virtual',
                                    meas_array=np.random.random(100))

    def test_add_channel(self):
        self.channel_registry.addChannel(self.test_channel)
        for k, v in self.channel_registry.items():
            self.assertIsInstance(k, str)
            self.assertIsInstance(v, Channel)

    def test_load_from_channel(self):
        self.channel_registry.loadFromFile("/home/chris/Espy/MeasData/HelioxTesting/2014-04-09T10-48-33-Cool-Down.tdms")
        for k, v in self.channel_registry.items():
            self.assertIsInstance(k, str)
            self.assertIsInstance(v, Channel)

if __name__ == "__main__":
    unittest.main()
