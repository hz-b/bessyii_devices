#test for oease end station
import pytest
import bessyii_devices
from bessyii_devices.valve import PositionerBessyValve
from ophyd import PVPositioner
import time


# Connect to soft Valve 11 at EMIL
v11= PositionerBessyValve('V11V02U112L:', name = 'v11')
v11.wait_for_connection() 


#### Check the structure of the classes #########

#Check that the device is a PV positioner
def is_pvpositioner(device):

    return isinstance(device,PVPositioner) == True



#check that the positioner readback name is the same as the name of the positioner

def check_positioner_readback_struct(device):
    
    return device.name == device.readback.name


#### Check that the positioners work as expected given their exec commands

def check_moves(valve):
    
    #stage the device
    valve.stage()
    
    current_pos = valve.readback.get()
    
    mov_status = valve.move(not(current_pos), wait=True, timeout=10.0)
    time.sleep(1)

    
    #Move it back
    mov_status = valve.move(current_pos, wait=True)
    time.sleep(1)
    
   
    #unstage the device
    valve.unstage()
    
    return mov_status.done and mov_status.success

def check_non_moves(valve):
    
    #stage the device
    valve.stage()
    
    current_pos = valve.readback.get()
    current_status = valve.status.get()
    
    #attempt to move to the same position
    mov_status = valve.move(current_pos, wait=True, timeout=10.0)
    
    new_status = valve.status.get()

       
    #unstage the device
    valve.unstage()
    
    return mov_status.done and mov_status.success and current_status == new_status

#### Perform the tests ####
def test_connection_v11():
    assert v11.connected == True

def test_v11_positioner():
    
    assert is_pvpositioner(v11) == True
    
def test_v11_readback_name():
    
    assert check_positioner_readback_struct(v11) == True

def test_v11_moves():
    
    assert check_moves(v11) == True

def test_v11_doesnt_move():
    
    assert check_non_moves(v11) == True
