# Descargar y abrir DIROPE Calc

**[Descargar DIROPE-Calc.zip](https://github.com/12FOCUS21/DIROPE_APP/releases/latest/download/DIROPE-Calc.zip)** · [Versiones publicadas](https://github.com/12FOCUS21/DIROPE_APP/releases)

1. Instala **Python 3.10 o superior con Tcl/Tk** si aún no lo tienes. En Windows puedes obtenerlo en [python.org](https://www.python.org/downloads/windows/). El ZIP no es un instalador de Python.
2. Elige **Extraer todo** y abre la carpeta `DIROPE Calc`. No abras el lanzador dentro del ZIP.
3. En Windows, ejecuta `Abrir_programa.bat`. En macOS o Linux, usa `python3 preparar.py` desde la carpeta extraída.
4. Si necesitas paquetes adicionales, el lanzador te dirá cuáles son, para qué sirven y si requiere internet. Instala solo con **Sí**. Con **No** puedes calcular, usar tu biblioteca y exportar HTML sin instalar paquetes.

En Windows x64 con CPython 3.10–3.14, el ZIP incluye los paquetes para instalar sin conexión. Si ya usas DIROPE, puedes extraer esta copia en otra carpeta: los ejercicios guardados residen en la carpeta de datos, no en la carpeta del programa.

## Si algo no abre

- Comprueba que extrajiste `iniciar.py`, `preparar.py`, `src/` y `dependencias/` junto al lanzador.
- Usa `Abrir_programa.bat --diagnostico` en Windows, o `python3 iniciar.py --diagnostico` en macOS/Linux. Dentro de la app está en **Ajustes → Información y diagnóstico**.
- Si aparece un error al pulsar un botón, anota la acción y adjunta el fragmento reciente de `registro.log`. El diagnóstico indica la ruta. No compartas la carpeta de datos completa.
