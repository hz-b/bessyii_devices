from ophyd import Device, EpicsMotor
from ophyd import Component as Cpt





class DCMmySpot(Device):
    monoz = Cpt(EpicsMotor, 'l0201002')
    cr2latr = Cpt(EpicsMotor, 'l0201003')
    cr1roll = Cpt(EpicsMotor, 'l0201004')
    cr2roll = Cpt(EpicsMotor, 'l0201005')
    monobr = Cpt(EpicsMotor, 'l0202000')
    cr2vetr = Cpt(EpicsMotor, 'l0202001')
    monoy = Cpt(EpicsMotor, 'l0202002')
    cr2ropi= Cpt(EpicsMotor, 'l0202003')
    cr2yaw = Cpt(EpicsMotor, 'l0202004')

