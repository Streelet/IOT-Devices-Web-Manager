import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os
import time

load_dotenv()

broker = os.getenv("MQTT_BROKER_HOST")
port = int(os.getenv("MQTT_PORT"))
base_topic = os.getenv("MQTT_TOPIC")  # Store the base topic

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"Conectado al broker con código de resultado: {rc}")

client.on_connect = on_connect

print(f"Conectando al broker {broker} en el puerto {port}...")
client.connect(broker, port, 60)
client.loop_start()  # Start the loop in the background

def publish_message(device_topic, message):
    """Publishes a message to a specific device topic."""
    full_topic = f"{base_topic}/{device_topic}"
    result = client.publish(full_topic, message)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Mensaje publicado en '{full_topic}': {message}")
        return True
    else:
        print(f"Error al publicar mensaje en '{full_topic}': {message} (código {status})")
        return False

if __name__ == '__main__':
    # Example usage (you can remove this later)
    publish_message("sama", "on_959f5e")
    time.sleep(5)
    publish_message("sama", "off_959f5e")
    time.sleep(5)
    client.loop_stop()
    client.disconnect()