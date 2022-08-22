from ophyd import Device, EpicsMotor, EpicsSignalRO
from ophyd import Component as Cpt

from ophyd import PseudoPositioner, PseudoSingle
from ophyd.pseudopos import pseudo_position_argument,  real_position_argument

import numpy as np

mono_table = {'Si111':{'monoh':25, 'monod':3.1356, 'c1height':0.0, 'monoz':-38.0, 
              'encoder_zero':-0.557, 'cr2ropi':0.104, 'cr1roll': 0.078,
              'cr2roll':0.075, 'cr2vetrCorr':0.0038},
     'Si311':{'monoh':25, 'monod':1.63751, 'c1height':5.718, 'monoz':0.0, 
              'encoder_zero':-0.399, 'cr2ropi':0.025, 'cr1roll': 0.0278,
              'cr2roll':0.0776, 'cr2vetrCorr':0.0},
     'B4CML':{'monoh':5, 'monod':20.0, 'c1height':6.46, 'monoz':41.5, 
              'encoder_zero':-0.38564, 'cr2ropi':0.027, 'cr1roll': 0.053,
              'cr2roll':0.205, 'cr2vetrCorr':0.0020}
      }


class DCMmySpot(Device):
    monoz = Cpt(EpicsMotor, 'l0201002')
    cr2latr = Cpt(EpicsMotor, 'l0201003')
    cr1roll = Cpt(EpicsMotor, 'l0201004')
    cr2roll = Cpt(EpicsMotor, 'l0201005')
    monobr = Cpt(EpicsMotor, 'l0202000')
    cr2vetr = Cpt(EpicsMotor, 'l0202001')
    monoy = Cpt(EpicsMotor, 'l0202002')
    cr2ropi= Cpt(EpicsMotor, 'l0202003')
    cr2yaw = Cpt(EpicsMotor, 'l0202004')

class DCMmySpot_new(PseudoPositioner):
    ''' This class implements apertures with four blades (top, bottom, left, right)
    and four pseudo motors (htop,hoffset,vgap,voffset)
    '''

    # constants
    hc_over_e = 12.398419111
    
    # others
    mono_type = 'Si111'
    # The pseudo positioner axes:
    energy    = Cpt(PseudoSingle)
    height    = Cpt(PseudoSingle)

    # The real (or physical) positioners:
    monoz = Cpt(EpicsMotor, 'l0201002')
    cr2latr        = Cpt(EpicsMotor, 'l0201003')
    cr1roll        = Cpt(EpicsMotor, 'l0201004')
    cr2roll        = Cpt(EpicsMotor, 'l0201005')
    monobr         = Cpt(EpicsMotor, 'l0202000')
    cr2vetr        = Cpt(EpicsMotor, 'l0202001')
    monoy          = Cpt(EpicsMotor, 'l0202002')
    cr2ropi        = Cpt(EpicsMotor, 'l0202003')
    cr2yaw         = Cpt(EpicsMotor, 'l0202004')
    monobr_encoder = Cpt(EpicsSignalRO, 'IK1380002')

    def set_mono_type(mono_type):
        if mono_type in mono_table.keys():
            self.mono_type=mono_type
        else:
            raise ValueError('This mono type does not exist')

    @pseudo_position_argument
    def forward(self, pseudo_pos):
        '''Run a forward (pseudo -> real) calculation'''
        return self.RealPosition(top    = pseudo_pos.voffset+pseudo_pos.vgap/2,
                                 bottom = -pseudo_pos.voffset+pseudo_pos.vgap/2,
                                 left   = -pseudo_pos.hoffset+pseudo_pos.hgap/2,
                                 right  = pseudo_pos.hoffset+pseudo_pos.hgap/2 
                                 )

    @real_position_argument
    def inverse(self, real_pos):
        '''Run an inverse (real -> pseudo) calculation'''
        L = (2*mono_table[self.mono_type]*np.sin(rad(BR))) 
        return self.PseudoPosition(energy =hc_over_e/L ,
                                   height = 2.0 * (A[cr2vetr]-MYSPOT_BL_MONO_c1height[MYSPOT_BL_MONO]-A[cr2latr]*MYSPOT_BL_MONO_cr2vetrCorr[MYSPOT_BL_MONO]-0*(85-A[monoz])*sin(rad(A[cr2roll])) ) *cos(rad(BRAGG_ANGLE))  
                                   )

    def set_current_position(self, axis, pos):
        '''Configure the motor user position to the given value, 
           works also for psuedo motors
        Parameters
        ----------
        axis
            string, axis to set
        pos
           float, Position to set.
        '''
        axis_pt   = eval("self.{}".format(axis))
        axis_name = "self_{}".format(axis)
        try:
           axis_pt.set_current_position(pos)
        except AttributeError:
            pseudopos = []
            for i,axis in enumerate(self.pseudo_positioners):
                # when looping over the axis that we want to set
                # add pos passed by the user
                if axis.name == axis_pt.name:
                    pseudopos.append(pos)
                # else just read the motor position
                else:
                    pseudopos.append(self.read()[axis.name]['value'])
            # calculate real position from pseudo positions
            rpos = self.forward(pseudopos)
            # now loop over real motors to set them
            for i,axis in enumerate(self.real_positioners):
                axis.set_current_position(rpos[i])


