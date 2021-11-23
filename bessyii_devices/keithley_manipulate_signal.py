
#
from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device, DerivedSignal, PseudoPositioner, PseudoSingle
from ophyd import Component as Cpt
from ophyd import status, DeviceStatus, Signal
from ophyd.ophydobj import Kind
from ophyd.status import SubscriptionStatus, MoveStatus, AndStatus 
from ophyd.pseudopos import (pseudo_position_argument, real_position_argument)
import time
from types import SimpleNamespace
from bessyii_devices.positioners import PVPositionerComparator
from ophyd import FormattedComponent as FCpt
from decimal import *
from bessyii_devices.keithley import Keithley6514, Keithley6517
 

class MultiSignal(DerivedSignal):    
    #the init is important for input values
    def __init__(self, *args, signal, **kwargs):
        self._signal = signal
        super().__init__(*args, **kwargs)
    
    def inverse(self,value):
        return value

    
class MultiSameSignal(DerivedSignal):    
    #the init is important for input values
    def __init__(self, *args, **kwargs):
        #self._signal = signal
        super().__init__(*args, **kwargs)
    
    def test(value):
        return value*value


class ScaleSignal(DerivedSignal):    
    #the init is important for input values
    def __init__(self, *args, factor, **kwargs):
        self.scaling_factor = factor
        super().__init__(*args, **kwargs) 
    
    def inverse(self, value):
        return value*self.scaling_factor   
 
    
class PseudoPosSignal(PVPositionerComparator):
    
    setpoint = Cpt(EpicsSignalRO, 'rdCur')
    readback = Cpt(EpicsSignalRO, 'rdCur')
    
    atol = 0.1
    
    def done_comparator(self, readback, setpoint):
        return setpoint-self.atol < readback < setpoint+self.atol

    
class PseudoPosSignalKeithley(PVPositionerComparator):

    setpoint = FCpt(EpicsSignalRO,'{self.prefix}rdCur')
    readback = FCpt(EpicsSignalRO,'{self.prefix}rdCur', kind=Kind.normal)

    atol = 0.1  # tolerance before we set done to be 1 (in um) we should check what this should be!

    def done_comparator(self, readback, setpoint):
        return setpoint-self.atol < readback < setpoint+self.atol
                
    def __init__(self, prefix, **kwargs):        
        super().__init__(prefix, **kwargs)

  
class PseudoTwoKeithleys(PseudoPositioner):
    # this is only working if: ValueError: Must have at least 1 positioner and pseudo-positioner
    
    # The pseudo positioner axes:   
    p_kth01 = Cpt(PseudoSingle, limits=(-6283186.0, 6283186.0), kind="normal")
    p_kth02 = Cpt(PseudoSingle, limits=(-6283186.0, 6283186.0), kind="normal")


    r_kth01            = Cpt(PseudoPosSignalKeithley, 'Keithley00:', kind="normal")
    r_kth02            = Cpt(PseudoPosSignalKeithley, 'Keithley01:', kind="normal")

    factor = 1e15
    
    @pseudo_position_argument
    def forward(self, pseudo_pos):
        '''Run a forward (pseudo -> real) calculation'''
        return self.RealPosition(r_kth01=-1e5*pseudo_pos.p_kth01,
                                 r_kth02=-1e5*pseudo_pos.p_kth02)

    @real_position_argument
    def inverse(self, real_pos):
        '''Run an inverse (real -> pseudo) calculation'''
        return self.PseudoPosition(p_kth01=-self.factor*(real_pos.r_kth01),
                                   p_kth02=1e0*((real_pos.r_kth01)/(real_pos.r_kth02)))
                                   #p_mkth=((real_pos.r_kth01)*(real_pos.r_kth02)))                   

