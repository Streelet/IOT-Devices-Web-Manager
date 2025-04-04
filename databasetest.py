from database import get_all_devices_status

# filepath: c:/Users/erick/Documents/GitHub/IOT-Devices-Web-Manager/databasetest.py

def show_all_devices():
    devices = get_all_devices_status()
    if devices:
        print("Dispositivos registrados:")
        for device in devices:
            print(f"ID: {device['id']}, Nombre: {device['device_id']}, Tópico: {device['topic']}, Estado: {device['status']}, Estado del dispositivo: {device['device_status']}")
    else:
        print("No hay dispositivos registrados.")

if __name__ == '__main__':
    show_all_devices()