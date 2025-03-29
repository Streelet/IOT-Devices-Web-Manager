import sqlite3
import os

DB_NAME = 'devices.db'  

def init_db():
    """
    Initializes the SQLite database.
    
    If the database does not exist, it creates a new file and sets up the 'devices' table.
    The table stores information about network devices, including:
    
    - id: Unique identifier (Auto-incremented).
    - name: Device name (Must be unique).
    - topic: MQTT topic for communication (Can be duplicated).
    - ip: Device IP address (Optional).
    - status: Device connection status (e.g., 'online', 'offline').
    - device_status: Device on/off status (0: off, 1: on).
    
    Returns:
        str: The name of the database file created or verified to exist.
    """
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Create the 'devices' table with the new 'device_status' numeric field
        cursor.execute('''
            CREATE TABLE devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,   -- Unique device name
                topic TEXT NOT NULL,         -- MQTT topic (can be duplicated)
                ip TEXT,                     -- Optional IP address
                status TEXT NOT NULL DEFAULT 'offline',  -- Connection status (default 'offline')
                device_status INTEGER NOT NULL DEFAULT 0 -- Device on/off status (0: off, 1: on)
            )
        ''')

        conn.commit()
        conn.close()
        return DB_NAME  # Database created successfully
    else:
        print(f"Database '{DB_NAME}' already exists.")
        return DB_NAME

def add_device(name, topic):
    """
    Adds a new device to the database.
    
    Parameters:
    - name (str): Name of the device (must be unique).
    - topic (str): MQTT topic associated with the device.
    
    Returns:
    - int: 1 if the device was added successfully,
           -1 if the name is duplicated,
           -2 for other errors.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Insert new device into 'devices' table, including the 'device_status' as 0 (off)
        cursor.execute("INSERT INTO devices (name, topic, status, device_status) VALUES (?, ?, ?, ?)", 
                       (name, topic, 'offline', 0))  # Default status: offline, device_status: 0 (off)

        conn.commit()
        return 1  # Success

    except sqlite3.IntegrityError:
        print(f"Error: A device with the name '{name}' already exists.")
        return -1  # Name duplication error
    except Exception as e:
        print(f"Error adding device: {e}")
        return -1  # Other errors

    finally:
        if conn:
            conn.close()  # Ensure the connection is closed



def update_device_status(device_id, status):
    """
    Updates the device's on/off status (0: off, 1: on) in the database.
    
    Parameters:
    - device_id (int): ID of the device to update.
    - status (int): The new status of the device (0 for off, 1 for on).
    
    Returns:
    - int: 1 if the update was successful,
           -2 if an error occurred during the update.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Update the device's on/off status in the database
        cursor.execute("UPDATE devices SET device_status = ? WHERE id = ?", (status, device_id))

        conn.commit()
        return 1  # Success

    except Exception as e:
        print(f"Error updating device status: {e}")
        return -2  # Error occurred during update

    finally:
        if conn:
            conn.close()  # Ensure the connection is closed


def update_device(device_id, name=None, status=None, device_status=None):
    """
    Updates the device details such as name, status, and device_status.
    
    Parameters:
    - device_id (int): ID of the device to update.
    - name (str, optional): New name of the device.
    - status (str, optional): New connection status.
    - device_status (int, optional): New device on/off status (0 or 1).
    
    Returns:
    - int: 1 if update was successful,
           -2 if the device is not found,
           -3 if the update failed.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Check if the device exists
        cursor.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
        device = cursor.fetchone()

        if not device:
            return -2  # Device not found

        # Update the device details
        if name:
            cursor.execute("UPDATE devices SET name = ? WHERE id = ?", (name, device_id))
        if status:
            cursor.execute("UPDATE devices SET status = ? WHERE id = ?", (status, device_id))
        if device_status is not None:
            cursor.execute("UPDATE devices SET device_status = ? WHERE id = ?", (device_status, device_id))

        conn.commit()
        return 1  # Success

    except Exception as e:
        print(f"Error updating device: {e}")
        return -3  # Failed to update

    finally:
        if conn:
            conn.close()


def delete_device(device_id):
    """
    Deletes a device from the database.
    
    Parameters:
    - device_id (int): ID of the device to delete.
    
    Returns:
    - int: 1 if delete was successful,
           -2 if the device is not found,
           -3 if deletion failed.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Check if the device exists
        cursor.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
        device = cursor.fetchone()

        if not device:
            return -2  # Device not found

        # Delete the device
        cursor.execute("DELETE FROM devices WHERE id = ?", (device_id,))
        conn.commit()
        return 1  # Success

    except Exception as e:
        print(f"Error deleting device: {e}")
        return -3  # Deletion failed

    finally:
        if conn:
            conn.close()


def turn_on_device(client, device_id):
    """
    Turns on the device and updates the device status in the database.
    
    Parameters:
    - client: The MQTT client.
    - device_id (int): ID of the device to turn on.
    """
    # MQTT call to turn on the device
    # client.publish("device/{device_id}/control", "on")
    
    # Update the device's status in the database
    update_device_status(device_id, 1)  # 1 indicates the device is turned on
    
    # Optional: Confirmation of the device being turned on (if needed)





def turn_off_device(client, device_id):
    """
    Turns off the device and updates the device status in the database.
    
    Parameters:
    - client: The MQTT client.
    - device_id (int): ID of the device to turn off.
    """
    # MQTT call to turn off the device
    # client.publish("device/{device_id}/control", "off")
    
    # Update the device's status in the database
    update_device_status(device_id, 0)  # 0 indicates the device is turned off
    
    # Optional: Confirmation of the device being turned off (if needed)


# Initialize the database
init_db()
