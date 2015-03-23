#!/usr/bin/env python
###########################################################################
# indicator_io.py
#
# @Author Tim Grunshaw
#
# This file abstracts the indicator io.
# GPIO22 and GPIO23 (pins 15 & 16) are short circuited when the indicator
# is turned on. Therefore this class drives GPIO22 high output and when
# a high is detected on GPIO23 (input, pull down) it knows that the indicator
# is turned on.
#
###########################################################################

import RPi.GPIO as GPIO
import time

class Indicator:
    DRIVE_GPIO = 22
    DETECT_GPIO = 23
    
    def __init__(self, logger):
        # Use GPIO numbering (not RPi pin numbers)
        self.logger = logger
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(Indicator.DRIVE_GPIO, GPIO.OUT)
        GPIO.output(Indicator.DRIVE_GPIO, 1)
        GPIO.setup(Indicator.DETECT_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	self.lastTime = time.time()
	self.lastState = False

    def isIndicatingLeft(self):
	notIndicating = GPIO.input(Indicator.DETECT_GPIO)
	indicating = not notIndicating
	
	# Check it isn't just in off phase
	if not indicating:
            timeNow = time.time()
            if(timeNow > (self.lastTime + 1)):
		self.lastTime = timeNow
                self.lastState = False
		return False
	    else: # Just return last state
	        return self.lastState
	else:
            self.lastTime = time.time()
	    self.lastState = True
	    return True

    # Always run this method
    def cleanup(self):
        GPIO.cleanup()
