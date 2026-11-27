# Revisión de estabilidad — 27 de noviembre de 2026

Entorno local: Windows, Python 3.12.7, Tcl/Tk 8.6 y ReportLab 4.5.1.
Los ensayos de biblioteca emplean carpetas temporales, no los ejercicios personales.

## Comprobaciones realizadas

| Área | Resultado |
|---|---|
| Pruebas automatizadas | 125 pruebas aprobadas, con ReportLab disponible |
| Cálculos | Banco de 1 000 casos con referencias independientes, ejemplos originales y entradas inválidas |
| Persistencia | Guardado, reapertura, edición, copias, archivos dañados y fallos de disco |
| Entradas | Ayudas para cada campo, 1 000 casos válidos, tipos incorrectos, límites, relaciones entre campos y corrección desde Tk en los 10 métodos |
| Interfaz general | Ejemplos, navegación guiada y directa, borradores, biblioteca, informes y gráficos |
| Recuadros de fórmulas | Columnas proporcionadas, apilado, actualización, copia y términos de sustituciones |
| Adaptación | Anchos grandes y pequeños, temas Claro/Oscuro/Aurora y escala aumentada; Aurora sin Pillow |
| Navegación mixta | 180 acciones, sin errores de interfaz |
| Sin Pillow | Comprobación general de interfaz aprobada con `DIROPE_SIN_PILLOW=1` |
| Copia limpia de Windows | Lanzador y diagnóstico probados en una ruta con espacios y acento. Comprobación de interfaz desde otro directorio sin paquetes opcionales (`python -S`) |
| Preparación de paquetes | Se verificaron los siete archivos y sus hashes. Instalación real sin índice de pip en un entorno limpio de Windows x64 con Python 3.12, `pip check` y comprobación de interfaz aprobados. El consentimiento, la cancelación y el modo básico se prueban de forma automatizada. |
| No conformes | Desplegable real en los tres temas; vacío rechazado, cero explícito y equivalencia de 5 unidades o 4 % sobre 125 |
| Exportación | HTML y PDF de los 10 métodos y ejemplos originales; contenido escapado y explicaciones extensas paginadas |
| Protección de exportaciones | Fallos simulados de sincronización, reemplazo y generación conservan el documento anterior |
| Contraste | 162 pares comprobados, sin fallos |
| Fondo Aurora | 441 puntos del degradado: texto ≥ 7:1 y controles ≥ 3:1; redimensionado, caché, limpieza de tareas y alternativa sin Pillow |
| Sintaxis | Compilación de los archivos Python sin errores |

Una ejecución general de interfaz superó su límite de 120 segundos durante los cambios de tamaño. Una repetición con diagnóstico terminó correctamente; esto no acredita un objetivo formal de rendimiento.

La revisión de entradas detectó un ciclo de ajuste del ancho de los mensajes en páginas ocultas. Se corrigió evitando recalcular el ancho de texto hasta que el control es visible, y las pruebas de cambio de método y recuperación de entradas pasan. La comprobación general, su variante sin Pillow y las 180 acciones mixtas se repitieron correctamente tras estos cambios. Aurora se inspeccionó también mediante una captura de su propia ventana con mensajes de entrada inválida.

La revisión del degradado amplió el fondo al área de trabajo, conservando tarjetas blancas y botones principales azul oscuro. Se repitieron las 110 pruebas, las comprobaciones generales con y sin Pillow, las 180 acciones mixtas y el contraste de las tres paletas. Se inspeccionó una captura de la propia ventana con el fondo actualizado. Fuentes y decisiones en [Aurora](diseno/AURORA.md).

La revisión de conformidad corrigió una excepción reproducible al introducir exponentes fuera de rango. Ahora aparece un aviso de campo en vez del diálogo genérico. Se añadió diagnóstico local y una comprobación de instalación completa en el lanzador de Windows. No se reprodujo el fallo del equipo que envió la captura al elegir el método: para confirmar su causa falta el `registro.log` de ese equipo.

## Protección y mantenimiento

- Núcleo, formato e informes separados de Tkinter; no se modificaron las fórmulas de cálculo.
- Ejecución local sin internet. ReportLab sigue siendo opcional y no se añadieron dependencias.
- Informes escritos en un temporal junto al destino y reemplazados solo al completarse.
- Descripciones centralizadas y pruebas de cobertura de términos en las fórmulas actuales. Los símbolos nuevos requieren descripción explícita.
- Integración continua ampliada para ejecutar PDF, interfaz y contraste en Windows. El resultado remoto solo podrá comprobarse tras publicar los cambios.

## Pendiente o fuera de esta verificación

- La prueba intensiva anterior de los 1 000 ejercicios por Tk fue cancelada por reinicio del servidor, no aprobada. En esta revisión se validó el banco completo sin interfaz y la corrección de entradas por Tk en los 10 métodos, no se afirma una nueva ejecución intensiva completa por Tk.
- Inspección visual manual de todas las páginas de exportación y combinaciones de pantalla.
- Validación local en macOS y Linux, lectores de pantalla y medición formal de cobertura y rendimiento.
- Ejecutable sin Python y exportación nativa a Word/Excel: siguen pendientes según `VIABILIDAD.md`.

Estas comprobaciones no demuestran ausencia de todos los errores posibles. Comandos reproducibles en el [README](../README.md#verificación).
