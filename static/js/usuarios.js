function buscar_empleados() {
    const buscar_texto = document.getElementById('buscar').value.toLowerCase();
    const filas = document.querySelectorAll('#tblusuarios tr');

    filas.forEach(fila => {
        const nombre = fila.cells[0].textContent.toLowerCase();
        const puesto = fila.cells[1].textContent.toLowerCase();
        const telefono = fila.cells[2].textContent.toLowerCase();
        const estatus = fila.cells[3].textContent.toLowerCase();

        if (nombre.includes(buscar_texto) || 
            puesto.includes(buscar_texto) || 
            telefono.includes(buscar_texto) || 
            estatus.includes(buscar_texto)) {
            fila.style.display = '';
        } else {
            fila.style.display = 'none';
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".btn-eliminar, .btn-reactivar").forEach(boton => {
        boton.addEventListener("click", function (event) {
            event.preventDefault();

            const url = this.getAttribute("href");
            const accion = this.classList.contains("btn-eliminar") ? "eliminar" : "reactivar";
            
            Swal.fire({
                title: `¿Estás seguro de ${accion} este empleado?`,
                text: "¡Cuidado!",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#a65323",
                cancelButtonColor: "#f5c19b",
                confirmButtonText: "Sí, proceder",
                cancelButtonText: "Cancelar"
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.href = url;
                }
            });
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const btnGuardar = document.querySelector(".btn-guardar-cambios");

    if (btnGuardar) {
        btnGuardar.addEventListener("click", function (event) {
            event.preventDefault();

            Swal.fire({
                title: "¿Estás seguro?",
                text: "Se modificarán los datos del empleado.",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#a65323",
                cancelButtonColor: "#f5c19b",
                confirmButtonText: "Sí, guardar cambios",
                cancelButtonText: "Cancelar"
            }).then((result) => {
                if (result.isConfirmed) {
                    btnGuardar.closest("form").submit();
                }
            });
        });
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const btnGuardarEmpleado = document.querySelector(".btn-guardar-empleado");

    if (btnGuardarEmpleado) {
        btnGuardarEmpleado.addEventListener("click", function (event) {
            event.preventDefault(); 

            Swal.fire({
                title: "¿Estás seguro?",
                text: "Se registrará un nuevo empleado.",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#a65323",
                cancelButtonColor: "#f5c19b",
                confirmButtonText: "Sí, registrar",
                cancelButtonText: "Cancelar"
            }).then((result) => {
                if (result.isConfirmed) {
                    btnGuardarEmpleado.closest("form").submit();
                }
            });
        });
    }
});
