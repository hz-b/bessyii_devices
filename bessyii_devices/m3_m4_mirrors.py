from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device, EpicsMotor
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FCpt
from bessyii_devices.axes import HexapodAxis, M1AxisAquarius, AxisTypeA
from ophyd import PseudoPositioner,PseudoSingle, PositionerBase, Signal
from bessyii_devices.positioners import  InternalSignal
from ophyd.pseudopos import (pseudo_position_argument,
                             real_position_argument)

        
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

class SMUChoiceCoordSysPositions(Device):
    
    """
    A class to capture the positions that are moved to for each co-ordinate system
    
    x: tx
    y: ty
    z: tz
    a: rx
    b: ry
    c: rz
    
    """
    x = FCpt(EpicsSignal, '{self.prefix}hexapod:getMir{self.mirror}PoseUserX', write_pv ='{self.prefix}hexapod:setMir{self.mirror}PoseUserX' , kind='config')
    y = FCpt(EpicsSignal, '{self.prefix}hexapod:getMir{self.mirror}PoseUserY', write_pv ='{self.prefix}hexapod:setMir{self.mirror}PoseUserY' , kind='config')
    z = FCpt(EpicsSignal, '{self.prefix}hexapod:getMir{self.mirror}PoseUserZ', write_pv ='{self.prefix}hexapod:setMir{self.mirror}PoseUserZ' , kind='config')
    a = FCpt(EpicsSignal, '{self.prefix}hexapod:getMir{self.mirror}PoseUserA', write_pv ='{self.prefix}hexapod:setMir{self.mirror}PoseUserA' , kind='config')
    b = FCpt(EpicsSignal, '{self.prefix}hexapod:getMir{self.mirror}PoseUserB', write_pv ='{self.prefix}hexapod:setMir{self.mirror}PoseUserB' , kind='config')
    c = FCpt(EpicsSignal, '{self.prefix}hexapod:getMir{self.mirror}PoseUserC', write_pv ='{self.prefix}hexapod:setMir{self.mirror}PoseUserC' , kind='config')

    
    def __init__(self, prefix, mirror=None, **kwargs):
        self.mirror = mirror
        super().__init__(prefix, **kwargs)
        

class SMU2Choice(PVPositioner):

    """
    A Positioner to change co-ordinate systems for an SMU
    """
    setpoint = Cpt(EpicsSignal,    'hexapod:mbboMirrorChoicerRun'               )                   
    readback = Cpt(EpicsSignalRO,  'hexapod:mbboMirrorChoicerRun',string='True', kind='hinted', labels={"mirrors", "SMU"})
    done     = Cpt(EpicsSignalRO,  'multiaxis:running'                  )
    pmac = Cpt(EpicsSignal, 'pmac.AOUT',string='True', kind = 'omitted') #send &1a to clear errors

    pos1 = Cpt(SMUChoiceCoordSysPositions,'',mirror=1,kind = 'config')
    pos2 = Cpt(SMUChoiceCoordSysPositions,'',mirror=2,kind = 'config')

    done_value = 0
    
    def _setup_move(self, position):
        '''Move and do not wait until motion is complete (asynchronous)'''
        self.log.debug('%s.setpoint = %s', self.name, position)
        self.pmac.put('&1a') #clear any errors
        self.setpoint.put(position, wait=True)
        
        if self.actuate is not None:
            self.log.debug('%s.actuate = %s', self.name, self.actuate_value)
            self.actuate.put(self.actuate_value, wait=False)

class SMU3Choice(SMU2Choice):
    
    """
    An extra position 
    """
    pos3 = Cpt(SMUChoiceCoordSysPositions,'',mirror=3,kind = 'config')

    
class Hexapod(PseudoPositioner):
    """
    
    A class for all hexapods controlled by geo-brick motion controllers
    Using a PseudoPositioner allows us to read and set positions as groups like this:
    
      hex.move(tx,ty,tz,rx,ry,rz)
    
    as well as individually like:
    
      hex.ty.move(3700)
    
    The _concurrent_move method is rewritten to allow all axes to be written first before the move is executed.
    
    The error bits from the axes are reset before each move by sending the command '&1a' to the geobrick
    
    Note, if you are doing a mesh scan with an instance of this class, you should use 'snake' so that only one axes is moved at once
    
    
    """
    #Pseudo Axes
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
    pmac = Cpt(EpicsSignal, 'pmac.AOUT',string='True', kind = 'omitted') #send &1a to clear errors before any move

    @pseudo_position_argument
    def forward(self, pseudo_pos):
        '''Run a forward (pseudo -> real) calculation'''
        return self.RealPosition(rrx=pseudo_pos.rx,
                                 rry=pseudo_pos.ry,
                                 rrz=pseudo_pos.rz,
                                 rtx=pseudo_pos.tx,
                                 rty=pseudo_pos.ty,
                                 rtz=pseudo_pos.tz
                                 )


    @real_position_argument
    def inverse(self, real_pos):
        '''Run an inverse (real -> pseudo) calculation'''
        return self.PseudoPosition(rx=real_pos.rrx,
                                 ry=real_pos.rry,
                                 rz=real_pos.rrz,
                                 tx=real_pos.rtx,
                                 ty=real_pos.rty,
                                 tz=real_pos.rtz
                                 )

    def _concurrent_move(self, real_pos, **kwargs):
        '''Move all real positioners to a certain position, in parallel'''
        
        self.pmac.put('&1a')
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
        #self.read_attrs = ['rtx','rty','rtz','rrx','rry','rrz']

        
    
    
class SMU2(Hexapod):

    """
    A hexapod that can change between two different co-ordinate systems
    """
    _real = ['rrx','rry','rrz','rtx','rty','rtz']
    choice = Cpt(SMU2Choice,'',kind="normal")
 
    
class SMU3(Hexapod):


    """
    A hexapod that can change between three different co-ordinate systems
    """
    _real = ['rrx','rry','rrz','rtx','rty','rtz']
    choice = Cpt(SMU3Choice,'')  

    
 
    
    
class SMUAquariusPGM1(Device):

    tx = Cpt(M1AxisAquarius, 'M2', labels={"mirrors"})
    rx = Cpt(M1AxisAquarius, 'M3', labels={"mirrors"})
    ry = Cpt(M1AxisAquarius, 'M4', labels={"mirrors"})
    rz = Cpt(M1AxisAquarius, 'M5', labels={"mirrors"})


class SMUAquariusPGM2(Device):

    tx = Cpt(M1AxisAquarius, 'M6', labels={"mirrors"})
    rx = Cpt(M1AxisAquarius, 'M7', labels={"mirrors"})
    ry = Cpt(M1AxisAquarius, 'M8', labels={"mirrors"})
    rz = Cpt(M1AxisAquarius, 'M9', labels={"mirrors"})


# used for METRIXS and UE52-SGM

#Metrixs implementation should be changed similar to ue52-sgm
class SMUMetrixs(Device):

    tx = Cpt(EpicsMotor, 'M2', labels={"mirrors"})
    rx = Cpt(EpicsMotor, 'M3', labels={"mirrors"})
    ry = Cpt(EpicsMotor, 'M4', labels={"mirrors"})
    rz = Cpt(EpicsMotor, 'M5', labels={"mirrors"})


class SMUUE52SGM(Device):

    tx   = Cpt(EpicsMotor, ":M2", name='tx')
    rx   = Cpt(EpicsMotor, ":M3", name='rx')
    ry   = Cpt(EpicsMotor, ":M4", name='ry')
    rz   = Cpt(EpicsMotor, ":M5", name='rz')
