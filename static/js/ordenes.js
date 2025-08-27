//Abrir modal de pagos al  proveedor
function abrirModalOrdenes() {
    document.getElementById('modalOrdenes').style.display = 'flex';
}
//Cerrar el modal de pagos al  proveedor
function cerrarModalOrdenes() {
    document.getElementById('modalOrdenes').style.display = 'none';
}

// ocultar mensajes automáticamente
const messages = document.querySelectorAll('.auto-hide');
messages.forEach(function(message) {
    setTimeout(function() {
        message.style.transition = 'opacity 0.5s ease';
        message.style.opacity = '0';
        setTimeout(function() {
            message.remove();
        }, 500); // termina la transición antes de eliminar
    }, 5000);
});
