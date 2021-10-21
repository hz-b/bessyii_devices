from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device
from ophyd import Component as Cpt
from ophyd import FormattedComponent as FCpt
from .positioners import PVPositionerComparator


# This class can be used for the Exit Slits

class ExitSlit(PVPositionerComparator):
    setpoint         = Cpt(EpicsSignal,   '_Input'           ) # in micrometer
    readback         = Cpt(EpicsSignalRO, '_SW',kind='hinted', labels={"motors", "exitslits"}) # in micrometer
#    done             = Cpt(EpicsSignalRO,    '_REF_STAT' )
    
    bandwidth        = Cpt(EpicsSignalRO, '_BW') # in meV
    resolving_power  = Cpt(EpicsSignalRO, '_ResPow') 

    atol = 1  # tolerance before we set done to be 1 (in um) we should check what this should be!

    def done_comparator(self, readback, setpoint):
        return setpoint-self.atol < readback < setpoint+self.atol
    
    def __init__(self, prefix, ch_name=None, **kwargs):
        self._ch_name = ch_name
        super().__init__(prefix, **kwargs)


class ExitSlit_withDone(PVPositioner):
    '''
    This would be the correct way to do it but the done signal oscillates.
    '''
    setpoint         = FCpt(EpicsSignal,   '{self.prefix}ES_{self._ch_number}_Input'           ) # in micrometer
    readback         = FCpt(EpicsSignalRO, '{self.prefix}ES_{self._ch_number}_SW',kind='hinted', labels={"motors", "exitslits"}) # in micrometer
    done             = FCpt(EpicsSignalRO, '{self.prefix}axis{self._axis_number}:running' )
    
    bandwidth        = FCpt(EpicsSignalRO, '{self.prefix}ES_{self._ch_number}_BW') # in meV
    resolving_power  = FCpt(EpicsSignalRO, '{self.prefix}ES_{self._ch_number}_ResPow') 

    def __init__(self, prefix, ch_number=None, axis_number=None, **kwargs):
        self._ch_number = ch_number
        self._axis_number=axis_number
        super().__init__(prefix, **kwargs)
