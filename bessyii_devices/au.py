from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FCpt
from .axes import AxisTypeA, AxisTypeB

# This class can be used for the motorized aperture (SLITS) AU1 and AU3
# Starting from those motors we shoudl define gap and offset as pseudo motors

# BlueSky should follow always the same conventions for the slits: 
# we look downstream and use top/bottom/left/right


#prefix list 
#prefix: AUYU15L

#Readback 		AUYU15L:Top.RBV
#Set			AUYU15L:Top.VAL
#Set range		AUYU15L:Top.TWV
#Status 			AUYU15L:Top.STOP
#Stop			AUYU15L:Top.stMotor


class AU13(Device):
    _default_read_attrs = ['top.readback', 'bottom.readback', 'left.readback', 'right.readback']
    top         = Cpt(AxisTypeA, 'Top')
    bottom      = Cpt(AxisTypeA, 'Bottom')
    left        = Cpt(AxisTypeA, 'Left') 
    right       = Cpt(AxisTypeA, 'Right') 
    


    
 
