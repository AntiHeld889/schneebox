import cellular
import machine
"""Your main code goes here!"""

print("V4")
print('GPRS-Status:', cellular.gprs())

try:
  if not cellular.gprs():
    try:
      print("Trying to connect\r\n")
      cellular.gprs("pepper", "", "")
      print("Connected to gprs...\r\n")
    except Exception as e:
    print("Couldn't connect to gprs:", e)
    machine.reset()
