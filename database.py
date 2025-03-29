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
    - status: Device status (e.g., 'online', 'offline').
    Returns:
        str: The name of the database file created or verified to exist.
    """
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Creating the 'devices' table 
        cursor.execute('''
            CREATE TABLE devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,   -- Name must be unique
                topic TEXT NOT NULL,         -- MQTT topic (can be duplicated)
                ip TEXT,                     -- IP address (optional)
                status TEXT NOT NULL         -- Status (e.g., online, offline)
            )
        ''')

        conn.commit()
        conn.close()
        return  DB_NAME  # Database created successfully
    else:
        print(f"Database '{DB_NAME}' already exists.")
        return DB_NAME

def add_device(name, topic):
    """
    Adds a new device to the database.

    Parameters:
    - name (str): Name of the device (must be unique).
    - topic (str): Topic associated with the device.

    Returns:
    - int: 1 if the device was added successfully,
           -1 if the name is duplicated,
           -2 for other errors.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Insert new device into 'devices' table
        cursor.execute("INSERT INTO devices (name, topic, status) VALUES (?, ?, ?)", 
                       (name, topic, 'offline'))  # Default status: offline

        conn.commit()
        return 1  # Success

    except sqlite3.IntegrityError:
        print(f"Error: A device with the name '{name}' already exists.")
        return -1  # Name duplication error
    except Exception as e:
        print(f"Error adding device: {e}")
        return -1 # Other errors

    finally:
        if conn:
            conn.close()  # Ensure the connection is closed in any case


# Initialize the database
init_db()
