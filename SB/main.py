import cellular
import machine
from env import mqtt_name, mqtt_server, mqtt_port, mqtt_username, mqtt_password
from umqtt import robust
import socket
import time
import json
import senko

version_state = "V2.0"

# Initialisierung der Pins
led = machine.Pin(27, machine.Pin.OUT, 0)
relais1 = machine.Pin(29, machine.Pin.OUT, 0)
relais2 = machine.Pin(26, machine.Pin.OUT, 0)
relais3 = machine.Pin(25, machine.Pin.OUT, 0)
relais4 = machine.Pin(30, machine.Pin.OUT, 0)
Box1 = machine.Pin(18, machine.Pin.IN)
Box2 = machine.Pin(16, machine.Pin.IN)

# Initialisierung der Zählvariable
counter = 0
TIME_PERIOD = 10
LINEAR_MOTOR_OPERATION_TIME = 19  # Sekunden

# MQTT-Topics
topics = {
    "IP": "0_userdata/0/SB/IP",
    "B1": "0_userdata/0/SB/B1",
    "B2": "0_userdata/0/SB/B2",
    "Box1": "0_userdata/0/SB/KSBox1",
    "Box2": "0_userdata/0/SB/KSBox2",
    "relais1": "0_userdata/0/SB/R1",
    "relais2": "0_userdata/0/SB/R2",
    "relais3": "0_userdata/0/SB/R3",
    "relais4": "0_userdata/0/SB/R4",
    "data": "0_userdata/0/SB/Counter",
    "answer": "0_userdata/0/SB/Antwort",
    "signal": "0_userdata/0/SB/Signal",
    "version": "0_userdata/0/SB/Version",
    "update": "0_userdata/0/SB/Update",
    "reset": "0_userdata/0/SB/Reset"
}

# Boot-Phase
def initialize_system():
    print("Version: ", version_state)
    print("Boot start")
    led.value(1)
    time.sleep(5)
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
    machine.watchdog_on(180)
    print("Watchdog ON")
    print("Boot end")
    led.value(0)

def configure_mqtt_client():
    #client = robust.MQTTClient("SB", "r3dfp.de", 1883, "admin", "Schneewitte-99")
    client = robust.MQTTClient(mqtt_name, mqtt_server, mqtt_port, mqtt_username, mqtt_password)
    client.connect()
    client.set_callback(mqtt_callback)
    for topic in topics.values():
        client.subscribe(topic)
    print("MQTT connected.")
    return client

def mqtt_callback(topic, msg):
    print('Received Data:  Topic = {}, Msg = {}'.format(topic, msg))
    topic = topic.decode('utf-8')
    msg = msg.decode('utf-8')
    
    if topic == topics["relais1"]:
        handle_relais_state(relais1, relais2, msg)
    elif topic == topics["relais2"]:
        handle_relais_state(relais2, relais1, msg)
    elif topic == topics["relais3"]:
        handle_relais_state(relais3, relais4, msg)
    elif topic == topics["relais4"]:
        handle_relais_state(relais4, relais3, msg)
    elif topic == topics["B1"]:
        if msg == "true":
            box1_start()
    elif topic == topics["B2"]:
        if msg == "true":
            box2_start()
    elif topic == topics["reset"]:
        if msg == "true":
            print("Neustart in 3 Sekunden")
            time.sleep(3)
            machine.reset()
    elif topic == topics["update"]:
        if msg == "true":
            update()

def update()
    publish_data(client, topics["answer"], "Update wird gestartet")
    time.sleep(1)
    OTA = senko.Senko(user="AntiHeld889", repo="schneebox",branch="master", working_dir="SB", files=["main.py"])
    
    if OTA.update():
    publish_data(client, topics["answer"], "Update durchgeführt! Nestart...")
    print("Updated to the latest version! Rebooting...")
    machine.reset()
    

def handle_relais_state(primary_relais, secondary_relais, state):
    if state == "false":
        primary_relais.value(0)
    elif state == "true":
        secondary_relais.value(0)
        time.sleep(0.5)
        primary_relais.value(1)

def publish_data(client, topic, data):
    msg = json.dumps(data)
    print('Seceived Data:  Topic = {}, Msg = {}'.format(topic, msg))
    client.publish(topic, msg)

def box1_start():
    control_box(relais1, relais2, topics["Box1"], "Linearmotor Box 1 wird ausgefahren", "Linearmotor Box 1 fertig ausgefahren", "Linearmotor Box 1 wird eingefahren", "Linearmotor Box 1 fertig eingefahren")

def box2_start():
    control_box(relais3, relais4, topics["Box2"], "Linearmotor Box 2 wird ausgefahren", "Linearmotor Box 2 fertig ausgefahren", "Linearmotor Box 2 wird eingefahren", "Linearmotor Box 2 fertig eingefahren")

def control_box(primary_relais, secondary_relais, box_topic, starta_msg, startb_msg, enda_msg, endb_msg):
    secondary_relais.value(0)
    publish_data(client, topics["answer"], starta_msg)
    time.sleep(0.5)
    primary_relais.value(1)
    time.sleep(12)
    box_state = Box1.value() == 1 if box_topic == topics["Box1"] else Box2.value() == 1
    publish_data(client, box_topic,not box_state)
    time.sleep(LINEAR_MOTOR_OPERATION_TIME)
    publish_data(client, topics["answer"], startb_msg)
    machine.watchdog_reset()
    box_state = Box1.value() == 1 if box_topic == topics["Box1"] else Box2.value() == 1
    publish_data(client, box_topic,not box_state)
    time.sleep(0.2)
    publish_data(client, topics["answer"], enda_msg)
    primary_relais.value(0)
    time.sleep(0.5)
    secondary_relais.value(1)
    time.sleep(16)
    time.sleep(LINEAR_MOTOR_OPERATION_TIME)
    machine.watchdog_reset()
    secondary_relais.value(0)
    publish_data(client, topics["answer"], endb_msg)

def increment_counter():
    global counter
    counter += 1
    publish_data(client, topics["data"], counter)
    client.check_msg()
    publish_box_states()

def publish_box_states():
    box1_state = Box1.value() == 1
    box2_state = Box2.value() == 1
    publish_data(client, topics["Box1"],not box1_state)
    publish_data(client, topics["Box2"],not box2_state)
    publish_data(client, topics["IP"], socket.get_local_ip())
    signal_quality = cellular.get_signal_quality()[0]
    publish_data(client, topics["signal"], signal_quality)

def reset_mqtt():
    client.connect()
    time.sleep(0.5)
    client.set_callback(mqtt_callback)
    for topic in topics.values():
        client.subscribe(topic)

def check_gprs():
    try:
        if not cellular.gprs():
            print('GPRS-Status:', cellular.gprs())
            time.sleep(5)
            cellular.gprs("pepper", "", "")
            time.sleep(1)
            reset_mqtt()
        else:
            print("Already connected...")
            client.check_msg()
            machine.watchdog_reset()
    except Exception as err:
        print("GPRS check error:", str(err))

# Hauptprogramm
if __name__ == "__main__":
    initialize_system()
    client = configure_mqtt_client()

    while True:
        for _ in range(TIME_PERIOD):
            for _ in range(2):
                check_gprs()
                time.sleep(1)
        increment_counter()
