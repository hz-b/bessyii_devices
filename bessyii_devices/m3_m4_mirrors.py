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

from ophyd import PseudoPositioner, PseudoSingle, PositionerBase, Signal, InternalSignal
from .positioners import  InternalSignal


class M3M4(PseudoPositioner):
    
    rx = Cpt(PseudoSingle)
    ry = Cpt(PseudoSingle)
    rz = Cpt(PseudoSingle)
    tx = Cpt(PseudoSingle)
    ty = Cpt(PseudoSingle)
    tz = Cpt(PseudoSingle)

    #Real Axes
    rrx = Cpt(HexapodAxis, '', ch_name='A', labels={"mirrors"},kind='normal')
    rry = Cpt(HexapodAxis, '', ch_name='B', labels={"mirrors"},kind='normal')
    rrz = Cpt(HexapodAxis, '', ch_name='C', labels={"mirrors"},kind='normal')
    rtx = Cpt(HexapodAxis, '', ch_name='X', labels={"mirrors"},kind='normal')
    rty = Cpt(HexapodAxis, '', ch_name='Y', labels={"mirrors"},kind='normal')
    rtz = Cpt(HexapodAxis, '', ch_name='Z', labels={"mirrors"},kind='normal')
    
    start_immediately = Cpt(EpicsSignal, 'hexapod:mbboRunAfterValue', kind = 'omitted')
    do_it = Cpt(EpicsSignal, 'hexapod:setPoseA.PROC', kind = 'omitted')
    multiaxis_running = Cpt(EpicsSignalRO,   'multiaxis:running' , kind='omitted'         )

    @pseudo_position_argument
    def forward(self, pseudo_pos):
        '''Run a forward (pseudo -> real) calculation'''
        return self.RealPosition(pseudo_pos)

    @real_position_argument
    def inverse(self, real_pos):
        '''Run an inverse (real -> pseudo) calculation'''
        return self.PseudoPosition(real_pos)

    def _concurrent_move(self, real_pos, **kwargs):
        '''Move all real positioners to a certain position, in parallel'''
    
        self.start_immediately.put(0)
        for real, value in zip(self._real, real_pos):
            self.log.debug('[concurrent] Moving %s to %s', real.name, value)
            real.setpoint.put(value)
        
        self.start_immediately.put(1)
        self.do_it.put(1)

        #Now having put the values to the axes we need to set a done signal to 0, then initiate the move and add a callback which will
        # move the done write 

    def _real_finished(self, *args,**kwargs):
        '''Callback: A single real positioner has finished moving. 	Used for asynchronous motion, if all have finished moving 	then fire a callback (via Positioner._done_moving)'''
        with self._finished_lock:
                if self.multiaxis_running.get() == 0:
                        self._done_moving()

    def __init__(self, prefix, **kwargs):
        super().__init__(prefix, **kwargs)
        self.multiaxis_running.subscribe(self._real_finished)



  
        


    



    
        


    
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


# used for METRIXS and UE52-SGM
class SMUMetrixs(Device):

    tx   = Cpt(AxisTypeA, '', ch_name='M2', labels={"mirrors"})
    rx   = Cpt(AxisTypeA, '', ch_name='M3', labels={"mirrors"})
    ry   = Cpt(AxisTypeA, '', ch_name='M4', labels={"mirrors"})
    rz   = Cpt(AxisTypeA, '', ch_name='M5', labels={"mirrors"})

