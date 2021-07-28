from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FCpt
from .axes import AxisTypeA 

#prefix list U17
# PHY01U012L:

class Pinhole(Device):
    
    h = Cpt(AxisTypeA, '', ch_name='H')
    v = Cpt(AxisTypeA, '', ch_name='V')
