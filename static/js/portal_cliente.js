document.addEventListener('DOMContentLoaded', function() {
    cargarTiposGalletas();
    actualizarCarrito();
});

async function cargarTiposGalletas() {
    try {
        const response = await fetch('portal/api/tipos-galletas');
        const tipos = await response.json();
        
        const select = document.getElementById('tipo_galleta');
        select.innerHTML = '<option value="">Seleccione un tipo</option>';
        
        tipos.forEach(tipo => {
            const option = document.createElement('option');
            option.value = tipo.id;
            option.textContent = `${tipo.nombre} ($${tipo.costo.toFixed(2)})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error al cargar tipos de galletas:', error);
    }
}

async function cargarGalletas() {
    const tipoId = document.getElementById('tipo_galleta').value;
    const selectGalleta = document.getElementById('galleta');
    
    if (!tipoId) {
        selectGalleta.disabled = true;
        selectGalleta.innerHTML = '<option value="">Primero seleccione un tipo</option>';
        return;
    }
    
    try {
        const response = await fetch(`/api/galletas-por-tipo/${tipoId}`);
        const galletas = await response.json();
        
        selectGalleta.innerHTML = '<option value="">Seleccione una galleta</option>';
        
        galletas.forEach(galleta => {
            const option = document.createElement('option');
            option.value = galleta.id;
            option.textContent = `${galleta.nombre} (${galleta.existencia} disponibles)`;
            selectGalleta.appendChild(option);
        });
        
        selectGalleta.disabled = false;
    } catch (error) {
        console.error('Error al cargar galletas:', error);
    }
}

async function agregarAlCarrito() {
    const tipoId = document.getElementById('tipo_galleta').value;
    const galletaId = document.getElementById('galleta').value;
    const cantidad = document.getElementById('cantidad').value;
    
    if (!tipoId || !galletaId || !cantidad || cantidad < 1) {
        alert('Por favor complete todos los campos correctamente');
        return;
    }
    
    const galletaSelect = document.getElementById('galleta');
    const galletaNombre = galletaSelect.options[galletaSelect.selectedIndex].text.split(' (')[0];
    
    try {
        const response = await fetch('/api/agregar-carrito', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                galleta_id: galletaId,
                nombre: galletaNombre,
                precio: document.getElementById('tipo_galleta').options[document.getElementById('tipo_galleta').selectedIndex].text.match(/\d+\.\d+/)[0],
                cantidad: cantidad
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            actualizarCarrito();
            // Limpiar selección
            document.getElementById('cantidad').value = 1;
            document.getElementById('galleta').selectedIndex = 0;
        } else {
            alert('Error al agregar al carrito: ' + (data.error || ''));
        }
    } catch (error) {
        console.error('Error al agregar al carrito:', error);
        alert('Error al agregar al carrito');
    }
}

async function eliminarDelCarrito(galletaId) {
    try {
        const response = await fetch(`/api/eliminar-item-carrito/${galletaId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            actualizarCarrito();
        } else {
            alert('Error al eliminar del carrito: ' + (data.error || ''));
        }
    } catch (error) {
        console.error('Error al eliminar del carrito:', error);
        alert('Error al eliminar del carrito');
    }
}

function actualizarCarrito() {
    fetch('/api/obtener-carrito')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('tblDetalleVenta');
            tbody.innerHTML = '';
            
            if (data.items && data.items.length > 0) {
                data.items.forEach(item => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${item.nombre}</td>
                        <td>${item.tipo}</td>
                        <td>$${item.precio.toFixed(2)}</td>
                        <td>${item.cantidad}</td>
                        <td>$${item.subtotal.toFixed(2)}</td>
                        <td><button onclick="eliminarDelCarrito(${item.galleta_id})">Eliminar</button></td>
                    `;
                    tbody.appendChild(tr);
                });
                
                document.getElementById('total-importe').textContent = `$${data.total.toFixed(2)}`;
                document.getElementById('total-carrito').textContent = `$${data.total.toFixed(2)}`;
            } else {
                tbody.innerHTML = '<tr><td colspan="6">No hay items en el carrito</td></tr>';
                document.getElementById('total-importe').textContent = '$0.00';
                document.getElementById('total-carrito').textContent = '$0.00';
            }
        })
        .catch(error => {
            console.error('Error al actualizar carrito:', error);
        });
}

function verCarrito() {
    window.location.href = '/ver-carrito';
}

function limpiarCarrito() {
    if (confirm('¿Está seguro que desea vaciar el carrito?')) {
        fetch('/api/limpiar-carrito', { method: 'DELETE' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    actualizarCarrito();
                }
            })
            .catch(error => {
                console.error('Error al limpiar carrito:', error);
            });
    }
}

// Hacer funciones accesibles globalmente
window.cargarGalletas = cargarGalletas;
window.agregarAlCarrito = agregarAlCarrito;
window.eliminarDelCarrito = eliminarDelCarrito;
window.verCarrito = verCarrito;
window.limpiarCarrito = limpiarCarrito;