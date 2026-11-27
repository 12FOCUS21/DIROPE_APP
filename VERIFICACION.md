# Revisión de estabilidad — 26 de noviembre de 2026

Entorno local: Windows, Python 3.12.7, Tcl/Tk 8.6 y ReportLab 4.5.1.
Los ensayos de biblioteca emplean carpetas temporales, no los ejercicios personales.

## Comprobaciones realizadas

| Área | Resultado |
|---|---|
| Pruebas automatizadas | 96 pruebas aprobadas, con ReportLab disponible |
| Cálculos | Banco de 1 000 casos con referencias independientes, ejemplos originales y entradas inválidas |
| Persistencia | Guardado, reapertura, edición, copias, archivos dañados y fallos de disco |
| Interfaz general | Ejemplos, navegación guiada y directa, borradores, biblioteca, informes y gráficos |
| Recuadros de fórmulas | Columnas proporcionadas, apilado, actualización, copia y términos de sustituciones |
| Adaptación | Anchos grandes y pequeños, temas Claro/Oscuro y escala aumentada |
| Navegación mixta | 180 acciones, sin errores de interfaz |
| Sin Pillow | Comprobación general de interfaz aprobada con `DIROPE_SIN_PILLOW=1` |
| Exportación | HTML y PDF de los 10 métodos y ejemplos originales; contenido escapado y explicaciones extensas paginadas |
| Protección de exportaciones | Fallos simulados de sincronización, reemplazo y generación conservan el documento anterior |
| Contraste | 109 pares comprobados, sin fallos |
| Sintaxis | Compilación de los archivos Python sin errores |

Una ejecución general de interfaz superó su límite de 120 segundos durante los cambios de tamaño. Una repetición con diagnóstico terminó correctamente; esto no acredita un objetivo formal de rendimiento.

## Protección y mantenimiento

- Núcleo, formato e informes separados de Tkinter; no se modificaron los cálculos.
- Ejecución local sin internet. ReportLab sigue siendo opcional y no se añadieron dependencias.
- Informes escritos en un temporal junto al destino y reemplazados solo al completarse.
- Descripciones centralizadas y pruebas de cobertura de términos en las fórmulas actuales. Los símbolos nuevos requieren descripción explícita.
- Integración continua ampliada para ejecutar PDF, interfaz y contraste en Windows. El resultado remoto solo podrá comprobarse tras publicar los cambios.

## Pendiente o fuera de esta verificación

- La prueba intensiva de los 1 000 ejercicios por Tk está iniciada, pero todavía no tiene resultado confirmado para esta entrega.
- Inspección visual manual de todas las páginas de exportación y combinaciones de pantalla.
- Validación local en macOS y Linux, lectores de pantalla y medición formal de cobertura y rendimiento.
- Ejecutable sin Python y exportación nativa a Word/Excel: siguen pendientes según `VIABILIDAD.md`.

Estas comprobaciones no demuestran ausencia de todos los errores posibles. Comandos reproducibles en `README.md`.
