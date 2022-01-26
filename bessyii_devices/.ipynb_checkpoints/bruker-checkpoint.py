from ophyd.mca import EpicsMCA, ROI

from ophyd import EpicsSignal, EpicsSignalRO
from ophyd import status, DeviceStatus, Signal
from ophyd.status import SubscriptionStatus, MoveStatus, AndStatus 
from collections import OrderedDict

from ophyd.device import (Device, Component as Cpt, DynamicDeviceComponent as DDC,
                     Kind)

class ROI(Device):

    # 'name' is not an allowed attribute
    label = Cpt(EpicsSignal, 'NM', lazy=True, kind='config')
    count = Cpt(EpicsSignalRO, '', lazy=True, kind='hinted')
    net_count = Cpt(EpicsSignalRO, 'N', lazy=True, kind='config')
    preset_count = Cpt(EpicsSignal, 'P', lazy=True, kind='config')
    is_preset = Cpt(EpicsSignal, 'IP', lazy=True, kind='config')
    bkgnd_chans = Cpt(EpicsSignal, 'BG', lazy=True, kind='config')
    hi_chan = Cpt(EpicsSignal, 'HI', lazy=True, kind='config')
    lo_chan = Cpt(EpicsSignal, 'LO', lazy=True, kind='config')

    def __init__(self, prefix, *, read_attrs=None, configuration_attrs=None,
                 name=None, parent=None, **kwargs):

        super().__init__(prefix, read_attrs=read_attrs,
                         configuration_attrs=configuration_attrs,
                         name=name, parent=parent, **kwargs)



class MyEpicsMCA(EpicsMCA):
    
    erase_start = Cpt(EpicsSignal, 'EraseStart', kind='omitted')
    acquiring = Cpt(EpicsSignalRO, '.ACQG', kind='omitted')
    
        #Acquisition Throughput 
    throughput = Cpt(EpicsSignalRO, 'Throughput', kind='omitted')
    
    
    #None of these are consistent enough
    reading = Cpt(EpicsSignalRO, '.READ', kind='omitted')
    readingg = Cpt(EpicsSignalRO, '.RDNG', kind='omitted')
    readings = Cpt(EpicsSignalRO, '.RDNS', kind='omitted')
    
    roi0 =Cpt(ROI, '.R0')
    roi1 =Cpt(ROI, '.R1')
    roi2 =Cpt(ROI, '.R2')
    roi3 =Cpt(ROI, '.R3')
    roi4 =Cpt(ROI, '.R4')
    roi5 =Cpt(ROI, '.R5')
    roi6 =Cpt(ROI, '.R6')
    roi7 =Cpt(ROI, '.R7')
    roi8 =Cpt(ROI, '.R8')
    roi9 =Cpt(ROI, '.R9')
    roi10 =Cpt(ROI, '.R10')
    
    #calibration
    offset = Cpt(EpicsSignalRO, '.CALO',kind='config')
    slope = Cpt(EpicsSignalRO, '.CALS',kind='config')
    quadratic = Cpt(EpicsSignalRO, '.CALQ',kind='config')
    egu = Cpt(EpicsSignalRO, '.EGU',kind='config')
    two_theta = Cpt(EpicsSignalRO, '.TTH',kind='config')
    

    def trigger(self):
        
        callback_signal = self.acquiring
        #variable used as an event flag
        acquisition_status = False
           
        def acquisition_started(status):
            nonlocal acquisition_status #Define as nonlocal as we want to modify it
            acquisition_status = True
                
        def check_value(*, old_value, value, **kwargs):
            #Return True when the acquisition is complete, False otherwise.
                                   
            if not acquisition_status:  #But only report done if acquisition was already started
                
                return False
                       
            return (value == 0 and old_value == 1 and self.preset_real_time.get() == self.elapsed_real_time.get())
        
        # create the status with SubscriptionStatus that add's a callback to check_value.
        sta_cnt = SubscriptionStatus(callback_signal, check_value, run=False, settle_time = 3)
         
        # Start the acquisition
        sta_acq = self.erase_start.set(1)
        
        sta_acq.add_callback(acquisition_started)
        
        stat = AndStatus(sta_cnt, sta_acq)
        
        return stat



        
       
   
