# GalleteriaLaTradicionalVF

Este proyecto fue elaborado por 5 estudiantes de desarrollo de software dividiendo de esta manera el proyecto, donde cada uno se hizo responsable de su area encargada, donde cada uno realizo sus archivos de controladores en pyhton usando flask, vistas (HTML y CSS), forms, orm y uso de Javascript.

*El contenido de archivos sencibles fue eliminado, remplazado por plantillas o instrucciones para que se pueda ejecutar de manera correcta, ademas de indicar que se debe de instalar para poder hacer funcionar este proyecto.*

Este proyecto se desarrollo en:
*  Visual Studio Code 1.103.2
*  Node.js 22.17.0
*  MySQL Workbench 8.0 CE

En cuanto a las areas encargadas por estudiante son:

# [Oscar Gomez](https://github.com/Oscar-Gomez-Luna)
  * **En el apartado de administrador:**
    * CRUD de proveedores.
    * CRUD de usuarios (empleados).
  * **Ventas:**
    * Ver e imprimir ticket de la venta.
    * Realizar ventas del local.
    * Realizar ventas del portal.
    * Cobrar ventas del portal.
    * Detalles de la venta.
    * Cambiar estatus de la orden a entregado una vez que se cobra.
    * Saber si ya esta lista la orden.
    * Corte de caja.
    * Merma de galletas.
  * **Logs:**
    * Errores.
    * Auditoria.

# [Carlos Lopez](https://github.com/IDGS-901-22002224)
  * **Login:**
    * *Seguridad de inicio de sesión:*
      * Captcha.
  * **Registro:**
    * *Seguridad de registro:*
      * Confirmación de dos pasos via correo electronico.
      * Prohibir contraseñas inseguras.
      * Hashear contraseñas en el registro.
  * **Dashboard:**
    * Grafico de lineas de ventas diarias en relacion con el dinero en los ultimos 7 días.
    * Grafico de barras de las galletas más vendidas.
    * Grafico de pastel de las presentaciones más vendidas.

# [Diego Landin](https://github.com/nombre-de-usuario)
  * **En el apartado de administrador:**
    * CRUD de usuarios (clientes).
    * *CRUD de recetas:*
      * Se pueden agregar todos los campos de ingredientes como se necesiten.
      * Permite subir una foto (de como queda la galleta).
  * **El portal del cliente:**
    * Home para el usuario.
    * Realizar pedidos como una función de carrito de compras.
    * Ver historial de pedidos.
    * Ver detalles de pedidos.
  * **Pagina de error 404.**
  * **Home principal.**

# [Yael Lopez](https://github.com/IDGS-901-22001379)
  * **Producción:**
    * Empaquetar galletas dependiendo su presentación.
    * Alertas de preparación proximas a terminarse.
    * Orden de producción que crea su lote.
    * Merma de galletas.
    * Merma de insumos.
  * **Producto terminado (Galletas):**
    * Galletas listas y sus diferentes presentaciones.
    * Asociar galletas con recetas registradas.
    * Agregar una galleta nueva con stock 0.
    * Merma de galletas.

# [Angel Ascencio](https://github.com/Angel-Ascencio)
  * **Insumos:**
      * Alertas de caducidad y existencia.
      * Registrar nuevos insumos.
      * Pagos pendientes con proveedores.
      * Orden de compra de insumos a proveedores como una función de carrito de compras.
      * Insumos comprados con fechas de caducidad.
      * Merma de insumos.
  * **Ordenes de produccion del portal:**
      * Información de cuantas galletas se necesitan.
      * Calculos de insumos a ocupar en relación a la receta.
      * Al terminar una orden cambiar estatus a terminada.
      * Si una orden pasa de su fecha de entrega se cambia su estatus y se envia al stock total.
      * Si se puede cubrir el stock total lo marca como terminado.
      * Merma de galletas.
      * Merma de insumos.
