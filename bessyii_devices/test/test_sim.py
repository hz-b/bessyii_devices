import pytest
from bessyii_devices.sim import SimPositionerDone, SimStage, SimStageOfStage, Pseudo3x3, SynGaussMonitorInteger, sim_motor, noisy_det_monitor
from ophyd import PVPositioner

#### Check the structure of the devices ####


#### Check that the axis can move
def check_moves(axis):
    
    #stage the device
    axis.stage()
    
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
    assert sim_motor.name == sim_motor.readback.name
    
def test_sim_motor_moves():
    
    assert check_moves(sim_motor) == True
