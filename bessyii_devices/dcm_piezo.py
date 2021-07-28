
from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device, DerivedSignal,PseudoPositioner,PseudoSingle,EpicsMotor
from ophyd import Component as Cpt
from ophyd.pseudopos import (pseudo_position_argument,
                             real_position_argument)
from ophyd.signal import Signal, SignalRO
import time

# The three conversion here below have been worked out by A.Gaupp on the basis
# of the technical drawings of the BESTEC DCM. I leave them here so that
# we already have them around. SV

class ConvertPitch(DerivedSignal):
    def inverse(self, c2_enc):
        ctmm  = 5.0e-6			#mm/count
        C2pitBesTecOffset = (3260320-3800000)
        C2rolBesTecOffset = (3263554-3800000)
        CT2BesTecOffset = (3220620-3800000)
        c2pit=c2pit*ctmm
        c2height=c2height*ctmm
        pitchangle = ((c2_enc[0] - C2pitBesTecOffset*ctmm)-(c2_enc[2] - CT2BesTecOffset*ctmm))/64.75*1000000.
        return pitchangle

class convertRoll(DerivedSignal):
    def inverse(self, c2_enc):
        ctmm  = 5.0e-6			#mm/count
        C2pitBesTecOffset = (3260320-3800000)
        C2rolBesTecOffset = (3263554-3800000)
        CT2BesTecOffset = (3220620-3800000)
        c2pit=c2pit*ctmm
        c2height=c2height*ctmm
        rollangle = ((c2roll - C2rolBesTecOffset*ctmm)-(c2height - CT2BesTecOffset*ctmm))/127.75*1000000
        return rollangle
    
class convertHeight(DerivedSignal):
    def inverse(self, c2_enc):
        ctmm  = 5.0e-6			#mm/count
        C2pitBesTecOffset = (3260320-3800000)
        C2rolBesTecOffset = (3263554-3800000)
        CT2BesTecOffset = (3220620-3800000)
        c2pit=c2pit*ctmm
        c2height=c2height*ctmm
        position = c2height - CT2BesTecOffset*ctmm
        return position

class DCMPiezo():    
    '''
    This is a non ideal implementation of the Piezo motors of the DCM.
    At the moment it is possible only to read the values
    '''
    #status (on/off) of parvathi feedback
    #c2pit_status    = Cpt(EpicsSignalRO,    'piezoPitchfbStatus',    kind='config')
    #c2roll_status   = Cpt(EpicsSignalRO,    'piezoRollfbStatus',    kind='config')
    
    #target value for parvathis's feedback 
    #c2pit_target    = Cpt(EpicsSignalRO,    'SetPointpiezoPitch',    kind='config')
    #c2roll_target   = Cpt(EpicsSignalRO,    'SetPointpiezoRoll',    kind='config')
    
    #TO BE TESTED, why there is prefix:dcm:-suffix???
    # These epics-pv will return an encoder values in steps.
    # AG wrote a rountine to convert them in mm and microrad
    # in emil17 computer in /home/specadm/macros/U17DCM.mac, line 2160
    # Pitch Encoder, u171dcm1:dcm:cr2PitchEncoder
    c2pit           = Cpt(EpicsSignalRO,    'dcm:cr2PitchEncoder')
    c2roll           = Cpt(EpicsSignalRO,    'dcm:cr2PitchEncoder')
    c2height_counts        = Cpt(EpicsSignalRO,    'dcm:cr2TraHeightEncoder')
    
    # we need to pass always two feedback to be able to calculate the values.
    # I am not sure this would work, I try to put them in a list and pass the list
    # LIKE THIS IT DOES NOT WORK
    #c2_enc = [c2pit_counts.get(), c2roll_counts.get(), c2height_counts.get()]
    #readback_c2pit                  = Cpt(convertPitch, derived_from="c2_enc", kind="hinted")
    #readback_c2roll                 = Cpt(convertRoll, derived_from="c2_enc", kind="hinted")
    #readback_c2height               = Cpt(convertHeight, derived_from="c2_enc", kind="hinted")


class DCMPiezoPseudo(PseudoPositioner):
    '''
    This is not working at the moment. In the example on the documentation
    the real positioners are implemented using EpicsMotors. This does not
    work for us because our epics motor records do not have the field .RBV.
    A possible solution would be to use another positioner. The problem using
    a positioner is that the motors we want to look at have no done signal.
    One could subclass the PVPositioner class and fake a done signal only
    waiting 0.1 second, but I did not manage to do it. SV
    '''
# The pseudo positioner axes:
    c2pit     = Cpt(PseudoSingle)
    c2roll    = Cpt(PseudoSingle)
    c2hei     = Cpt(PseudoSingle)

    # The real (or physical) positioners:
    c2pit_counts   = Cpt(PVPositionerDone, 'dcm:cr2PitchEncoder')
    c2roll_counts  = Cpt(EpicsSignal, 'dcm:cr2RollEncoder')
    c2hei_counts   = Cpt(PVPositionerDone, 'dcm:cr2TraHeightEncoder')
    
    # constant definition
    ctmm  = 5.0e-6			#mm/count        
    C2pitBesTecOffset = (3260320-3800000)
    C2rolBesTecOffset = (3263554-3800000)
    CT2BesTecOffset = (3220620-3800000)
    
    @pseudo_position_argument
    def forward(self, pseudo_pos):
        '''Run a forward (pseudo -> real) calculation'''
        return self.RealPosition(c2pit_counts=-pseudo_pos.c2pit,
                                 c2roll_counts=-pseudo_pos.c2roll,
                                 c2hei_counts=-pseudo_pos.c2hei)

    @real_position_argument
    def inverse(self, real_pos):
        '''Run an inverse (real -> pseudo) calculation'''
        return self.PseudoPosition(c2pit=-real_pos.c2pit_counts,
                                   c2roll=-real_pos.c2roll_counts,
                                   c2hei=-real_pos.c2hei_counts)
