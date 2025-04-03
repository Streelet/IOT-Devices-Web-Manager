from flask import Flask, request, jsonify, render_template, redirect, url_for
import database as dbm
import broker_actions as bk
import sqlite3
import esp_configuration as espwifi

app = Flask(__name__)

# Initialize the database
DB_NAME = dbm.init_db()

# Connect to the MQTT broker
client = bk.connect_mqtt()
# Start the MQTT client loop to process network traffic and callbacks
client.loop_start()

def mqtt_on_message(client, userdata, msg):
    try:
        message = msg.payload.decode('utf-8')
        print("Mensaje MQTT recibido en el tópico", msg.topic, ":", message)
        # Se espera mensaje con formato: dc_<device_id>_1_<ip>
        if message.startswith("dc_"):
            parts = message.split("_")
            if len(parts) >= 4:
                dev_id = parts[1]
                # parts[2] puede indicar estado (ej.: "1" = encendido)
                ip = parts[3]
                dbm.update_device_online_status_by_dev_id(dev_id, ip)
    except Exception as e:
        print("Error al procesar mensaje MQTT:", e)

# Configurar el cliente MQTT para escuchar en el tópico base "streelet"
client.on_message = mqtt_on_message
client.subscribe("streelet")

wifi_credentials = {}

# Verifica que las credenciales WiFi estén configuradas antes de procesar la petición
@app.before_request
def ensure_wifi_credentials():
    global wifi_credentials
    if request.endpoint not in ['wifi_setup', 'static'] and not wifi_credentials:
        return redirect(url_for('wifi_setup'))

@app.route('/devices', methods=['GET'])
def get_devices_endpoint():
    """
    Endpoint para obtener todos los dispositivos desde la base de datos.
    """
    devices = []
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM devices")
            rows = cursor.fetchall()
            for row in rows:
                devices.append({
                    'id': row[0],
                    'name': row[1],
                    'topic': row[2],
                    'ip': row[3],
                    'status': row[4]
                })
    except Exception as e:
        print("Error retrieving devices:", e)
    return jsonify(devices)

@app.route('/devices', methods=['POST'])
def add_device_endpoint():
    """
    Agrega un nuevo dispositivo.
    Se espera recibir en el cuerpo de la petición JSON los campos 'name' y 'topic',
    y opcionalmente 'ip' (por defecto se asigna cadena vacía).
    """
    try:
        data = request.get_json()
        if 'name' not in data or 'topic' not in data:
            return jsonify({'error': 'Missing name or topic'}), 400
        name = data['name']
        topic = data['topic']
        ip = data.get('ip', '')
        result = dbm.add_device(name, topic, ip)
        if result == 1:
            return jsonify({'message': 'Device added successfully'}), 201
        elif result == -1:
            return jsonify({'error': f'Device with name \"{name}\" already exists'}), 409
        else:
            return jsonify({'error': 'Failed to add device'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/devices/<int:device_id>', methods=['PUT'])
def update_device_endpoint(device_id):
    try:
        data = request.get_json()
        name = data.get('name')
        status = data.get('status')
        device_status = data.get('device_status')
        result = dbm.update_device(device_id, name, status, device_status)
        if result == 1:
            return jsonify({'message': 'Device updated successfully'}), 200
        elif result == -2:
            return jsonify({'error': 'Device not found'}), 404
        else:
            return jsonify({'error': 'Failed to update device'}), 500
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/devices/<int:device_id>', methods=['DELETE'])
def delete_device_endpoint(device_id):
    try:
        result = dbm.delete_device(device_id)
        if result == 1:
            return jsonify({'message': 'Device deleted successfully'}), 200
        elif result == -2:
            return jsonify({'error': 'Device not found'}), 404
        else:
            return jsonify({'error': 'Failed to delete device'}), 500
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/devices/status', methods=['GET'])
def get_all_devices_status():
    """Obtiene el estado de conexión y potencia de todos los dispositivos."""
    devices = dbm.get_all_devices_status()
    return jsonify(devices)

@app.route('/devices/<int:device_id>/connection', methods=['GET'])
def get_device_connection_status(device_id):
    """Obtiene el estado de conexión (online/offline) de un dispositivo específico."""
    status = dbm.get_device_connection_status(device_id)
    if status:
        return jsonify({"status": status})
    return jsonify({"error": "Device not found"}), 404

@app.route('/devices/<int:device_id>/power', methods=['GET'])
def get_device_power_status(device_id):
    """Obtiene el estado de encendido/apagado de un dispositivo específico."""
    device = dbm.get_device_status(device_id)
    if device:
        return jsonify({"device_status": device['device_status']})
    return jsonify({"error": "Device not found"}), 404

@app.route('/devices/<int:device_id>/set_connection/<status>', methods=['POST'])
def update_device_connection_status(device_id, status):
    if status not in ['online', 'offline']:
        return jsonify({"error": "Invalid status"}), 400
    success = dbm.update_device_connection_status(device_id, status)
    if success:
        return jsonify({"message": f"Device {device_id} set to {status}"})
    return jsonify({"error": "Device not found"}), 404

@app.route('/configure', methods=['POST'])
def configure_device():
    data = request.get_json()
    ssid = data.get('ssid')
    password = data.get('password')
    if not ssid or not password:
        return jsonify({'message': 'Datos incompletos'}), 400
    message = espwifi.configure_esp(ssid, password)
    return jsonify({'message': message})

@app.route('/devices/<int:device_id>/set_power/<int:state>', methods=['POST'])
def update_device_power_status_endpoint(device_id, state):
    print(f"Device ID: {device_id}, State: {state}")
    current_status = dbm.get_device_power_status(device_id)
    if current_status is None:
        return jsonify({'message': 'Device not found'}), 404
    if current_status == state:
        return jsonify({'message': f'Device is already {"on" if state == 1 else "off"}'}), 200
    success = dbm.update_device_power_status(device_id, state)
    if success:
        return jsonify({'message': 'Device power state updated successfully'}), 200
    else:
        return jsonify({'message': 'Failed to update device power state'}), 500

@app.route('/wifi', methods=['GET', 'POST'])
def wifi_setup():
    global wifi_credentials
    if request.method == 'POST':
        ssid = request.form.get('ssid')
        password = request.form.get('password')
        if not ssid or not password:
            return "Error: Debes ingresar tanto el SSID como la contraseña", 400
        wifi_credentials = {"ssid": ssid, "password": password}
        return redirect(url_for('home'))
    else:
        return render_template('wifi_setup.html')
    

@app.route('/scan_wifi', methods=['GET'])
def scan_wifi():
   wifi_scanned_networks = espwifi.scan_wifi_networks()  # Escanea y obtiene las redes
   return render_template("add_device_page.html", wifi_networks=wifi_scanned_networks)

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/add_device')
def add_device():
    return render_template('add_device_page.html')


if __name__ == '__main__':
    app.run(debug=True)
