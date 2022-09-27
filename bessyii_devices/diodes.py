
from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device, EpicsMotor
from ophyd.signal import Signal, SignalRO
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FCpt
from ophyd import Kind


class DiodeEMIL(EpicsMotor):

    """
    A device which exposes the motor as well as the saved positioners
    """
    
    select = Cpt(EpicsSignal, ":MOVETO", string=True, kind = "normal")
