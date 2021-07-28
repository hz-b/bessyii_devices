from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device
from ophyd import Component as Cpt
from .axes import AxisTypeB


class DiamondFilter(Device):

    read_attrs=['h.readback', 'v.readback']
    
    h = Cpt(AxisTypeB,      'PH_1', labels={"motors"})
    v = Cpt(AxisTypeB,      'PH_2', labels={"motors"})
    
