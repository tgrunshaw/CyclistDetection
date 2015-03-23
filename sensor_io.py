#!/usr/bin/env python
###########################################################################
# sensor_io.py
#
# @Author Tim Grunshaw
#
# This file abstracts the ultrasound sensor interface.
#
###########################################################################

import serial
import time
import RPIO
from RPIO import PWM

class UsSensor:
    PWM_GPIO = 18
    BAUD_RATE = 9600
    PWM_FREQUENCY = 5 # Go below the 6Hz max
    PWM_WIDTH = 10000 # Pulse width in uS, 50uS > 20uS required by ultrasound
                   # sensor.
    
    def __init__(self, logger, serialPort):
        # The sensor serial interface
        self.logger = logger
        self.serialPort = serialPort
	RPIO.setup(UsSensor.PWM_GPIO, RPIO.IN) # Default to input
	self.sensor = serial.Serial(self.serialPort, UsSensor.BAUD_RATE)
	self.logger.displayText("Ultrasound transducer opened on port: " + serialPort)
	self.clearBuffer()
        self.skipToStartOfLine()
        
    def startTriggeredMode(self):
        # Setup PWM and DMA channel 0
        PWM.setup()
        # Subcycle time in ms
        PWM.init_channel(0, subcycle_time_us=int(1000000 / UsSensor.PWM_FREQUENCY))
        
        # Add some pulses to the subcycle
        pwmWidth = int(UsSensor.PWM_WIDTH / PWM.get_pulse_incr_us()) # width is in multiples of pulse-width 
                                                            # increment granularity
        PWM.add_channel_pulse(0, UsSensor.PWM_GPIO, start=0, width=pwmWidth)

	self.logger.displayText("Ultrasound set to triggered mode at frequency: " + str(UsSensor.PWM_FREQUENCY) + str("Hz"))


    # Clears the input buffer
    def clearBuffer(self):
        self.sensor.flushInput()
    
    def cleanup(self):
	RPIO.cleanup()

    #Returns the reading in milimeters
    def getReading(self):
        rChar = self.sensor.read()
        rangeStr = self.sensor.read(4)
        nlChar = self.sensor.read()
        range = int(rangeStr) 
        return range

    # Reads a whole or part of line
    def skipToStartOfLine(self):
        # Find the first newline character ('\r')
        for i in range(6):
            if(self.sensor.read() == '\r'):
                break
        # Next reading will now be start of actual line
        

if(__name__ == "__main__"):
    us = UsSensor(None, "/dev/ttyUSB0")
    us.startTriggeredMode()
    t = time.time()
    while(True):
        print((time.time() - t))
        t = time.time()
        print us.getReading()
        
    
