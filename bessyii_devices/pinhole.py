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
