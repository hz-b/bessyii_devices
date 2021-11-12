from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device, DerivedSignal
from ophyd import Component as Cpt


class Ring(Device):
    
    """
    Object to query machine BESSY II Beam status.

    """
        
    current  = Cpt(EpicsSignalRO,      'current',   kind="hinted", labels={"detectors"})
    lifetime = Cpt(EpicsSignalRO,      'lt10',      kind="hinted"                      )
