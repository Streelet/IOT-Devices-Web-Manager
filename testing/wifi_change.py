import time
import subprocess
import requests  # Necesitarás instalar esta librería si no la tienes

# Datos de la red inicial
initial_ssid = "Tenda_704E60"
initial_password = "RV74J3C4"
esp_ip = "http://192.168.4.1"  # Dirección IP del ESP en modo AP

# Función para conectarse a una red Wi-Fi usando netsh
def connect_wifi(ssid, password):
    try:
        print(f"Conectando a {ssid}...")
        subprocess.run(f'netsh wlan set hostednetwork mode=allow ssid={ssid} key={password}', shell=True)
        subprocess.run(f'netsh wlan connect name={ssid}', shell=True)
        print(f"Conectado a {ssid}")
    except Exception as e:
        print(f"Error al conectarse a {ssid}: {str(e)}")

# Función para escanear redes Wi-Fi disponibles usando netsh
def scan_wifi():
    networks = []
    try:
        result = subprocess.run(["netsh", "wlan", "show", "network", "mode=bssid"], capture_output=True, text=True, shell=True)
        output = result.stdout
        for line in output.splitlines():
            if "SSID" in line and "Streelet" in line:  # Filtra redes que empiezan con "Streelet"
                networks.append(line.split(":")[1].strip())
    except Exception as e:
        print(f"Error al escanear redes Wi-Fi: {str(e)}")
    return networks

# Función para enviar datos de red Wi-Fi al ESP en la ruta correcta (/setup)
def send_wifi_to_esp(ssid, password):
    try:
        print(f"Enviando configuración Wi-Fi al ESP: {ssid}, {password}")
        response = requests.post(f"{esp_ip}/setup", json={'ssid': ssid, 'password': password})
        if response.status_code == 200:
            print("Configuración enviada con éxito al ESP.")
        else:
            print(f"Error al enviar configuración al ESP: {response.status_code}")
    except Exception as e:
        print(f"Error al intentar enviar configuración al ESP: {str(e)}")

# Conexión inicial a la red principal
connect_wifi(initial_ssid, initial_password)

while True:
    print("Escaneando redes Wi-Fi...")
    bombillo_networks = scan_wifi()  # Busca redes cuyo SSID comience con 'Streelet'

    if bombillo_networks:
        print("Redes 'Streelet' encontradas: ", bombillo_networks)
        connect_wifi(bombillo_networks[0], "")  # Se conecta a la primera red "Streelet" (abierta)
        time.sleep(5)  # Espera 5 segundos para asegurar la conexión

        # Envía los datos de la red Wi-Fi inicial al ESP
        send_wifi_to_esp(initial_ssid, initial_password)

        # Regresa a la red original
        print("Desconectando de la red 'Streelet' y regresando a la red habitual...")
        connect_wifi(initial_ssid, initial_password)  # Regresa a la red original
    else:
        print("No se encontraron redes 'Streelet'")

    time.sleep(80)  # Repite el escaneo cada 20 segundos