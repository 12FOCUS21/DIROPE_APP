# Viabilidad y decisiones

## Dictamen

La versión 1.0 es técnicamente viable como aplicación local con Python 3.10+ y Tkinter. Son operaciones pequeñas y deterministas; no requieren servidor, base de datos ni conexión. No se han medido todavía los tiempos del requisito de menos de un segundo.

El equipo actual tiene Windows, Python 3.12.7 y Tkinter 8.6. La compatibilidad con macOS exige una prueba real y un empaquetado propio de ese sistema.

## Mejoras implementadas

1. Inicio local sin paquetes externos, sin instalación del proyecto y con rutas independientes del directorio desde donde se abre.
2. Núcleo puro y registro declarativo de formularios: los módulos nuevos no necesitan cambiar los anteriores.
3. Diferenciación entre productividad laboral por hora y por costo, corrigiendo la ambigüedad de T3.
4. Validación adicional de NaN, infinitos, booleanos, agrupación de miles y resultados desbordados.
5. Tolerancia de personal explícita y visible; se conserva como supuesto, no como regla académica confirmada.
6. Pruebas con biblioteca estándar y registro de errores fuera del código, en una carpeta de usuario escribible.
7. Flujo de cinco etapas separadas, problemas con datos propios, revisión explícita del método y desarrollo paso a paso antes de presentar resultados.
8. Navegación con transiciones cancelables, gráficos Canvas animados y opción de desactivar el movimiento, sin dependencias adicionales.

## Cambios propuestos

| Prioridad | Cambio | Motivo |
|---|---|---|
| Alta | Confirmar tolerancia de personal y añadir opción «techo estricto» | Evitar subestimar capacidad cuando la productividad es exacta. |
| Alta | Escenarios y calidad con tablas antes/después | Completar RF-03 y RF-05 y llevar T6 a la interfaz. |
| Alta | JSON con versión de esquema y validación | Conservar problemas e intercambiarlos entre compañeros sin depender de Excel. |
| Alta | Unidades, moneda y período explícitos | Evitar comparaciones dimensionalmente incompatibles. |
| Alta | pytest y medición de cobertura | Medir el objetivo de 90 %; ya existe una configuración de pruebas unittest en GitHub Actions. |
| Media | Word y Excel como dependencias separadas de la apertura básica | Mantener una instalación mínima; añadir python-docx y openpyxl previo aviso. |
| Media | Ejecutable Windows con PyInstaller | Doble clic sin instalar Python; construir en Windows, probar antivirus y tamaño. |
| Media | Prueba manual de accesibilidad y equipo macOS | El funcionamiento en Windows no prueba la compatibilidad completa. |

## Límites de la entrega inicial

No hay todavía exportaciones, persistencia, historial, instalador ni los cinco módulos completos. El núcleo contempla los seis casos, pero la interfaz solo tres módulos. El rediseño incorpora inicio, navegación lateral, cinco etapas guiadas, indicadores y gráficos con Canvas; ver `DISENO_INTERFAZ.md`. La identificación depende de la herramienta elegida y de datos estructurados: no interpreta automáticamente enunciados ni resuelve temas ajenos a esos módulos. No se ha medido la cobertura del 90 %. Las pruebas actuales usan unittest, no pytest.approx; se compara con tolerancia equivalente de 1e-4 para los resultados publicados.

No se copia el documento original al repositorio por defecto: incluye nombres y contexto académico. Se ha resumido el alcance técnico en estos documentos para poder colaborar sin publicar esa información accidentalmente.
