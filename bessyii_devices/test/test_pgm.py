#test for oease end station
import pytest
import bessyii_devices
from bessyii_devices.pgm import *

# Monochromators
u17_pgm = PGMHard('u171pgm1:', name='u17_pgm',read_attrs=['en.readback']) # old
ue48_pgm = PGMSoft('ue481pgm1:', name='ue48_pgm',read_attrs=['en.readback'])
u49_2_pgm = PGM_Aquarius('pgm2os15l:', name='pgm',read_attrs=['en.readback'])

ue48_pgm.wait_for_connection()
u17_pgm.wait_for_connection()
#u49_2_pgm.wait_for_connection()


#### Check the structure of the devices ####

# Is there an attribute called en? and is it a pv positioner
def check_en_struct(device):
    if hasattr(device,'en') :
        return isinstance(device.en,PVPositioner)
    else:
        return False   
    
# Check that the en attribute get() method returns an integer and not a tuple
def check_en_get(device):

    return isinstance(device.en.get(),float)

#check that the positioner readback name is the same as the name of the positioner

def check_positioner_readback_struct(axis):
    
    return axis.name == axis.readback.name


#### Check that the axis can move
def check_moves(axis):
    
    #stage the device
    axis.stage()
    
    current_pos = axis.readback.get()
    
    mov_status = axis.move(current_pos+0.1(), wait=True, timeout=10.0)
    
    #Move it back
    axis.move(current_pos, wait=True)
    
    #unstage the device
    axis.unstage()
    
    return mov_status.done and mov_status.sucess

#### Perform the tests #####
def test_connection_ue48_pgm():
    assert ue48_pgm.connected == True

   
   
@pytest.mark.skip()
def test_connection_u17_pgm():
    assert u17_pgm.connected == True

@pytest.mark.skip()   
def test_connection_u49_2_pgm():
    assert u49_2_pgm.connected == True

def test_en_exists_ue48_pgm():
    
    assert check_en_struct(ue48_pgm) == True

def test_en_get_ue48_pgm():
    
    assert check_en_get(ue48_pgm) == True
    
@pytest.mark.skip()
def test_en_exists_u17_pgm():
    
    assert check_en_struct(u17_pgm) == True

@pytest.mark.skip()
def test_en_get_u17_pgm():
    
    assert check_en_get(u17_pgm) == True

@pytest.mark.skip()
def test_en_exists_u49_2_pgm():
    
    assert check_en_struct(u49_2_pgm) == True

@pytest.mark.skip()
def test_en_get_u49_2_pgm():
    
    assert check_en_get(u49_2_pgm) == True
    
def test_en_readback_struct():
    
    assert check_positioner_readback_struct(ue48_pgm.en) == True

def test_grating_readback_struct():
    
    assert check_positioner_readback_struct(ue48_pgm.grating_translation) == True
    
def test_m2_readback_struct():
    
    assert check_positioner_readback_struct(ue48_pgm.m2_translation) == True

def test_ue48_pgm_struct():

    assert isinstance(ue48_pgm,Device) == True
    assert hasattr(ue48_pgm,"restore") == True
    assert isinstance(ue48_pgm.en,PositionerBase) == True
    assert isinstance(ue48_pgm.grating_translation,PositionerBase) == True
    assert isinstance(ue48_pgm.slit,PositionerBase) == True

def test_sim_mono_restore():

    #start a resotore
    initial_positions = {ue48_pgm.slit.setpoint.name : ue48_pgm.slit.setpoint.get(),ue48_pgm.en.setpoint.name : ue48_pgm.en.setpoint.get(),ue48_pgm.grating_translation.setpoint.name : ue48_pgm.grating_translation.setpoint.get()}

    restore_dict = {sim_mono.slit.setpoint.name : 1,sim_mono.en.setpoint.name : 2,sim_mono.grating_translation.setpoint.name: 2}

    status = sim_mono.restore(restore_dict)
    status.wait()
    assert status.success == True

def test_sim_mono_restore_stops():

    #start a resotore
    sim_mono.en.settle_time = 0.1
    sim_mono.slit.settle_time = 0.1
    sim_mono.grating_translation.settle_time = 2

    restore_dict = {sim_mono.slit.setpoint.name : 1,sim_mono.en.setpoint.name : 2,sim_mono.grating_translation.setpoint.name: 2}

    status = sim_mono.restore(restore_dict)
    time.sleep(1)

    sim_mono.stop()

    assert status.success == False

    