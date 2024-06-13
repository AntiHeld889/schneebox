import cellular, machine, socket, time, json
from env import mqtt_name, mqtt_server, mqtt_port, mqtt_username, mqtt_password
from umqtt import robust


version_state = "V2.3"

# Initialisierung der Pins

adc = machine.ADC(1)
led = machine.Pin(27, machine.Pin.OUT, 0)
relais1 = machine.Pin(29, machine.Pin.OUT, 0)
relais2 = machine.Pin(26, machine.Pin.OUT, 0)
relais3 = machine.Pin(25, machine.Pin.OUT, 0)
relais4 = machine.Pin(30, machine.Pin.OUT, 0)
Box1 = machine.Pin(18, machine.Pin.IN)
Box2 = machine.Pin(16, machine.Pin.IN)

# Initialisierung Variablen

counter = 0
TIME_PERIOD = 10
LINEAR_MOTOR_OPERATION_TIME = 19  # Sekunden
WATCHDOG_TIMEOUT = 180

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
    "lmopt": "0_userdata/0/SB/LMOPT",
    "Bat": "0_userdata/0/SB/Battery",
    "JS": "0_userdata/0/SB/JS",
    "reset": "0_userdata/0/SB/Reset"
}

# Boot-Phase
def initialize_system():
    print("Version: ", version_state)
    print("Boot start")
    led.value(1)
    time.sleep(6)
    try:
        print("Trying to connect to GPRS...")
        cellular.gprs("pepper", "", "") #internet.telekom
        print("Connected to GPRS.")
    except Exception as e:
        print("Couldn't connect to GPRS:", e)
        machine.reset()
    time.sleep(1)
    print("IP:", socket.get_local_ip())
    quality = round(cellular.get_signal_quality()[0] * 100 / 31)
    print("Signal quality: {}%".format(quality))
    machine.watchdog_on(WATCHDOG_TIMEOUT)
    print("Watchdog ON")
    print("Boot end")
    led.value(0)

def configure_mqtt_client():
    client = robust.MQTTClient(mqtt_name, mqtt_server, mqtt_port, mqtt_username, mqtt_password)
    client.connect()
    client.set_callback(mqtt_callback)
    for topic in topics.values():
        client.subscribe(topic)
    print("MQTT connected.")
    return client

def mqtt_callback(topic, msg):
    global lmop_time
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
            reset()
    elif topic == topics["update"]:
        if msg == "true":
            update()
    elif topic == topics["lmopt"]:
        try:
            lmop_time = int(msg)
            print('Neues Blinkintervall erhalten: {} Sekunden'.format(lmop_time))
        except ValueError:
            print('Ungültige Nachricht: {}'.format(lmop_time))


def reset():
    publish_data(client, topics["answer"], "Reset Befehl erhalten")
    time.sleep(1)
    machine.reset()

def update():
    import gc
    import senko
    gc.collect()
    gc.enable()
    time.sleep(0.2)
    publish_data(client, topics["answer"], "Update gestartet...")
    OTA = senko.Senko(user="AntiHeld889", repo="schneebox", working_dir="SB", files=["main.py"])
    
    if OTA.update():
        print("Updated to the latest version! Rebooting...")
        time.sleep(0.2)
        publish_data(client, topics["answer"], "Update durchgeführt! Neustart...")
        time.sleep(1)
        machine.reset()
    
def handle_relais_state(primary_relais, secondary_relais, state):
    if state == "false":
        primary_relais.value(0)
    elif state == "true":
        secondary_relais.value(0)
        time.sleep(0.5)
        primary_relais.value(1)

def publish_data(client, topic, data):
    machine.watchdog_reset()
    msg = json.dumps(data)
    print('Seceived Data:  Topic = {}, Msg = {}'.format(topic, msg))
    client.publish(topic, msg)

def box1_start():
    control_box(relais1, relais2, topics["Box1"], "Linearmotor Box 1 wird ausgefahren", "Linearmotor Box 1 fertig ausgefahren", "Linearmotor Box 1 wird eingefahren", "Linearmotor Box 1 fertig eingefahren")

def box2_start():
    control_box(relais3, relais4, topics["Box2"], "Linearmotor Box 2 wird ausgefahren", "Linearmotor Box 2 fertig ausgefahren", "Linearmotor Box 2 wird eingefahren", "Linearmotor Box 2 fertig eingefahren")

def control_box(primary_relais, secondary_relais, box_topic, starta_msg, startb_msg, enda_msg, endb_msg):
    global B_state
    B_state = False
    machine.watchdog_reset()
    secondary_relais.value(0)
    publish_data(client, topics["answer"], starta_msg)
    time.sleep(0.5)
    primary_relais.value(1)
    time.sleep(12)
    box_state = Box1.value() == 1 if box_topic == topics["Box1"] else Box2.value() == 1
    publish_data(client, box_topic,not box_state)
    time.sleep(LINEAR_MOTOR_OPERATION_TIME)
    publish_data(client, topics["answer"], startb_msg)
    box_state = Box1.value() == 1 if box_topic == topics["Box1"] else Box2.value() == 1
    publish_data(client, box_topic,not box_state)
    time.sleep(0.2)
    publish_data(client, topics["answer"], enda_msg)
    primary_relais.value(0)
    time.sleep(0.5)
    secondary_relais.value(1)
    time.sleep(16)
    time.sleep(LINEAR_MOTOR_OPERATION_TIME)
    secondary_relais.value(0)
    publish_data(client, topics["answer"], endb_msg)
    machine.watchdog_reset()

def publish_box_states():
    battery_value = adc.read()
    voltage = battery_value #* (3.3 / 65535) * VOLTAGE_DROP_FACTOR
    global counter
    counter += 1
    if counter >= 6000:
        print("Counter reached 6000, restarting...")
        publish_data(client, topics["answer"], "Counter 6000 Restart...")
        time.sleep(1)
        machine.reset()
    box1_state = Box1.value() == 1
    box2_state = Box2.value() == 1
    signal_quality = round(cellular.get_signal_quality()[0] * 100 / 31)
    
    # Sammle die Daten in einem Dictionary
    alldata = {
        "box1_state": not box1_state,
        "box2_state": not box2_state,
        "battery": voltage,
        "counter": counter,
        "ip": socket.get_local_ip(),
        "version": version_state,
        "signal_quality": signal_quality
    }
    
    # Veröffentliche den JSON-String an das Topic JS
    publish_data(client, topics["JS"], alldata)
    
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
    except Exception as err:
        print("GPRS check error:", str(err))

# Hauptprogramm
if __name__ == "__main__":
    time.sleep(2)
    initialize_system()
    client = configure_mqtt_client()

    while True:
        for _ in range(TIME_PERIOD):
            for _ in range(2):
                check_gprs()
                time.sleep(1)
        publish_box_states()

