#!/usr/bin/python

import BME280
import RPi.GPIO as GPIO
import time
from child_mqtt import child_mqtt
from time import sleep

GPIO.setmode(GPIO.BOARD)

NAME = "HVAC_HARPi"
TOPIC = "Brennen/Temp"
BROKER_IP = "HARPIO.DUCKDNS.ORG"
TOKEN = "TEMP" 
DESC =  "TEMP inside HVAC"

HVAC_HARPi_Child = child_mqtt(NAME, TOPIC, BROKER_IP, TOKEN, DESC)

coil_1_pin = 15  # orange
coil_2_pin = 13  # yellow
coil_3_pin = 11  # pink
coil_4_pin = 7   # blue
coilList = [15,13,11,7]

GPIO.setwarnings(False)
GPIO.setup(coilList, GPIO.OUT)


# Steps
steps = 128     #128-steps * 8-StepCount = 1024-steps: 90-degrees
delay = 1/1000  #1ms
StepCount = 8   #number of steps in Seq
Seq = {}
Seq[0] = [1,0,0,0]
Seq[1] = [1,1,0,0]
Seq[2] = [0,1,0,0]
Seq[3] = [0,1,1,0]
Seq[4] = [0,0,1,0]
Seq[5] = [0,0,1,1]
Seq[6] = [0,0,0,1]
Seq[7] = [1,0,0,1]
 
def setStep(w1, w2, w3, w4):
    GPIO.output(coil_1_pin, w1)
    GPIO.output(coil_2_pin, w2)
    GPIO.output(coil_3_pin, w3)
    GPIO.output(coil_4_pin, w4)
 
def open():
    for i in range(steps): 
        for j in range(StepCount): 
            setStep(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3]) #
            time.sleep(delay)
            
def close():
    for i in range(steps):
        for j in range(StepCount):
            setStep(Seq[j][3], Seq[j][2], Seq[j][1], Seq[j][0])
            time.sleep(delay)

while(StepCount == 8):
    temperature,pressure,humidity = BME280.readBME280All()             #instantiate  temperature, pressure, and humidty and pass the respective values with readBME280All()
    HVAC_HARPi_Child.status_msg("{:.2f}".format(temperature))          #send temperature to MQTT broker as a string (was a float)
    
    desiredTemp = int(input("What is the desired temperature? ")  )         #ask user for desired temperature 
    pressure = float(input("What is the static pressure inside HVAC node? ")) #ask user for static pressure to overwrite barometric pressure reading from BME280
    if(pressure > 0.75):                                               #if pressure is greater than 0.75 inches of water column, then pressure is too high and the node must be opened
        open()
    if((pressure <= 0.75) and (desiredTemp != temperature)):           #if pressure is less than or equal to 0.75 inches of water column AND desiredTemp is not equal to temperature then close the node
        close()
        
    setStep(0,0,0,0)
    time.sleep(5)



    
GPIO.cleanup()

   
    