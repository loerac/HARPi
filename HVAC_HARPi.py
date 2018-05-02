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

GPIO.setup(coilList, GPIO.OUT)

# Steps
StepCount = 8
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
    delay = 1/1000
    steps = 128
    for i in range(steps): 
        for j in range(StepCount): 
            setStep(Seq[j][0], Seq[j][1], Seq[j][2], Seq[j][3])
            time.sleep(delay)
            
def close():
    delay = 1/1000
    steps = 128
    for i in range(steps):
        for j in range(StepCount):
            setStep(Seq[j][3], Seq[j][2], Seq[j][1], Seq[j][0])
            time.sleep(delay)

def sendTemp(temperature):
    HVAC_HARPi_Child.status_msg(temperature)

temperature,pressure,humidity = BME280.readBME280All()
open()
close()
sendTemp("{:.2f}".format(temperature))


    
GPIO.cleanup()

   
    