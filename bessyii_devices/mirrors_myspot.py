from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device, EpicsMotor
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FCpt
from .axes import AxisTypeA, AxisTypeB, AxisTypeD
from ophyd import (PseudoPositioner, PseudoSingle, EpicsMotor)
from ophyd.pseudopos import (pseudo_position_argument,
                             real_position_argument)


class M1mySpot(PseudoPositioner):
    ''' This class does cool stuff!
    '''
    # The pseudo positioner axes:
    hgap    = Cpt(PseudoSingle)
    vgap    = Cpt(PseudoSingle)
    hoffset = Cpt(PseudoSingle)
    voffset = Cpt(PseudoSingle)

    # The real (or physical) positioners:
    top    = Cpt(EpicsMotor, 'l0204000')
    bottom = Cpt(EpicsMotor, 'l0204001')
    left   = Cpt(EpicsMotor, 'l0204002')
    right  = Cpt(EpicsMotor, 'l0204003')


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
        return self.PseudoPosition(hgap    = real_pos.right+real_pos.left,
                                   hoffset = (real_pos.right-real_pos.left)/2,
                                   vgap    = real_pos.top+real_pos.bottom,
                                   voffset = (real_pos.top-real_pos.bottom)/2  
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
