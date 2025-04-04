import sys
import os
import time
import subprocess
import requests
import threading

# Dirección IP del ESP en modo AP
ESP_IP = "http://192.168.4.1"

def get_current_ssid():
    try:
        result = subprocess.run("netsh wlan show interfaces", capture_output=True, text=True, shell=True)
        output = result.stdout
        for line in output.splitlines():
            if "SSID" in line and "BSSID" not in line:
                ssid = line.split(":", 1)[1].strip()
                return ssid
    except Exception as e:
        print(f"\nError al obtener el SSID actual: {str(e)}\n")
    return None

def wait_for_esp_connection(timeout=20):
    print("\nVerificando conexión con el ESP...\n")
    for _ in range(timeout):
        try:
            response = requests.get(ESP_IP, timeout=2)
            if response.status_code == 200:
                print("\nConexión establecida con el ESP.\n")
                return True
        except requests.ConnectionError:
            print("Esperando conexión con el ESP...")
            time.sleep(1)
    print("\nNo se pudo conectar con el ESP. Verifica la red.\n")
    return False

def send_wifi_to_esp(ssid, password, grupo, name):
    """
    Envía los datos de la red Wi-Fi al ESP a través de un POST a la ruta /setup.
    Se envían los parámetros: ssid, password, grupo y name.
    """
    try:
        print(f"\nEnviando configuración Wi-Fi al ESP: {ssid}, {password}, {grupo}, {name}\n")
        response = requests.post(f"{ESP_IP}/setup", data={'ssid': ssid, 'password': password, 'grupo': grupo, 'nombre': name}) # Include 'nombre'
        if response.status_code == 200:
            print("\nConfiguración enviada con éxito al ESP.\n")
        else:
            print(f"\nError al enviar configuración al ESP: {response.status_code}\n")
    except Exception as e:
        print(f"\nError al intentar enviar configuración al ESP: {str(e)}\n")

def process_configuration(original_ssid, original_password, grupo, name):
    """
    Envía la configuración al ESP sin esperar por la red o la conexión.
    """
    send_wifi_to_esp(original_ssid, original_password, grupo, name) # Pass the name

def configure_esp(ssid, password, grupo, name):
    """
    Función pública para iniciar la configuración del ESP.
    Se lanza en un hilo para no bloquear la respuesta del endpoint.
    """
    threading.Thread(target=process_configuration, args=(ssid, password, grupo, name)).start() # Pass the name
    return "Configuración iniciada, espere por favor..."