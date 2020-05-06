# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 17:47:38 2019

@author: jeremy
"""

from PyDAQmx import *
from PyDAQmx.DAQmxTypes import *
from PyDAQmx import Task
import numpy as np

value = 1.3

task = Task()
task.CreateAOVoltageChan("Dev1/ao1","",-10.0,10.0,DAQmx_Val_Volts,None)
task.StartTask()
task.WriteAnalogScalarF64(1,10.0,value,None)
task.StopTask()