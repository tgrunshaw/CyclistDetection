#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
ZetCode Tkinter tutorial

This program creates a quit
button. When we press the button,
the application terminates. 

author: Jan Bodnar
last modified: December 2010
website: www.zetcode.com
'''

from Tkinter import *
from ttk import *

import controller
import cyclist_detector


class MainWindow(Frame):
  
    def __init__(self, parent, model, controller):
        Frame.__init__(self, parent)   
         
        self.parent = parent
        self.model = model
        self.controller = controller
        self.scrollLock = False
        
        self.initUI()
        
    def initUI(self):
        self.parent.title("Cyclist Detector [Alpha] - By Tim Grunshaw")
        self.style = Style()
        self.style.theme_use("clam")
        


        # Create inner frame for everything else
        self.mainFrame = Frame(self, relief=RAISED, borderwidth=1)
        self.addDebugOutputFr(self.mainFrame)
        
        # Buttons
        # buttonsLabel = Label(self.mainFrame, text="Enable checking of...")
        # buttonsLabel.pack(pady=4)
        self.addControlButtons(self.mainFrame)
        
        self.mainFrame.pack(fill=BOTH, expand=1)

        # Buttons in outermost frame.
        stopScrollButton = Button(self, text="Scrolllock", command=self.scrollLockToggle)
        stopScrollButton.pack(side=LEFT)
        closeButton = Button(self, text="Close", command=self.controller.quit)
        closeButton.pack(side=RIGHT, padx=5, pady=5)
        
        self.pack(fill=BOTH, expand=1)
    
    # Debug output
    def addDebugOutputFr(self,frame):
		#define a new frame and put a text area in it
		textfr=Frame(frame)
		self.text=Text(textfr,height=10,width=50,background='white')
		
		# put a scroll bar in the frame
		scroll=Scrollbar(textfr)
		self.text.configure(yscrollcommand=scroll.set)
		
		#pack everything
		self.text.pack(side=LEFT)
		scroll.pack(side=RIGHT,fill=Y)
		textfr.pack(side=LEFT)
		return
        
    # Control buttons
    def addControlButtons(self, frame):
        # Indicator
        indFrame = Frame(frame, relief=RAISED, borderwidth=1)
        indLbl = Label(indFrame, text="Indicator:         ")
        indLbl.pack(side=LEFT,padx=4)
        self.indTextValue = StringVar()
        self.indTextValue.set("Off") # Default
        indValueLbl = Label(indFrame, textvariable=self.indTextValue)
        indValueLbl.pack(side=LEFT,padx=4)
        indCB = Checkbutton(indFrame, text="Ignore?", command=self.controller.indicatorToggle)
        indCB.pack(side=RIGHT)
        indFrame.pack(fill=X,pady=2)
        
        # Speed
        speedFrame = Frame(frame, relief=RAISED, borderwidth=1)
        speedLbl = Label(speedFrame, text="Vehicle Speed: ")
        speedLbl.pack(side=LEFT,padx=4)
        self.speedValue = StringVar()
        self.speedValue.set(0) # Default
        speedValueLbl = Label(speedFrame, textvariable=self.speedValue)
        speedValueLbl.pack(side=LEFT,padx=4)
        speedCB = Checkbutton(speedFrame, text="Ignore?", command=self.controller.vehicleSpeedToggle)
        speedCB.pack(side=RIGHT)
        speedFrame.pack(fill=X,pady=2)
        
        
        # Jitter
        jitterFrame = Frame(frame, relief=RAISED, borderwidth=1)
        jitterLbl = Label(jitterFrame, text="Jitter setting:    ")
        jitterLbl.pack(side=LEFT,padx=4)
        jitterValueLbl = Label(jitterFrame, text=cyclist_detector.CyclistDetector.ALLOWABLE_VELOCITY_JITTER)
        jitterValueLbl.pack(side=LEFT,padx=4)
        jitterCB = Checkbutton(jitterFrame, text="Ignore?", command=self.controller.jitterToggle)
        jitterCB.pack(side=RIGHT)
        jitterFrame.pack(fill=X,pady=2)

        
        testLightsButton = Button(frame, text="Test Warning Lights", command=self.controller.testWarningLights)
        testLightsButton.pack(fill=X,pady=2,side=BOTTOM)
        

    def setIsIndicating(self, state):
        if(state):
            self.indTextValue.set("On")
        else:
            self.indTextValue.set("Off")
    
    def setSpeed(self, speed):
        self.speedValue.set(speed)
        
    def addText(self, theText):
        self.text.insert(END, theText)
        if not self.scrollLock:
            self.text.see(END)
    
    def scrollLockToggle(self):
        self.scrollLock = not self.scrollLock


      
if __name__ == "__main__":
    cd = cyclist_detector.CyclistDetector(False,False)
    c = controller.Controller(cd)
    cd.startGui()    
