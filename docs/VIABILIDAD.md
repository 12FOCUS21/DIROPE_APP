# Viabilidad y requisitos pendientes

DIROPE Calc usa Python y Tkinter. El motor de cálculo, el análisis, el formato numérico y los informes HTML y PDF son independientes de Tkinter. El registro de módulos conserva los tres puntos de entrada existentes y los datos anteriores siguen admitidos por sus funciones de cálculo.

## Rediseño implementado

- Inicio con tres tarjetas, historial real y navegación lateral dentro de los módulos.
- Comparación multifactor de hasta tres escenarios en total y costos directos.
- Calidad como producción conforme o valor de producción por categorías.
- Meta de capacidad directa o por crecimiento, plantilla opcional y techo estricto en el flujo actual.
- Procedimiento guiado y acceso directo a resultados con el mismo cálculo.
- Borradores durante la sesión y guardado local en JSON versionado.
- Informes copiables y exportación local a HTML y PDF A4. La exportación PDF usa ReportLab como dependencia opcional.

Las funciones heredadas de capacidad conservan el ajuste de personal documentado para sus llamadores. La interfaz utiliza el cálculo explícito con techo y personal incremental donde corresponde.

## Pendientes de la versión 1.0

| Requisito | Estado |
|---|---|
| Exportación nativa a Word y Excel | Pendiente |
| Ejecutable sin instalación de Python | Pendiente |
| Verificación en macOS, lectores de pantalla y escalado de Windows | Pendiente |
| Medición formal de cobertura y del objetivo de rendimiento | Pendiente |

Las comparaciones usan una unidad y moneda comunes declaradas por el usuario. Las conversiones son manuales. La aplicación implementa modelos específicos de productividad y capacidad y toma las cifras de los campos del formulario.
