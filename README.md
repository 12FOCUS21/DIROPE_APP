# DIROPE Calc

Aplicación local en español para Dirección de Operaciones. **Versión inicial, no versión 1.0 completa.** No usa internet, cuentas ni servicios externos para calcular.

## Abrir en Windows

1. Se necesita Python 3.10 o superior con Tcl/Tk. En este equipo se detectó Python 3.12.7 y Tkinter 8.6.
2. Haz doble clic en **`Abrir_programa.bat`** dentro de esta carpeta.
3. En **Inicio**, elige una herramienta o pulsa **Explorar un ejemplo guiado**. Puedes escribir un problema nuevo o cargar y modificar un ejemplo opcional.
4. Recorre **Planteamiento → Datos → Identificación → Desarrollo → Resultados**. Confirma el método y sus supuestos antes de desarrollar; avanza por cada paso para llegar a la presentación final.

Alternativa desde una terminal abierta en esta carpeta: `python iniciar.py`. No hace falta ejecutar `pip install`. Mantén la carpeta `src` junto a `iniciar.py`.

En macOS: instala Python con soporte Tk y ejecuta `python3 iniciar.py`. Para usar el lanzador, dale permiso una vez con `chmod +x Abrir_programa.command`. macOS aún no se ha probado.

## Qué incluye

- Productividad de un factor: dos escenarios, diferencia y porcentaje.
- Multifactor: filas de insumos que se añaden o quitan, costos, productividad por hora y por costo laboral.
- Capacidad: crecimiento porcentual, horas y personal; muestra el ajuste a personas enteras.
- Cinco ejemplos precargados (T1, T2, T3, T4 inicial y T5), problemas con datos propios, decimales configurables y copia del informe completo.
- Cinco etapas separadas: enunciado y objetivo, datos conocidos, método propuesto con fórmulas y supuestos, desarrollo paso a paso y presentación final con indicadores, interpretación y gráficos. Puedes volver al inicio sin perder los datos de la sesión.
- Efectos de puntero, transiciones suaves entre pantallas y pasos, indicador de avance y barras animadas; desmarca **Efectos** para quitar el movimiento. Usa Tab para recorrer controles y Alt+Inicio para regresar.
- Validación de vacíos, negativos, divisiones por cero, texto, infinitos y desbordamientos.

Usa punto decimal. Los espacios solo se admiten como agrupadores de miles: `1 500.25`. En multifactor todos los costos deben estar en la misma moneda; esta versión usa `$` como símbolo. Marca **Horas** únicamente si la cantidad corresponde a horas laborales. Los períodos deben coincidir.

La identificación propone el método de la herramienta que elegiste y valida sus datos estructurados. **No interpreta automáticamente el enunciado ni extrae sus cifras.** Los problemas del profesor pueden resolverse si corresponden a una de las tres herramientas actuales; otros temas siguen pendientes. Cambiar el enunciado o los datos invalida el resultado anterior y exige revisar el análisis.

**Corrección T3:** 65 / 520 = 0.125 alfombras/h; 65 / 6 760 = 0.0096154 alfombras/$ laboral. Se muestran ambas razones por separado.

**Supuesto de personal pendiente de confirmar:** si el valor está a una distancia de hasta 0.01 de un entero positivo, se toma ese entero; si no, se redondea hacia arriba. Por ejemplo, 5.0001 → 5. No usar este ajuste como garantía de capacidad con datos exactos.

## Pruebas y errores

Desde la carpeta del proyecto:

```text
python -m unittest discover -s pruebas -v
python iniciar.py --comprobar-interfaz
```

Los seis casos se comprueban en el núcleo. T6 todavía no tiene formulario. Se usa `unittest` para no instalar dependencias; la migración a pytest y la medición del objetivo de cobertura del 90 % están pendientes.

Errores inesperados: `%LOCALAPPDATA%\DIROPE Calc\registro.log` en Windows; `~/DIROPE Calc/registro.log` en macOS. No se guarda automáticamente el trabajo: copia el procedimiento antes de cerrar.

## Pendientes para 1.0

Escenarios vinculados, formulario de calidad/T6, meta directa de capacidad, unidades de producción editables en multifactor, Word/Excel, guardar/abrir JSON, historial y ejecutable sin Python. Consulta `VIABILIDAD.md`. El criterio del rediseño y sus fuentes están en `DISENO_INTERFAZ.md`.

## Colaboración

Consulta `CONTRIBUTING.md`. No publiques datos personales, documentos privados del curso ni archivos de configuración con credenciales.
