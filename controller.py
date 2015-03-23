#!/usr/bin/env python
###########################################################################
# controller.py
#
# @Author Tim Grunshaw
#
# Controller providing an interface between model & view
#
###########################################################################



class Controller:

    def __init__(self, model):
        self.model = model
    
    # Callbacks
    def indicatorToggle(self):
        self.model.testIndicator  = not self.model.testIndicator
        
    def vehicleSpeedToggle(self):
        self.model.testVehicleSpeed  = not self.model.testVehicleSpeed
        
    def jitterToggle(self):
        self.model.testJitter  = not self.model.testJitter
        
    def testWarningLights(self):
        self.model.warningLEDS.flash(2)

    def quit(self):
        self.model.quitGui()