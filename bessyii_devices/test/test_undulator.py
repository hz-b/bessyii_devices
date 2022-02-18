#test for oease end station
import pytest
import bessyii_devices
from bessyii_devices.undulator import UndulatorGap, UndulatorShift, UndulatorBase, HelicalUndulator

ue48 = HelicalUndulator('UE48IT6R:', name='ue48') 
ue48.wait_for_connection()

u17   = UndulatorBase('U17IT6R:', name='u17')
u17.wait_for_connection()




#### Check the structure of the classes #########

#Check that the Gap and Shift devices are PV positioners
def is_pvpositioner(device):

    return isinstance(device,PVPositioner) == True

#Check that the UndulatorBase contains UndulatorGap 
def check_base_struct(device):
    if hasattr(device,'gap') and not hasattr(device,'shift'):
        return isinstance(device.gap,UndulatorGap)
    else:
        return False

#Check that the device has gap and shift and is based on UndulatorBase contains UndulatorGap 
def check_helical_struct(device):
    if hasattr(device,'gap') and hasattr(device,'shift'):
        return isinstance(device,UndulatorBase)
    else:
        return False   

#check that the positioner readback name is the same as the name of the positioner

def check_positioner_readback_struct(axis):
    
    return axis.name == axis.readback.name


#### Check that the positioners work as expected given their exec commands

def check_moves(axis):
    
    #stage the device
    axis.stage()
    
    current_pos = axis.readback.get()
    
    mov_status = axis.move(current_pos+axis.delta.get(), wait=True, timeout=10.0)
    
    #Move it back
    axis.move(current_pos, wait=True)
    
    #unstage the device
    axis.unstage()
    
    return mov_status.done and mov_status.sucess



#### Perform the tests ####
def test_connection_ue48():
    assert ue48.connected == True
    
def test_connection_u17():
    assert u17.connected == True
    
def test_u17_gap_positioner():
    
    assert is_pvpositioner(u17.gap) == True

def test_ue48_gap_positioner():
    
    assert is_pvpositioner(u17.gap) == True
    
def test_ue48_shift_positioner():
    
    assert is_pvpositioner(u17.shift) == True
    
def test_u17_struct():
    
    assert check_base_struct(u17) == True
    
def test_ue48_struct():
    
    assert check_helical_struct(ue48) == True

def test_gap_readback_name():
    
    assert check_positioner_readback_struct(ue48.gap) == True
    
def test_shift_readback_name():
    
    assert check_positioner_readback_struct(ue48.shift) == True

def test_u17_gap_moves():
    
    assert check_moves(u17.gap) == True
    
def test_ue48_gap_moves():
    
    assert check_moves(ue48.gap) == True

def test_ue48_shift_moves():
    
    assert check_moves(ue48.shift) == True
    
    
