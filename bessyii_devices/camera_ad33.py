# create the SimDetector Device with a TIFF filesave mixin

# https://github.com/NSLS-II-OPLS/profile_collection/blob/6960f16e4b622e1cc2bf4703cfa07e3340a617f2/startup/45-pilatus.py#L53-L54

from ophyd import ( Component as Cpt, ADComponent, Device, PseudoPositioner,
                    EpicsSignal, EpicsSignalRO, EpicsMotor,
                    ROIPlugin, ImagePlugin,
                    SingleTrigger, PilatusDetector,
                    OverlayPlugin, FilePlugin, TIFFPlugin, SimDetector, TIFFPlugin, StatsPlugin, SimDetectorCam, ColorConvPlugin)
from ophyd.areadetector.filestore_mixins import FileStoreTIFFIterativeWrite
from ophyd import Component as Cpt

from ophyd.areadetector.plugins import StatsPlugin_V33
from bessyii.ad33 import StatsPluginV33
from bessyii.ad33 import SingleTriggerV33

class SimDetectorCamV33(SimDetectorCam):
    '''This is used to update the SimDetectorCam to AD33.'''

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
    


class SimDetector(SimDetector):
    cam = Cpt(SimDetectorCamV33, 'cam1:')

class TIFFPluginWithFileStore(TIFFPlugin, FileStoreTIFFIterativeWrite):
    ...

class MySimDetectorV33(SingleTriggerV33, SimDetector):
    tiff = Cpt(TIFFPluginWithFileStore,
               suffix="TIFF1:",
               write_path_template="/home/emil/Apps/autosave/images/")
    stats = Cpt(StatsPluginV33, 'Stats1:')
    image = Cpt(ImagePlugin, 'image1:')
    colour = Cpt(ColorConvPlugin, 'CC1:')
    
## URL Camera

from ophyd.areadetector import URLDetector, URLDetectorCam

class URLDetectorCamV33(URLDetectorCam):
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
    


class URLDetector(URLDetector):
    cam = Cpt(URLDetectorCamV33, 'cam1:')

class TIFFPluginWithFileStore(TIFFPlugin, FileStoreTIFFIterativeWrite):
    ...

class MyURLDetectorV33(SingleTriggerV33, URLDetector):
    tiff = Cpt(TIFFPluginWithFileStore,
               suffix="TIFF1:",
               write_path_template="/home/emil/Apps/autosave/images/")
    stats = Cpt(StatsPluginV33, 'Stats1:')
    image = Cpt(ImagePlugin, 'image1:')
    colour = Cpt(ColorConvPlugin, 'CC1:')


def set_detectorV33(det):

    det.tiff.kind = 'normal' 
    det.stats.kind = 'hinted'
    det.colour.kind = 'normal'
    det.image.kind = 'hinted'
    det.stats.fwhm_x.kind = 'hinted'
    det.stats.fwhm_y.kind = 'hinted'
    det.stats.total.kind = 'normal' 
    det.stats.centroid.kind = 'hinted'  # We need both to display the bottom...
    det.stats.centroid.x.kind = 'hinted' 
    det.stats.centroid.y.kind = 'hinted' 
    det.stats.read_attrs= ['centroid.x', 'centroid.y', 'total', 'fwhm_x', 'fwhm_y', 'sigma_x', 'sigma_y', 'max_value']
    det.cam.ensure_nonblocking()
    det.tiff.nd_array_port.put(det.colour.port_name.get()) # makes the tiff plugin take the output of the colour change plugin