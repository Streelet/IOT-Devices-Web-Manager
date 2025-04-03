new Vue({
  el: '#app',
  data: {
    isSidebarActive: true,
    // Datos de ejemplo para las tarjetas de métricas
    stats: [
      { title: 'Devices', value: 5, subtitle: 'Connected', colorClass: 'bg-blue' },
      { title: 'Device Groups', value: 2, subtitle: 'Active Groups', colorClass: 'bg-purple' },
      { title: 'Device Categories', value: 5, subtitle: 'Categories in use', colorClass: 'bg-orange' },
      { title: 'Device Jobs', value: 1, subtitle: 'Scheduled Jobs', colorClass: 'bg-red' }
    ],
    devices: []
  },
  methods: {
    toggleSidebar() {
      this.isSidebarActive = !this.isSidebarActive;
    },
    fetchDevices() {
      // Aquí llamas a tu endpoint para obtener los dispositivos.
      // Ejemplo:
      // fetch('/devices')
      //   .then(response => response.json())
      //   .then(data => { this.devices = data; })
      //   .catch(error => console.error('Error fetching devices:', error));

      // Para el demo, usamos datos estáticos:
      this.devices = [
        {
          id: 1,
          name: 'Fan 02',
          ip: '192.168.1.10',
          status: 'online',
          device_status: 1,
          thermal: 20,
          iconUrl: 'https://via.placeholder.com/48'
        },
        {
          id: 2,
          name: 'Pump 01',
          ip: '192.168.1.11',
          status: 'offline',
          device_status: 0,
          thermal: 25,
          iconUrl: 'https://via.placeholder.com/48'
        },
        {
          id: 3,
          name: 'Light 03',
          ip: '192.168.1.12',
          status: 'online',
          device_status: 1,
          thermal: 22,
          iconUrl: 'https://via.placeholder.com/48'
        }
      ];
    },
    toggleDevicePower(device) {
      const newState = device.device_status === 1 ? 0 : 1;
      // Llama a tu backend para actualizar el estado del dispositivo.
      // fetch(`/devices/${device.id}/set_power/${newState}`, { method: 'POST' })
      //   .then(() => { this.fetchDevices(); })
      //   .catch(error => console.error('Error toggling device power:', error));
      // Para demo, actualizamos el estado localmente:
      device.device_status = newState;
    },
    showDeviceInfo(device) {
      // Aquí puedes implementar la lógica para mostrar información detallada
      // por ejemplo, abriendo un modal o redirigiendo a otra vista.
      alert(`Mostrar información de ${device.name}`);
    }
  },
  mounted() {
    this.fetchDevices();
  }
});
