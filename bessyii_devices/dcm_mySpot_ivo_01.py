from ophyd import PVPositioner, EpicsSignal, EpicsSignalRO, Device, DerivedSignal,PseudoPositioner,PseudoSingle,EpicsMotor
from ophyd import Component as Cpt
from ophyd.pseudopos import (pseudo_position_argument,
                             real_position_argument)
from ophyd.signal import Signal, SignalRO
from ophyd import FormattedComponent as FCpt
from .positioners import *
from .mostab import Mostab

import numpy as np 
import math


class AxisPositioner(PVPositionerDone):
    
  
    setpoint = FCpt(EpicsSignal,    '{self._pre_volt}Piezo{self._pz_num}U1') 
    readback = FCpt(EpicsSignalRO,  '{self._pre_enc}dcm:cr2{self._ch_name}Encoder', kind='hinted')
   
    def __init__(self,prefix, pre_volt=None, pre_enc=None, ch_name=None, pz_num=None, **kwargs):
        self._ch_name = ch_name
        self._pz_num = pz_num
        self._pre_volt = pre_volt
        self._pre_enc = pre_enc
        super().__init__(prefix, **kwargs)


class DCMTranslationAxis(PVPositionerComparator):

    setpoint = FCpt(EpicsSignal,'{self.prefix}PH_{self._ch_num}_SET')
    readback = FCpt(EpicsSignalRO,'{self.prefix}PH_{self._ch_num}_GET')

    atol = 0.1  # tolerance before we set done to be 1 (in um) we should check what this should be!

    def done_comparator(self, readback, setpoint):
        return setpoint-self.atol < readback < setpoint+self.atol
        
        
    def __init__(self, prefix, ch_num=None, **kwargs):
        self._ch_num = ch_num
        super().__init__(prefix, **kwargs)
    
#https://nsls-ii.github.io/ophyd/positioners.html#pseudopositioner
class Piezo3Axis(PseudoPositioner):
    # The pseudo positioner axes:
    # we have to set the limits to the biggest of the input or output
    pitch     = Cpt(PseudoSingle, limits=(-6283186.0, 6283186.0), labels={"dcm", "motors"} ) 
    roll      = Cpt(PseudoSingle, limits=(-6283186.0, 6283186.0), labels={"dcm", "motors"} )
    height    = Cpt(PseudoSingle, limits=(-6283186.0, 6283186.0), labels={"dcm", "motors"} )

    # The real (or physical) positioners:
    # wait for 1 second before reporting done
    r_pitch     = Cpt(AxisPositioner,'',pre_volt='MONOY01U112L:', pre_enc='u171dcm1:',ch_name='Pitch' ,pz_num='2', settle_time=.1)      
    r_roll      = Cpt(AxisPositioner,'',pre_volt='MONOY01U112L:', pre_enc='u171dcm1:',ch_name='Roll'  ,pz_num='3', settle_time=.1)
    r_height    = Cpt(AxisPositioner,'',pre_volt='MONOY01U112L:', pre_enc='u171dcm1:',ch_name='TraHeight',pz_num='1', settle_time=.1)

    
    
    
    @pseudo_position_argument
    def forward(self, pseudo_pos):
        '''Run a forward (pseudo -> real) calculation'''
        return self.RealPosition(r_pitch    =pseudo_pos.pitch,
                                 r_roll     =pseudo_pos.roll,
                                 r_height   =pseudo_pos.height)

    
    @real_position_argument
    def inverse(self, real_pos):
    
        #http://sissy-pi-01/dokuwiki/doku.php?id=beamlines:devices:piezo_control
        c2um = 5.0      
        p_o = 3260320 - 3800000
        r_o = 3263554 - 3800000
        h_o = 3220620 - 3800000
        
        offsets = np.array([p_o,r_o,h_o])
        a = np.array ([[ 1,0,-1],
                       [ 0,1,-1],
                       [ 0,0,1]])
        p_x = 64750000
        r_x = 127750000
        
        d = c2um*np.matmul(a,np.subtract(real_pos,offsets))
                   
        '''Run an inverse (real -> pseudo) calculation'''
        return self.PseudoPosition(pitch  = 1000000 * math.atan(d[0]/p_x), 
                                   roll   = 1000000 * math.atan(d[1]/r_x), 
                                   height = d[2])


