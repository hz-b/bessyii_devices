from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO
from ophyd import Component as Cpt

class DCMKmc3(PVPositioner):
    """
    DCM at KMC3
    prefix: DCM1OB013L
    """

    #prefix at emil: MONOY01U112L
    setpoint        = Cpt(EpicsSignal,      'DCM_ENERGY_SP'                  )
    readback        = Cpt(EpicsSignalRO,    'DCM_ENERGY_MON.M',    kind='hinted', labels={"dcm"})
    done            = Cpt(EpicsSignalRO,    'DCM_ERDY_STS'                  )

    exafs              = Cpt(EpicsSignal,      'DCM_EXAFS_STS')
    start_integrate_I1 = Cpt(EpicsSignal,      'I200:AVG_gate')
    I1_fast            = Cpt(EpicsSignal,      'I200:I1')
    integratedi1       = Cpt(EpicsSignal,      'I200:AVG_AVG_I1')
    piezo              = Cpt(EpicsSignal,      'I200:Volt')
