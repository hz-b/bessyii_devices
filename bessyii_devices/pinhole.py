from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FCpt
from .axes import AxisTypeA, AxisTypeD 


class Pinhole(Device):
    
    h = Cpt(AxisTypeA, '', ch_name='H')
    v = Cpt(AxisTypeA, '', ch_name='V')


class Pinhole2(Device):
    
    h = Cpt(AxisTypeD, 'Hor')
    v = Cpt(AxisTypeD, 'Vert')
    
    
class PinholeMetrixs(Device):
        
    h = Cpt(AxisTypeD, 'PHHORES6L')  # horizontal
    v = Cpt(AxisTypeD, 'PHVERES6L')  # vertical


class PinholeUE52SGM(Device):
        
    h = Cpt(AxisTypeD, '2')  # horizontal
    v = Cpt(AxisTypeD, '3')  # vertical


# Note: Shall we add labels here? Then it is easier to read/find the devices using magics