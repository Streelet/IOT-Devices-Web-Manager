import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener las variables de entorno
mqtt_broker_host = os.getenv("MQTT_BROKER_HOST")
mqtt_port = int(os.getenv("MQTT_PORT"))
mqtt_topic = os.getenv("MQTT_TOPIC")

def on_connect(client, userdata, flags, rc):
    print(f"Conectado con código {rc}")
    client.subscribe(mqtt_topic)

def on_message(client, userdata, msg):
    print(f"Mensaje recibido en el tópico {msg.topic}: {msg.payload.decode()}")

client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

# Conectar al broker MQTT usando las variables de entorno
client.connect(mqtt_broker_host, mqtt_port, 60)

# Iniciar el bucle para escuchar los mensajes de forma continua
client.loop_forever()
