import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve the environment variables
MQTT_BROKER = os.getenv('MQTT_BROKER')
MQTT_PORT = int(os.getenv('MQTT_PORT'))

# Function to establish connection to the MQTT broker
def connect_mqtt():
    """
    Connects to the MQTT broker using the environment variables.
    
    Returns:
    - client: The connected MQTT client instance.
    
    Raises:
    - Exception: If there's an error connecting to the broker.
    
    This function uses the MQTT broker address and port stored in environment variables
    to create a client and establish a connection to the broker. If the connection is
    successful, it prints a message indicating the connection details. If there is an error,
    it raises an exception with the error message.
    """
    # Create the MQTT client
    client = mqtt.Client()

    try:
        # Connect to the MQTT broker using the environment variables
        client.connect(MQTT_BROKER, MQTT_PORT)
        print(f"Connected to the broker {MQTT_BROKER} on port {MQTT_PORT}")
    except Exception as e:
        print(f"Error connecting to the broker: {e}")
        raise

    return client
