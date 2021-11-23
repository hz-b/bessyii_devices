from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FCpt
from .axes import AxisTypeA, AxisTypeB, AxisTypeD

# This class can be used for the motorized aperture (SLITS) AU1 and AU3
# Starting from those motors we shoudl define gap and offset as pseudo motors

# BlueSky should follow always the same conventions for the slits: 
# we look downstream and use top/bottom/left/right


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



#AQUARIUS
#prefix list 
#prefix: AUYU15L

#Readback 		AUYU15L:Top.RBV
#Set			AUYU15L:Top.VAL
#Set range		AUYU15L:Top.TWV
#Status 			AUYU15L:Top.STOP
#Stop			AUYU15L:Top.stMotor


class AU1Aquarius(Device):
    _default_read_attrs = ['top.readback', 'bottom.readback', 'left.readback', 'right.readback']
    top         = Cpt(AxisTypeD, 'Top')
    bottom      = Cpt(AxisTypeD, 'Bottom')
    left        = Cpt(AxisTypeD, 'Left') 
    right       = Cpt(AxisTypeD, 'Right') 
    


    