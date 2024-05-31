import cellular
import machine
import socket
import time
import json

"""Your main code goes here!"""

print("V7")
time.sleep(10)
try:
    print("Trying to connect\r\n")
    cellular.gprs("pepper", "", "")
    print("Connected to gprs...\r\n")
except Exception as e:
    print("Couldn't connect to gprs:", e)
    machine.reset()
