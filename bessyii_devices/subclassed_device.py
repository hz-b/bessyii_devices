from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device, DerivedSignal,PseudoPositioner,PseudoSingle,EpicsMotor
from ophyd import Component as Cpt
from .positioners import *
from ophyd import FormattedComponent as FCpt
from ophyd.pseudopos import (pseudo_position_argument,
                             real_position_argument)
from ophyd.signal import Signal, SignalRO


## Explore creating a device from other devices

class Axis(PVPositionerComparator):

    setpoint = FCpt(EpicsSignal,'{self.prefix}set{self._ch_name}') # component is itself a class
    readback = FCpt(EpicsSignal,'{self.prefix}get{self._ch_name}')
            
    atol = 0.001  # tolerance before we set done to be 1

    def done_comparator(self, readback, setpoint):
        return setpoint-self.atol < readback < setpoint+self.atol
        
        
    def __init__(self, prefix, ch_name=None, **kwargs):
        self._ch_name = ch_name
        super().__init__(prefix, **kwargs)
    
class Robot(Device):

    axis_1 = Cpt(Axis, 'axis1:',ch_name='Pos')
    axis_2 = Cpt(Axis, 'axis2:',ch_name='Pos')
    axis_3 = Cpt(Axis, 'axis3:')
