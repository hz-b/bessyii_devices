from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device
from ophyd import Component as Cpt
from ophyd import status, DeviceStatus, Signal
from ophyd.status import SubscriptionStatus, MoveStatus, AndStatus 
import time
from types import SimpleNamespace

class Channeltron(Device):


    #Define the signals in our component
    
    read_cmd    = Cpt(EpicsSignal,  'Start-CMD', kind='omitted')         # Starts a read
    count       = Cpt(EpicsSignalRO,'Counter-RB',       kind='hinted') # hinted makes it show up in visualisations.
 
 
    interval    = Cpt(EpicsSignal,  'Interval-SP',      kind='config')
    threshold   = Cpt(EpicsSignal,  'Threshold-SP',     kind='config')
    high_voltage = Cpt(EpicsSignal, 'HighVoltage-RB', write_pv = 'HighVoltage-SP',   kind='config')
    dead_time    = Cpt(EpicsSignal,  'DeadTime-SP',      kind='config')


    def trigger(self):
    
        #variable used as an event flag
        acquisition_status = False
           
        def acquisition_started():
            nonlocal acquisition_status #Define as nonlocal as we want to modify it
            acquisition_status = True
                
        def check_value(*, old_value, value, **kwargs):
            #Return True when the acquisition is complete, False otherwise.
                                   
            if not acquisition_status:  #But only report done if acquisition was already started
                
                return False
                       
            return (old_value != value)
        
        # create the status with SubscriptionStatus that add's a callback to check_value.
        # timeout is set at 1 second + whatever the duration is in ms
        sta_cnt = SubscriptionStatus(self.count, check_value, timeout=10.0, run=False)
         
        # Start the acquisition
        sta_acq = self.read_cmd.set(1)
        
        sta_acq.add_callback(acquisition_started)
        
        stat = AndStatus(sta_cnt, sta_acq)
        
        return stat
