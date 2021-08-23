#test for oease end station
import pytest
import bessyii_devices
from bessyii_devices.keithley import Keithley6514
from bessyii_devices.end_stations import OAESE

#instantiate device
oaese = OAESE('SISSY2EX:', name='oaese')
oaese.wait_for_connection()


def test_connection():
    assert oaese.connected == True
