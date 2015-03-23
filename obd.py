#!/usr/bin/env python
###########################################################################
# obd.py
#
# @Author Tim Grunshaw
# Modified from Martin O'Hanlon's code: https://github.com/martinohanlon/pyobd
#
# Provides OBD functionality as needed for the CyclistDetector project.
#
###########################################################################

import obd_io
import serial
import platform
import obd_sensors
from datetime import datetime
import time

class OBD():
    
    '''
        Initalises and connects to OBD, then identifies supported sensors (takes >6seconds)
    '''
    def __init__(self, logger, serialPort):
        self.logger = logger
        self.serialPort = serialPort
        self.obdPort = None
        self.connect()
        time.sleep(3)
        if not self.is_connected():
            self.logger.displayText("Not connected")
            self.logger.displayText("Ignoring OBD: setting fixed speed of 1000")
	    self.logger.displayText("Continuing...")
        else:
            self.identify_sensors()      

    '''
        Internal method to connect
    '''
    def connect(self):
        self.obdPort = obd_io.OBDPort(self.logger, self.serialPort, None, 2, 2)
            
    
    '''
        Returns whether connected or not
    '''
    def is_connected(self):
        return self.obdPort.State
    
	'''
        Call this when exiting.
    '''
	def closePort(self):
		self.obdPort.close()
		
	'''
		Internal method to indentify support sensors.
	'''
    def identify_sensors(self):

        #Find supported sensors - by getting PIDs from OBD
        # its a string of binary 01010101010101 
        # 1 means the sensor is supported
        self.supp = self.obdPort.sensor(0)[1]
        self.supportedSensorList = []
        self.unsupportedSensorList = []

        # loop through PIDs binary
        for i in range(0, len(self.supp)):
            if self.supp[i] == "1":
                # store index of sensor and sensor object
                self.supportedSensorList.append([i+1, obd_sensors.SENSORS[i+1]])
            else:
                self.unsupportedSensorList.append([i+1, obd_sensors.SENSORS[i+1]])
        
        for supportedSensor in self.supportedSensorList:
            self.logger.displayText("supported sensor index = " + str(supportedSensor[0]) + " " + str(supportedSensor[1].shortname))        
        
        time.sleep(3)
        
        if(self.obdPort is None):
            return None

    '''
        Return the value of sensor with shortname == sensorName
    '''
    def getReading(self, sensorIndex):
	if(not self.is_connected()):
	    return 1000 #Override to allow program to run
        (name, value, unit) = self.obdPort.sensor(sensorIndex)
        return value  # If none of the sensor match
