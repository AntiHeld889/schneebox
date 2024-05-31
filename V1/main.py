import cellular
import machine
import socket
import time
import json

"""Your main code goes here!"""
machine.watchdog_reset()
print("Watchdog reset\r\n")

machine.watchdog_on(180)
print("Watchdog ON\r\n")

print("V5")
time.sleep(10)
print('GPRS-Status:', cellular.gprs())
time.sleep(4)

try:
    print("Trying to connect\r\n")
    cellular.gprs("pepper", "", "")
    print("Connected to gprs...\r\n")
except Exception as e:
    print("Couldn't connect to gprs:", e)
    machine.reset()
