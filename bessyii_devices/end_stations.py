#OAESE Motors
from ophyd import Device, EpicsMotor
from ophyd import Component as Cpt
from .keithley import Keithley6514


class OAESE(Device):
    x = Cpt(EpicsMotor, 'motor0:mx')
    y = Cpt(EpicsMotor, 'motor0:my')
    z = Cpt(EpicsMotor, 'motor0:mz')
    kth00 = Cpt(Keithley6514, 'Keithley00:')
    kth01 = Cpt(Keithley6514, 'Keithley00:')

