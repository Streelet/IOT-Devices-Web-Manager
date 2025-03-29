from flask import Flask, request, jsonify
from database import init_db, add_device
from broker_actions import connect_mqtt
import sqlite3

app = Flask(__name__)

# Initialize the database

DB_NAME = init_db()

# Connect to the MQTT broker
client = connect_mqtt()
# Start the MQTT client loop to process network traffic and callbacks
client.loop_start()

@app.route('/devices', methods=['GET'])
def get_devices_endpoint():
    """
    Endpoint to retrieve all devices from the database.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM devices")
    devices = cursor.fetchall()

    conn.close()

    devices_list = []
    for device in devices:
        devices_list.append({
            'id': device[0],
            'name': device[1],
            'topic': device[2],
            'ip': device[3],
            'status': device[4]
        })
    return jsonify(devices_list)



@app.route('/devices', methods=['POST'])
def add_device_endpoint():
    """
    Handles the POST request to add a new device.
    The device information is expected to be sent in the request body in JSON format.
    """
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Check if the required fields are in the JSON data
        if 'name' not in data or 'topic' not in data:
            return jsonify({'error': 'Missing name or topic'}), 400  # Bad request

        # Extract name and topic
        name = data['name']
        topic = data['topic']

        # Add device to the database 
        result = add_device(name, topic)  # add_device_to_db is the database function

        # Check result and return the appropriate response
        if result == 1:
            return jsonify({'message': 'Device added successfully'}), 201  # Created
        elif result == -1:
            return jsonify({'error': f'Device with name "{name}" already exists'}), 409  # Conflict (duplicate)
        else:
            return jsonify({'error': 'Failed to add device'}), 500  # Backend Error

    except Exception as e:
        return jsonify({'error': str(e)}), 500  # General error



@app.route('/devices/<int:device_id>', methods=['PUT'])
def update_device_endpoint(device_id):
    """
    Endpoint to update a device's status.
    The new status is expected to be sent in the request body in JSON format.
    """
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Check if the required field is in the JSON data
        if 'name' not in data and 'status' not in data:
            return jsonify({'error': 'Missing name or status'}), 400

        name = data.get('name')
        status = data.get('status')

        # Get the current device by ID from the database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
        device = cursor.fetchone()  # Fetch the first row

        # Check if the device exists
        if not device:
            return jsonify({'error': 'Device not found'}), 404

        # Update the device's status and name if provided
        if name:
            cursor.execute("UPDATE devices SET name = ? WHERE id = ?", (name, device_id))
        if status:
            cursor.execute("UPDATE devices SET status = ? WHERE id = ?", (status, device_id))

        conn.commit()
        conn.close()

        return jsonify({'message': 'Device updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500  # General error


@app.route('/devices/<int:device_id>', methods=['DELETE'])
def delete_device_endpoint(device_id):
    """
    Endpoint to delete a device by its ID.
    The device is removed from the database if it exists.
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Check if the device exists in the database
        cursor.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
        device = cursor.fetchone()  # Fetch the first row

        # If the device does not exist, return an error
        if not device:
            return jsonify({'error': 'Device not found'}), 404  # Not found

        # Delete the device from the database
        cursor.execute("DELETE FROM devices WHERE id = ?", (device_id,))
        conn.commit()

        return jsonify({'message': 'Device deleted successfully'}), 200  # Success

    except Exception as e:
        # Return an error if something goes wrong
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500  # General error

    finally:
        # Ensure the connection is always closed, even in case of error
        if conn:
            conn.close()




# Control Methods



@app.route('/devices/<int:device_id>/turn_on', methods=['POST'])
def turn_on(device_id):
    """
    Turns on the device by sending a command to the broker.
    """
    client = connect_mqtt()
    try:
        client.publish(MQTT_TOPIC, f"turn_on_{device_id}")
        return jsonify({"message": f"Device {device_id} turned on."}), 200
    except Exception as e:
        return jsonify({"error": f"Error turning on device {device_id}: {e}"}), 500

# Método para apagar el dispositivo
@app.route('/devices/<int:device_id>/turn_off', methods=['POST'])
def turn_off(device_id):
    """
    Turns off the device by sending a command to the broker.
    """
    client = connect_mqtt()
    try:
        client.publish(MQTT_TOPIC, f"turn_off_{device_id}")
        return jsonify({"message": f"Device {device_id} turned off."}), 200
    except Exception as e:
        return jsonify({"error": f"Error turning off device {device_id}: {e}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
