from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device
from ophyd import Component as Cpt


# Based on U17IT6R. See http://wiki.trs.bessy.de/pub/IDs/WebHome/UserPanelsEnglisch.pdf for notes
# prefix: U49ID8R:

# this is for emil
class Undulator(PVPositioner):

    """
    Object to query undulator status
    """
    def __init__(self, prefix, *args, **kwargs):
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name 
    
    setpoint        = Cpt(EpicsSignal,    'BaseParGapsel.B',kind = 'hinted')
    readback        = Cpt(EpicsSignalRO,  'BaseIPmGap.A',kind = 'hinted', labels={"motors", "undulators"})
    done            = Cpt(EpicsSignalRO,  'BaseStatISLbl' ,string='True'    ,kind = 'config' )
    actuate         = Cpt(EpicsSignal,    'BaseCmdCalc.PROC'                                 )

    # Setpoint and Config
    gap_velocity    = Cpt(EpicsSignal,    'DiagPhyVelSet'                   ,kind = 'config' )
    gap_delta       = Cpt(EpicsSignal,    'BaseParGapTrs'                   ,kind = 'config' )
    return_pos      = Cpt(EpicsSignal,    'BaseHomeRPos.A'                  ,kind = 'config' )
    
    # Commands
    id_control      = Cpt(EpicsSignal,    'BaseCmdLswitch'                  ,kind = 'config' )   # allows us to select control from the panel or from the monochromator panel
    cmd_stop        = Cpt(EpicsSignal,    'BaseCmnUsrStop',string='True'    ,kind = 'config' )   # an bo record that lets us stop or start (1=stopped, 0=enabled)
    cmd_sel         = Cpt(EpicsSignal,    'BaseCmdMcmd'   ,string='True'    ,kind = 'config' )   # an mbbo record that lets us select what we are going to do
    
    # Readback
    harmonic_01_eV  = Cpt(EpicsSignalRO,  'BasePmEnergy'                    ,kind = 'hinted' )   # approximated energy of the 1stharmonic with standard electron beam condition
    harmonic_01_nM  = Cpt(EpicsSignalRO,  'BasePmWLength'                   ,kind = 'hinted' )   





