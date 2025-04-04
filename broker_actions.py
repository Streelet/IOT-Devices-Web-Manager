import paho.mqtt.client as mqtt
import os
import time
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Recuperar las variables de entorno
MQTT_BROKER = os.getenv('MQTT_BROKER_HOST')
MQTT_PORT = int(os.getenv('MQTT_PORT'))
MQTT_TOPIC = os.getenv('MQTT_TOPIC')  # Tópico base, por ejemplo "streelet"

mqtt_client = None

def connect_mqtt():
    """
    Conecta al broker MQTT y maneja la reconexión automática en caso de fallo.
    
    Retorna:
      - client: Instancia del cliente MQTT conectado.
    """
    client = mqtt.Client()
    
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to the broker {MQTT_BROKER} on port {MQTT_PORT}")
            client.subscribe("streelet")
        else:
            print(f"Connection failed with error code {rc}")
    
    def on_disconnect(client, userdata, rc):
        print("[MQTT] Disconnected. Attempting to reconnect...")
        while True:
            try:
                client.reconnect()
                print("[MQTT] Reconnected successfully.")
                break
            except Exception as e:
                print(f"[MQTT] Reconnection error: {e}")
                time.sleep(5)  # Espera antes de reintentar
    
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT)
    except Exception as e:
        print(f"Error connecting to the broker: {e}")
        
        raise
    
    return client

def get_mqtt_client():
    """
    Retorna el cliente MQTT, conectándolo si es necesario o si la conexión se perdió.
    """
    global mqtt_client
    if mqtt_client is None or not mqtt_client.is_connected():
        print("MQTT client is not connected. Connecting...")
        mqtt_client = connect_mqtt()
    else:
        print("MQTT client already connected.")
    return mqtt_client

def publish_message(client, topic, message):
    """
    Publica un mensaje en el tópico especificado.
    """
    try:
        client.publish(topic, message)
        print(f"Published message '{message}' to topic '{topic}'")
    except Exception as e:
        print(f"Error publishing message to topic {topic}: {e}")
        raise

def turn_on_device(client, device_id, topic=None):
    """
    Enciende un dispositivo enviando un comando MQTT en formato "on_<id>".
    """
    if topic is None:
        topic = MQTT_TOPIC
    message = f"on_{device_id}"
    try:
        publish_message(client, topic, message)
        print(f"Device {device_id} turned on (published '{message}' to '{topic}').")
    except Exception as e:
        print(f"Error turning on device {device_id}: {e}")
        raise

def turn_off_device(client, device_id, topic=None):
    """
    Apaga un dispositivo enviando un comando MQTT en formato "off_<id>".
    """
    if topic is None:
        topic = MQTT_TOPIC
    message = f"off_{device_id}"
    try:
        publish_message(client, topic, message)
        print(f"Device {device_id} turned off (published '{message}' to '{topic}').")
    except Exception as e:
        print(f"Error turning off device {device_id}: {e}")
        raise