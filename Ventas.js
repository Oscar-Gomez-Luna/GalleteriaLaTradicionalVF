let ventas;

function cargarCatalogoVentas() {            
    fetch("http://localhost:8081/DON_GALLETO_Ventas/api/venta/getAll?activo=true")
            .then(response => response.json())
            .then(response => {
                let mostrar = "";
                ventas = response;

                for (let i = 0; i < response.length; i++) {
                    mostrar += "<tr data-id-venta='" + response[i].id + "'>"; // Añadir el id_venta como atributo de datos
                    mostrar += "<td>" + response[i].fecha + "</td>";
                    mostrar += "<td>" + response[i].hora + "</td>";
                    mostrar += "<td> $ " + response[i].total + "</td>";
                    mostrar += "<td>" + response[i].descripcion + "</td>";
                    mostrar += "</tr>";
                }

                // Asignar todo el HTML generado a la tabla
                document.getElementById("tblVentas").innerHTML = mostrar;

                // Agregar el evento de clic a cada fila de la tabla
                const filas = document.querySelectorAll("#tblVentas tr");
                filas.forEach(fila => {
                    fila.addEventListener("click", function () {
                        const idVenta = fila.getAttribute("data-id-venta");
                        cargarDetalleVenta(idVenta); // Cargar los detalles de la venta seleccionada
                    });
                });
            })
            .catch(error => {
                console.error("Error al cargar el catálogo de ventas:", error);
            });
}

function cargarDetalleVenta(idVenta) {
    fetch("http://localhost:8081/DON_GALLETO_Ventas/api/detalleVenta/getAll?activo=true")
            .then(response => response.json())
            .then(detalles => {
                let mostrarDetalles = "<ul>";

                // Filtrar el detalle de la venta por el id_venta
                const detallesVenta = detalles.filter(detalle => detalle.venta.id_venta === idVenta);

                for (let i = 0; i < detallesVenta.length; i++) {
                    mostrarDetalles += "<li>";
                    mostrarDetalles += "Producto " + (i + 1) + ": " + detallesVenta[i].galleta.galleta + "<br>";
                    mostrarDetalles += "Tipo de Producto: " + detallesVenta[i].galleta.tipo + "<br>";
                    mostrarDetalles += "Cantidad: " + detallesVenta[i].cantidad + " pz<br>";
                    mostrarDetalles += "Subtotal: $" + detallesVenta[i].subtotal + "<br>";
                    mostrarDetalles += "<br>";
                    mostrarDetalles += "</li>";
                }


                mostrarDetalles += "</ul>";

                // Mostrar los detalles en la sección de descripción
                document.querySelector(".descripcion-compra p").innerHTML = mostrarDetalles;
            })
            .catch(error => {
                console.error("Error al cargar los detalles de la venta:", error);
            });
}

