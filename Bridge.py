#!/usr/bin/python

#===============================================
# Program name: bridge.py
# Desc: Linking  the  children  nodes  to  the
#       parent  node.  The  parent  node  will
#       receive the name, topic, IP, token, and
#       description of the children where. There
#       is  also  the  aspect  of  pinging  the
#       children to check if they're connected.
#
# Author: HARPi
# Date: 25.04.18
#===============================================

# Imports
#===============================================
# MQTT
import paho.mqtt.client as mqtt

# Time
from time import sleep

# Socket for IP address
import socket

# Splitting token
import shlex

# Pinging
import subprocess

# Print Pretty
from pprint import pprint

# Global Variables
from global_var import Global_Var

# JSON
import json

class Bridge:
    def __init__(self):
        # Getting IP address
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))

        # Initialize MQTT
        #self.BROKER = sock.getsockname()[0]
        self.BROKER = "harpio.duckdns.org"
        sock.close()
        self.PORT = 1883
        self.ALIVE = 60
        self.MQTTC = mqtt.Client()
        self.TOPIC = "HARPi/#"
        print("IP/DNS     : %s" %self.BROKER)
        print("Main topic : %s" %self.TOPIC)

        # Global Variables
        self.gv = Global_Var()
        self.NODE_LIST = []
        self.NODE_DICT = {self.gv.get_complete() : 0}
        self.NODE_BIT = 0

        # Set up MQTT with broker
        self.MQTTC.connect(self.BROKER, self.PORT, self.ALIVE)

        # Set up event handlers
        self.MQTTC.on_connect = self.connect
        self.MQTTC.on_message = self.message
        self.MQTTC.on_publish = self.publish

    # Subscribe to a topic
    def connect(self, mosq, obj, flag, rc):
        self.MQTTC.subscribe(self.TOPIC, 0)

    # Print out incoming messages
    def message(self, mosq, obj, msg):
        topic = msg.topic.split("HARPi/")[1]
        data = msg.payload
        if topic[:7] != "webdata":
            print("[ in ] %s : %s" %(topic, data))

        if topic[:8] == self.gv.get_set_node():
            self.set_node(topic[9:], data)
        elif topic[:6] == self.gv.get_status():
            self.status_node(topic[7:], data)

    # Send message
    def publish(self, client, userdata, msg):
        return

    # Message event handler
    def send_msg(self, msg):
        self.MQTTC.publish("HARPi/webdata/", json.dumps(msg))

    # Store new node values in dictionary
    def set_node(self, key, value):
        self.NODE_DICT[key] = value
        print("[ st ] {} : {}".format(key, value))
        if self.NODE_DICT[self.gv.get_complete()] == "1":
            self.NODE_BIT |= self.gv.get_new_node()
            self.NODE_LIST.append(self.NODE_DICT.copy())
            print("[ ok ] New node entered.....")

    # Setting the status of the node
    def status_node(self, key, value):
        for i in range(0, len(self.NODE_LIST)):
            if key == self.NODE_LIST[i][self.gv.get_topic()]:
                self.NODE_LIST[i][self.gv.get_status()] = value
                self.NODE_LIST[i][self.gv.get_complete()] = 1
                self.NODE_BIT |= self.gv.get_status_node()
                print("[ ok ] {} : {}".format(self.NODE_LIST[i][self.gv.get_topic()], value))

    # Return dictionary with new child values
    def get_node(self):
        self.NODE_DICT[self.gv.get_complete()] = 0
        self.NODE_BIT &= (self.gv.get_new_node() ^ self.gv.get_clear_bit())
        return self.NODE_DICT.copy()

    # Return updated dictionary
    def update_node(self):
        for i in range(0, len(self.NODE_LIST)):
            if self.NODE_LIST[i][self.gv.get_complete()] == 1:
                self.NODE_BIT &= (self.gv.get_status_node() ^ self.gv.get_clear_bit())
                self.NODE_LIST[i][self.gv.get_complete()] = 0
                return self.NODE_LIST[i]

    # Check if new node is ready
    def node_status(self, st):
        if st == self.gv.get_new_node():
            return (self.NODE_BIT & self.gv.get_new_node())
        elif st == self.gv.get_status_node():
            return (self.NODE_BIT & self.gv.get_status_node())

    # Run MQTT loop
    def mqtt_loop(self):
        self.MQTTC.loop()

    # Check connection with children
    def check_connection(self):
        for i in range(0, len(self.NODE_LIST)):
            ip = self.NODE_LIST[i][self.gv.get_ip()]
            conn = shlex.split("ping -c1 %s" %ip)
            try:
                output = subprocess.check_output(conn)
            except subprocess.CalledProcessError, e:
                # Call out to GUI letting know cannot connect to given IP
                print("[ ER ] Error: not able to connnect to %s" %ip)
            else:
                print("[ ok ] Connected: %s" %ip)

if __name__=="__main__":
    bd = Bridge()
    my_list = []
    while True:
        bd.mqtt_loop()
        if bd.node_status(1) == 1:
            print("New node:")
            my_list.append(bd.get_node())
            parsed = json.loads(json.dumps(my_list))
            print(json.dumps(parsed, indent=4))
            bd.send_msg(my_list)
        elif bd.node_status(2) == 2:
            print("Updated node:")
            temp_list = bd.update_node()
            key = temp_list['topic']
            for i in range(0, len(my_list)):
                if my_list[i]['topic'] == key:
                    my_list[i] = temp_list
            parsed = json.loads(json.dumps(my_list))
            print(json.dumps(parsed, indent=4))
            bd.send_msg(my_list)
