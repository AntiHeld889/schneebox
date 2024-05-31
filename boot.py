import cellular
import machine
import socket
import time
import json

led = machine.Pin(27, machine.Pin.OUT)
led.value(1)
time.sleep(10)
try:
    print("Trying to connect to GPRS...")
    cellular.gprs("pepper", "", "")
    print("Connected to GPRS.")
except Exception as e:
    print("Couldn't connect to GPRS:", e)
    machine.reset()
time.sleep(1)

print("IP:", socket.get_local_ip())
quality = cellular.get_signal_quality()
print("Signal quality: {} -> {}%".format(quality[0], quality[0] * 100 / 31))
time.sleep(1)
print("OTA start")
ota_updater = OTAUpdater(firmware_url, "main.py")
ota_updater.download_and_install_update_if_available()
