from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device, DerivedSignal,PseudoPositioner,PseudoSingle,EpicsMotor
from ophyd import Component as Cpt
from ophyd.pseudopos import (pseudo_position_argument,
                             real_position_argument)
from ophyd.signal import Signal, SignalRO
from ophyd import FormattedComponent as FCpt
from .positioners import *
from .mostab import Mostab
from .pgm import Energy
from .axes import AxisTypeB, AxisTypeBChoice
import numpy as np 
import math
from ophyd import Kind


class AxisPositioner(PVPositionerDone):
    
  
    setpoint = FCpt(EpicsSignal,    '{self._pre_volt}Piezo{self._pz_num}U1',kind='normal') 
    readback = FCpt(EpicsSignalRO,  '{self._pre_enc}dcm:cr2{self._ch_name}Encoder', kind='hinted')
   
    def __init__(self,prefix, pre_volt=None, pre_enc=None, ch_name=None, pz_num=None, **kwargs):
        self._ch_name = ch_name
        self._pz_num = pz_num
        self._pre_volt = pre_volt
        self._pre_enc = pre_enc
        super().__init__(prefix, **kwargs)

class DCMCrystalAxis(PVPositioner):

    def __init__(self, prefix,ch_name=None, **kwargs):
        self._ch_name = ch_name
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name

    setpoint = FCpt(EpicsSignal,'{self.prefix}dcm:set{self._ch_name}',kind='normal')
    readback=FCpt(EpicsSignalRO, '{self.prefix}dcm:{self._ch_name}', labels={"dcm", "motors"},kind='hinted')
    done=Cpt(EpicsSignalRO,  'multiaxis:running' , kind='omitted')
    done_value= 0

class DCMThetaAxis(PVPositioner):

    setpoint = Cpt(EpicsSignal,'SetTheta', kind='normal')
    readback = Cpt(EpicsSignalRO,'Theta', kind = 'hinted')
    done     = Cpt(EpicsSignalRO,'Status', kind='omitted')
    done_value = 0

    def __init__(self, prefix, **kwargs):
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name

    
#https://nsls-ii.github.io/ophyd/positioners.html#pseudopositioner
class Piezo3Axis(PseudoPositioner):
    
    # The pseudo positioner axes:
    # we have to set the limits to the biggest of the input or output
    pitch     = Cpt(PseudoSingle, limits=(-6283186.0, 6283186.0), labels={"dcm", "motors"} ) 
    roll      = Cpt(PseudoSingle, limits=(-6283186.0, 6283186.0), labels={"dcm", "motors"} )
    height    = Cpt(PseudoSingle, limits=(-6283186.0, 6283186.0), labels={"dcm", "motors"} )

    # The real (or physical) positioners:
    # wait for 1 second before reporting done
    r_pitch     = Cpt(AxisPositioner,'',pre_volt='MONOY01U112L:', pre_enc='u171dcm1:',ch_name='Pitch' ,pz_num='2', settle_time=.1)      
    r_roll      = Cpt(AxisPositioner,'',pre_volt='MONOY01U112L:', pre_enc='u171dcm1:',ch_name='Roll'  ,pz_num='3', settle_time=.1)
    r_height    = Cpt(AxisPositioner,'',pre_volt='MONOY01U112L:', pre_enc='u171dcm1:',ch_name='TraHeight',pz_num='1', settle_time=.1)

    
    
    
    @pseudo_position_argument
    def forward(self, pseudo_pos):
        '''Run a forward (pseudo -> real) calculation'''
        return self.RealPosition(r_pitch    =pseudo_pos.pitch,
                                 r_roll     =pseudo_pos.roll,
                                 r_height   =pseudo_pos.height)

    
    @real_position_argument
    def inverse(self, real_pos):
    
        #http://sissy-pi-01/dokuwiki/doku.php?id=beamlines:devices:piezo_control
        c2um = 5.0      
        p_o = 3260320 - 3800000
        r_o = 3263554 - 3800000
        h_o = 3220620 - 3800000
        
        offsets = np.array([p_o,r_o,h_o])
        a = np.array ([[ 1,0,-1],
                       [ 0,1,-1],
                       [ 0,0,1]])
        p_x = 64750000
        r_x = 127750000
        
        d = c2um*np.matmul(a,np.subtract(real_pos,offsets))
                   
        '''Run an inverse (real -> pseudo) calculation'''
        return self.PseudoPosition(pitch  = 1000000 * math.atan(d[0]/p_x), 
                                   roll   = 1000000 * math.atan(d[1]/r_x), 
                                   height = d[2])

       
        
    
