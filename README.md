# Sistema de Gestión de Dispositivos (IOT) / IOT Device Manager

Este es un sistema web para la gestión de dispositivos, construido con **Flask**, **SQLite** y **MQTT**. Permite la gestión de dispositivos, incluyendo agregar, actualizar, eliminar y controlar su estado. El sistema está diseñado para ser fácilmente ampliado con más características según sea necesario.

This is a web-based device management system built with **Flask**, **SQLite**, and **MQTT**. It allows for the management of devices, including adding, updating, deleting, and controlling their status. The system is designed to be easily extended with more features as needed.

## Características / Features

- **Gestión de Dispositivos / Device Management:**
  - Agregar nuevos dispositivos con nombres y tópicos únicos. / Add new devices with unique names and topics.
  - Actualizar detalles de los dispositivos, como el nombre y el estado. / Update device details such as name and status.
  - Eliminar dispositivos del sistema. / Delete devices from the system.

- **Control de Dispositivos / Device Control:**
  - Encender o apagar dispositivos remotamente a través de MQTT. / Turn devices on or off remotely via MQTT.

- **Base de Datos / Database:**
  - Utiliza una base de datos SQLite para almacenar información de dispositivos. / Uses an SQLite database to store device information.
  - Cada dispositivo tiene un nombre, tópico, dirección IP, estado y estado de control (encendido/apagado). / Each device has a name, topic, IP address, status, and control status (on/off).

## Tecnologías Usadas / Technologies Used

- **Flask:** Para la aplicación web y los puntos finales de la API. / For the web application and API endpoints.
- **SQLite:** Para la base de datos local que almacena la información de los dispositivos. / For the local database storing device information.
- **MQTT:** Para enviar comandos de control a los dispositivos. / For sending control commands to the devices.

## Puntos Finales de la API / API Endpoints

1. **GET /devices**  
   Recupera todos los dispositivos de la base de datos. / Retrieve all devices from the database.

2. **POST /devices**  
   Agrega un nuevo dispositivo a la base de datos. Requiere los campos `name` y `topic` en el cuerpo de la solicitud. / Add a new device to the database. Requires `name` and `topic` fields in the request body.

3. **PUT /devices/<int:device_id>**  
   Actualiza los detalles de un dispositivo existente. Requiere los campos `name` o `status` en el cuerpo de la solicitud. / Update the details of an existing device. Requires `name` or `status` fields in the request body.

4. **DELETE /devices/<int:device_id>**  
   Elimina un dispositivo por su ID. / Delete a device by its ID.

5. **POST /devices/<int:device_id>/turn_on**  
   Enciende el dispositivo identificado por `device_id`. / Turn on the device identified by `device_id`.

6. **POST /devices/<int:device_id>/turn_off**  
   Apaga el dispositivo identificado por `device_id`. / Turn off the device identified by `device_id`.

## Esquema de la Base de Datos / Database Schema

La base de datos tiene una tabla llamada `devices`, con los siguientes campos / The database has a single table called `devices`, with the following fields:

- `id`: Identificador único auto-incrementado. / Auto-incremented unique identifier.
- `name`: El nombre del dispositivo (debe ser único). / The name of the device (must be unique).
- `topic`: El tópico MQTT asociado con el dispositivo. / The MQTT topic associated with the device.
- `ip`: La dirección IP del dispositivo (opcional). / The IP address of the device (optional).
- `status`: El estado actual del dispositivo (por ejemplo, "online" o "offline"). / The current status of the device (e.g., "online" or "offline").
- `control_status`: El estado de control del dispositivo (0 para apagado, 1 para encendido). / The control status of the device (0 for off, 1 for on).

## Instalación y Configuración / Setup and Installation

### Requisitos / Requirements

- Python 3.x
- Flask
- SQLite (pre-instalado con Python) / SQLite (pre-installed with Python)
- Cliente Paho MQTT / Paho MQTT client

## Estado Actual del Desarrollo / Current Development Status

Actualmente, el proyecto está en desarrollo y aún no cuenta con una versión operativa. Aunque no está completamente disponible para su uso general, estoy trabajando activamente en su mejora y perfeccionamiento. Se está integrando la funcionalidad principal, como la gestión de dispositivos y el control de los mismos a través de una interfaz web y MQTT. En breve, se lanzará una versión estable con las funcionalidades básicas implementadas y listas para ser probadas.

The project is currently under development and does not yet have an operational version. Although it is not fully available for general use, I am actively working on its enhancement and refinement. The core functionality, such as device management and control through a web interface and MQTT, is being integrated. A stable version with the basic functionalities implemented will be released soon and ready for testing.
