import paho.mqtt.client as mqtt
import os
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
    Conecta al broker MQTT usando las variables de entorno.
    
    Retorna:
      - client: Instancia del cliente MQTT conectado.
      
    En caso de error, imprime el error y lo propaga.
    """
    client = mqtt.Client()
    try:
        client.connect(MQTT_BROKER, MQTT_PORT)
        print(f"Connected to the broker {MQTT_BROKER} on port {MQTT_PORT}")
    except Exception as e:
        print(f"Error connecting to the broker: {e}")
        raise
    return client

def get_mqtt_client():
    """
    Retorna el cliente MQTT, conectándolo si es necesario.
    
    Si ya está creado y conectado, retorna la instancia existente.
    """
    global mqtt_client
    if mqtt_client is None:
        print("MQTT client is not connected. Connecting...")
        mqtt_client = connect_mqtt()
    else:
        print("MQTT client already connected.")
    return mqtt_client

def publish_message(client, topic, message):
    """
    Publica un mensaje en el tópico especificado.
    
    Parámetros:
      - client: Cliente MQTT.
      - topic: Tópico donde publicar el mensaje.
      - message: Mensaje a publicar.
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
    
    Parámetros:
      - client: Cliente MQTT.
      - device_id (int): Identificador del dispositivo.
      - topic (str, opcional): Tópico específico donde enviar el comando.
        Si no se proporciona, se usa MQTT_TOPIC.
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
    
    Parámetros:
      - client: Cliente MQTT.
      - device_id (int): Identificador del dispositivo.
      - topic (str, opcional): Tópico específico donde enviar el comando.
        Si no se proporciona, se usa MQTT_TOPIC.
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
