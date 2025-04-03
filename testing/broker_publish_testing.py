import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os
import time

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Leer las variables de entorno
broker = os.getenv("MQTT_BROKER_HOST")
port = int(os.getenv("MQTT_PORT"))
topic = os.getenv("MQTT_TOPIC")+"/sala"

# Mensaje a publicar
message = "on_5"  # Usamos la palabra "reset" como mensaje

# Función de callback cuando el cliente se conecta
def on_connect(client, userdata, flags, rc):
    print(f"Conectado al broker con código de resultado: {rc}")
    if rc == 0:  # Si la conexión es exitosa
        # Publicar el mensaje una vez que se ha conectado
        client.publish(topic, message)
        print(f"Mensaje publicado: {message}")
        client.disconnect()  # Desconectarse después de publicar el mensaje
    else:
        print("Error al conectar con el broker MQTT. Código de resultado:", rc)

# Crear una instancia del cliente MQTT
client = mqtt.Client()

# Asignar el callback de conexión
client.on_connect = on_connect

# Conectar al broker
print(f"Conectando al broker {broker} en el puerto {port}...")
client.connect(broker, port, 60)

# Iniciar el ciclo de procesamiento del cliente MQTT
while True:
    try:
        client.loop()  # Usamos loop() en lugar de loop_forever()
        time.sleep(1)  # Damos un pequeño retraso para evitar que el script se ejecute demasiado rápido
    except KeyboardInterrupt:
        print("Interrupción por parte del usuario, cerrando cliente MQTT.")
        client.disconnect()
        break
