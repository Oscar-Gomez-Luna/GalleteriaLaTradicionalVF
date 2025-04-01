// static/js/dashboard.js
document.addEventListener('DOMContentLoaded', function () {
    // Obtener los datos pasados desde la plantilla
    const fechas = JSON.parse(document.getElementById('fechas').textContent);
    const totalesVentas = JSON.parse(document.getElementById('totalesVentas').textContent);
    const nombresProductos = JSON.parse(document.getElementById('nombresProductos').textContent);
    const cantidadesProductos = JSON.parse(document.getElementById('cantidadesProductos').textContent);
    const nombresPresentaciones = JSON.parse(document.getElementById('nombresPresentaciones').textContent);
    const cantidadesPresentaciones = JSON.parse(document.getElementById('cantidadesPresentaciones').textContent);

    // Configuración global para los gráficos
    Chart.defaults.font.family = 'Arial';
    Chart.defaults.font.size = 14;
    Chart.defaults.color = '#666';

    // Gráfica de Ventas Diarias (Línea)
    const ctxVentasDiarias = document.getElementById('ventasDiariasChart').getContext('2d');
    new Chart(ctxVentasDiarias, {
        type: 'line',
        data: {
            labels: fechas,
            datasets: [{
                label: 'Ventas Diarias ($)',
                data: totalesVentas,
                borderColor: '#4CAF50',
                backgroundColor: 'rgba(76, 175, 80, 0.2)',
                fill: true,
                tension: 0.3,
                pointBackgroundColor: '#4CAF50',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#4CAF50'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#eee' },
                    ticks: { color: '#666' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#666' }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        font: { size: 14 },
                        color: '#333'
                    }
                }
            }
        }
    });

    // Gráfica de Productos Más Vendidos (Barras)
    const ctxProductosVendidos = document.getElementById('productosVendidosChart').getContext('2d');
    new Chart(ctxProductosVendidos, {
        type: 'bar',
        data: {
            labels: nombresProductos,
            datasets: [{
                label: 'Cantidad Vendida',
                data: cantidadesProductos,
                backgroundColor: 'rgba(33, 150, 243, 0.7)',
                borderColor: 'rgba(33, 150, 243, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#eee' },
                    ticks: { color: '#666' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#666' }
                }
            },
            plugins: {
                legend: {
                    labels: {
                        font: { size: 14 },
                        color: '#333'
                    }
                }
            }
        }
    });

    // Gráfica de Presentaciones Más Vendidas (Pastel)
    const ctxPresentacionesVendidas = document.getElementById('presentacionesVendidasChart').getContext('2d');
    new Chart(ctxPresentacionesVendidas, {
        type: 'pie',
        data: {
            labels: nombresPresentaciones,
            datasets: [{
                label: 'Cantidad Vendida',
                data: cantidadesPresentaciones,
                backgroundColor: [
                    'rgba(244, 67, 54, 0.7)',
                    'rgba(33, 150, 243, 0.7)',
                    'rgba(255, 193, 7, 0.7)',
                    'rgba(76, 175, 80, 0.7)',
                    'rgba(156, 39, 176, 0.7)',
                ],
                borderColor: [
                    'rgba(244, 67, 54, 1)',
                    'rgba(33, 150, 243, 1)',
                    'rgba(255, 193, 7, 1)',
                    'rgba(76, 175, 80, 1)',
                    'rgba(156, 39, 176, 1)',
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        font: { size: 14 },
                        color: '#333'
                    }
                }
            }
        }
    });

    // Lógica para ocultar mensajes automáticamente
    const messages = document.querySelectorAll('.auto-hide');
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.transition = 'opacity 0.5s ease';
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 500); // Espera a que termine la transición antes de eliminar
        }, 5000); // 5 segundos
    });
});