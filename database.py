import sqlite3
import os
import time
import broker_actions as bk

DB_NAME = 'devices.db'

def init_db():
    if not os.path.exists(DB_NAME):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE devices (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    topic TEXT NOT NULL,
                    ip TEXT,
                    status TEXT NOT NULL DEFAULT 'offline',
                    device_status INTEGER NOT NULL DEFAULT 0,
                    last_seen INTEGER
                )
            ''')
            conn.commit()
        return DB_NAME
    else:
        print(f"Database '{DB_NAME}' already exists.")
        return DB_NAME

def add_device(device_id, topic, ip=''):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            # Se inserta el device_id directamente en la columna id
            cursor.execute("INSERT INTO devices (id, name, topic, ip, status, device_status) VALUES (?, ?, ?, ?, ?, ?)",
                            (device_id, device_id, topic, ip, 'offline', 0))
            conn.commit()
            return 1
    except sqlite3.IntegrityError:
        print(f"Error: El dispositivo con device_id '{device_id}' ya existe.")
        return -1
    except Exception as e:
        print(f"Error adding device: {e}")
        return -1

def update_device_online_status_by_id(id, ip):
    now = int(time.time())
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ip, status FROM devices WHERE id = ?", (id,))
            result = cursor.fetchone()
            if result:
                current_ip, current_status = result
                if current_status == 'online' and current_ip == ip:
                    cursor.execute("UPDATE devices SET last_seen = ? WHERE id = ?", (now, id))
                    conn.commit()
                    print(f"[HEARTBEAT] Actualizado solo last_seen para {id}")
                    return
            cursor.execute("UPDATE devices SET ip = ?, status = 'online', last_seen = ? WHERE id = ?", (ip, now, id))
            conn.commit()
            print(f"[HEARTBEAT] Actualizado {id} como online con IP {ip}")
    except Exception as ex:
        print("Error al actualizar estado en DB:", ex)

def check_heartbeats(timeout=20):
    now = int(time.time())
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, last_seen FROM devices WHERE status = 'online'")
            devices = cursor.fetchall()
            for device in devices:
                device_id, last_seen = device
                if last_seen is None or (now - last_seen) > timeout:
                    cursor.execute("UPDATE devices SET status = 'offline' WHERE id = ?", (device_id,))
                    print(f"[HEARTBEAT] Dispositivo {device_id} marcado como offline (timeout)")
            conn.commit()
    except Exception as ex:
        print("Error en check_heartbeats:", ex)

# Resto de funciones (update_device, delete_device, etc.) se mantienen...
def update_device(device_db_id, name=None, status=None, device_status=None):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM devices WHERE id = ?", (device_db_id,))
            device = cursor.fetchone()
            if not device:
                return -2
            if name:
                cursor.execute("UPDATE devices SET name = ? WHERE id = ?", (name, device_db_id))
            if status:
                cursor.execute("UPDATE devices SET status = ? WHERE id = ?", (status, device_db_id))
            if device_status is not None:
                cursor.execute("UPDATE devices SET device_status = ? WHERE id = ?", (device_status, device_db_id))
            conn.commit()
            return 1
    except Exception as e:
        print(f"Error updating device: {e}")
        return -3

def delete_device(device_db_id):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM devices WHERE id = ?", (device_db_id,))
            device = cursor.fetchone()
            if not device:
                return -2
            cursor.execute("DELETE FROM devices WHERE id = ?", (device_db_id,))
            conn.commit()
            return 1
    except Exception as e:
        print(f"Error deleting device: {e}")
        return -3

def update_device_connection_status(device_db_id, status):
    try:
        if status not in ["online", "offline"]:
            raise ValueError("Estado inválido. Debe ser 'online' o 'offline'.")
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE devices SET status = ? WHERE id = ?", (status, device_db_id))
            if cursor.rowcount == 0:
                return -2
            conn.commit()
            return 1
    except Exception as e:
        print(f"Error updating device connection status: {e}")
        return -3

def get_all_devices_status():
    devices = []
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, topic, status, device_status FROM devices")
            rows = cursor.fetchall()
            for row in rows:
                devices.append({
                    "id": row[0],
                    "device_id": row[1],  # Usamos 'name' como 'device_id' basado en tu tabla
                    "topic": row[2],
                    "status": row[3],
                    "device_status": row[4]
                })
    except Exception as e:
        print(f"Error fetching devices: {e}")
    return devices


def get_device_status_by_id(device_db_id):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM devices WHERE id = ?", (device_db_id,))
            device = cursor.fetchone()
            return device if device else None
    except Exception as e:
        print(f"Error fetching device status: {e}")
        return None 

def get_device_connection_status(device_db_id):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM devices WHERE id = ?", (device_db_id,))
            device = cursor.fetchone()
            return device[0] if device else None
    except Exception as e:
        print(f"Error fetching device connection status: {e}")
        return None

def get_device_power_status(device_db_id):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT device_status FROM devices WHERE id = ?", (device_db_id,))
            device = cursor.fetchone()
            return device[0] if device else None
    except Exception as e:
        print(f"Error fetching device status: {e}")
        return None

def get_device_status(device_db_id):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM devices WHERE id = ?", (device_db_id,))
            device = cursor.fetchone()
            return dict(device) if device else None
    except Exception as e:
        print(f"Error fetching device info: {e}")
        return None

if __name__ == '__main__':
    init_db()