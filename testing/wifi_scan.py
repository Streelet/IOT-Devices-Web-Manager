import subprocess
import platform

def scan_wifi():
    
    if platform.system() == "Windows":
        # Ejecutar comando para listar redes Wi-Fi en Windows
        result = subprocess.run(["netsh", "wlan", "show", "network", "mode=bssid"], capture_output=True, text=True)
        print(result.stdout)
    elif platform.system() == "Linux":
        # Ejecutar comando para listar redes Wi-Fi en Linux
        result = subprocess.run(["nmcli", "-t", "-f", "SSID,SIGNAL", "dev", "wifi"], capture_output=True, text=True)
        print(result.stdout)
    else:
        print("Sistema operativo no compatible")

scan_wifi()
