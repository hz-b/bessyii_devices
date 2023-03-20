# create the SimDetector Device with a TIFF filesave mixin

# https://github.com/NSLS-II-OPLS/profile_collection/blob/6960f16e4b622e1cc2bf4703cfa07e3340a617f2/startup/45-pilatus.py#L53-L54

from ophyd import ( Component as Cpt, ADComponent, Device, PseudoPositioner,
                    EpicsSignal, EpicsSignalRO, EpicsMotor,
                    ROIPlugin, ImagePlugin,
                    SingleTrigger, PilatusDetector,
                    OverlayPlugin, FilePlugin,SimDetector, StatsPlugin, SimDetectorCam, ColorConvPlugin)
from ophyd.areadetector.filestore_mixins import FileStoreTIFFIterativeWrite
from ophyd import Component as Cpt
from ophyd.areadetector.base import (ADBase, ADComponent as ADCpt, ad_group, EpicsSignalWithRBV)
from ophyd.areadetector.plugins import StatsPlugin_V33, TIFFPlugin_V33, HDF5Plugin_V33, ImagePlugin_V33, ProcessPlugin_V33, ROIPlugin_V33

#from bessyii.ad33 import StatsPluginV33
from bessyii.ad33 import SingleTriggerV33
from bessyii_devices.positioners import PVPositionerComparator
from ophyd.areadetector.cam import CamBase
from ophyd.areadetector.detectors import DetectorBase
from ophyd.areadetector.base import EpicsSignalWithRBV

from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
class HDF5PluginWithFileStore(HDF5Plugin_V33, FileStoreHDF5IterativeWrite):
    ...
    
    
class SimDetectorCamV33(SimDetectorCam):
    '''This is used to update the SimDetectorCam to AD33.'''

    wait_for_plugins = Cpt(EpicsSignal, 'WaitForPlugins',
                           string=True, kind='config')

    # it's not possible to do RE(scan([sim_cam],sim_cam.cam.sim_peak_width_x,10,20,2)), not sure why :(
    sim_peak_width_x = ADCpt(EpicsSignalWithRBV,'PeakWidthX')
    sim_peak_width_y = ADCpt(EpicsSignalWithRBV,'PeakWidthY')
    
    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        self.stage_sigs['wait_for_plugins'] = 'Yes'

    def ensure_nonblocking(self):
        self.stage_sigs['wait_for_plugins'] = 'Yes'
        for c in self.parent.component_names:
            cpt = getattr(self.parent, c)
            if cpt is self:
                continue
            if hasattr(cpt, 'ensure_nonblocking'):
                cpt.ensure_nonblocking()


class SimDetector(SimDetector):
    cam = Cpt(SimDetectorCamV33, 'cam1:')

class TIFFPluginWithFileStore(TIFFPlugin_V33, FileStoreTIFFIterativeWrite):
    ...

class MySimDetectorV33(SingleTriggerV33, SimDetector):
    #tiff = Cpt(TIFFPluginWithFileStore,suffix="TIFF1:",write_path_template="/home/emil/Apps/autosave/images/")
    hdf5 = Cpt(HDF5PluginWithFileStore,  suffix="HDF1:", write_path_template="/home/emil/Apps/autosave/images/")
    stats = Cpt(StatsPlugin_V33, 'Stats1:')
    image = Cpt(ImagePlugin_V33, 'image1:')
    #colour = Cpt(ColorConvPlugin, 'CC1:')
    
    def set_detector(self):

        self.hdf5.kind = 'normal' 
        self.hdf5.stage_sigs["file_template"] = "%s%s_%4.4d.h5"
        
        #self.tiff.kind = 'normal'
        #self.tiff.stage_sigs["file_template"] = "%s%s_%4.4d.tif"
        self.stats.kind = 'hinted'
        #self.stats.profile_average.x.kind = 'hinted'
        self.stats.read_attrs = ['profile_average','total']
        self.image.kind = 'hinted'
        self.cam.ensure_nonblocking()
        
        #self.cam.sim_peak_width_x.kind = 'normal'
        #self.cam.sim_peak_width_y.kind = 'normal'

    
## URL Camera

from ophyd.areadetector import URLDetector, URLDetectorCam

class URLDetectorCamV33(URLDetectorCam):
    '''This is used to update the URLDetectorCam to AD33.'''

    wait_for_plugins = Cpt(EpicsSignal, 'WaitForPlugins',string=True, kind='config')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stage_sigs['wait_for_plugins'] = 'Yes'

    def ensure_nonblocking(self):
        self.stage_sigs['wait_for_plugins'] = 'Yes'
        for c in self.parent.component_names:
            cpt = getattr(self.parent, c)
            if cpt is self:
                continue
            if hasattr(cpt, 'ensure_nonblocking'):
                cpt.ensure_nonblocking()
    


class URLDetector(URLDetector):
    cam = Cpt(URLDetectorCamV33, 'cam1:')


class MyURLDetectorV33(SingleTriggerV33, URLDetector):
    tiff = Cpt(TIFFPluginWithFileStore,
               suffix="TIFF1:",
               write_path_template="/home/emil/Apps/autosave/images/")
    stats = Cpt(StatsPlugin_V33, 'Stats1:')
    image = Cpt(ImagePlugin_V33, 'image1:')
    #colour = Cpt(ColorConvPlugin, 'CC1:')

    
    
#FLIR Camera for PMFC at OAESE

from ophyd.areadetector import PointGreyDetector, PointGreyDetectorCam

