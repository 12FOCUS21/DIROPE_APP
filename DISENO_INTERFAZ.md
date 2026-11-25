# Diseño de interfaz

La referencia de Inicio en `INTERFACES/` guía los colores, la cabecera y las tarjetas. La barra lateral azul marino aparece dentro de los módulos. Inicio utiliza todo el ancho para las tres tarjetas y los cálculos guardados.

- **Planteamiento.** Título y enunciado opcionales, selector de cálculo y ejemplos editables.
- **Datos.** Campos según el modo. La vista previa comparte el resultado con el flujo guiado y señala qué entrada necesita revisión. La tabla multifactor permite cambiar de escenario, duplicar el inicial y desplazarse horizontalmente cuando las columnas exceden el ancho.
- **Identificación y desarrollo.** Datos utilizados y supuestos, seguidos por el procedimiento principal. El detalle desplegable conserva los costos individuales y demás cálculos auxiliares.
- **Resultados.** Respuesta principal, indicadores pertinentes, gráfica cuando hay datos e interpretación. Desde esta etapa se accede al procedimiento, copia, PDF, HTML y guardado.

Las entradas válidas habilitan **Ver resultado**. Editar los datos invalida el resultado anterior. Cambiar de módulo conserva los borradores. Los ejercicios guardados conservan las entradas en JSON y se recalculan al abrirlos.

Tab y Shift+Tab recorren los controles. Enter activa la acción correspondiente y Alt+Inicio regresa al inicio. La animación es opcional y empieza desactivada.

La comprobación de Tkinter cubre ventanas de 960 × 600 y 1280 × 760 en Windows y simula un aumento del 25 % en la escala de Tk. macOS, lectores de pantalla y otros ajustes de pantalla requieren validación adicional.
