from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device
from ophyd import Component as Cpt
from .axes import AxisTypeB, AxisTypeFoil


class DiamondFilterSub(Device):

    read_attrs=['h.move.readback', 'v.move.readback']
    
    move           = Cpt(AxisTypeFoil,     '', ch_name = '', labels={"motors"})
    # we need to create a "lock" that makes it impossible use setpoint when choice_diamand is called 
    choice_diamand = Cpt(AxisTypeFoil,     '', ch_name = 'N', labels={"motors"})


    
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
