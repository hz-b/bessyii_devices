from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO
from ophyd import Component as Cpt
#from ophyd import FormattedComponent as FCpt
from .positioners import PVPositionerDone

# This class can be used for the photon shutter 

# prefix list U17
# PSHY01U012L:


class PhotonShutter(PVPositionerDone):
    setpoint    = Cpt(EpicsSignal, 'SetTa', string='True') 
    readback    = Cpt(EpicsSignalRO, 'State1', string='True',kind='hinted') 
