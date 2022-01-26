from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FCpt
from .axes import HexapodAxis, M1AxisAquarius, AxisTypeA

        
# This class can be used for any M3 and M4 mirror of U17 and Ue48 CAT, SISSY I and SISSY II

#prefix list U17
# M3 SISSY: HEX3OS12L
# M3 CAT: HEX3OS12L
# for M3 same as for M4:
# HEX3OS12L:hexapod:mbboMirrorChoicerRun

# M4 SISSY I-II: HEX5OS12L
# to choose M4 SISSY II or II I have to write and read to this pv
# HEX5OS12L:hexapod:mbboMirrorChoicerRun,
# it takes ascii charcater either "SISSY I", or "SISSY II"

# M4 CAT: HEX8OS12L

#prefix list UE48
# prefix list UE48 # to be reviewed with ELA
# M3 SISSY: HEX1OS12L:
# M4 SISSY: HEX6OS12L # this could be I, and I miss II
# M3 CAT: HEX4OS12L
# M4 CAT: HEX7OS12L

#HEX3OS12L:hexapod:mbboMirrorChoicerRun



class SMUChoice(PVPositioner):

    
    setpoint = Cpt(EpicsSignal,    'hexapod:mbboMirrorChoicerRun'               )                   
    readback = Cpt(EpicsSignalRO,  'hexapod:mbboMirrorChoicerRun',string='True', kind='hinted', labels={"mirrors", "SMU"})
    done     = Cpt(EpicsSignalRO,  'multiaxis:running'                  )
    
    done_value = 0

                
class M3M4(Device):
#move simulataneously does not work unless you activate the start_immediately PV        
    rx = Cpt(HexapodAxis, '', ch_name='A', labels={"mirrors"})
    ry = Cpt(HexapodAxis, '', ch_name='B', labels={"mirrors"})
    rz = Cpt(HexapodAxis, '', ch_name='C', labels={"mirrors"})
    tx = Cpt(HexapodAxis, '', ch_name='X', labels={"mirrors"})
    ty = Cpt(HexapodAxis, '', ch_name='Y', labels={"mirrors"})
    tz = Cpt(HexapodAxis, '', ch_name='Z', labels={"mirrors"})
    start_immediately = Cpt(EpicsSignal, 'hexapod:mbboRunAfterValue')
    
class SMU(M3M4):

    choice = Cpt(SMUChoice,'')
    
    
    
class SMUAquariusPGM1(Device):

    tx   = Cpt(M1AxisAquarius, 'M2', labels={"mirrors"})
    rx   = Cpt(M1AxisAquarius, 'M3', labels={"mirrors"})
    ry   = Cpt(M1AxisAquarius, 'M4', labels={"mirrors"})
    rz   = Cpt(M1AxisAquarius, 'M5', labels={"mirrors"})

class SMUAquariusPGM2(Device):

    tx   = Cpt(M1AxisAquarius, 'M6', labels={"mirrors"})
    rx   = Cpt(M1AxisAquarius, 'M7', labels={"mirrors"})
    ry   = Cpt(M1AxisAquarius, 'M8', labels={"mirrors"})
    rz   = Cpt(M1AxisAquarius, 'M9', labels={"mirrors"})
    
    


class SMUMetrixs(Device):

    tx   = Cpt(AxisTypeA, '', ch_name='M2', labels={"mirrors"})
    rx   = Cpt(AxisTypeA, '', ch_name='M3', labels={"mirrors"})
    ry   = Cpt(AxisTypeA, '', ch_name='M4', labels={"mirrors"})
    rz   = Cpt(AxisTypeA, '', ch_name='M5', labels={"mirrors"})

