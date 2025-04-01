function buscar_proveedores() {
    const buscar_texto = document.getElementById('buscar').value.toLowerCase();
    const filas = document.querySelectorAll('#tblProveedores tr');

    filas.forEach(fila => {
        const proveedor = fila.cells[0].textContent.toLowerCase();
        const direccion = fila.cells[1].textContent.toLowerCase();
        const fechaInicio = fila.cells[2].textContent.toLowerCase();
        const rfc = fila.cells[3].textContent.toLowerCase();
        const email = fila.cells[4].textContent.toLowerCase();

        if (proveedor.includes(buscar_texto) || 
            direccion.includes(buscar_texto) || 
            fechaInicio.includes(buscar_texto) || 
            rfc.includes(buscar_texto) ||
            email.includes(buscar_texto)) {
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
                title: `¿Estás seguro de ${accion} este proveedor?`,
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
                text: "Se modificarán los datos del proveedor.",
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
    const btnGuardarproveedor = document.querySelector(".btn-guardar-proveedor");

    if (btnGuardarproveedor) {
        btnGuardarproveedor.addEventListener("click", function (event) {
            event.preventDefault(); 

            Swal.fire({
                title: "¿Estás seguro?",
                text: "Se registrará un nuevo proveedor.",
                icon: "warning",
                showCancelButton: true,
                confirmButtonColor: "#a65323",
                cancelButtonColor: "#f5c19b",
                confirmButtonText: "Sí, registrar",
                cancelButtonText: "Cancelar"
            }).then((result) => {
                if (result.isConfirmed) {
                    btnGuardarproveedor.closest("form").submit();
                }
            });
        });
    }
});
