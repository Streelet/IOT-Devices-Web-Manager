import sys
import os
import time
import subprocess
import requests

# Dirección IP del ESP en modo AP
ESP_IP = "http://192.168.4.1"

##################################################################
#              OBTENCIÓN DEL SSID DE LA CONEXIÓN ACTUAL          #
##################################################################
def get_current_ssid():
    """
    Obtiene el SSID de la red Wi-Fi a la que está conectado el sistema.
    Utiliza el comando 'netsh wlan show interfaces' de Windows.
    """
    try:
        result = subprocess.run("netsh wlan show interfaces", capture_output=True, text=True, shell=True)
        output = result.stdout
        for line in output.splitlines():
            # Se busca la línea que contenga 'SSID' pero se omiten aquellas con 'BSSID'
            if "SSID" in line and "BSSID" not in line:
                ssid = line.split(":", 1)[1].strip()
                return ssid
    except Exception as e:
        print(f"\n❌ Error al obtener el SSID actual: {str(e)}\n")
    return None

##################################################################
#                   FUNCIÓN PARA ESPERAR CONEXIÓN A ESP          #
##################################################################
def wait_for_esp_connection(timeout=20):
    """
    Espera hasta que la conexión al ESP esté establecida.
    """
    print("\n🌐 Verificando conexión con el ESP...\n")
    for _ in range(timeout):
        try:
            response = requests.get(ESP_IP, timeout=2)
            if response.status_code == 200:
                print("\n✅ Conexión establecida con el ESP.\n")
                return True
        except requests.ConnectionError:
            print("⌛ Esperando conexión con el ESP...")
            time.sleep(1)
    print("\n❌ No se pudo conectar con el ESP. Verifica la red.\n")
    return False

##################################################################
#         FUNCIÓN PARA ENVIAR CREDENCIALES AL ESP8266          #
##################################################################
def send_wifi_to_esp(ssid, password):
    """
    Envía los datos de la red Wi-Fi al ESP a través de un POST a la ruta /setup.
    """
    try:
        print(f"\n📤 Enviando configuración Wi-Fi al ESP: {ssid}, {password}\n")
        response = requests.post(f"{ESP_IP}/setup", data={'ssid': ssid, 'password': password})
        if response.status_code == 200:
            print("\n✅ Configuración enviada con éxito al ESP.\n")
        else:
            print(f"\n❌ Error al enviar configuración al ESP: {response.status_code}\n")
    except Exception as e:
        print(f"\n❌ Error al intentar enviar configuración al ESP: {str(e)}\n")

##################################################################
#          PROCESO PARA VERIFICAR Y ENVIAR CONFIGURACIÓN         #
##################################################################
def process_configuration(original_ssid, original_password):
    """
    Verifica de forma continua que la red actual tenga un SSID que comience con "Streelet_".
    Muestra un mensaje solo la primera vez (ya sea de no estar conectado o de haberse conectado)
    y, una vez que se detecta la red, espera conexión con el ESP y envía la configuración.
    """
    mensaje_mostrado = False
    while True:
        current_ssid = get_current_ssid()
        if current_ssid and current_ssid.startswith("Streelet_"):
            if not mensaje_mostrado:
                print(f"\n✅ Conectado a una red de dispositivo (Streelet_): {current_ssid}\n")
                mensaje_mostrado = True
            # Una vez detectada la red, verificamos la conexión con el ESP
            if wait_for_esp_connection(timeout=20):
                send_wifi_to_esp(original_ssid, original_password)
            else:
                print("\n⚠ No se pudo establecer conexión con el ESP.\n")
            break
        else:
            if not mensaje_mostrado:
                print("\n⚠ El equipo no está conectado a una red 'Streelet_'. Por favor, conéctate manualmente para configurar el dispositivo.\n")
                mensaje_mostrado = True
        time.sleep(2)

##################################################################
#               FUNCIÓN PÚBLICA PARA CONFIGURAR EL ESP           #
##################################################################
def configure_esp(ssid, password):
    """
    Función pública que puede ser llamada desde el app.py.
    Ejecuta el proceso de configuración usando las variables ssid y password.
    """
    # Se lanza en un hilo para que no bloquee el request del endpoint
    import threading
    threading.Thread(target=process_configuration, args=(ssid, password)).start()
    return "Configuración iniciada, espere por favor..."


import subprocess
import time

def scan_wifi_networks(scan_duration=3, prefix="Streelet_", retries=5):
    """
    Escanea las redes Wi-Fi varias veces (retries) y filtra aquellas que comienzan con el prefijo dado.
    Devuelve una lista de nombres de redes únicas.
    """
    print("Iniciando escaneo de redes Wi-Fi...")
    networks = set()  # Usamos un set para evitar duplicados
    
    
    for _ in range(retries):
            time.sleep(scan_duration)
            try:
                result = subprocess.run("netsh wlan show networks", capture_output=True, text=True, shell=True)
                output = result.stdout
                
                # Procesamos la salida del comando para extraer solo los SSID
                for line in output.splitlines():
                    if "SSID" in line:
                        ssid = line.split(":", 1)[1].strip()
                        if ssid.startswith(prefix):  # Filtramos redes que comienzan con el prefijo
                            networks.add(ssid)  # Añadimos al set (sin duplicados)
            except Exception as e:
                print(f"Error al realizar el escaneo de redes Wi-Fi: {e}")
    
    return list(networks)  # Convertimos el set a lista para devolver las redes encontradas

# Prueba de escaneo
networks = scan_wifi_networks()
print("Redes encontradas:", networks)


# Ejemplo de uso
if __name__ == "__main__":
    available_networks = scan_wifi_networks(5)  # Escaneo durante 5 segundos
    print("Redes Wi-Fi disponibles que comienzan con 'Streelet_':", available_networks)
