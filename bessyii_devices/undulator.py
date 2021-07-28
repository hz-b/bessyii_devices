from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device
from ophyd import Component as Cpt


# Based on U17IT6R. See http://wiki.trs.bessy.de/pub/IDs/WebHome/UserPanelsEnglisch.pdf for notes

class Undulator(Device):

    """
    Object to query undulator status
    """
    
    # Setpoint and Config
    gap             = Cpt(EpicsSignal,   'BaseIPmGap.A', write_pv='BaseParGapsel.B',kind = 'hinted', labels={"motors", "undulators"})
    gap_velocity    = Cpt(EpicsSignal,    'DiagPhyVelSet'                   ,kind = 'config' )
    gap_delta       = Cpt(EpicsSignal,    'BaseParGapTrs'                   ,kind = 'config' )
    return_pos      = Cpt(EpicsSignal,    'BaseHomeRPos.A'                  ,kind = 'config' )
    
    # Commands
    id_control      = Cpt(EpicsSignal,    'BaseCmdLswitch'                  ,kind = 'config' )   # allows us to select control from the panel or from the monochromator panel
    cmd_stop        = Cpt(EpicsSignal,    'BaseCmnUsrStop',string='True'    ,kind = 'config' )   # an bo record that lets us stop or start (1=stopped, 0=enabled)
    cmd_sel         = Cpt(EpicsSignal,    'BaseCmdMcmd'   ,string='True'    ,kind = 'config' )   # an mbbo record that lets us select what we are going to do
    cmd_exec        = Cpt(EpicsSignal,    'BaseCmdCalc.PROC'                                 )   # processing this record will enact whatever is selected by cmd_sel
    
    # Readback
    harmonic_01_eV  = Cpt(EpicsSignalRO,  'BasePmEnergy'                    ,kind = 'hinted' )   # approximated energy of the 1stharmonic with standard electron beam condition
    harmonic_01_nM  = Cpt(EpicsSignalRO,  'BasePmWLength'                   ,kind = 'hinted' )   
    status          = Cpt(EpicsSignalRO,  'BaseStatISLbl' ,string='True'    ,kind = 'config' )   # Stop = done  (could use this for a pv-positioner, generally we let the mono take control though)