class DCM_direct_drive(PseudoPositioner):
    # Table of values, should be somewhere where we put other tables

    # The pseudo positioner axes:
    # we have to set the limits to the biggest of the input or output
    monoE     = Cpt(PseudoSingle, limits=(0, 30), labels={"dcm", "motors"} ) # 0-30 keV, normally up to 20
    monoh     = Cpt(PseudoSingle, limits=(0, 30), labels={"dcm", "motors"} ) # 0-30 mm, normally 5 or 25
    
    #offset: the offset in encoder. This is going to chcange if we change the encoder hardware

    # The real (or physical) positioners:
    # wait for 1 second before reporting done
    r_pitch     = Cpt(AxisPositioner,'',pre_volt='MONOY01U112L:', pre_enc='u171dcm1:',ch_name='Pitch' ,pz_num='2', settle_time=.1)      

    #These are the motors I need to read and position from here
    # monobr
    # cr2latr
    # cr2vetr

    # I also need these to set the parameters
    # monoz
    # cr2ropi
    # I also need the readback value, but I don't use it as a readback value, I just want to read it adn save it as a detector value
    

    # monochromator mode:
    # depending on the value of the MONO_mode, I move 1, 2 or 3 motors when changing the energy.
    # MONO_mode == 3
    #   when changing the energy, monobr is moved to the bragg angle, 
    #   cr2vetr is moved to keep the monoh at the same value,
    #   and cr2latr is moved to catch the foorprint of the beam
    # MONO_mode == 2
    #   when changing the energy, monobr is moved to the bragg angle, 
    #   cr2vetr is moved to keep the monoh at the same value, 
    #   cr2latr is NOT MOVED. this has no influence at monoh
    # MONO_mode == 1
    #   when changing the energy, monobr is moved to the bragg angle, 
    #   cr2vetr is not moved: this means that the beam height is changed: monoh is recalculated to reflect this change, 
    #   cr2latr is NOT MOVED. this has no influence at monoh

    self.MONO_mode=3

    self.mono=[]
    # these parameters should be saved somewhere in a file, so that they can be updated if better values are found 
    self.add_mono( 1,  "Si 111",  25,    3.1356,       0.0,      -38.0,     -0.557,       0.104,      0.078,    0.075      0.0038)
    self.add_mono( 2,  "Si 311",  25,    1.63751,     5.718,     0.0,      -0.399,        0.025,     0.0278,   0.0776       0.0)
    self.add_mono( 3,  "B4C ML",  5,      20.0,       6.46,      41.5,     -0.38564,	   0.0270,   0.053,    0.205      0.0020)
