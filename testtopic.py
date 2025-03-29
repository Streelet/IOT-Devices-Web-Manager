import os
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Leer las variables de entorno
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC")

#Conexion con el Broker
def on_connect(client, userdata, flags, rc):
    print(f"Conectado con el código {rc}")

    # Suscribirse al tópico al que se quiere escuchar
    client.subscribe(MQTT_TOPIC)
    print(f"Suscrito al tópico: {MQTT_TOPIC}")

# Función para recepción de mensajes
def on_message(client, userdata, msg):
    print(f"Mensaje recibido: {msg.payload.decode()} en el tópico: {msg.topic}")

# Creación del cliente MQTT
client = mqtt.Client(client_id="client1", clean_session=True)

# Asignar las funciones de conexión y mensaje
client.on_connect = on_connect
client.on_message = on_message

# Conectarse al broker
client.connect(MQTT_BROKER_HOST, MQTT_PORT, 60)

# Iniciar el ciclo de escucha para procesar los mensajes
client.loop_start()

# Publicar un mensaje después de unos segundos para asegurarnos de que la suscripción esté lista
import time
time.sleep(2)  # Esperar un momento para estar seguro de que estamos suscritos

# Publicar un mensaje en el tópico
client.publish(MQTT_TOPIC, "¡Hola desde Python!")

# Dejar el cliente MQTT escuchando por un tiempo para recibir mensajes
time.sleep(10)

# Detener el ciclo de escucha
client.loop_stop()