class PointGreyDetectorCamV33(PointGreyDetectorCam):
    '''This is used to update the URLDetectorCam to AD33.'''

    wait_for_plugins = Cpt(EpicsSignal, 'WaitForPlugins',
                           string=True, kind='config')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stage_sigs['wait_for_plugins'] = 'Yes'

    def ensure_nonblocking(self):
        self.stage_sigs['wait_for_plugins'] = 'Yes'
        for c in self.parent.component_names:
            cpt = getattr(self.parent, c)
            if cpt is self:
                continue
            if hasattr(cpt, 'ensure_nonblocking'):
                cpt.ensure_nonblocking()
    

class PointGreyDetector(PointGreyDetector):
    cam = Cpt(PointGreyDetectorCamV33, 'cam1:')



class SISSY1FocusCam(SingleTriggerV33, PointGreyDetector):
    tiff = Cpt(TIFFPluginWithFileStore,
               suffix="TIFF1:",
               write_path_template="/home/emil/Apps/autosave/images/")
    stats = Cpt(StatsPlugin_V33, 'Stats1:')
    proc = Cpt(ProcessPlugin_V33, 'Proc1:')
    roi1 = Cpt(ROIPlugin_V33, 'ROI1:')

    
    
# General method

def set_detectorV33(det):

    det.tiff.kind = 'normal' 
    det.stats.kind = 'hinted'
    det.stats.total.kind = 'hinted' 
    det.stats.sigma_readout.kind = 'hinted'
    det.stats.max_value.kind = 'hinted'
    det.stats.centroid.kind = 'hinted' 
    det.stats.centroid.x.kind = 'hinted' 
    det.stats.centroid.y.kind = 'hinted' 
    det.stats.read_attrs= ['centroid.x', 'centroid.y', 'total','sigma_readout', 'max_value']
    det.cam.ensure_nonblocking()
    det.tiff.nd_array_port.put(det.proc.port_name.get()) # makes the tiff plugin take the output of the colour change plugin
    det.stats.nd_array_port.put(det.roi1.port_name.get())
    
##### Great Eyes Cam

class GreateyesTempController(PVPositionerComparator):
  
    setpoint = ADCpt(EpicsSignalWithRBV, 'Temperature')
    readback = ADCpt(EpicsSignalRO, 'TemperatureActual', kind='hinted')
    ena = ADCpt(EpicsSignalWithRBV,'GreatEyesEnableCooling',kind='config')
    hotside_temp = ADCpt(EpicsSignalRO,'GreatEyesHotSideTemp')
    
    egu = '°c'
    
    atol = 0.5  # tolerance before we set done to be 1 (in um) we should check what this should be!

    def done_comparator(self, readback, setpoint):
        return setpoint-self.atol < readback < setpoint+self.atol


    def __init__(self, prefix, ch_name=None, **kwargs):
        self._ch_name = ch_name
        super().__init__(prefix, **kwargs)
        self.readback.name = self.name 
    
    
class GreateyesDetectorCamV33(CamBase):
    
    wait_for_plugins = Cpt(EpicsSignal, 'WaitForPlugins',
                           string=True, kind='config')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stage_sigs['wait_for_plugins'] = 'Yes'

    def ensure_nonblocking(self):
        self.stage_sigs['wait_for_plugins'] = 'Yes'
        for c in self.parent.component_names:
            cpt = getattr(self.parent, c)
            if cpt is self:
                continue
            if hasattr(cpt, 'ensure_nonblocking'):
                cpt.ensure_nonblocking()

    #500KHz, 1 MHz, 3MHz
    adc_speed = ADCpt(EpicsSignalWithRBV,'GreatEyesAdcSpeed',string='True',kind='config')
    
    #(0)Standard, (1)Low
    gain = ADCpt(EpicsSignalWithRBV,'GreatEyesGain',string='True',kind='config')
    
    #Readout Amplifier configuration. See manual for details http://sissy-pi-01.basisit.de/dokuwiki/lib/exe/fetch.php?media=endstations:systems:es:areadetector_adgreateyesccd_driver.pdf
    readout_amp = ADCpt(EpicsSignalWithRBV,'GreatEyesReadoutDir',string='True',kind='config')
    
    #Outputnode Capacity (0)Low noise (1)Higher signal level
    capacity = ADCpt(EpicsSignalWithRBV,'GreatEyesCapacity',kind='config')
    
    #Positioner device that allows us to control the temperature. Must be enabled 
    temp_control = ADCpt(GreateyesTempController, '',kind='hinted')
    
    
class GreateyesDetector(DetectorBase):
    cam = Cpt(GreateyesDetectorCamV33, 'cam1:')

class MyGreateyesDetectorV33(SingleTriggerV33,GreateyesDetector):
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cam.ensure_nonblocking()
        self.cam.temp_control.ena.set(1)
    
    hdf5 = Cpt(HDF5PluginWithFileStore,  suffix="HDF1:", write_path_template="/home/emil/Apps/autosave/images/")
    stats = Cpt(StatsPlugin_V33, 'Stats1:')
    image = Cpt(ImagePlugin_V33, 'image1:')
    
    def set_detector(self):

        self.hdf5.kind = 'normal' 
        self.hdf5.stage_sigs["file_template"] = "%s%s_%4.4d.h5"
        self.stats.kind = 'hinted'
        self.stats.profile_average.x.kind = 'hinted'
        self.stats.read_attrs = ['profile_average']
        self.image.kind = 'hinted'
        self.cam.kind = 'hinted'   
        self.cam.read_attrs= ['temp_control.readback']
        