class DCMEMIL(Device):


    prefix_1 = 'u171dcm1:'
    prefix_2 = 'MONOY01U112L:'

    en              = Cpt(Energy,  prefix_1,kind='hinted')


    # horizontal translation to select the Si 111,311,422 crystal 
    # Si111: 108 +/- 10, Si311: 66  +/- 10, Si 422: 24  +/- 10
    
    cr1             = Cpt(DCMCrystalAxis,    prefix_1, ch_name = 'CR1', kind=Kind.config|Kind.normal)
    cr2             = Cpt(DCMCrystalAxis,    prefix_1, ch_name = 'CR2', kind=Kind.config|Kind.normal)
    ct1             = Cpt(DCMCrystalAxis,    prefix_1, ch_name = 'CT', kind=Kind.config|Kind.normal)
    
    crystal_translate = Cpt(AxisTypeB, prefix_1+'PH_0',labels={"dcm","motors"},kind=Kind.config|Kind.normal)
    crystal_select  = Cpt(AxisTypeBChoice, prefix_1+'PH_0',labels={"dcm","motors"},kind=Kind.config|Kind.normal)
    crystal_calc         = Cpt(EpicsSignal,  prefix_1+'SetGratingNo',  string='True',    kind=Kind.config|Kind.normal, labels={"dcm", "motors"})      

    

    table           = Cpt(EpicsSignal,    prefix_1+'idMbboIndex', string='True',kind='config') 
    table_filename  = Cpt(EpicsSignalRO,  prefix_1+'idFilename', string='True',kind='config')
    channelcut_disable      = Cpt(EpicsSignal,    prefix_1+'disableCT',kind='config')
    harmonic        = Cpt(EpicsSignal,    prefix_1+'GetIdHarmonic', write_pv=prefix_1+'Harmonic', string='True', kind='config')
    ID_on           = Cpt(EpicsSignal,    prefix_1+'SetIdOn', string='True',kind='config')
    theta           = Cpt(DCMThetaAxis,    prefix_1, kind='config', labels={"dcm", "motors"})
    bw              = Cpt(EpicsSignalRO,  prefix_1+'crystal_bw',kind='config')
    dspacing        = Cpt(EpicsSignalRO,  prefix_1+'d_hkl',kind='config')
    slope           = Cpt(EpicsSignal,  prefix_1+'aiIdSlope', write_pv=prefix_1+'aoIdSlope',kind='config' )
    offset          = Cpt(EpicsSignal,  prefix_1+'aiIdOffset', write_pv=prefix_1+'aoIdOffset',kind='config' )
   
     # Temperature
    temp1_111           = Cpt(EpicsSignalRO,    prefix_2+'Crystal1T1', labels={"dcm"},kind='normal')
    temp2_111           = Cpt(EpicsSignalRO,    prefix_2+'Crystal2T1', labels={"dcm"},kind='normal')
    temp1_311           = Cpt(EpicsSignalRO,    prefix_2+'Crystal1T2', labels={"dcm"},kind='normal')
    temp2_311           = Cpt(EpicsSignalRO,    prefix_2+'Crystal2T2', labels={"dcm"},kind='normal')
    temp1_422           = Cpt(EpicsSignalRO,    prefix_2+'Crystal1T3', labels={"dcm"},kind='normal')
    temp2_422           = Cpt(EpicsSignalRO,    prefix_2+'Crystal2T3', labels={"dcm"},kind='normal')

    # Piezo
    piezo           = Cpt(Piezo3Axis,'',kind=Kind.config|Kind.normal)
    
    # Mostab 
    
    pitch_mostab = Cpt(Mostab,'EMILEL:Mostab0:',kind=Kind.config|Kind.normal)
    roll_mostab = Cpt(Mostab,'EMILEL:Mostab1:',kind=Kind.config|Kind.normal)
