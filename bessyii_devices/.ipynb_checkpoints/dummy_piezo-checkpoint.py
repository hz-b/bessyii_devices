from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device, DerivedSignal,PseudoPositioner,PseudoSingle,EpicsMotor
from ophyd import Component as Cpt
from ophyd.pseudopos import (pseudo_position_argument,
                             real_position_argument)
from ophyd.signal import Signal, SignalRO
from ophyd import FormattedComponent as FCpt
from .positioners import *

import numpy as np 
import math

class AxisPositioner(PVPositionerDone):
    
  
    setpoint = FCpt(EpicsSignal,    '{self.prefix}Piezo{self._pz_num}U1') 
    readback = FCpt(EpicsSignalRO,  '{self.prefix}dcm:cr2{self._ch_name}Encoder', kind='hinted')
   
    def __init__(self, prefix, ch_name=None, pz_num=None, **kwargs):
        self._ch_name = ch_name
        self._pz_num = pz_num
        super().__init__(prefix, **kwargs)
    
#https://nsls-ii.github.io/ophyd/positioners.html#pseudopositioner
class Pseudo3x3(PseudoPositioner):
    
 
    
    # The pseudo positioner axes:
    p_pitch     = Cpt(PseudoSingle, limits=(-6283186.0, 6283186.0) ) # we have to set the limits to the biggest of the input or output
    p_roll      = Cpt(PseudoSingle, limits=(-6283186.0, 6283186.0) )
    p_height    = Cpt(PseudoSingle, limits=(-6283186.0, 6283186.0) )

    # The real (or physical) positioners:
    r_pitch     = Cpt(AxisPositioner,'',ch_name='Pitch' ,pz_num='2', settle_time=1)      #wait for 1 second before reporting done
    r_roll      = Cpt(AxisPositioner,'',ch_name='Roll'  ,pz_num='3', settle_time=1)
    r_height    = Cpt(AxisPositioner,'',ch_name='TraHeight',pz_num='1', settle_time=1)

    
    
    
    @pseudo_position_argument
    def forward(self, pseudo_pos):
        '''Run a forward (pseudo -> real) calculation'''
        return self.RealPosition(r_pitch    =pseudo_pos.p_pitch,
                                 r_roll     =pseudo_pos.p_roll,
                                 r_height   =pseudo_pos.p_height)

    
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
        return self.PseudoPosition(p_pitch  = 1000000 * math.atan(d[0]/p_x), 
                                   p_roll   = 1000000 * math.atan(d[1]/r_x), 
                                   p_height = d[2])