class PseudoTwoKeithleysShort(PseudoPositioner):
    # this is only working if: ValueError: Must have at least 1 positioner and pseudo-positioner
    
    # The pseudo positioner axes:   
    p_kth01 = Cpt(PseudoSingle, limits=(-6283186.0, 6283186.0))
    p_kth02 = Cpt(PseudoSingle, limits=(-6283186.0, 6283186.0))


    r_kth01            = Cpt(PseudoPosSignalKeithley, 'Keithley00:')
    r_kth02            = Cpt(PseudoPosSignalKeithley, 'Keithley01:')

    factor = 1e15
    
    @real_position_argument
    def inverse(self, real_pos):
        '''Run an inverse (real -> pseudo) calculation'''
        return self.PseudoPosition(p_kth01=-self.factor*(real_pos.r_kth01),
                                   p_kth02=1e0*((real_pos.r_kth01)/(real_pos.r_kth02)))
                                   #p_mkth=((real_pos.r_kth01)*(real_pos.r_kth02)))                   
   
   
class ManipulateKeithleysSignals(PseudoPositioner):
    # this is only working if: ValueError: Must have at least 1 positioner and pseudo-positioner
    
    # The pseudo positioner axes:   
    #p_kth01 = Cpt(PseudoSingle, limits=(-6283186.0, 6283186.0), name = 'test_01')
    ratio_12 = Cpt(PseudoSingle, limits=(-6283186.0, 6283186.0))

    kth01            = Cpt(PseudoPosSignalKeithley, 'Keithley00:')
    kth02            = Cpt(PseudoPosSignalKeithley, 'Keithley01:')

    kth01.kind.normal
    
    factor = 1e15
    factor_real = 1e0
    
    @real_position_argument
    def inverse(self, real_pos):
        '''Run an inverse (real -> pseudo) calculation'''
        return self.PseudoPosition(ratio_12=self.factor_real*(real_pos.kth01/real_pos.kth02))
                            

def set_detector(det):
    pass
    #det.p_kth01.kind = 'normal' 
    #det.p_kth02.kind = 'normal' 
    #det.r_kth01.kind = 'normal' 
    #det.r_kth02.kind = 'normal' 
    
 

# das geht...
class TwoKeithleysB(Keithley6517):
    readback            = Cpt(EpicsSignalRO, 'rdCur', kind='hinted', labels={"detectors", "keithley"})
    #kth_readback = kth01_read.readback.get()
    scaling_factor = 10
    scaling_signal = Cpt(ScaleSignal, derived_from="readback", factor=scaling_factor, kind="hinted")


class TwoKeithleysB(Device):    
    #kth01_read = Keithley6517.readback
    kth01readback            = Cpt(EpicsSignalRO, 'Keithley00:rdCur', name='Keithley01_readback', kind="hinted")
    kth02readback            = Cpt(EpicsSignalRO,  'Keithley01:rdCur', name='Keithley02_readback', kind="hinted")
    
    #kth_readback = kth01_read.readback.get()
    scaling_factor = 1e5
    scaling_signal = Cpt(ScaleSignal, derived_from="kth02readback", factor=scaling_factor, kind="hinted")
    
    



class TwoKeithleysC(Device):
    kth01readback            = Cpt(EpicsSignalRO, 'Keithley00:rdCur', name='Keithley01_readback', kind="hinted")
    kth02readback            = Cpt(EpicsSignalRO,  'Keithley01:rdCur', name='Keithley02_readback', kind="hinted")
    
    kth01readback1            = Cpt(PseudoPosSignalKeithley, 'Keithley00:', kind="normal")
    kth02readback1            = Cpt(PseudoPosSignalKeithley, 'Keithley01:', kind="normal")
    
    
    #kth_readback = kth01_read.readback.get()
    scaling_factor = 1e5
    scaling_signal = Cpt(ScaleSignal, derived_from="kth02readback", factor=scaling_factor, kind="hinted")
    
    

def set_detector_C(det):
    det.kth01readback.kind = 'normal' 
    det.kth02readback.kind = 'normal' 
    det.kth01readback1.kind = 'normal' 
    det.kth02readback1.kind = 'normal' 
    det.scaling_signal.kind = 'hinted' 