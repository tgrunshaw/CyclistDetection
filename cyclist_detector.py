#!/usr/bin/env python
###########################################################################
# CyclistDetector.py
#
# @Author Tim Grunshaw
#
# Main file for the cyclist detector project.
#
###########################################################################

import time
import sensor_io
import indicator_io
import obd
import leds_io
import controller
import gui
import threading
import serial
import RPi.GPIO as GPIO
from Tkinter import *
from ttk import *
from collections import deque
from collections import namedtuple

# Debugging message on or off
shouldDebug = True

# Identify serial interfaces
s=serial.Serial("/dev/ttyUSB0")
if(s.baudrate == 9600):
    # obd has 38400 baudrate
    ultraSoundSerialPort = "/dev/ttyUSB0"
    obdSerialPort = "/dev/ttyUSB1"
else:
    obdSerialPort = "/dev/ttyUSB0"
    ultraSoundSerialPort = "/dev/ttyUSB1"
s.close()

# Tuple to store range readings
RangeReading = namedtuple('RangeReading', 'time range')

GPIO.setwarnings(False)

'''
 Main class
'''
class CyclistDetector:
    READINGS_TO_STORE = 3 # How many range readings to use in calculations
    RELATIVE_VELOCITY_ALERT_THRESHOLD = 2.0 # ms-1 : the relative velocity of the
                                            # cyclist to alert on
    ALLOWABLE_VELOCITY_JITTER = 0.2;# Ratio of average velocity over several readings
                                    # an indivdual velocity between just two readings may be
                                    # off by. Larger allows more spurious results (more false
                                    # positives, less false negatives). Valid range: 0-1.
    RPM_THRESHOLD = 500 # Minimum RPM required for warning to be initiated (mimics min-speed for lab)
    
    WARMUP_TIME = 10 # Seconds, do not alert for this period of time after starting and after an alert
    LOOP_SPEED = 5 # Hz = Frequency of loop (which should always be the sensor triggered  polling rate)
              
    '''
        shouldLog: whether or not the results should be logged
        shouldPrint: whether or not the results should be printed

        It will always print an alert.
    '''
    def __init__(self, shouldLog, shouldPrint):
        # Variables able to be controlled from gui
        self.testIndicator = True
        self.testVehicleSpeed = True
        self.testJitter = True
        self.shouldQuit = False
        self.isInWarmup = True 
        #GUI
        self.controller = controller.Controller(self)
        self.tkRoot = Tk()
        self.tkRoot.protocol("WM_DELETE_WINDOW", self.quitGui)
        self.window = gui.MainWindow(self.tkRoot, self, self.controller)
 
        self.shouldLog = shouldLog
        self.shouldPrint = shouldPrint
        if(shouldLog):
            self.logFile = open(createFileName(), 'w')
        
        #self.warningLEDS.flash(1)# Flash for one second to show working. 
         
    def quitGui(self):
        debug("Waiting for background processes to exit cleanly...")
        self.shouldQuit = True
        time.sleep(3)
        self.tkRoot.destroy()
        
    def cleanup(self):
        #Close port etc
	self.usSensor.cleanup()
        self.indicator.cleanup()
	print("Exited cleanly!")

    '''
        Infinite gui loop
    '''
    def startGui(self):
        print("Gui started")
        self.tkRoot.mainloop()
        
        
        
    '''
        Start the cyclist detector infinite loop
    '''
    def start(self):
        print("Running...")
        
        # Init stuff
        self.usSensor = sensor_io.UsSensor(self, ultraSoundSerialPort)
        self.usSensor.startTriggeredMode()
	self.indicator = indicator_io.Indicator(self)
	self.rangeReadings = deque() # A queue holding an array of RangeReading tuples.
        self.obdPort = obd.OBD(self, obdSerialPort) # Takes over 6 seconds to init
        self.warningLEDS = leds_io.Warning_LEDS()

        count = 0
        while True:
            if self.shouldQuit:
                self.cleanup()
                break
                
            self.window.setIsIndicating(self.indicator.isIndicatingLeft())
            self.window.setSpeed(self.obdPort.getReading(12))                
             
            nowTime = int(time.time()*1000) # Time in miliseconds
            fieldNowTime = str(nowTime)

            # Range reading (in mm)
            usRange = self.usSensor.getReading()
            self.rangeReadings.append(RangeReading(nowTime, usRange))
            if len(self.rangeReadings) > CyclistDetector.READINGS_TO_STORE:
                self.rangeReadings.popleft() # Remove the first element
            fieldRangeReading = "{:10.4f}".format(usRange)
           
	    debug(fieldRangeReading)
            # Determine if we should alert
            alert = self.shouldAlert()
            count += 1
	    if self.isInWarmup and count > (CyclistDetector.WARMUP_TIME * CyclistDetector.LOOP_SPEED):
		# Warmed Up
		self.isInWarmup = False

	    if alert and not self.isInWarmup :
                count = 0 # Must warmup again after alerit
		self.isInWarmup = True
		self.displayText("******************************************")
		self.displayText("Alerted!!! Approach speed: " + "{:10.4f}".format(alert) + "ms-1")
                self.displayText("******************************************")
		self.warningLEDS.flash(2) # Flash warning leds for 2 seconds
            
            if self.shouldLog:
                self.logFile.write(fieldNowTime + "," + fieldRangeReading + "," + str(alert) + "\n")
            if self.shouldPrint:
                print(fieldNowTime + "," + fieldRangeReading + "," + str(alert) + "\n")

    '''
        Internal: check if range readings match an alert.
	Returns False if not, otherwise the approach velocity.
    '''
    def shouldAlert(self):
        # Wait for queue to fill up
        if not len(self.rangeReadings) == CyclistDetector.READINGS_TO_STORE:
            debug("Filling queue: " + str(len(self.rangeReadings)))
            # Debug messages
            if self.indicator.isIndicatingLeft():
                debug("Indicating!!")
            else:
                debug("NO_INDICATOR")
            debug("Vehicle RPM: " + str(self.obdPort.getReading(12)))
            
            return False
        
        # Check that the average velocity is greater than threshold
        deltaDistance = self.rangeReadings[0].range - self.rangeReadings[-1].range
        deltaTime = self.rangeReadings[-1].time - self.rangeReadings[0].time
        averageVelocity = deltaDistance / float(deltaTime) # ms-1 as range in mm and time in ms (mm/ms)
        #debug("ddistance: " + str(deltaDistance))
        #debug("dtime: " + str(deltaTime))

        if averageVelocity > CyclistDetector.RELATIVE_VELOCITY_ALERT_THRESHOLD:
            # Check that velocity between two readings does deviate too much from
            # average velocity (if it is somewhat similar, this indicates a constantly
            # approaching object rather than a single faulty oldest or newest reading.
            if self.testJitter:
                for i in xrange(len(self.rangeReadings) - 2):
                    deltaD = self.rangeReadings[i].range - self.rangeReadings[i+1].range
                    deltaT = self.rangeReadings[i+1].time - self.rangeReadings[i].time
                    v = deltaD / float(deltaT)
                    if ((v > (averageVelocity * (1 + CyclistDetector.ALLOWABLE_VELOCITY_JITTER))) or
                            (v < (averageVelocity * (1 - CyclistDetector.ALLOWABLE_VELOCITY_JITTER)))):
		        if not self.isInWarmup:
			    self.displayText("Alert blocked. Reason: Too much ultrasound jitter. ")
                        return False # Outside of allowable jitter
                    # else continue
            if self.indicator.isIndicatingLeft() or  not self.testIndicator:
                rpm = self.obdPort.getReading(12)
                if  rpm > CyclistDetector.RPM_THRESHOLD or not self.testVehicleSpeed:
                    return averageVelocity
                else:
			self.displayText("Alert blocked. Reason: Vehicle rpm too low: " + str(rpm))
            else:
		    self.displayText("Alert blocked. Reason: Indicator not going.")
        else:
            # Cyclist not going fast enough.
	    #self.displayText("Average velocity too low: " + str(averageVelocity))
            return False;
                
    def displayText(self, text):
        self.window.addText(text + "\n")
        
'''
    Print message if shouldDebug is True
'''
def debug(message):
    if shouldDebug:
        print message
                          

'''
    Returns the filename in the format
    us_log_yyyy-mm-dd_hh-mm-ss
'''
def createFileName():
    return "us_log_" + time.strftime("%Y-%m-%d_%H-%M-%S")


'''
    Main method
'''
if __name__ == "__main__":
    cyclistDetector = CyclistDetector(False, False)
    thread1 = threading.Thread(target=cyclistDetector.start)
    #thread1.daemon = True
    thread1.start()
    cyclistDetector.startGui()


        
        
        