#       add_mono 4  "SiW ML"    5      30.0        6.5     0      -0.399        0.1     0.0    0.0      0.0045
#       add_mono 5 "Ge 111"  25    3.26631       6.5     41      -0.399        0.1     0.0    0.0      0.0045

    self.detect_mono_type()

    # when starting, I have no idea which monochromator is in the beam. to avoid movin everything to the default position, 
    # I detect the position of the monoz (which move monochromator HORIZONTALLY) and decide which crystal is in the beam
    def detect_mono_type(self):
        # somehow get the coordinate of the motor monoz
        get_angles;
        self.MONOTYPE = 2
        if (A[monoz]< -15):
            self.MONOTYPE = 1;
        if (A[monoz]> 15):
            self.MONOTYPE = 3;
	

    def calibrate(self):
        """
        this controls the heidenhein encoder and makes it reset the counter when the encoder is moved over the 
        latch position. This is done by sending the config commands to the encoder and driving the monobr motor up and down 
        Before doing this it is recommended to drive the motor to the limit switch and set the coordinate 
        """
        
        #switch off updating of monoh cr2latr...
        waitall
        
        # make the hardware limit accessible
        set_lim( monobr, -20 ,200)
        # the following hits the lower limit
        #umv monobr -10
        #position= A[monobr]
        #mvr monobr 1
        #waitall
        #set_dial monobr -2.8815
        #set monobr -2.8815

        mv monobr 2 0
        epics_put("DCM1OS2L:l0202000.URIP", 0)           # unbind the feedback connection (I am not using this at mySpot in currrent configuration)
        sleep(1)
        epics_put("DCM1OS2L:IK1380002rM.VAL",3)           # rM clear counter
        sleep(1)
        epics_put("DCM1OS2L:IK1380002cR.VAL",4)           # cR stop counter
        mv monobr -2
        waitall
        
        sleep(1)
        epics_put("DCM1OS2L:IK1380002.AOFF",0)            # set offset to 0
        sleep(1)
        #epics_put("DCM1OS2L:IK1380002.AOFF",-1*epics_get("DCM1OS2L:IK1380002")) # than set offset 
        sleep(1)
        epics_put("DCM1OS2L:IK1380002rM.VAL",1)           # RM start counter
        sleep(1)
        epics_put("DCM1OS2L:IK1380002.ASLO",9.765625E-6)
        sleep(1)
        epics_put("DCM1OS2L:IK1380002.EGU","Deg")
        
        mv monobr 2
        waitall
        sleep(1)
        epics_put("DCM1OS2L:IK1380002rM.VAL",0)           # no action
        sleep(1)
        epics_put("DCM1OS2L:IK1380002cR.VAL",0)           # use latch0
        sleep(1)
        
        # now the encoder is zeroed at the latch
        # donot reset the encoder, donot put any offset in it
        # set the dial coordinate of the motor to the encoder value
        sleep(1)
        waitall

        # I actually want to do this:
        # set_dial monobr epics_get("DCM1OS2L:IK1380002")
        # But: BUG! - use tricks here: talk directly to epics!

        epics_put("DCM1OS2L:l0202000.SET","Set")
        epics_put("DCM1OS2L:l0202000.DVAL",epics_get("DCM1OS2L:IK1380002"))
        epics_put("DCM1OS2L:l0202000.OFF",-0.3)    # offset back to 0
        epics_put("DCM1OS2L:l0202000.SET","Use")

        # now make sure that the retry deaadband of the motor is larger than encoder resolution
        epics_put("DCM1OS2L:l0202000.RDBD",2E-5)
        
        # p "do  not forget the offset of -0.3 if the mirror 1 is used"
        # p " The offset is set automatically by monosetup, hete it is set to -0.3"
        


        # this was uset for setting the offset of the encoder
        #mv monobr 0
        #wait()
        #sleep(1)
        epics_put("DCM1OS2L:IK1380002.AOFF",-0.3)            # set offset to 0
        #sleep(1)
        #epics_put("DCM1OS2L:IK1380002.AOFF",-1*epics_get("DCM1OS2L:IK1380002"))
        
        # set_lim( monobr, -1 ,80)
        # spec buggy
        epics_put("DCM1OS2L:l0202000.LLM",-1)
        epics_put("DCM1OS2L:l0202000.HLM",80)

        mv monobr 3
        
        #_monobr_use_encoder 0
            
        # you can do this manually
        # switch on the multimotor mode 
        #MYSPOT_BL_MONO_mode=0
            
        # after this I called "monosetup", which is responsible for setting the offsets depending on which monochromator we use.
        

    def set_parameter(self,N,name, monoh,   monod,     c1height,       monoz,     encoder_zero,  cr2ropi,   cr1roll,  cr2roll,  cr2vetrCorr):
        param={}
        param["N"]=N
        param["name"]=name
        param["monoh"]=monoh
        param["monod"]=monod
        param["c1height"]=c1height
        param["monoz"]=monoz
        param["encoder_zero"]=encoder_zero
        param["cr2ropi"]=cr2ropi
        param["cr1roll"]=cr1roll
        param["cr2roll"]=cr2roll
        param["cr2vetrCorr"]=cr2vetrCorr
        self.mono.append(param)

    # this is probably not the right place for this. It calls methods to get coordinates and set the energy.
    def set_mono(self,monotype, monoE=8.0):
        self.MONOTYPE=monotype
	slef.param = self.mono[self.MONOTYPE]
        #
        # if the monochromator chcanged move to the default position. Let's say 8kev, 
        # for practical resons later we are going to move to the same energy where we were, or where we want to perform the next measurement
        sef.move monoz to param["monoz"]
        self.move to energy!!!

    @pseudo_position_argument
    def forward(self, pseudo_pos):
        hc_over_e = 12.398419111 # http://physics.nist.gov
        '''Run a forward (pseudo -> real) calculation'''
        A_monoE=pseudo_pos.monoE
        A_monoh=pseudo_pos.monoh

        # for now, traditionally in SPEC, BRAGG_ANGLE is in degree. I should maybe do it in radian?
        BRAGG_ANGLE= np.rad2deg(np.asin(hc_over_e/(2.0 * self.param["monod"]*A_monoE)));
		LAMBDA=hc_over_e / A_monoE
         		
        L=2*self.param["monod"]*np.sin(np.rad(BRAGG_ANGLE))

        return self.RealPosition(monobr  = BRAGG_ANGLE,
                                 cr2latr   = -1*A_monoh/(2*sin(np.deg2rad(BRAGG_ANGLE))) 
                                 cr2latr   = pseudo_pos.roll     )

    
    @real_position_argument
    def inverse(self, real_pos):
        BRAGG_ANGLE= real_pos.monobr
        
class DCMEnergy(PVPositioner):
    # sdf
    """
    Class to set and read energy of the DCM. Will not be necessary with new DCM implementation
    
    DOES NOT WORK FOR mySpot. I left it here to keep the structure only
    """
    #prefix at emil: MONOY01U112L
    setpoint        = Cpt(EpicsSignal,      'monoSetEnergy'                  )
    readback        = Cpt(EpicsSignalRO,    'monoGetEnergy',    kind='hinted', labels={"dcm", "motors"}) 
    done            = Cpt(EpicsSignalRO,    'GK_STATUS'                  )
    

class DCMmySpot(Device):
    monoz = Cpt(EpicsMotor, 'l0201002')
    cr2latr = Cpt(EpicsMotor, 'l0201003')
    cr1roll = Cpt(EpicsMotor, 'l0201004')
    cr2roll = Cpt(EpicsMotor, 'l0201005')
    monobr = Cpt(EpicsMotor, 'l0202000')
    cr2vetr = Cpt(EpicsMotor, 'l0202001')
    monoy = Cpt(EpicsMotor, 'l0202002')
    cr2ropi= Cpt(EpicsMotor, 'l0202003')
    cr2yaw = Cpt(EpicsMotor, 'l0202004')

