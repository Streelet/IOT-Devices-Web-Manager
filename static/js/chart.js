// Función para inicializar la gráfica de pastel: Distribución de Estados
function initStatusChart() {
  const ctx = document.getElementById('statusChart').getContext('2d');
  // Datos de ejemplo: reemplaza con datos reales de tu backend
  const onlineCount = 4;
  const offlineCount = 2;

  new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ['Online', 'Offline'],
      datasets: [{
        data: [onlineCount, offlineCount],
        backgroundColor: ['#4CAF50', '#F44336'],
        hoverBackgroundColor: ['#66BB6A', '#EF5350']
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom' }
      }
    }
  });
}

// Función para inicializar la gráfica de barras: Uptime de Dispositivos
function initUptimeChart() {
  const ctx = document.getElementById('uptimeChart').getContext('2d');
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Fan 02', 'Pump 01', 'Light 03'],
      datasets: [{
        label: 'Uptime (Hours)',
        data: [24, 18, 30],
        backgroundColor: ['#2196F3', '#9C27B0', '#FF9800'],
        borderColor: ['#1976D2', '#7B1FA2', '#F57C00'],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true }
      },
      plugins: { legend: { position: 'bottom' } }
    }
  });
}

// Inicializa las gráficas cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
  if (document.getElementById('statusChart')) {
    initStatusChart();
  }
  if (document.getElementById('uptimeChart')) {
    initUptimeChart();
  }
});
