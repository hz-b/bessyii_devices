import sys
from os import path

from setuptools import find_packages, setup

import versioneer

setup(name='bessyii_devices',
      version='1.1.0',
      description='A collection of ophyd devices that can be used with IOCs at BESSY II',
      url='https://gitlab.helmholtz-berlin.de/sissy/experiment-control/beamlineOphydDevices',
      author='Will Smith, Simone Vadilonga, Sebastian Kazarski',
      author_email='william.smith@helmholtz-berlin.de',
      # license='MIT',
      packages=['bessyii_devices'],
      install_requires=[
          'ophyd',
          'numpy'
      ]
      # zip_safe=False
)