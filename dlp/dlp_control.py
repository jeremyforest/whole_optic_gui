# -*- coding: utf-8 -*-
"""
Created on Mon Jun 17 21:46:50 2019

@author: Jeremy
"""

from dm365 import dm365

dlp = dm365()
dlp.connect()


def turn_on_blue():
	dlp.displayInternalTestPattern(4)
	
def turn_off_light():
	dlp.displayInternalTestPattern(1)
	
#dlp.close()
