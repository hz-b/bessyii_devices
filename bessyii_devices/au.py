from ophyd import EpicsSignal, EpicsSignalRO
from bessyii_devices.epics_motor import EpicsMotorBessy
from bessyii_devices.device import BESSYDevice

from bessyii_devices.positioners import PseudoPositionerBessy
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FCpt
from .axes import AxisTypeA, AxisTypeB, AxisTypeD
from ophyd.pseudopos import (pseudo_position_argument,
                             real_position_argument)
from ophyd.pseudopos import PseudoSingle

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
class AU4(BESSYDevice):

    top = Cpt(EpicsMotorBessy, "M3", labels={"apertures"})
    bottom = Cpt(EpicsMotorBessy, "M1", labels={"apertures"})
    left = Cpt(EpicsMotorBessy, "M2", labels={"apertures"})
    right = Cpt(EpicsMotorBessy, "M0", labels={"apertures"})

class AU13(BESSYDevice):
    #_default_read_attrs = ['top.readback', 'bottom.readback', 'left.readback', 'right.readback']
    top         = Cpt(AxisTypeA, '', ch_name='M1',restore_readback=True, labels={"apertures"})
    bottom      = Cpt(AxisTypeA, '', ch_name='M2',restore_readback=True, labels={"apertures"})
    left        = Cpt(AxisTypeA, '', ch_name='M3',restore_readback=True, labels={"apertures"}) # wall in old convention
    right       = Cpt(AxisTypeA, '', ch_name='M4',restore_readback=True, labels={"apertures"}) #ring in old convention
    

#prefix list U17
# AU2: u171pgm1


# prefix list UE48
# AU2: ue481pgm1

    
class AU2(BESSYDevice):
    
    #_default_read_attrs = ['top.readback', 'bottom.readback', 'left.readback', 'right.readback']
    top         = Cpt(AxisTypeB,      'PH_2',restore_readback=True, labels={"apertures"})
    bottom      = Cpt(AxisTypeB,      'PH_3',restore_readback=True, labels={"apertures"})
    left        = Cpt(AxisTypeB,      'PH_4',restore_readback=True, labels={"apertures"}) # wall in old convention
    right       = Cpt(AxisTypeB,      'PH_5',restore_readback=True, labels={"apertures"}) #ring in old convention

# EMIL STXM Horizontal slit
class STXM_HS(BESSYDevice):
    
    #_default_read_attrs = ['trans.readback', 'width.readback', 'b_axis.readback' ]
    trans   = Cpt(AxisTypeB,      'PH_0',restore_readback=True, labels={"slit"}) # horizontal translation
    width      = Cpt(AxisTypeB,      'PH_1',restore_readback=True, labels={"slit"}) # horizontal slitwidth
    b_axis    = Cpt(AxisTypeB,      'PH_3',restore_readback=True, labels={"slit"}) # beam-axis
    


#AQUARIUS
#prefix list 
#prefix: AUYU15L

#Readback 		AUYU15L:Top.RBV
#Set			AUYU15L:Top.VAL
#Set range		AUYU15L:Top.TWV
#Status 			AUYU15L:Top.STOP
#Stop			AUYU15L:Top.stMotor

# AQUARIUS
class AU1Aquarius(BESSYDevice):
    _default_read_attrs = ['top.readback', 'bottom.readback', 'left.readback', 'right.readback']
    top         = Cpt(AxisTypeD, 'Top')
    bottom      = Cpt(AxisTypeD, 'Bottom')
    left        = Cpt(AxisTypeD, 'Left') 
    right       = Cpt(AxisTypeD, 'Right') 



# METRIXS
# not in use since end of shutdown august 2020 
class AU1Metrixs(BESSYDevice):
    _default_read_attrs = ['top.readback', 'bottom.readback', 'left.readback', 'right.readback']
    top         = Cpt(AxisTypeD, 'AUTOPES6L')
    bottom      = Cpt(AxisTypeD, 'AUBOTES6L')
    left        = Cpt(AxisTypeD, 'AUWALLES6L') 
    right       = Cpt(AxisTypeD, 'AURINGES6L') 

# METRIXS Spectrometer AU
class AUspecMETRIXS(BESSYDevice):
    #_default_read_attrs = ['top.user_readback', 'bottom.user_readback', 'left.user_readback', 'right.user_readback']
    top    = Cpt(EpicsMotor, 'Blade-Up', labels={"aperture"})
    bottom = Cpt(EpicsMotor, 'Blade-Down', labels={"aperture"})
    left   = Cpt(EpicsMotor, 'Blade-Wall', labels={"aperture"})
    right  = Cpt(EpicsMotor, 'Blade-Ring', labels={"aperture"})


    
# UE52-SGM
class AU1UE52SGM(BESSYDevice):
    _default_read_attrs = ['top.readback', 'bottom.readback', 'left.readback', 'right.readback']
    top         = Cpt(AxisTypeD, '0')
    bottom      = Cpt(AxisTypeD, '1')
    left        = Cpt(AxisTypeD, '4') 
    right       = Cpt(AxisTypeD, '5') 

class AU1UE52SGM(PseudoPositionerBessy):
    ''' This class implements apertures with four blades (top, bottom, left, right)
    and four pseudo motors (htop,hoffset,vgap,voffset)
    '''

    # The pseudo positioner axes:
    hgap    = Cpt(PseudoSingle)
    vgap    = Cpt(PseudoSingle)
    hoffset = Cpt(PseudoSingle)
    voffset = Cpt(PseudoSingle)

    # The real (or physical) positioners:
    top         = Cpt(AxisTypeD, '0')
    bottom      = Cpt(AxisTypeD, '1')
    right       = Cpt(AxisTypeD, '4')
    left        = Cpt(AxisTypeD, '5')
    
    @pseudo_position_argument
    def forward(self, pseudo_pos):
        '''Run a forward (pseudo -> real) calculation'''
        return self.RealPosition(top    = pseudo_pos.voffset+pseudo_pos.vgap/2,
                                 bottom = pseudo_pos.voffset-pseudo_pos.vgap/2,
                                 right  = pseudo_pos.hoffset+pseudo_pos.hgap/2,
                                 left   = pseudo_pos.hoffset-pseudo_pos.hgap/2
                                 )

    @real_position_argument
    def inverse(self, real_pos):
        '''Run an inverse (real -> pseudo) calculation'''
        return self.PseudoPosition(hgap    = -real_pos.left+real_pos.right,
                                   hoffset = (real_pos.right+real_pos.left)/2,
                                   vgap    = real_pos.top-real_pos.bottom,
                                   voffset = (real_pos.top+real_pos.bottom)/2  
                                   )



    
    
# Note: Shall we add labels here? Then it is easier to read/find the devices using magics
