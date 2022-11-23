
from ophyd import EpicsSignal
from ophyd.signal import Signal, SignalRO
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FCpt
from ophyd import Kind
from bessyii_devices.epics_motor import EpicsMotorBessy as EpicsMotor



class DiodeEMIL(EpicsMotor):

    """
    A device which exposes the motor as well as the saved positioners
    """
    
    select = Cpt(EpicsSignal, ":MOVETO", string=True, kind = "normal")
