import pytest

from bessyii_devices.sim import SimPositionerDone, SimStage, SimStageOfStage, Pseudo3x3, SynGaussMonitorInteger, sim_motor, noisy_det_monitor, sim_hex, sim_smu
from ophyd import PVPositioner, PseudoPositioner

#### Check the structure of the devices ####


#### Check that the axis can move
def check_moves(axis):
    
    #stage the device
    axis.stage()
    
    if isinstance(axis, PseudoPositioner):

        current_pos = axis.position


        mov_status = axis.move([pos+1 for pos in axis.position], wait=True, timeout=10.0)

        axis.move(current_pos, wait=True)


    else:
        current_pos = axis.readback.get()
        

        mov_status = axis.move(current_pos+0.1, wait=True, timeout=10.0)
        
        #Move it back
        axis.move(current_pos, wait=True)
    
    #unstage the device
    axis.unstage()
    
    return mov_status.done and mov_status.success

## Perform the tests

def test_sim_motor_struct():
    
    assert isinstance(sim_motor,PVPositioner) == True
    assert hasattr(sim_motor,"restore") == True
    assert sim_motor.name == sim_motor.readback.name
    
def test_sim_motor_moves():
    
    assert check_moves(sim_motor) == True

def test_sim_hex_struct():
    
    assert isinstance(sim_hex,PseudoPositioner) == True
    assert hasattr(sim_hex,"restore") == True
    
    
def test_sim_hex_moves():
    
    assert check_moves(sim_hex) == True

def test_sim_smu_struct():
    
    assert isinstance(sim_smu,PseudoPositioner) == True
    assert hasattr(sim_smu,"restore") == True
    assert hasattr(sim_smu,"choice") == True
    assert isinstance(sim_smu.choice,PVPositioner) == True
    assert hasattr(sim_smu.choice,"restore") == True
    assert sim_smu.choice.name == sim_smu.choice.readback.name
   
def test_sim_smu_moves():
    
    assert check_moves(sim_smu.choice) == True
    assert check_moves(sim_smu) == True
