from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device, EpicsMotor
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FCpt
from .axes import AxisTypeA, AxisTypeB, AxisTypeD
from ophyd import (PseudoPositioner, PseudoSingle, EpicsMotor)
from ophyd.pseudopos import (pseudo_position_argument,
                             real_position_argument)

# This class can be used for the motorized aperture (SLITS) AU1 and AU3
# Starting from those motors we shoudl define gap and offset as pseudo motors

# BlueSky should follow always the same conventions for the slits: 
# we look downstream and use top/bottom/left/right


# EMIL

#prefix list U17
# AU1: WAUY02U012L
# AU3: AUY01U212L


# prefix list UE48:
# AU1: WAUY01U012L
# AU3 SISSY: AUY02U112L   
# AU3 CAT: AUY02U212L


class AU13(Device):
    _default_read_attrs = ['top.readback', 'bottom.readback', 'left.readback', 'right.readback']
    top         = Cpt(AxisTypeA, '', ch_name='M1', labels={"apertures"})
    bottom      = Cpt(AxisTypeA, '', ch_name='M2', labels={"apertures"})
    left        = Cpt(AxisTypeA, '', ch_name='M3', labels={"apertures"}) # wall in old convention
    right       = Cpt(AxisTypeA, '', ch_name='M4', labels={"apertures"}) #ring in old convention
    

#prefix list U17
# AU2: u171pgm1


# prefix list UE48
# AU2: ue481pgm1

    
class AU2(Device):
    
    _default_read_attrs = ['top.readback', 'bottom.readback', 'left.readback', 'right.readback']
    top         = Cpt(AxisTypeB,      'PH_2', labels={"apertures"})
    bottom      = Cpt(AxisTypeB,      'PH_3', labels={"apertures"})
    left        = Cpt(AxisTypeB,      'PH_4', labels={"apertures"}) # wall in old convention
    right       = Cpt(AxisTypeB,      'PH_5', labels={"apertures"}) #ring in old convention

# EMIL STXM 
class STXM(Device):
    
    _default_read_attrs = ['h_trans.readback', 'h_sw.readback', 'v_sw.readback', 'b_axis.readback', 'piezo.readback']
    h_trans   = Cpt(AxisTypeB,      'PH_0', labels={"slit"}) # horizontal translation
    h_sw      = Cpt(AxisTypeB,      'PH_1', labels={"slit"}) # horizontal slitwidth
    v_sw      = Cpt(AxisTypeB,      'PH_2', labels={"slit"}) # vertical slitwidth
    b_axis    = Cpt(AxisTypeB,      'PH_3', labels={"slit"}) # beam-axis
    piezo     = Cpt(AxisTypeB,      'PH_4', labels={"slit"}) # piezo


#AQUARIUS
#prefix list 
#prefix: AUYU15L

#Readback 		AUYU15L:Top.RBV
#Set			AUYU15L:Top.VAL
#Set range		AUYU15L:Top.TWV
#Status 			AUYU15L:Top.STOP
#Stop			AUYU15L:Top.stMotor


# AQUARIUS
class AU1Aquarius(Device):
    _default_read_attrs = ['top.readback', 'bottom.readback', 'left.readback', 'right.readback']
    top         = Cpt(AxisTypeD, 'Top')
    bottom      = Cpt(AxisTypeD, 'Bottom')
    left        = Cpt(AxisTypeD, 'Left') 
    right       = Cpt(AxisTypeD, 'Right') 




# METRIXS
class AU1Metrixs(Device):
    _default_read_attrs = ['top.readback', 'bottom.readback', 'left.readback', 'right.readback']
    top         = Cpt(AxisTypeD, 'AUTOPES6L')
    bottom      = Cpt(AxisTypeD, 'AUBOTES6L')
    left        = Cpt(AxisTypeD, 'AUWALLES6L') 
    right       = Cpt(AxisTypeD, 'AURINGES6L') 



# mySpot


class AUmySpot(PseudoPositioner):
    ''' This class implements apertures with four blades (top, bottom, left, right)
    and four pseudo motors (htop,hoffset,vgap,voffset)
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
