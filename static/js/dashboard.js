new Vue({
  el: '#app',
  delimiters: ['[[', ']]'],
  data: {
    isSidebarActive: true,
    activeRange: '1h',
    stats: [
      { title: 'Devices', value: 5, subtitle: 'Connected', colorClass: 'bg-blue' },
      { title: 'Device Groups', value: 0, subtitle: 'Active Groups', colorClass: 'bg-purple' },
      { title: 'Device Categories', value: 5, subtitle: 'Categories in use', colorClass: 'bg-orange' },
      { title: 'Device Jobs', value: 0, subtitle: 'Scheduled Jobs', colorClass: 'bg-red' }
    ],
    devices: []
  },
  methods: {
    // Métodos de UI
    toggleSidebar() {
      this.isSidebarActive = !this.isSidebarActive;
    },
    setRange(range) {
      this.activeRange = range;
      this.loadTemperatureData();
    },
    loadTemperatureData() {
      // Llamada a endpoint de temperatura, si se requiere.
    },
    
    // Métodos de Dispositivos
    fetchDevices() {
      fetch('/devices')
        .then(response => response.json())
        .then(data => {
          this.devices = data.map(device => ({
            id: device.id,
            name: device.name,
            device_status: device.status === 'online' ? 1 : 0,
            thermal: 25, // Ajusta según tu lógica o valor real
            iconUrl: 'https://cdn4.iconfinder.com/data/icons/minimal-set-four/32/minimal-86-512.png',
            gradientBg: getDeterministicGradient(device.status, device.id)
          }));
        })
        .catch(error => console.error('Error fetching devices:', error));
    },
    toggleDevicePower(device) {
      const newState = device.device_status === 1 ? 0 : 1;
      fetch(`/devices/${device.id}/set_power/${newState}`, { method: 'POST' })
        .then(response => response.json())
        .then(() => { device.device_status = newState; })
        .catch(error => console.error('Error toggling device power:', error));
    },
    showDeviceInfo(device) {
      alert(`Mostrar información de ${device.name}`);
    },
    initChart() {
      const ctx = document.getElementById('tempChart').getContext('2d');
      new Chart(ctx, {
        type: 'line',
        data: {
          labels: ['10:00', '10:10', '10:20', '10:30', '10:40', '10:50'],
          datasets: [{
            label: 'Temperature (°C)',
            data: [20, 22, 21, 23, 24, 22],
            backgroundColor: 'rgba(33,150,243,0.2)',
            borderColor: '#2196F3',
            borderWidth: 2,
            fill: true
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: { y: { beginAtZero: false } }
        }
      });
    }
  },
  mounted() {
    this.fetchDevices();
    this.initChart();
    // Actualizar la lista de dispositivos cada 5 segundos
    setInterval(() => {
      this.fetchDevices();
    }, 5000);
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
