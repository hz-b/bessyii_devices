from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device, DerivedSignal
from ophyd import Component as Cpt


class Ring(Device):
    
    """
    Object to query machine BESSY II Beam status.

    """
        
    current  = Cpt(EpicsSignalRO,      'current',   kind="hinted", labels={"detectors"})
    lifetime = Cpt(EpicsSignalRO,      'lt10',      kind="hinted"                      )
    

class Topup(Device):
    
    """
    Object to query machine BESSY II topup status (TOPUPCC:)
    http://elog-v2.trs.bessy.de:8080/Machine+Devel.,+Comm./1770
    
    blankout is asserted when there is an injection
    """
    
    countdown = Cpt(EpicsSignalRO,     'estCntDwnS',   kind="hinted")
    blankout = Cpt(EpicsSignalRO,      'stBlankout2', kind="hinted")
