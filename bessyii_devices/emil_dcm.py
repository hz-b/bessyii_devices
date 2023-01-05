from ophyd import Device, Component as Cpt, EpicsMotor, EpicsSignalRO

class U17_DCM(Device):

    """
    Work In Progress
    
    An Ophyd Device which exposes control to the EMIL U17 DCM using the EPICS Motor Record Interface

    Instantiated with:

    u17_dcm = U17_DCM("myDCM:")
    """

    en = Cpt(EpicsMotor, "axis_Energy")
    theta = Cpt(EpicsMotor, "axis_Theta")
    theta_cryo = Cpt(EpicsMotor, "pmacAxis4")