function insertarVenta() {
    const detallesVenta = [];
    const filas = document.getElementById("tblDetalleVenta").getElementsByTagName("tr");

    let descripcion_venta = ""; // Variable para la descripción de la venta
    let total = 0; // Variable para acumular el total
    let tiposGalleta = new Set(); // Set para contar tipos de galleta diferentes

    for (let i = 0; i < filas.length; i++) {
        const fila = filas[i];
        const tipoGalleta = fila.querySelector("td:nth-child(1)").innerText; // Descripción
        const precio = parseFloat(fila.querySelector("td:nth-child(2)").innerText); // Precio
        const cantidad = parseInt(fila.querySelector("td:nth-child(3)").innerText); // Cantidad
        const importe = parseFloat(fila.querySelector("td:nth-child(4)").innerText); // Importe
        const id_galleta = parseInt(fila.getAttribute("data-id")); // Obtener el id del atributo data-id

        descripcion_venta = "Venta de " + (i + 1) + " tipo de galletas."; // Descripción dinámica

        total += importe;

        // Agregar el tipo de galleta al Set (solo se almacenarán los valores únicos)
        tiposGalleta.add(tipoGalleta); // Solo cuenta los tipos sin almacenarlos

        detallesVenta.push({
            galleta: {
                id_galleta: id_galleta
            },
            cantidad: cantidad,
            subtotal: importe
        });
    }
    const cantidadTiposGalleta = tiposGalleta.size;
    let tipos_de_venta = "";
    if (cantidadTiposGalleta > 1) {
        tipos_de_venta = "Variado";
    } else {
        tipos_de_venta = [...tiposGalleta][0];
    }
    let venta = {
        descripcion: descripcion_venta,
        total: total,
        ticket: "Ticket----------",
        tipo_venta: tipos_de_venta
    };

    let params = {v: JSON.stringify(venta), ldv: JSON.stringify(detallesVenta)};

    let ruta = "http://localhost:8081/DON_GALLETO_Ventas/api/venta/insertar";
    fetch(ruta, {
        method: "POST",
        headers: {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'},
        body: new URLSearchParams(params)
    })
            .then(response => response.json())
            .then(response => {
                if (response.result) {
                    Swal.fire("¡Exito!", response.result, "success");
                }
                if (response.error) {
                    Swal.fire("¡Error!", response.error, "error");
                }
                cargarCatalogoVentas();
                document.getElementById("tblDetalleVenta").innerHTML = "";
                document.getElementById("total-importe").innerText = "Total: $00.00";
                document.getElementById("tipo_venta").style.display = 'block';
            })
            .catch(error => {
                console.error("Error al insertar laventa:", error);
                Swal.fire("Error", "Hubo un problema al insertar la venta", "error");
            });
}

function cargarSelectGalletas(galletas, tipoVentaSeleccionado) {
    let galletasFiltradas;

    // Filtrar las galletas dependiendo del tipo de venta seleccionado
    if (tipoVentaSeleccionado === 'Por Kilo' || tipoVentaSeleccionado === 'Por Cantidad Monetaria') {
        // Solo mostrar las galletas de tipo 'Unitario' si es tipo 'Por Kilo' o 'Por Cantidad Monetaria'
        galletasFiltradas = galletas.filter(galleta => galleta.tipo === 'Unidad');
    } else {
        // De lo contrario, filtrar por el tipo de venta seleccionado
        galletasFiltradas = galletas.filter(galleta => galleta.tipo === tipoVentaSeleccionado);
    }

    let datosGalletas = `
        <option value='' disabled selected>
            Selecciona un tipo de galleta
        </option>`;

    galletasFiltradas.forEach(galleta => {
        datosGalletas += `
            <option value='${galleta.id_galleta}' 
                    data-precio='${galleta.costo}' 
                    data-existencia='${galleta.existencia}'>
                ${galleta.galleta}
            </option>`;
    });

    document.getElementById("tipoGalleta").innerHTML = datosGalletas;

    // Evento para actualizar el precio y calcular total
    document.getElementById("tipoGalleta").addEventListener("change", function () {
        let selectedOption = this.options[this.selectedIndex];
        let precio = selectedOption.getAttribute("data-precio");
        document.getElementById("precio").value = precio;

        calcularTotal(); // Actualizar total si ya hay cantidad ingresada
    });

    // Evento para recalcular el total al cambiar la cantidad
    document.getElementById("cantidad").addEventListener("input", calcularTotal);
}


function cargarSelectTipoVenta() {
    fetch("http://localhost:8081/DON_GALLETO_Ventas/api/galleta/getAll")
            .then(response => response.json())
            .then(response => {
                let galletas = response;

                // Usamos un Set para almacenar tipos de venta únicos
                let tiposVentaUnicos = new Set();

                let datosGalletas = `
                <option value='' disabled selected>
                    Selecciona un tipo de venta
                </option>`;

                // Recorrer las galletas y agregar solo tipos únicos
                galletas.forEach(galleta => {
                    if (!tiposVentaUnicos.has(galleta.tipo)) {
                        tiposVentaUnicos.add(galleta.tipo); // Agregar el tipo al Set
                        datosGalletas += `
                        <option value='${galleta.tipo}'>
                            ${galleta.tipo}
                        </option>`;
                    }
                });
                datosGalletas += `
                        <option value='Por Kilo'>
                            Por Kilo
                        </option>`;
                datosGalletas += `
                        <option value='Por Cantidad Monetaria'>
                            Por Cantidad Monetaria
                        </option>`;

                document.getElementById("tipo_venta").innerHTML = datosGalletas;
                
                // Añadir el evento al cambio del tipo de venta
                document.getElementById("tipo_venta").addEventListener("change", function () {
                    cargarSelectGalletas(galletas, this.value); // Llamar a cargarSelectGalletas con el tipo de venta seleccionado
                });
            })
            .catch(error => {
                console.error("Error al cargar los tipos de venta:", error);
                document.getElementById("tipo_venta").innerHTML = `
                <option value='' disabled selected>
                    Error al cargar tipos de venta
                </option>`;
            });
}


function calcularTotal() {
    let precio = parseFloat(document.getElementById("precio").value) || 0;
    let cantidad = parseInt(document.getElementById("cantidad").value) || 0;
    let total = precio * cantidad;

    document.getElementById("total").value = total.toFixed(2);
}

let totalAcumulado = 0; // Variable global para acumular el total

function guardarDetalleVenta() {
    // Obtener los valores del formulario
    let tipoGalletaSelect = document.getElementById("tipoGalleta");
    let tipoGalletaTexto = tipoGalletaSelect.options[tipoGalletaSelect.selectedIndex].text;
    let precio = parseFloat(document.getElementById("precio").value);
    let cantidad = parseInt(document.getElementById("cantidad").value);
    let total = parseFloat(document.getElementById("total").value);
    let id = parseFloat(document.getElementById("tipoGalleta").value);

    if (!cantidad || cantidad <= 0) {
        Swal.fire("¡Error!", "Por favor ingresa una cantidad válida.", "error");
        return;
    }

    // Obtener la existencia de la galleta seleccionada
    const selectOption = document.querySelector(`#tipoGalleta option[value='${id}']`);
    const existencia = parseInt(selectOption.getAttribute("data-existencia"));

    // Validación de existencia
    if (cantidad > existencia) {
        Swal.fire("¡Error!", `La cantidad solicitada de ${tipoGalletaTexto} excede la existencia (${existencia}).`, "error");
        return; // Detener la ejecución si la cantidad excede la existencia
    }

    // Crear una nueva fila con botones de "Eliminar" y "Agregar"
    let nuevaFila = `
    <tr data-id="${id}">
        <td>${tipoGalletaTexto}</td>
        <td>${precio.toFixed(2)}</td>
        <td>${cantidad}</td>
        <td>${total.toFixed(2)}</td>
        <td>
            <button type="button" onclick="eliminarFila(this)">Eliminar</button>
            <button type="button" onclick="agregarFila(this)">Agregar</button>
        </td>
    </tr>`;

    // Agregar la nueva fila a la tabla
    document.getElementById("tblDetalleVenta").insertAdjacentHTML('beforeend', nuevaFila);

    // Sumar el total a la variable acumulada
    totalAcumulado += total;

    // Actualizar el total en el DOM
    document.getElementById("total-importe").innerText = `$${totalAcumulado.toFixed(2)}`;
    document.getElementById('tipo_venta').style.display = 'none';

    // Limpiar el formulario
    document.getElementById("ventaForm").reset();
    document.getElementById("precio").value = ""; // Precio es readonly, reiniciar manualmente
    document.getElementById("total").value = "";  // Total es readonly, reiniciar manualmente

    cerrarModalVenta(); // Cierra el modal si es necesario
}
function cerrarModalRegistroPago() {
    document.getElementById("modalRegistroPago").style.display = "none";
}


function cobrarVenta(conTicket, idVenta) {
    const total = parseFloat(document.getElementById("montoTotal").value);
    const pagado = parseFloat(document.getElementById("montoPagado").value);
    const cambio = parseFloat(document.getElementById("cambio").value);

    if (pagado < total) {
        Swal.fire("Error", "El monto pagado es insuficiente.", "error");
        return;
    }

    // Insertar venta (como ya está implementado)
    insertarVenta();

    if (conTicket) {

        generarTicket(total, pagado, cambio);


    }

    cerrarModalRegistroPago();
    Swal.fire("Éxito", "Venta realizada exitosamente.", "success");
}

function generarTicket(total, pagado, cambio) {
    // Crear el contenido del ticket
    let ticketContenido = `
        <html>
        <head>
            <style>
                body {
                    font-family: Helvetica, Arial, sans-serif;
                    font-size: 10px;
                    margin: 0;
                    padding: 0;
                    width: 250px;
                }
                .ticket {
                    padding: 10px;
                    text-align: left;
                    border: 1px solid #000;
                    width: 100%;
                }
                .ticket h2 {
                    margin: 0;
                    font-size: 12px;
                    text-align: center;
                }
                .ticket p {
                    margin: 2px 0;
                }
                .ticket table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                    font-size: 10px; /* Ajusta el tamaño de la fuente */
                }
                .ticket th, .ticket td {
                    border: 1px solid #000;
                    padding: 3px;
                    text-align: center;
                }
                .ticket th {
                    font-weight: bold;
                }
                .ticket .total {
                    margin-top: 10px;
                    font-weight: bold;
                    text-align: left;
                }
                .ticket .line {
                    border-top: 1px dashed #000;
                    margin: 5px 0;
                }
            </style>
        </head>
        <body>
            <div class="ticket">
                <h2>Ticket de Venta</h2>
                <p><strong>Fecha:</strong> ${new Date().toLocaleDateString()}</p>
                <p><strong>Hora:</strong> ${new Date().toLocaleTimeString()}</p>
                <div class="line"></div>
                <table>
                    <thead>
                        <tr>
                            <th>Producto</th>
                            <th>Cantidad</th>
                            <th>Precio</th>
                            <th>Importe</th>
                        </tr>
                    </thead>
                    <tbody>
    `;

    // Agregar los detalles de los productos
    const filasDetalle = document.getElementById("tblDetalleVenta").getElementsByTagName("tr");

    for (let i = 0; i < filasDetalle.length; i++) {
        const fila = filasDetalle[i];
        const tipoGalleta = fila.querySelector("td:nth-child(1)").innerText; // Descripción
        const precio = parseFloat(fila.querySelector("td:nth-child(2)").innerText); // Precio
        const cantidad = parseInt(fila.querySelector("td:nth-child(3)").innerText); // Cantidad
        const importe = parseFloat(fila.querySelector("td:nth-child(4)").innerText); // Importe

        ticketContenido += `
            <tr>
                <td>Galleta de ${tipoGalleta}</td>
                <td>${cantidad}</td>
                <td>$${precio.toFixed(2)}</td>
                <td>$${importe.toFixed(2)}</td>
            </tr>
        `;
    }

    ticketContenido += `
                    </tbody>
                </table>
                <div class="line"></div>
                <div class="total">
                    <p>Subtotal: $${total.toFixed(2)}</p>
                    <p>Total: $${total.toFixed(2)}</p>
                    <p>Pagado: $${pagado.toFixed(2)}</p>
                    <p>Cambio: $${cambio.toFixed(2)}</p>
                </div>
                <div class="line"></div>
                <p>Gracias por su compra!</p>
            </div>
        </body>
        </html>
    `;

    // Crear una ventana emergente con un tamaño adecuado
    const ventanaImpresion = window.open('', '', 'width=300,height=500,scrollbars=yes');
    ventanaImpresion.document.write(ticketContenido);
    ventanaImpresion.document.close();
}

function abrirModalRegistroPago() {
    // Obtener el valor del total acumulado y asignarlo al modal
    const totalbien = totalAcumulado || 0;

    // Asignar ese valor al campo montoTotal
    document.getElementById("montoTotal").value = totalbien;

    // Limpiar los campos montoPagado y cambio
    document.getElementById("montoPagado").value = '';
    document.getElementById("cambio").value = '';

    // Mostrar el modal
    document.getElementById("modalRegistroPago").style.display = "block";
}

function calcularCambio() {
    const total = parseFloat(document.getElementById("montoTotal").value) || 0;
    const pagado = parseFloat(document.getElementById("montoPagado").value) || 0;
    const cambio = Math.max(pagado - total, 0);
    document.getElementById("cambio").value = cambio.toFixed(2);
}

function abrirmodalmerma() {
    document.getElementById("modalMermas").style.display = "flex";
}

// Función para cerrar el modal
function cerrarmodalmerma() {
    document.getElementById("modalMermas").style.display = "none";
}

function cargarSelectGalletas2() {
    fetch("http://localhost:8081/DON_GALLETO_Ventas/api/galleta/getAll")
        .then(response => response.json())
        .then(response => {
            let galletas = response;
            let datosGalletas = `
            <option value='' disabled selected>
                Selecciona un tipo de galleta
            </option>`;

            // Filtrar y cargar solo las galletas de tipo "Unidad"
            galletas.forEach(galleta => {
                if (galleta.tipo === 'Unidad') {  // Filtrar por tipo
                    datosGalletas += `
                    <option value='${galleta.galleta}'>
                        ${galleta.galleta}
                    </option>`;
                }
            });

            // Asignar las opciones al select
            document.getElementById("tipoGalleta2").innerHTML = datosGalletas;
        })
        .catch(error => {
            console.error("Error al cargar las galletas:", error);
            document.getElementById("tipoGalleta2").innerHTML = `
            <option value='' disabled selected>
                Error al cargar galletas
            </option>`;
        });
}

function guardarMerma() {
    // Obtener los valores de la galleta, cantidad, descripción y fecha del formulario
    const nombreGalleta = document.getElementById('tipoGalleta2').value;  // Nombre de la galleta
    const cantidad = document.getElementById('cantidad2').value;  // Cantidad de galletas
    const descripcion = document.getElementById('descripcion').value;  // Descripción
    const fecha = document.getElementById('fecha').value;  // Fecha

    // Verificar que se haya seleccionado una galleta, que la cantidad no sea cero
    // y que la descripción y la fecha estén completas
    if (!nombreGalleta || cantidad <= 0 || !descripcion || !fecha) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Por favor, completa todos los campos: galleta, cantidad, descripción y fecha.'
        });
        return;
    }

    // URL del servicio REST
    const url = `http://localhost:8081/DON_GALLETO_Ventas/api/galleta/disminuirCantidad?nombreGalleta=${encodeURIComponent(nombreGalleta)}&cantidad=${cantidad}`;

    // Realizamos la solicitud GET
    fetch(url)
        .then(response => response.json()) // Convertimos la respuesta a formato JSON
        .then(data => {
            // Manejo de la respuesta del servidor
            if (data.message) {
                Swal.fire({
                    icon: 'success',
                    title: 'Éxito',
                    text: data.message // Si hay un mensaje de éxito, lo mostramos
                });
            } else if (data.error) {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Error: ' + data.error // Si hay un error, lo mostramos
                });
            }
            // Limpiar el formulario y cerrar el modal
            limpiarFormulario();
            cerrarmodalmerma();
        })
        .catch(error => {
            // Si ocurre un error en la solicitud, lo mostramos
            console.error("Error en la solicitud:", error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Hubo un error al realizar la solicitud.'
            });
        });
}

