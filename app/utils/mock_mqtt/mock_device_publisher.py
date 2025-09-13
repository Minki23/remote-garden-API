import json
import time
import random
import threading
import ssl
import logging
import paho.mqtt.client as mqtt
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

BROKER = "mqtt-broker"
PORT = 8883
DEVICE_MAC = "77:9B:2A:89:B7:80"  # schange base on your user
USER_KEY = "auth_f28a656b452944f3b3916d681558028f"  # change base on your user

CA_CERT = "/app/certs/ca/ca.crt"
CLIENT_CERT = "/app/certs/mock-client/mock-client.crt"
CLIENT_KEY = "/app/certs/mock-client/mock-client.key"

TOPIC_CONN = f"{DEVICE_MAC}/conn"
TOPIC_STATUS = f"{DEVICE_MAC}/status"
TOPIC_SENSOR = f"{DEVICE_MAC}/device/sensor"
TOPIC_CONFIRM = f"{DEVICE_MAC}/device/confirm"
TOPIC_CONTROL = f"{DEVICE_MAC}/device/control"

ACTION_MAP = {
    0: {"device": "water", "action": "on"},      # WATER_ON
    1: {"device": "water", "action": "off"},     # WATER_OFF
    2: {"device": "atomize", "action": "on"},    # ATOMIZE_ON
    3: {"device": "atomize", "action": "off"},   # ATOMIZE_OFF
    4: {"device": "fan", "action": "on"},        # FAN_ON
    5: {"device": "fan", "action": "off"},       # FAN_OFF
    6: {"device": "heating_mat", "action": "on"},  # HEATING_MAT_ON
    7: {"device": "heating_mat", "action": "off"}  # HEATING_MAT_OFF
}

# Sensor data
SENSORS = {
    "light": {"min": 100, "max": 1000, "unit": "lux"},
    "air_humidity": {"min": 30, "max": 70, "unit": "%"},
    "soil_moisture": {"min": 20, "max": 80, "unit": "%"},
    "air_temperature": {"min": 15, "max": 35, "unit": "°C"},
    "signal_strenght": {"min": -90, "max": -30, "unit": "dBm"},
    "battery": {"min": 20, "max": 100, "unit": "%"}
}

# Device states
DEVICE_STATES = {
    "water": False,
    "atomize": False,
    "fan": False,
    "heating_mat": False
}


def on_connect(client, userdata, flags, rc):
    logging.info("Connected with result code: %s", rc)
    if rc == 0:
        client.subscribe(TOPIC_CONTROL)
        logging.info("Subscribed to: %s", TOPIC_CONTROL)

        client.publish(TOPIC_CONN, json.dumps({"userKey": USER_KEY}))
        client.publish(TOPIC_STATUS, json.dumps({"online": True}))
        logging.info("Sent initial connection and status messages")


def on_message(client, userdata, msg):
    logging.info("Received: %s -> %s", msg.topic, msg.payload.decode())

    if msg.topic == TOPIC_CONTROL:
        try:
            data = json.loads(msg.payload.decode())
            action_info = data.get("action", {})
            action_id = action_info.get("id")

            logging.info("Processing action ID: %s", action_id)

            if action_id in ACTION_MAP:
                mapping = ACTION_MAP[action_id]
                device = mapping["device"]
                action = mapping["action"]

                DEVICE_STATES[device] = (action == "on")

                response = {
                    "device": device,
                    "action": action,
                    "status": "success"
                }
                client.publish(TOPIC_CONFIRM, json.dumps(response))
                logging.info("Device %s -> %s (confirmed)", device, action)
            else:
                logging.warning("Unknown action ID: %s", action_id)

        except Exception as e:
            logging.error("Error processing message: %s", e)


def publish_sensors(client):
    logging.info("Starting sensor publishing...")
    while True:
        try:
            if client.is_connected():
                for sensor_name, config in SENSORS.items():
                    value = round(random.uniform(
                        config["min"], config["max"]), 2)

                    if sensor_name == "soil_moisture" and DEVICE_STATES["water"]:
                        value = max(value, 60)

                    payload = {
                        "sensor": sensor_name,
                        "values": [value],
                        "unit": config["unit"]
                    }

                    client.publish(TOPIC_SENSOR, json.dumps(payload))
                    logging.info("Sensor %s: %s %s", sensor_name,
                                 value, config["unit"])
                    time.sleep(0.5)
        except Exception as e:
            logging.error("Sensor error: %s", e)

        time.sleep(10)


def publish_heartbeat(client):
    logging.info("Starting heartbeat...")
    while True:
        try:
            if client.is_connected():
                client.publish(TOPIC_STATUS, json.dumps({"online": True}))
        except Exception as e:
            logging.error("Heartbeat error: %s", e)
        time.sleep(30)


def main():
    logging.info("Starting mock ESP device")
    logging.info("MAC: %s", DEVICE_MAC)
    if not all(os.path.exists(cert) for cert in [CA_CERT, CLIENT_CERT, CLIENT_KEY]):
        logging.error("Missing certificate files")
        return

    client = mqtt.Client(client_id=f"mock-{DEVICE_MAC}")
    client.on_connect = on_connect
    client.on_message = on_message

    client.tls_set(CA_CERT, CLIENT_CERT, CLIENT_KEY,
                   tls_version=ssl.PROTOCOL_TLSv1_2)
    client.tls_insecure_set(False)

    client.will_set(TOPIC_STATUS, json.dumps({"online": False}), retain=True)

    try:
        client.connect(BROKER, PORT, 60)

        threading.Thread(target=publish_sensors,
                         args=(client,), daemon=True).start()
        threading.Thread(target=publish_heartbeat,
                         args=(client,), daemon=True).start()

        client.loop_forever()

    except KeyboardInterrupt:
        logging.info("Shutting down...")
        client.publish(TOPIC_STATUS, json.dumps({"online": False}))
        client.disconnect()
    except Exception as e:
        logging.error("Error: %s", e)


if __name__ == "__main__":
    main()
