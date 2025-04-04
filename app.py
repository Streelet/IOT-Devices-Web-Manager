
from flask import Flask, request, jsonify, render_template, redirect, url_for
import database as dbm
import broker_actions as bk
import sqlite3
import esp_configuration as espwifi 
import time


app = Flask(__name__)

# Inicializa la base de datos
DB_NAME = dbm.init_db()

#Variable global para permitir agregar dispositivos manualmente
ADD_DEVICE_SESSION_COUNT = 0
# Conecta al broker MQTT y arranca el loop
client = bk.connect_mqtt()
client.loop_start()


# Variable global para las credenciales WiFi del servidor
wifi_credentials = {}

def mqtt_on_message(client, userdata, msg):
        """
        Callback que se ejecuta al recibir un mensaje MQTT.
        Se esperan mensajes con este formato:
          "dc_{device_id}_1_{ip}_{group}_{name}"

        Se extraen device_id, IP, grupo y nombre, y se registra o actualiza el dispositivo en la BD.
        El tópico que se almacena se construye como "streelet/{group}".
        """
        try:
            # Decodificar y limpiar el mensaje recibido
            message = msg.payload.decode('utf-8').strip()
            print(f"Mensaje recibido en {msg.topic}: {message}") # Mantener print para ver en consola

            device_id, ip, group, name = None, None, None, None

            if message.startswith("dc_"):
                parts = message.split("_")
                # Se esperan 6 partes: "dc", device_id, "1", ip, group, name
                if len(parts) == 6:
                    device_id = parts[1].strip()
                    ip = parts[3].strip()
                    group = parts[4].strip()
                    name = parts[5].strip()

                else:

                    print(f"Formato incorrecto en mensaje 'dc_'. Se esperaban 6 partes: dc, device_id, 1, ip, group, name. Se recibieron {len(parts)} partes: {parts}")
                    return

            else:

                print(f"Formato de mensaje no reconocido: {message}")
                return

            if device_id and ip and group and name:

                print(f"Extraído -> device_id: {device_id}, IP: {ip}, Grupo: {group}, Nombre: {name}")
            else:

                print("Error: No se pudieron extraer todos los campos necesarios (ID, IP, Grupo, Nombre).")
                return


            final_topic = f"streelet/{group}"

            # Registrar o actualizar el dispositivo en la BD
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, topic, name FROM devices WHERE id = ?", (device_id,))
                device = cursor.fetchone()
                now = int(time.time())

                if device:
                    cursor.execute("UPDATE devices SET ip = ?, status = ?, last_seen = ?, name = ? WHERE id = ?",
                                   (ip, 'online', now, name, device_id))
                    conn.commit()
                    print(f"Dispositivo {device_id} actualizado: IP={ip}, online, last_seen={now}, Nombre={name}")
                    existing_topic = device[1]
                    if existing_topic != final_topic:
                        cursor.execute("UPDATE devices SET topic = ? WHERE id = ?", (final_topic, device_id))
                        conn.commit()
                        print(f"Tópico actualizado de {existing_topic} a {final_topic}")
                    existing_name = device[2]
                    if existing_name != name:
                        cursor.execute("UPDATE devices SET name = ? WHERE id = ?", (name, device_id))
                        conn.commit()
                        print(f"Nombre actualizado de {existing_name} a {name}")
                else:
                    global ADD_DEVICE_SESSION_COUNT
                    if ADD_DEVICE_SESSION_COUNT > 0:
                        # Registrar un nuevo dispositivo
                        cursor.execute(
                            """INSERT INTO devices (id, name, topic, ip, status, device_status, last_seen)
                               VALUES (?, ?, ?, ?, ?, ?, ?)""",
                            (device_id, name, final_topic, ip, 'online', 0, now)
                        )
                        conn.commit()

                        print(f"Nuevo dispositivo registrado: ID={device_id}, Name={name}, Topic={final_topic}, IP={ip}")
                        print(ADD_DEVICE_SESSION_COUNT)
                    else:
                       print("Nuevo dispositivo no agregado (ADD_DEVICE_SESSION_COUNT <= 0).")
                       print(ADD_DEVICE_SESSION_COUNT)

        except Exception as e:

            print(f"Error en mqtt_on_message: {e}")

        
# Asignar el callback MQTT y suscribirse a "streelet/"
client.on_message = mqtt_on_message



# --------------------------------------------------------------
# Antes de cada request, se asegura que las credenciales WiFi estén definidas
@app.before_request
def ensure_wifi_credentials():
    global wifi_credentials
    if request.endpoint not in ['wifi_setup', 'static'] and not wifi_credentials:
        return redirect(url_for('wifi_setup'))

