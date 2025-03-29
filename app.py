from flask import Flask, request, jsonify, render_template
from database import init_db, add_device, update_device, delete_device
from broker_actions import connect_mqtt, turn_on_device, turn_off_device
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
    try:
        data = request.get_json()

        name = data.get('name')
        status = data.get('status')
        device_status = data.get('device_status')

        result = update_device(device_id, name, status, device_status)

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
        result = delete_device(device_id)

        if result == 1:
            return jsonify({'message': 'Device deleted successfully'}), 200
        elif result == -2:
            return jsonify({'error': 'Device not found'}), 404
        else:
            return jsonify({'error': 'Failed to delete device'}), 500

    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500



# Control Methods

@app.route('/devices/<int:device_id>/turn_on', methods=['POST'])
def turn_on_endpoint(device_id):
    """
    Endpoint to turn on a device.
    """
    try:
        turn_on_device(client, device_id)
        return jsonify({"message": f"Device {device_id} turned on successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/devices/<int:device_id>/turn_off', methods=['POST'])
def turn_off_endpoint(device_id):
    """
    Endpoint to turn off a device.
    """
    try:
        turn_off_device(client, device_id)
        return jsonify({"message": f"Device {device_id} turned off successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500




# Web App Routes


@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
