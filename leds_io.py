#!/usr/bin/env python
###########################################################################
# warning_leds_io.py
#
# @Author Tim Grunshaw
#
# Abstracts io logic for the warning leds.
# GPIO25 (pin 22) is set to output and drives a MOSFET gate which powers
# the leds when set high. 
#
###########################################################################

from time import sleep
import RPi.GPIO as GPIO

class Warning_LEDS:
    WARNING_LEDS_GPIO = 25
    FLASH_FREQUENCY = 5 # Hz - Integer frequency of flashes when in flash mode 
                        # Eg 5hz = 5 on & 5 off per second
    
    def __init__(self):
        # Use GPIO numbering (not RPi pin numbers)
        self.state = False # Default to not going
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(Warning_LEDS.WARNING_LEDS_GPIO, GPIO.OUT, initial=0) # Default to driving low.        

    def setState(self, state):
        self.state = state
        GPIO.output(Warning_LEDS.WARNING_LEDS_GPIO, self.state)
        
    def toggleState(self):
        self.state = not self.state
        GPIO.output(Warning_LEDS.WARNING_LEDS_GPIO, self.state)
       
    '''
        flashTime - the number of seconds to flash for. 
    '''
    def flash(self, flashTime):
        sleepTime = 0.5 / Warning_LEDS.FLASH_FREQUENCY
        
        for i in xrange(Warning_LEDS.FLASH_FREQUENCY * flashTime):
            GPIO.output(Warning_LEDS.WARNING_LEDS_GPIO, 0)
            sleep(sleepTime)
            GPIO.output(Warning_LEDS.WARNING_LEDS_GPIO, 1)
            sleep(sleepTime)
        
        GPIO.output(Warning_LEDS.WARNING_LEDS_GPIO, self.state) # Reset to original state
        

    # Always run this method
    def cleanup(self):
        GPIO.cleanup()
