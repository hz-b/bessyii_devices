from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device, DerivedSignal
from ophyd import Component as Cpt


class Ring(Device):
    
    """
    Object to query machine BESSY II Beam status.

    """
        
    current  = Cpt(EpicsSignalRO,      'current',   kind="hinted", labels={"detectors"})
    lifetime = Cpt(EpicsSignalRO,      'lt10',      kind="hinted"                      )
    
class BPM(Device):
    
    """
    Object to query machine BPM Status

    """

    x = Cpt(EpicsSignalRO,      'rdX',   kind="hinted", labels={"detectors"})
    y = Cpt(EpicsSignalRO,      'rdY',   kind="hinted", labels={"detectors"})
 
    
class Topup(Device):
    
    """
    Object to query machine BESSY II topup status (TOPUPCC:)
    http://elog-v2.trs.bessy.de:8080/Machine+Devel.,+Comm./1770
    
    blankout is asserted when there is an injection
    """
    
    countdown = Cpt(EpicsSignalRO,     'estCntDwnS',   kind="hinted")
    blankout = Cpt(EpicsSignalRO,      'stBlankout2', kind="hinted")
