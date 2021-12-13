"""
This file contains definitions for various BESSY II monochromators.
Most soft x-ray monochromators (both PGMs and SGMs) are having same API. 
There are few exceptions which later can be supported by "duck-typing" basic classes.
"""

class SoftMonoBase(PVPositioner):
    """
    SoftMonoBase is a core class which provides controls which are the same for all 
    standard BESSY soft x-ray monochromator, for both dipole and undulator beamlines.

    Generally all monochromators will have a possibility to:
    * set and read energy, energy ranges and etc
    * read (not always freely choose) c value
    * choose diffration order
    * ....
    """
    def __init__(self, prefix, *args, **kwargs):
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name 

    # this is an initial API 
    setpoint        = Cpt(EpicsSignal,      'monoSetEnergy'                                      )
    readback        = Cpt(EpicsSignalRO,    'monoGetEnergy', labels={"motors"},     kind='hinted') # the main output
    done            = Cpt(EpicsSignalRO,    'GK_STATUS'                                          )

    # AFAIK, for some monochromators cff is not a free choice parameter and can not be set.
    #cff             = Cpt(EpicsSignal, 'cff', write_pv='SetCff', kind='config')
    diff_order      = Cpt(EpicsSignal, 'Order',write_pv='SetOrder', kind='config')
    grating_no      = Cpt(EpicsSignal, 'SetGratingNo', string='True',kind='config')
    grating         = Cpt(EpicsSignalRO, 'lineDensity', kind='hinted') 

    eMin_eV         = Cpt(EpicsSignalRO, 'minEnergy', kind='hinted')
    eMax_eV         = Cpt(EpicsSignalRO, 'maxEnergy', kind='hinted')


    # slit driving is different at different monos
    #slitwidth       = Cpt(EpicsSignal,  'slitwidth', write_pv = 'SlitInput',     kind='config')


class UndulatorMonoBase(Device):
    """
    UndulatorMonoBase contains all additional signals used for monochromators at undulator beamlines. 
    It is intended to be used together with SoftMonoBase class
    """
    def __init__(self, prefix, *args, **kwargs):
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name 

    ID_on           = Cpt(EpicsSignal, 'SetIdOn', string='True',kind='config')
    mode            = Cpt(EpicsSignal, 'GetFormulaMode', write_pv = 'SetFormulaMode', string='True',kind='config') 
    table           = Cpt(EpicsSignal, 'idMbboIndex', string='True',kind='config')
    table_filename  = Cpt(EpicsSignalRO, 'idFilename', string='True',kind='config') 
    harmonic        = Cpt(EpicsSignal, 'GetIdHarmonic', write_pv = 'Harmonic', string='True',kind='config')

class ExitSlitBase(Device):
    """
    Base class stub (also standard API for many soft x-ray monos) for monochromator exit slit control

    TODO: some SGMs have also entrance slit - Epics API should be checked before finalizing API on ophyd side
    """
    slitwidth       = Cpt(EpicsSignal,  'slitwidth', write_pv = 'SetSlitWidth',     kind='config')
    # Many monos will allow also set "wish" energy resolution by driving exit slit. This shall be included in this class

class ExitSlitEMIL(ExitSlitBase):
    """
    EMIL specific exit slit implementation. EMIL beamlines uses different PV name for setting the slit
    """
    slitwidth       = Cpt(EpicsSignal,  'slitwidth', write_pv = 'SlitInput',     kind='config')


class PGM(SoftMonoBase):
    """
    PGM is a core class for PGM monochromators
    """

    # PGMs has a full control over cff, so override it here
    cff             = Cpt(EpicsSignal, 'cff', write_pv='SetCff', kind='config')


class SGM(SoftMonoBase):
    """
    SGM is a core class for SGM monochromators
    """
    cff             = Cpt(EpicsSignalRO, 'cff', kind='hinted')


# Example for final mono use
class PM4Mono(PGM,ExitSlitBase):
    """
    ophyd device class definition for PM4 monochromator
    """

# example for an undulator monocromator setup
class DummyUE521PGM(PGM,UndulatorMonoBase,ExitSlitBase):
    """
    ophyd device class definition for UE52/1-PGM monochromator
    """
