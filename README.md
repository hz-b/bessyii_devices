**bessyii_devices** 

A collection of ophyd devices for use at BESSY II

This work is based heavily on work at LCLS and their [PCDSDevices](https://github.com/pcdshub/pcdsdevices) repository.

**Installation**

To install pull this repository and then run 

`python3 setup.py develop`

**Motors and Axes**

Many motion systems at BESSY II do not use the [EPICS Motor Record](https://github.com/epics-modules/motor) This means rather than using the [Ophyd EpicsMotor Device](https://nsls-ii.github.io/ophyd/builtin-devices.html#epicsmotor) we need to make axes specific to many different IOC's and Support modules. These are based on the Ophyd PVPositioner Class or other Positioner classes (See Below). These axis defintions are held in the **axes.py** file.

**Positioners**

Various classes based on the PVPositoner are useful for other devices. These are collected together in the **positioners.py** file.

