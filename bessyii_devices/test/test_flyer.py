import pytest
import sys
sys.path.append('/home/will/.ipython/profile_test/startup/beamlineOphydDevices/')
from flyer import BasicFlyer, MyMotor, MyDetector
from ophyd import status, DeviceStatus, Signal
from ophyd.status import wait
fdev = MyMotor('EMILEL:TestIOC00:', name='fdev')
fdev.wait_for_connection()

fdev.start_pos.put(0.5)
fdev.end_pos.put(1.0)
fdev.velocity.put(0.2)

def kickoff(flyer):
    st = flyer.kickoff()
    wait(st, timeout=2)
    return st.done

def complete(flyer):
    st = flyer.complete()
    wait(st)
    return st.done

def describe_collect_type_check(flyer):
    return isinstance(fdev.describe_collect(), dict)

def describe_collect_name_check(flyer):
    return flyer.name in flyer.describe_collect()


def describe_collect_structure_check(flyer):
    structure = flyer.describe_collect()[fdev.name]
    return (fdev.name + '_' + fdev.read_attrs[0]) in structure

    


import types
def collect_type_check(flyer):
    return isinstance(fdev.collect(), types.GeneratorType)

def collect_structure_list_check(flyer):
    return isinstance(list(fdev.collect()), list)

def collect_structure_check(flyer):
    result = True
    for entry in list(fdev.collect()):
        result = result and len(entry) == 3 and 'time' in entry and 'data' in entry and 'timestamps' in entry

    return result


## Define Tests

def test_connected():
    assert fdev.connected == True

def test_kickoff():
    assert kickoff(fdev) == True

def test_complete():
    assert kickoff(fdev) == True

def test_describe_collect_type():
    assert describe_collect_type_check(fdev) == True

def test_describe_collect_name():
    assert describe_collect_name_check(fdev) == True

def test_describe_collect_structure():
    assert describe_collect_structure_check(fdev) == True

def test_collect_type():
    assert collect_type_check(fdev) == True

def test_collect_list():
    assert collect_structure_list_check(fdev) == True

def test_collect_structure():
    assert collect_structure_check(fdev) == True
    
"""
verify that describe_collect() returns a dictionary

d = flyer.describe_collect() d

verify that collect() returns a generator

g = flyer.collect() g

verify that generator is a list of data dictionaries

list(g)
"""

