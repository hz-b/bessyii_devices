import pytest
import sys
import bessyii_devices
from bessyii_devices.flyer import  BiologicPotentiostat
from bessyii.plans.flying import flycount

from databroker.v2 import temp


from bluesky.plans import count, fly
from bluesky.callbacks.best_effort import BestEffortCallback
import bluesky.preprocessors as bpp
import bluesky.plan_stubs as bps
from databroker import Broker
from event_model import RunRouter
from bluesky import RunEngine

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

from ophyd.sim import noisy_det,det
sd.baseline = [noisy_det]



data_dir = "Data/"

biologic = BiologicPotentiostat("SISSY2EX:BIOLOGIC:", name="biologic",sim_delay=1, data_dir=data_dir)
biologic.wait_for_connection()

flyer = biologic

def describe_collect_type_check(flyer):
    return isinstance(flyer.describe_collect(), dict)




    

## Define Tests

def test_connected():
    assert flyer.connected == True


def test_describe_collect_type():
    assert describe_collect_type_check(flyer) == True


def test_in_plan():

    RE(fly([biologic]))

    run = db[-1]

    run.biologic_CV_02.read()
    run.biologic_CA_03.read()
    run.biologic_OCV_04.read()





