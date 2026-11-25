# DIROPE Calc

Aplicación de escritorio para cálculos de productividad y dirección de operaciones. Funciona localmente con Python 3.10 o superior y Tcl/Tk.

## Inicio rápido

En Windows, abre `Abrir_programa.bat`. También puedes ejecutar `python iniciar.py` desde esta carpeta. En macOS, usa `python3 iniciar.py` con una instalación de Python que incluya Tk. La versión actual se verificó en Windows.

En **Inicio**, abre una de las tres tarjetas o continúa un cálculo guardado. Cada módulo incluye ejemplos editables en **Planteamiento**. En **Datos**, usa **Ver resultado** cuando las entradas sean válidas o avanza por Identificación y Desarrollo para revisar el procedimiento. Cambiar de módulo conserva el borrador de cada uno durante la sesión.

| Módulo | Cálculos disponibles |
|---|---|
| Un factor | Productividad individual, comparación, producción o recurso requerido, y productividad ajustada por conformidad. |
| Multifactor | Costos unitarios y directos, composición de costos, productividad con hasta dos alternativas frente al escenario inicial, y valor producido por categorías de calidad. |
| Capacidad y personal | Meta directa o crecimiento porcentual, horas-persona, personal requerido y diferencia respecto de la capacidad disponible. |

Usa punto decimal y espacios para agrupar miles, como `1 500.25`. Las comparaciones comparten unidades y moneda. Mantén el mismo período para la producción y los recursos de cada escenario. La aplicación usa los datos estructurados que ingresas y el enunciado es opcional.

Las horas por trabajador y las horas-persona totales son variables distintas. El personal requerido en la interfaz se redondea hacia arriba. Si registras una plantilla, la diferencia de personal se calcula frente a ella. Si indicas la producción actual, también puedes ver las horas adicionales respecto de esa producción.

En **Resultados** puedes volver al procedimiento, copiar el informe, exportar a HTML o PDF y guardar el cálculo. **Administrar** en Inicio permite abrir y eliminar ejercicios. El historial guarda las entradas en archivos JSON versionados y las vuelve a calcular al abrir. En Windows se guarda en `%LOCALAPPDATA%/DIROPE Calc/calculos`, en macOS en `~/Library/Application Support/DIROPE Calc/calculos` y en Linux bajo `XDG_DATA_HOME` o `~/.local/share`.

Para exportar PDF A4, instala la dependencia opcional ReportLab una vez:

```text
python -m pip install -r requirements.txt
```

La aplicación y la exportación funcionan localmente después de instalarla. Los cálculos, el historial, la copia y la exportación HTML funcionan con Python y Tcl/Tk.

## Verificación

```text
python -m unittest discover -s pruebas -v
python iniciar.py --comprobar-interfaz
```

La comprobación de interfaz recorre nueve ejemplos, datos propios, cambios de módulo, edición, duplicación de insumos, acceso directo a resultados, guardado y reapertura, informes y gráficos. Los requisitos pendientes de la versión 1.0 se registran en `VIABILIDAD.md`.

Los ejemplos 1.14 y 1.17 usan los datos de Heizer y Render, *Principios de administración de operaciones*, 7.ª edición, capítulo 1. [Enunciados del capítulo](https://matrixeducacion.com/wp-content/uploads/2023/07/Libro-5-Heizer-and-Render-Principios-de-Operaciones.pdf)

Consulta `CONTRIBUTING.md` para colaborar. Conserva los documentos privados del curso fuera de las publicaciones del proyecto.
