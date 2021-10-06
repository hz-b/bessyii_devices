from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO
from ophyd import Component as Cpt
from .positioners import PVPositionerDone

# This class can be used for the valves 

# prefix list U17
# V03V01U012L:


class Valve(PVPositionerDone):
    setpoint    = Cpt(EpicsSignal, 'SetTa', string='True') 
    readback    = Cpt(EpicsSignalRO, 'State1', string='True', kind='hinted', labels={"motors","valves"}) 
    #done       = Cpt(EpicsSignalRO, '_REF_STAT' )  # where to find?
    
    done_value = 0 

