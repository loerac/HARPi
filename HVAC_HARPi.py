#!/usr/bin/python

import BME280
import RPi.GPIO as GPIO
from child_mqtt import child_mqtt
import time
from time import sleep

GPIO.setmode(GPIO.BOARD)          #set so pin numbers are used to reference pins rather than GPIO numbers
GPIO.setwarnings(False)           #turn warnings off because they are annoying

NAME = "HVAC_HARPi"               #name of child node to pass to parent node
TOPIC = "Brennen/Temp"            #set topic heirarchy
BROKER_IP = "HARPIO.DUCKDNS.ORG"  #IP address of the MQTT broker
TOKEN = "TEMP"                    #token is predefined in child_mqtt for content formatting purposes
DESC =  "TEMP inside HVAC"        #description of child node to pass to parent

HVAC_HARPi_Child = child_mqtt(NAME, TOPIC, BROKER_IP, TOKEN, DESC) #instantiate child node; parent node is automatically notified

coil_1_pin = 15                # orange
coil_2_pin = 13                # yellow
coil_3_pin = 11                # pink
coil_4_pin = 7                 # blue
coilList = [15,13,11,7]

GPIO.setup(coilList, GPIO.OUT) #set GPIO pins for stepper to ouput

# Stepper Motor Specs #
# Stride Angle: 5.625 #
# Gear Ratio: 64      #
# Total number of steps per revolution is (360 / Stride Angle) * Gear Ratio #
# Total = (360 / 5.625)*64 = 4096 steps for 360-degrees of rotation #
# 90-degree rotation = 4096 / 4 = 1024 steps #
numSeqs = 128                  #numSeqs = 1024-steps / 8-StepCounts = 1024 / 8 = 128-sequences; a sequence is one iteration through the Step dictionary
delay = 1/1000                 #1ms
StepCount = 8                  #number of steps in a Seq
Step = {}                      #instatiate dictionary to be used like a 2-D Array in open() and close() functions that call setStep()
Step[0] = [1,0,0,0]
Step[1] = [1,1,0,0]
Step[2] = [0,1,0,0]
Step[3] = [0,1,1,0]
Step[4] = [0,0,1,0]
Step[5] = [0,0,1,1]
Step[6] = [0,0,0,1]
Step[7] = [1,0,0,1]
 
def setStep(w1, w2, w3, w4):  #pass the contents of the Step dictionary to the corresponding GPIO pins
    GPIO.output(coil_1_pin, w1)
    GPIO.output(coil_2_pin, w2)
    GPIO.output(coil_3_pin, w3)
    GPIO.output(coil_4_pin, w4)
 
def open():                                                         #open() will pass the values in the selected Step index from left to right
    for i in range(numSeqs):                                          #iterate over numSeqs; 128-Sequences
        for j in range(StepCount):                                    #iterate over StepCount; 8-Steps per Sequence; j selects the step index
            setStep(Step[j][0], Step[j][1], Step[j][2], Step[j][3])   #pass the values at the given indices to setStep()
            time.sleep(delay)                                         #delay 1ms
            
def close():                                                        #close() will pass the values in the selected Step index from right to left
    for i in range(steps):                                            #iterate over numSeqs; 128-Sequences
        for j in range(StepCount):                                    #iterate over StepCount; 8-Steps per Sequence; j selects the step index
            setStep(Step[j][3], Step[j][2], Step[j][1], Step[j][0])   #pass the values at the given indices to setStep()
            time.sleep(delay)                                         #delay 1ms

while(StepCount == 8):
    temperature,pressure,humidity = BME280.readBME280All()                    #instantiate  temperature, pressure, and humidty and pass the respective values with readBME280All()
    HVAC_HARPi_Child.status_msg("{:.2f}".format(temperature))                 #send temperature to MQTT broker as a string (was a float)
    
    desiredTemp = int(input("What is the desired temperature? ")  )           #ask user for desired temperature 
    pressure = float(input("What is the static pressure inside HVAC node? ")) #ask user for static pressure to overwrite barometric pressure reading from BME280
    if(pressure > 0.75):                                                      #if pressure is greater than 0.75 inches of water column, then pressure is too high and the node must be opened
        open()
    if((pressure <= 0.75) and (desiredTemp != temperature)):                  #if pressure is less than or equal to 0.75 inches of water column AND desiredTemp is not equal to temperature then close the node
        close()
        
    setStep(0,0,0,0)
    time.sleep(5)



    
GPIO.cleanup()

   
    
