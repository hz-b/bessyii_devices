from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device
from ophyd import Component as Cpt


# Based on U17IT6R. See http://wiki.trs.bessy.de/pub/IDs/WebHome/UserPanelsEnglisch.pdf for notes
class UndulatorGap(PVPositioner):

    """
    Object to query undulator status
    """
    def __init__(self, prefix, *args, **kwargs):
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name 
    
    setpoint        = Cpt(EpicsSignal,    'BaseParGapsel.B',kind = 'config')
    readback        = Cpt(EpicsSignalRO,  'BaseIPmGap.A',labels={"motors", "undulators"},kind = 'hinted')
    done            = Cpt(EpicsSignalRO,  'BaseStatISLbl' ,string='True'    ,kind = 'config' )
    actuate         = Cpt(EpicsSignal,    'BaseCmdCalc.PROC'  , kind = 'config'                     )
    done_value      = 'STOP'
    cmd             = Cpt(EpicsSignal,    'BaseCmdMcmd',string ='True', kind ='config' )
    
    vel = Cpt(EpicsSignal,    'DiagPhyVelSet', kind ='config' )
    delta = Cpt(EpicsSignal,    'BaseParGapTrs', kind ='config' )
        
    # Readback
    harmonic_01_eV  = Cpt(EpicsSignalRO,  'BasePmEnergy'                    ,kind = 'config' )   # approximated energy of the 1stharmonic with standard electron beam condition
    harmonic_01_nM  = Cpt(EpicsSignalRO,  'BasePmWLength'                   ,kind = 'config' )   

    read_attrs=['readback']
    
    def stage(self):

        self.cmd.set('START')      # update the EPICS PV as quick as we can
        
        super().stage()


class UndulatorShift(PVPositioner):
    
    
    def __init__(self, prefix, *args, **kwargs):
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name 
    
    setpoint        = Cpt(EpicsSignal,    'SBaseParGapsel.B',kind = 'config')
    readback        = Cpt(EpicsSignalRO,  'SBaseIPmGap.E',kind = 'hinted') # parrallel
    done            = Cpt(EpicsSignalRO,  'SBaseStatISLbl' ,string='True', kind = 'config' )
    actuate         = Cpt(EpicsSignal,    'SBaseCmdCalc.PROC' , kind = 'config'  ) # this will only work if the command is set to "START"
    done_value      = 'STOP'
    
    readback_anti   = Cpt(EpicsSignalRO,  'SBaseIPmGap.F',kind = 'config') # anti_parrallel
    cmd             = Cpt(EpicsSignal,    'SBaseCmdMcmd',string ='True', kind ='config' )
        
    vel = Cpt(EpicsSignal,    'SDiagPhyVelSet', kind ='config' )
    delta = Cpt(EpicsSignal,    'SBaseParGapTrs', kind ='config' )
    
    read_attrs=['readback']
    
    def stage(self):

        self.cmd.set('START')      # update the EPICS PV as quick as we can
        
        super().stage()


class UndulatorBase(Device): # PlanarDevice
    
    gap = Cpt(UndulatorGap, '')
    
    # Commands
    id_control      = Cpt(EpicsSignal,    'BaseCmdLswitch'                  ,kind = 'config' )   # allows us to select control from the panel or from the monochromator panel
    cmd_stop        = Cpt(EpicsSignal,    'BaseCmnUsrStop',string='True'    ,kind = 'config' )   # an bo record that lets us stop or start (1=stopped, 0=enabled)
    cmd_sel         = Cpt(EpicsSignal,    'BaseCmdMcmd'   ,string='True'    ,kind = 'config' )   # an mbbo record that lets us select what we are going to do
    
    # Readback
    harmonic_01_eV  = Cpt(EpicsSignalRO,  'BasePmEnergy'                    ,kind = 'config' )   # approximated energy of the 1stharmonic with standard electron beam condition
    harmonic_01_nM  = Cpt(EpicsSignalRO,  'BasePmWLength'                   ,kind = 'config' )   
    
    read_attrs = ['gap','harmonic_01_eV']
    

class HelicalUndulator(UndulatorBase):
    
    shift = Cpt(UndulatorShift, '') # include it as a device
    
    read_attrs = ['gap','shift','harmonic_01_eV']


class UndulatorMetrixs(UndulatorBase):

    gap_velocity    = Cpt(EpicsSignal  , 'DiagVelSet.A'                  , kind = 'config', labels={"motors", "undulators"}) # this is different compared to 
    

class UndulatorUE52(HelicalUndulator):
  
    gap_velocity     = Cpt(EpicsSignal,    'DiagPhyVelSet', kind ='config', labels={"motors", "undulators"}) # shall we put velocity and delta into 'UndulatorGap'?
    gap_delta        = Cpt(EpicsSignal,    'BaseParGapTrs', kind ='config', labels={"motors", "undulators"})
    
    mode             = Cpt(EpicsSignal,  'DiagTmdSet',kind = 'config') # where shall this be put? 
    couple_gap_shift = Cpt(EpicsSignal,  'DiagCplSet',kind = 'config') # where shall this be put? Do we need this?
    dynamic_vel      = Cpt(EpicsSignal,  'SBaseCmdDriveMode',kind = 'config') # where shall this be put? Do we need this?
    

