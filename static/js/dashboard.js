new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        isSidebarActive: true,
        stats: [
            { title: 'Devices', value: 0, subtitle: 'Connected', colorClass: 'bg-blue' },
            { title: 'Device Groups', value: 0, subtitle: 'Active Groups', colorClass: 'bg-purple' },
            { title: 'Device Categories', value: 0, subtitle: 'Categories in use', colorClass: 'bg-orange' },
            { title: 'Device Jobs', value: 0, subtitle: 'Scheduled Jobs', colorClass: 'bg-red' }
        ],
        devices: []
    },
    methods: {
        // Métodos de UI
        toggleSidebar() {
            this.isSidebarActive = !this.isSidebarActive;
        },

        // Métodos de Dispositivos
        fetchDevices() {
            fetch('/devices')
                .then(response => response.json())
                .then(data => {
                    this.devices = data.map(device => ({
                        id: device.id,
                        name: device.name || device_id,
                        status: device.status,
                        device_status: device.status === 'online' ? 1 : 0,
                        last_seen: device.last_seen,
                        iconUrl: 'https://cdn4.iconfinder.com/data/icons/minimal-set-four/32/minimal-86-512.png',
                        gradientBg: getDeterministicGradient(device.status, device.id)
                    }));
                    this.updateDeviceStats();
                })
                .catch(error => console.error('Error fetching devices:', error));
        },
        toggleDevicePower(device) {
            const action = device.device_status === 1 ? 'off' : 'on';

            fetch(`/devices/${device.id}/power/${action}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.message) {
                    device.device_status = device.device_status === 1 ? 0 : 1;
                    device.status = action === 'on' ? 'online' : 'offline';
                    console.log(`Dispositivo ${device.id} ahora está ${action}`);
                } else {
                    console.error('Error al cambiar el estado del dispositivo:', data.error);
                }
            })
            .catch(error => {
                console.error('Error al comunicarse con el servidor:', error);
            });
        },
        showDeviceInfo(device) {
            alert(`Mostrar información de ${device.name} (ID: ${device.id})`);
        },
        updateDeviceStats() {
            this.stats[0].value = this.devices.length; // Actualizar el número total de dispositivos
        },
        addDevice() {
            window.location.href = '/add_device';
        },
        getRandomColor() {
            const letters = '0123456789ABCDEF';
            let color = '#';
            for (let i = 0; i < 6; i++) {
                color += letters[Math.floor(Math.random() * 16)];
            }
            return color;
        },
        deleteDevice(deviceId) {
            if (confirm(`¿Estás seguro de que quieres eliminar el dispositivo con ID: ${deviceId}?`)) {
                fetch(`/devices/${deviceId}/delete`, {
                    method: 'POST'
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Error HTTP: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.message) {
                        console.log(data.message);
                        this.fetchDevices(); // Recargar la lista de dispositivos
                    } else if (data.error) {
                        console.error('Error al eliminar el dispositivo:', data.error);
                        alert(data.error);
                    }
                })
                .catch(error => {
                    console.error('Error al comunicarse con el servidor:', error);
                    alert('Error al comunicarse con el servidor.');
                });
            }
        }
    },
    mounted() {
        this.fetchDevices();
        // Actualizar la lista de dispositivos cada 2 segundos
        setInterval(() => {
            this.fetchDevices();
        }, 2000);
    }
});

// Función auxiliar fuera de Vue para asignar gradientes (determinista)
function getDeterministicGradient(status, id) {
    const gradientsOnline = [
        'linear-gradient(135deg, #1abc9c 0%, #16a085 100%)',
        'linear-gradient(135deg, #3498db 0%, #2980b9 100%)',
        'linear-gradient(135deg, #2ecc71 0%, #27ae60 100%)',
        'linear-gradient(135deg, #00c6ff 0%, #0072ff 100%)',
        'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
    ];
    const gradientsOffline = [
        'linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)',
        'linear-gradient(135deg, #ff4e50 0%, #f80759 100%)',
        'linear-gradient(135deg, #ff6a00 0%, #ee0979 100%)',
        'linear-gradient(135deg, #ff3e3e 0%, #ff0000 100%)',
        'linear-gradient(135deg, #ff5f6d 0%, #ff3c41 100%)'
    ];

    function seededRandom(seed) {
        let x = Math.sin(seed) * 10000;
        return x - Math.floor(x);
    }

    let seed = id * 99991;
    let index = Math.floor(seededRandom(seed) * (status === 'online' ? gradientsOnline.length : gradientsOffline.length));
    return status === 'online' ? gradientsOnline[index] : gradientsOffline[index];
}