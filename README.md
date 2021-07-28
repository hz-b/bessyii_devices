**Beamline Ophyd Devices** 

This contains Opyhd Devices that can be used at any beamline or end station at BESSY II. For an example of how to use it see [emilOphyd](https://gitlab.helmholtz-berlin.de/sissy/experiment-control/emilOphyd) 

This work is based heavily on work at LCLS and their [PCDSDevices](https://github.com/pcdshub/pcdsdevices) repository.

**Motors and Axes**

Many motion systems at BESSY II do not use the [EPICS Motor Record](https://github.com/epics-modules/motor) This means rather than using the [Ophyd EpicsMotor Device](https://nsls-ii.github.io/ophyd/builtin-devices.html#epicsmotor) we need to make axes specific to many different IOC's and Support modules. These are based on the Ophyd PVPositioner Class or other Positioner classes (See Below). These axis defintions are held in the **axes.py** file.

**Positioners**

Various classes based on the PVPositoner are useful for other devices. These are collected together in the **positioners.py** file.
