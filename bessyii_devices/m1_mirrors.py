from ophyd import PVPositioner, EpicsSignal,EpicsMotor, EpicsSignalRO, Device
from ophyd.signal import Signal, SignalRO
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FCpt
#from .positioners import *
from .axes import M1Axis



class M1(Device):

    tx   = Cpt(M1Axis, '', ch_name='Tx', labels={"mirrors"})
    ty   = Cpt(M1Axis, '', ch_name='Ty', labels={"mirrors"})
    rx   = Cpt(M1Axis, '', ch_name='Rx', labels={"mirrors"})
    ry   = Cpt(M1Axis, '', ch_name='Ry', labels={"mirrors"})
    rz   = Cpt(M1Axis, '', ch_name='Rz', labels={"mirrors"})

class M1SoftEmil(M1):
    temp1 = FCpt(EpicsSignalRO, 'MIRRORY02U012L:T1')
    temp2 = FCpt(EpicsSignalRO, 'MIRRORY02U012L:T2')

class M1HardEmil(M1):

    temp = FCpt(EpicsSignalRO, 'MIRRORY01U012L:T1')

class M1Aquarius(Device):

    tx = EpicsMotor('Tx', name='tx', labels={"mirrors"})
    ty = EpicsMotor('Ty', name='ty', labels={"mirrors"})
    tz = EpicsMotor('Tz', name='tz', labels={"mirrors"})
    rx = EpicsMotor('Rx', name='rx', labels={"mirrors"})
    ry = EpicsMotor('Ry', name='ry', labels={"mirrors"})
    rz = EpicsMotor('Rz', name='rz', labels={"mirrors"})



