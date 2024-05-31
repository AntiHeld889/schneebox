import cellular
import machine
import socket
import time
import json

print("Boot start")
time.sleep(1)
print("10")
time.sleep(1)
print("9")
time.sleep(1)
print("8")
time.sleep(1)
print("7")
time.sleep(1)
print("6")
time.sleep(1)
print("5")
time.sleep(1)
print("4")
time.sleep(1)
print("3")
time.sleep(1)
print("2")
time.sleep(1)
print("1")


try:
    print("Trying to connect\r\n")
    cellular.gprs("pepper", "", "")
    print("Connected to gprs...\r\n")
except Exception:
    print("Couldn't connect to gprs...\r\n")
    machine.reset()



# Watchdog-Timer aktivieren
machine.watchdog_on(180)
print("Watchdog ON\r\n")

# Check for OTA updates
import senko
OTA = senko.Senko(user="RangerDigital", repo="senko", working_dir="examples", files=["main.py"])

if OTA.update():
    print("Updated to the latest version! Rebooting...")
    machine.reset()

# Import mqtt (download client if necessary)
#import upip
#upip.install("micropython-urequests")

print("Ende\r\n")