# --------------------------------------------------------------
# Endpoints para obtener o agregar dispositivos manualmente

@app.route('/devices', methods=['GET'])
def get_devices_endpoint():
    devices = []
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, topic, ip, status, device_status, last_seen FROM devices")
            rows = cursor.fetchall()
            for row in rows:
                devices.append({
                    'id': row[0],
                    'device_id': row[0],
                    'name': row[1],
                    'topic': row[2],
                    'ip': row[3],
                    'status': row[4],
                    'device_status': row[5],
                    'last_seen': row[6]
                })
    except Exception as e:
        print(f"Error: {e}")  
    return jsonify(devices)

@app.route('/devices', methods=['POST'])
def add_device_endpoint():
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        name = data.get('name', f"Manual_{device_id}")
        topic = data.get('topic')
        ip = data.get('ip', '')
        if not device_id or not topic:
            return jsonify({'error': 'Faltan device_id o topic'}), 400
        result = dbm.add_device(device_id, name, topic, ip)
        if result == 1:
            return jsonify({'message': 'Dispositivo agregado correctamente'}), 201
        elif result == -1:
            return jsonify({'error': f'El dispositivo con device_id "{device_id}" ya existe'}), 409
        else:
            return jsonify({'error': 'Error al agregar dispositivo'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
    # ... (tus imports y configuraciones) ...

@app.route('/devices/<string:device_id>/delete', methods=['POST'])
def delete_device_endpoint(device_id):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()

            # Obtener el tópico del dispositivo antes de eliminarlo
            cursor.execute("SELECT topic FROM devices WHERE id = ?", (device_id,))
            result = cursor.fetchone()
            if result:
                topic_to_reset = result[0]
                print(f"Dispositivo encontrado: {device_id}, tópico: {topic_to_reset}")
                reset_message = "reset"  # Puedes definir otro mensaje si lo deseas
                bk.publish_message(client, topic_to_reset, reset_message)
                print(f"Mensaje de reset enviado al tópico: {topic_to_reset} para el dispositivo con ID: {device_id}")

                # Eliminar el dispositivo de la base de datos
                cursor.execute("DELETE FROM devices WHERE id = ?", (device_id,))
                conn.commit()
                global ADD_DEVICE_SESSION_COUNT
                ADD_DEVICE_SESSION_COUNT = 0
                return jsonify({'message': f'Dispositivo con ID "{device_id}" eliminado correctamente'}), 200
            else:
                return jsonify({'error': f'No se encontró el dispositivo con ID "{device_id}"'}), 404
    except Exception as e:
        print(f"Error al eliminar el dispositivo {device_id}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/configure', methods=['POST'])
def configure_device():
    data = request.get_json()
    ssid = wifi_credentials.get('ssid')
    password = wifi_credentials.get('password')
    grupo = data.get('grupo')
    name = data.get('name')  # Get the name from the request
    if not ssid or not password or not grupo or not name:
        return jsonify({'message': 'Datos incompletos para configurar el ESP'}), 400
    try:
        message = espwifi.configure_esp(ssid, password, grupo, name)  # Pass the name
        return jsonify({'message': message})
    except Exception as e:
        return jsonify({'message': f'Error al configurar ESP: {e}'}), 500
    
    
# --------------------------------------------------------------
# Configuración WiFi del servidor/aplicación

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

# --------------------------------------------------------------
# Rutas de la interfaz web
@app.route('/')
def home():
    return render_template('dashboard.html', wifi_ssid=wifi_credentials.get('ssid'), wifi_password=wifi_credentials.get('password'))

@app.route('/add_device')
def add_device_page():
    global ADD_DEVICE_SESSION_COUNT
    ADD_DEVICE_SESSION_COUNT += 1
    print(ADD_DEVICE_SESSION_COUNT)
    return render_template('add_device_page.html')



# --------------------------------------------------------------
# Endpoint para controlar el encendido/apagado de dispositivos
@app.route('/devices/<string:device_id>/power/<string:action>', methods=['POST'])
def control_device_power(device_id, action):
    try:
        device = dbm.get_device_status_by_id(device_id)
        if not device:
            return jsonify({'error': f'Device with id "{device_id}" not found.'}), 404

        topic = device[2]

        message = f"{action}_{device_id}"

        bk.publish_message(client, topic, message)

        return jsonify({'message': f'Device "{device_id}" command "{action}" sent successfully.'}), 200
    
    except Exception as e:
        return jsonify({'error': f'Failed to send command to device "{device_id}". Error: {str(e)}'}), 500



# --------------------------------------------------------------
# Inicio de la aplicación
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
