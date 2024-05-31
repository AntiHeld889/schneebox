import cellular
import gc
import time
import machine
import network
import upip

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



def main():
    # Install Senko from PyPi
    try:
        import senko
    except ImportError:
        upip.install("micropython-senko")
        import senko

    OTA = senko.Senko(user="AntiHeld889", repo="schneebox", working_dir="V1", files=["main.py", "testota.py"])

    if OTA.update():
        print("Updated to the latest version! Rebooting...")
        machine.reset()

if __name__ == "__main__":
    main()
