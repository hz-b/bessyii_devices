from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device
from ophyd import Component as Cpt
from .axes import AxisTypeB, AxisTypeFoil


class DiamondFilterSub(Device):

    

    motor  = Cpt(AxisTypeB,'', labels={"motors"})
    choice = Cpt(AxisTypeBChoice,'', labels={"motors"})


    
class DiamondFilter(Device):
    h = Cpt(DiamondFilterSub,     'PH_1') 
    v = Cpt(DiamondFilterSub,     'PH_2')
    
    
    
# old until 071121
"""
class DiamondFilter(Device):

    read_attrs=['h.readback', 'v.readback']
    
    h = Cpt(AxisTypeB,      'PH_1', labels={"motors"})
    v = Cpt(AxisTypeB,      'PH_2', labels={"motors"})
    
"""