function limpiarFormulario() {
    // Limpiar los campos del formulario
    document.getElementById('tipoGalleta2').value = '';
    document.getElementById('descripcion').value = '';
    document.getElementById('cantidad2').value = '';
    document.getElementById('fecha').value = '';
}



function eliminarFila(boton) {
    // Eliminar la fila correspondiente
    let fila = boton.parentNode.parentNode;
    fila.remove();
    document.getElementById('tipo_venta').style.display = 'block';
}

function agregarFila(boton) {
    const selectTipoVenta = document.getElementById('tipo_venta');
    const tipoVentaSeleccionada = selectTipoVenta.value;

    // Asignar la selección del tipo de venta al input correspondiente (si es necesario)
    document.getElementById('tipo_venta').value = tipoVentaSeleccionada;

    // Mostrar el select en lugar de un modal (suponiendo que el select está oculto inicialmente)
    document.getElementById('tipo_venta').style.display = 'block';

    // Enfocar el select
    document.getElementById('tipo_venta').focus();
}

// Funciones para abrir y cerrar el modal de ventas del día
function cerrarModalVENTAS() {
    document.getElementById('modalVENTAS').style.display = 'none';
}

function abrirModalventas() {
    document.getElementById('modalVENTAS').style.display = 'flex';
}

function cerrarModalVenta() {
    document.getElementById('modalVenta').style.display = 'none';
}

function abrirModalVenta() {
    const selectTipoVenta = document.getElementById('tipo_venta');
    const tipoVentaSeleccionada = selectTipoVenta.value;

    if (tipoVentaSeleccionada) {
        // Asignar el valor seleccionado al campo 'Tipo de venta' en el modal
        document.getElementById('tipoVenta').value = tipoVentaSeleccionada;

        // Mostrar el modal
        document.getElementById('modalVenta').style.display = 'block';
    }
}
function redireccionar(url) {
    window.location.href = "index.html";
}