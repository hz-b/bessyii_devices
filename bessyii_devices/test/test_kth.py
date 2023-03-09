#test for kth 6514 adn 6517B
import pytest
import bessyii_devices
from bessyii_devices.keithley import Keithley6514, Keithley6517

from databroker.v2 import temp
from bluesky.plans import count
from bluesky import RunEngine
from event_model import RunRouter

from bluesky.callbacks.best_effort import BestEffortCallback


RE = RunEngine({})
db = temp()
RE.subscribe(db.v1.insert)


def factory(name, doc):
    # Documents from each run is routed to an independent
    #   instance of BestEffortCallback
    bec = BestEffortCallback()
    return [bec], []

rr = RunRouter([factory])
RE.subscribe(rr)


from bluesky.preprocessors import SupplementalData
sd = SupplementalData()
RE.preprocessors.append(sd)

# connect to some real devices:

kth6517 = Keithley6517("SISSY2EX:Keithley02:", name = "kth6517")
kth6514 = Keithley6514("SISSY2EX:Keithley00:", name = "kth6514")

kth6514.wait_for_connection()
kth6517.wait_for_connection()

# define some tests

def check_staging(kth):

    """
    Check that when staging the device is correctly configured
    
    """
    kth.stage()

    assert kth.scan.get() == "Passive"
    assert kth.arm_src.get() == "Immediate"
    assert kth.trig_src.get() == "Immediate"
    assert kth.mdel.get() == -1
    assert kth.func.get() == "Current"

  

    kth.unstage()

    assert kth.scan.get() == ".1 second"


    if isinstance(kth, Keithley6517):
        assert kth.trig_mode.get() == "Continuous"

def check_triggering(kth):

    """
    Check that in passive mode triggering yields a new value with a different timestamp
    """

    name = kth.name
    val = kth.read()

    #Stage the device
    kth.stage()
    initial_val = val
    status = kth.trigger()

    status.wait()

    val = kth.read()
    new_val = val
    kth.unstage()

    init_time = initial_val[name]['timestamp']
    new_time = new_val[name]['timestamp']

    return new_time > init_time

def test_kth6517B_staging():

    check_staging(kth6517)

def test_kth6514_staging():

    check_staging(kth6514)

def test_kth_6517B_triggering():

    check_triggering(kth6517)

def test_kth_6514_triggering():

    check_triggering(kth6514)


