from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device
from ophyd import Component as Cpt
from bessyii_devices.positioners import PVPositionerComparator
from ophyd import status, DeviceStatus, Signal
from ophyd.status import SubscriptionStatus, MoveStatus, AndStatus 
import time
from types import SimpleNamespace

class ChanneltronHV(PVPositionerComparator):

    """
    A Positioner to control the HV of the channeltron, useful for commissioning
    """

    setpoint = Cpt(EpicsSignal, '-SP',   kind='normal')
    readback = Cpt(EpicsSignal, '-RB',   kind='hinted')

    atol = 1  # tolerance before we set done to be 1 (in um) we should check what this should be!


    def done_comparator(self, readback, setpoint):
        return setpoint-self.atol < readback < setpoint+self.atol
        
    def __init__(self, prefix, **kwargs):
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name

class Channeltron(Device):


    #Define the signals in our component
    
    start_cmd   = Cpt(EpicsSignal,  'Start-CMD',    kind='omitted')         # Starts a read
    count       = Cpt(EpicsSignalRO,'Counter-RB',   kind='hinted') # hinted makes it show up in visualisations.

    hv          = Cpt(ChanneltronHV,"HighVoltage",  kind='config')
    interval    = Cpt(EpicsSignal,  'Interval-RB',  write_pv = 'Interval-SP',  kind='config')
    threshold   = Cpt(EpicsSignal,  'Threshold-RB',  write_pv='Threshold-SP', kind='config')
    dead_time   = Cpt(EpicsSignal,  'DeadTime-RB',    write_pv = 'DeadTime-SP', string=True,  kind='config')

    def stage(self):

        self.start_cmd.set(1) #start the measurement


   