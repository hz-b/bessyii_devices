from ophyd.mca import EpicsMCA, ROI

from ophyd import EpicsSignal, EpicsSignalRO
from ophyd import status, DeviceStatus, Signal
from ophyd.status import SubscriptionStatus, MoveStatus, AndStatus 
from collections import OrderedDict

from ophyd.device import (Device, Component as Cpt, DynamicDeviceComponent as DDC,
                     Kind)

from ophyd import FormattedComponent as FCpt


class ROI(Device):

    # 'name' is not an allowed attribute
    label = FCpt(EpicsSignal, '{self.prefix}.R{self._ch}NM', lazy=True, kind='config')
    count = FCpt(EpicsSignal, '{self.prefix}.R{self._ch}', lazy=True, kind='normal')
    net_count = FCpt(EpicsSignalRO, '{self.prefix}.R{self._ch}N', lazy=True, kind='config')
    preset_count = FCpt(EpicsSignal, '{self.prefix}.R{self._ch}P', lazy=True, kind='config')
    is_preset = FCpt(EpicsSignal, '{self.prefix}.R{self._ch}IP', lazy=True, kind='config')
    bkgnd_chans = FCpt(EpicsSignal, '{self.prefix}.R{self._ch}BG', lazy=True, kind='config')
    hi_chan = FCpt(EpicsSignal, '{self.prefix}.R{self._ch}HI', lazy=True, kind='config')
    lo_chan = FCpt(EpicsSignal, '{self.prefix}.R{self._ch}LO', lazy=True, kind='config')
    hi_en = FCpt(EpicsSignal, '{self.prefix}:R{self._ch}HIENERGY', lazy=True, kind='config')
    lo_en = FCpt(EpicsSignal, '{self.prefix}:R{self._ch}LOENERGY', lazy =True, kind='config')

    def __init__(self, prefix,ch, *, read_attrs=None, configuration_attrs=None,
                 name=None, parent=None, **kwargs):
        super().__init__(prefix, read_attrs=read_attrs,
                         configuration_attrs=configuration_attrs,
                         name=name, parent=parent, **kwargs)
        self._ch = ch
        self.hide()
    
    def display(self):

        self.count.kind="hinted"
    
    def hide(self):

        self.count.kind="normal"
    
class Rontec(Device):
    
    throughput = Cpt(EpicsSignalRO, 'Throughput', kind='normal')
    temperature = Cpt(EpicsSignalRO, 'Temperature', kind='normal')
    status_rate = Cpt(EpicsSignal, 'ReadTemperature.SCAN', kind='config')
    
class MyEpicsMCA(EpicsMCA):
    
    erase_start = Cpt(EpicsSignal, 'EraseStart', kind='omitted')
    acquiring = Cpt(EpicsSignalRO, 'WhenAcqStops', kind='omitted')
    done_value = 0
    
    #device
    #rontec = Cpt(Rontec, , kind = 'normal')

    roi0 =Cpt(ROI, '', ch= 0,kind = 'normal')
    roi1 =Cpt(ROI, '', ch= 1,kind = 'normal')
    

    roi2 =Cpt(ROI, '',ch=1, kind='normal')
    roi3 =Cpt(ROI, '',ch=2, kind='normal')
    #roi4 =Cpt(ROI, '.R4')
    #roi5 =Cpt(ROI, '.R5')
    #roi6 =Cpt(ROI, '.R6')
    #roi7 =Cpt(ROI, '.R7')
    #roi8 =Cpt(ROI, '.R8')
    #roi9 =Cpt(ROI, '.R9')
    #roi10 =Cpt(ROI, '.R10')
    
    #calibration
    offset = Cpt(EpicsSignalRO, '.CALO',kind='config')
    slope = Cpt(EpicsSignalRO, '.CALS',kind='config')
    quadratic = Cpt(EpicsSignalRO, '.CALQ',kind='config')
    egu = Cpt(EpicsSignalRO, '.EGU',kind='config')
    two_theta = Cpt(EpicsSignalRO, '.TTH',kind='config')
    
    ##Config
    
    

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
                       
            return (value == self.done_value)
        
        # create the status with SubscriptionStatus that add's a callback to check_value.
        sta_cnt = SubscriptionStatus(callback_signal, check_value, run=False)
         
        # Start the acquisition
        sta_acq = self.erase_start.set(1)
        
        sta_acq.add_callback(acquisition_started)
        
        stat = AndStatus(sta_cnt, sta_acq)
        
        return stat

class Bruker(Device):
    

    mca = Cpt(MyEpicsMCA, 'mca1', name='mca', kind='normal')
    detector = Cpt(Rontec, 'Rontec1', name = 'detector',kind='config')
    
    def stage(self):
        
        self.detector.status_rate.put("Passive")
        
    def unstage(self):
        
        self.detector.status_rate.put(".1 second")
    
        
       
   
