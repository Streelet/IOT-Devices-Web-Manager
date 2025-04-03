import sqlite3
import os
import broker_actions as bk

DB_NAME = 'devices.db'

def init_db():
    """
    Inicializa la base de datos SQLite.
    Si no existe, crea la tabla 'devices' con los campos:
      - id: identificador único (auto-incremental)
      - name: nombre del dispositivo (único)
      - topic: tópico MQTT asociado
      - ip: dirección IP del dispositivo (opcional)
      - status: estado de conexión ('online' o 'offline', por defecto 'offline')
      - device_status: estado de encendido/apagado (0: off, 1: on)
    """
    if not os.path.exists(DB_NAME):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    topic TEXT NOT NULL,
                    ip TEXT,
                    status TEXT NOT NULL DEFAULT 'offline',
                    device_status INTEGER NOT NULL DEFAULT 0
                )
            ''')
            conn.commit()
        return DB_NAME
    else:
        print(f"Database '{DB_NAME}' already exists.")
        return DB_NAME

def add_device(name, topic, ip=''):
    """
    Agrega un nuevo dispositivo a la base de datos.
    Parámetros:
      - name: nombre del dispositivo (único)
      - topic: tópico MQTT
      - ip: dirección IP (opcional, por defecto cadena vacía)
    Retorna:
      1 si se agrega exitosamente, -1 en caso de error (por duplicación o de otro tipo).
    """
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO devices (name, topic, ip, status, device_status) VALUES (?, ?, ?, ?, ?)",
                           (name, topic, ip, 'offline', 0))
            conn.commit()
            return 1
    except sqlite3.IntegrityError:
        print(f"Error: A device with the name '{name}' already exists.")
        return -1
    except Exception as e:
        print(f"Error adding device: {e}")
        return -1

def update_device_power_status_db(device_id, status):
    """
    Actualiza el estado de encendido (device_status) de un dispositivo en la base de datos.
    """
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE devices SET device_status = ? WHERE id = ?", (status, device_id))
            conn.commit()
            return 1
    except Exception as e:
        print(f"Error updating device status: {e}")
        return -2

def update_device(device_id, name=None, status=None, device_status=None):
    """
    Actualiza detalles del dispositivo (nombre, estado de conexión y/o estado de encendido).
    Retorna:
      1 si se actualiza correctamente,
      -2 si no se encuentra el dispositivo,
      -3 en caso de error.
    """
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
            device = cursor.fetchone()
            if not device:
                return -2
            if name:
                cursor.execute("UPDATE devices SET name = ? WHERE id = ?", (name, device_id))
            if status:
                cursor.execute("UPDATE devices SET status = ? WHERE id = ?", (status, device_id))
            if device_status is not None:
                cursor.execute("UPDATE devices SET device_status = ? WHERE id = ?", (device_status, device_id))
            conn.commit()
            return 1
    except Exception as e:
        print(f"Error updating device: {e}")
        return -3

def delete_device(device_id):
    """
    Elimina un dispositivo de la base de datos.
    Retorna:
      1 si se elimina correctamente,
      -2 si no se encuentra,
      -3 si ocurre algún error.
    """
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
            device = cursor.fetchone()
            if not device:
                return -2
            cursor.execute("DELETE FROM devices WHERE id = ?", (device_id,))
            conn.commit()
            return 1
    except Exception as e:
        print(f"Error deleting device: {e}")
        return -3

def update_device_power_status(device_id, state):
    """
    Actualiza el estado de encendido/apagado del dispositivo.
    Llama a la acción MQTT correspondiente y actualiza la base de datos.
    Retorna:
      1 si la actualización fue exitosa, -2 en caso de error.
    """
    client = bk.get_mqtt_client()
    if state not in [0, 1]:
        raise ValueError("Invalid state: should be 1 (on) or 0 (off)")
    if state == 1:
        bk.turn_on_device(client, device_id)
    else:
        bk.turn_off_device(client, device_id)
    success = update_device_power_status_db(device_id, state)
    print(f"DB Update Success: {success}")
    return success

def get_all_devices_status():
    """
    Recupera el estado de conexión y el estado de encendido de todos los dispositivos.
    Retorna una lista de diccionarios.
    """
    devices = []
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, status, device_status FROM devices")
            rows = cursor.fetchall()
            for row in rows:
                devices.append({
                    "id": row[0],
                    "name": row[1],
                    "status": row[2],
                    "device_status": row[3]
                })
    except Exception as e:
        print(f"Error fetching devices: {e}")
    return devices

def get_device_power_status(device_id):
    """
    Recupera el estado de encendido (device_status) de un dispositivo específico.
    Retorna 0, 1 o None si no se encuentra.
    """
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT device_status FROM devices WHERE id = ?", (device_id,))
            device = cursor.fetchone()
            return device[0] if device else None
    except Exception as e:
        print(f"Error fetching device status: {e}")
        return None

def get_device_status(device_id):
    """
    Recupera la información completa de un dispositivo (como diccionario).
    """
    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
            device = cursor.fetchone()
            return dict(device) if device else None
    except Exception as e:
        print(f"Error fetching device info: {e}")
        return None

def get_device_connection_status(device_id):
    """
    Recupera el estado de conexión ('online' o 'offline') de un dispositivo.
    """
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM devices WHERE id = ?", (device_id,))
            device = cursor.fetchone()
            return device[0] if device else None
    except Exception as e:
        print(f"Error fetching device connection status: {e}")
        return None

def update_device_connection_status(device_id, status):
    """
    Actualiza el estado de conexión de un dispositivo ('online' o 'offline').
    Retorna:
      1 si se actualiza correctamente,
      -2 si no se encuentra,
      -3 si ocurre algún error.
    """
    try:
        if status not in ["online", "offline"]:
            raise ValueError("Invalid status. Must be 'online' or 'offline'.")
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE devices SET status = ? WHERE id = ?", (status, device_id))
            if cursor.rowcount == 0:
                return -2
            conn.commit()
            return 1
    except Exception as e:
        print(f"Error updating device connection status: {e}")
        return -3

def update_device_online_status_by_dev_id(dev_id, ip):
    """
    Actualiza en la base de datos el estado del dispositivo a 'online' y su IP,
    usando como identificador el campo 'name' (se asume que coincide con el device_id configurado en el ESP).
    """
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE devices SET ip = ?, status = 'online' WHERE name = ?", (ip, dev_id))
            conn.commit()
            print(f"Actualizado dispositivo {dev_id} como online con IP {ip}")
    except Exception as ex:
        print("Error al actualizar estado en DB:", ex)

if __name__ == '__main__':
    init_db()
