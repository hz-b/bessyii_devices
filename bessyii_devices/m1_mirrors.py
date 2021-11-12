from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device
from ophyd.signal import Signal, SignalRO
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FCpt
#from .positioners import *
from .axes import M1Axis,M1AxisAquarius



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

    tx   = Cpt(M1AxisAquarius, '', ch_name='Tx', labels={"mirrors"})
    ty   = Cpt(M1AxisAquarius, '', ch_name='Ty', labels={"mirrors"})
    rx   = Cpt(M1AxisAquarius, '', ch_name='Rx', labels={"mirrors"})
    ry   = Cpt(M1AxisAquarius, '', ch_name='Ry', labels={"mirrors"})
    rz   = Cpt(M1AxisAquarius, '', ch_name='Rz', labels={"mirrors"})




