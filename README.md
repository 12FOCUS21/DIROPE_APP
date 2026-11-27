# DIROPE Calc

Aplicación de escritorio para cálculos de productividad y dirección de operaciones. Funciona localmente con Python 3.10 o superior y Tcl/Tk.

> **[↓ Descargar DIROPE Calc (ZIP)](https://github.com/12FOCUS21/DIROPE_APP/releases/latest/download/DIROPE-Calc.zip)** · [Versiones publicadas](https://github.com/12FOCUS21/DIROPE_APP/releases)
>
> Extrae el ZIP completo y abre `Abrir_programa.bat` en Windows. No necesitas Git. El ZIP incluye los paquetes para Windows x64; **Python con Tkinter se instala por separado**.

**Recursos:** [Guía de descarga e instalación](docs/INICIO_RAPIDO.md) · [Índice de documentación](docs/README.md) · [Ejemplos](ejemplos/) · [Contribuir](CONTRIBUTING.md)

## Inicio rápido

En Windows, abre `Abrir_programa.bat`. En macOS o Linux puedes usar `python3 preparar.py` con una instalación de Python que incluya Tk. La versión actual se verificó en Windows. `python iniciar.py` sigue disponible para abrir la aplicación directamente, sin asistente de instalación.

Si descargaste el ZIP de GitHub, **extrae la carpeta completa** antes de abrir la aplicación. No ejecutes el `.bat` dentro del ZIP ni lo copies por separado: debe estar junto a `iniciar.py` y `src/`. En Windows, el lanzador verifica Python 3.10 o superior con Tkinter. Pillow no es obligatorio y ReportLab solo es necesario para exportar PDF directamente.

El lanzador comprueba que Tk abra y que se puedan cargar las versiones de Pillow, ReportLab y charset-normalizer. **Solo si faltan o son incompatibles**, indica qué versiones se instalarían, para qué sirve cada paquete y si se usará internet. Selecciona **Sí** para autorizar la creación de un entorno local (`.venv-dirope/`) junto al programa. **No** abre el modo básico —cálculos, historial y HTML— sin instalar ni descargar nada. Si el entorno ya pasa la comprobación, no vuelve a instalar.

El repositorio incluye los paquetes para **Windows x64 con CPython 3.10–3.14**, que se instalan sin internet y con verificación SHA-256. En otras plataformas, o si faltan los archivos incluidos, el lanzador puede ofrecer descargarlos de PyPI con autorización. Python con Tcl/Tk se instala por separado; el lanzador no lo instala ni requiere permisos de administrador. Si la carpeta del programa no admite escritura, extráela a una carpeta propia, como Documentos.

En **Inicio**, abre una de las tres tarjetas o continúa un cálculo guardado. Cada módulo incluye ejemplos editables en **Planteamiento**. En **Datos**, usa **Ver resultado** cuando las entradas sean válidas o avanza por Identificación y Desarrollo para revisar el procedimiento. Cambiar de módulo conserva el borrador de cada uno durante la sesión.

| Módulo | Cálculos disponibles |
|---|---|
| Un factor | Productividad individual, comparación, producción o recurso requerido, y productividad ajustada por conformidad. |
| Multifactor | Costos unitarios y directos, composición de costos, productividad con hasta dos alternativas frente al escenario inicial, y valor producido por categorías de calidad. |
| Capacidad y personal | Meta directa o crecimiento porcentual, horas-persona, personal requerido y diferencia respecto de la capacidad disponible. |

Usa punto decimal y espacios para agrupar miles, como `1 500.25`. Las comparaciones comparten unidades y moneda. Mantén el mismo período para la producción y los recursos de cada escenario. La aplicación usa los datos estructurados que ingresas y el enunciado es opcional.

### Apariencia clara u oscura

En la cabecera, **Tema → Claro / Oscuro** cambia la apariencia al instante, sin reiniciar ni perder entradas o resultados. Ambos temas distinguen cabecera, área de trabajo y tarjetas con distintos azules; el verde identifica resultados y el ámbar, notas y supuestos. La preferencia queda en `ajustes/preferencias.json`, separada de los ejercicios. Los diálogos de archivos y la barra de título conservan el aspecto del sistema operativo; las exportaciones usan su propio diseño de impresión.

También puedes elegir **Tema → Aurora**: fondo ambiental lavanda–cian que se aclara hacia abajo, tarjetas blancas, texto azul tinta y acciones principales azul oscuro. El degradado ocupa el entorno del contenido, no solo una banda decorativa; los campos permanecen sobre superficies opacas. El texto mantiene alto contraste. Los tres temas se conservan al volver a abrir la aplicación. Consulta el [diseño de Aurora](docs/diseno/AURORA.md).

### Entradas y mensajes de ayuda

Cada campo indica si requiere texto, un número positivo, un valor no negativo, un porcentaje o un entero de personas. Los campos opcionales explican qué significa dejarlos vacíos. Usa `2.5` o `1 500.25`; también se admite notación científica como `1e3`. No se admiten comas decimales, guiones bajos, NaN ni infinito. El crecimiento puede ser negativo hasta −100 %; los no conformes no pueden superar la producción o 100 %, según la medida seleccionada.

Puedes escribir y pegar sin que se bloquee el teclado. Los errores aparecen junto al campo y con borde de aviso; al intentar continuar se señalan los datos faltantes y se enfoca el primer campo incorrecto. Las filas de insumos muestran sus propios mensajes: cantidad y costo unitario, o costo directo, pero no ambos costos simultáneamente. No se guarda una resolución con entradas inválidas. Al corregirlas se elimina el aviso y se vuelve a calcular.

En **Un factor → Comparar conformidad**, «No conformes» son las unidades que no cumplen los requisitos de calidad. Si 5 de 125 unidades no cumplen, escribe `5` al elegir **Cantidad**, o `4` al elegir **%**. En ambos casos quedan 120 unidades conformes. Usa la misma medida en los dos escenarios. Si no hubo unidades no conformes, escribe `0`; dejar el campo vacío no confirma que no hubo defectos.

Las horas por trabajador y las horas-persona totales son variables distintas. El personal requerido en la interfaz se redondea hacia arriba. Si registras una plantilla, la diferencia de personal se calcula frente a ella. Si indicas la producción actual, también puedes ver las horas adicionales respecto de esa producción.

En **Resultados** puedes volver al procedimiento, copiar el informe y exportar a HTML o PDF.

## Mi biblioteca de ejercicios

- Cada ejercicio válido se guarda automáticamente al entrar en **Desarrollo** o usar **Ver resultado**. Las previsualizaciones y entradas inválidas no se guardan. Si falla el guardado, aparece un aviso y se conserva el borrador.
- Se conservan título, enunciado, datos, fecha, fórmulas, sustituciones, resultados sin redondear y una copia del informe con la precisión visible al guardar.
- En **Inicio → Ver todos / Buscar** puedes buscar por título, enunciado o datos, filtrar por módulo, abrir un ejercicio, consultar su resolución guardada sin recalcular o eliminarlo con confirmación.
- Editar y resolver de nuevo actualiza el mismo ejercicio. **Guardar copia**, en Resultados, crea otro registro independiente para conservar variantes. No hay historial de versiones de un mismo registro.
- Al abrir se recalcula con la versión actual del programa; **Ver resolución guardada** muestra el informe conservado. Los ejercicios antiguos siguen disponibles y reciben la resolución completa al abrirlos.
- Los borradores que todavía no se han desarrollado no se guardan automáticamente. **Guardar cálculo** permite reintentar un guardado fallido.

La minibase usa archivos JSON versionados (uno por ejercicio), con escritura atómica; no requiere servidor, internet ni dependencias nuevas. En Windows se encuentra en `%LOCALAPPDATA%/DIROPE Calc`, en macOS en `~/Library/Application Support/DIROPE Calc` y en Linux en `$XDG_DATA_HOME/DIROPE Calc` o `~/.local/share/DIROPE Calc`. Para respaldarla, cierra la aplicación y copia esa carpeta completa. Los datos se guardan localmente sin cifrado; no publiques esa carpeta si contiene información privada.

### Práctica inicial resuelta

`python cargar_practica.py` incorpora a la biblioteca Chuck Sox, Lori Cook, Kleen Karpet, Lakefront, Lackey y el caso hipotético de placas del documento inicial, además de Susan Williams y la batidora del Word del curso. Son ocho ejercicios en nueve registros: placas se separa en calidad laboral y multifactor. Cada registro incluye el enunciado resumido, entradas editables y resolución completa. Repetir la carga no duplica ni sobrescribe esos registros, aunque los hayas editado. Los resultados se calculan con los módulos del programa y tienen pruebas de regresión.

### Cambiar de método y banco de práctica

**¿Qué calcular?** conserva un borrador independiente por opción durante la sesión: título, enunciado, datos e identidad del ejercicio guardado. Al elegir otra opción por primera vez, se presenta un formulario limpio; al volver, se recuperan sus datos. No se convierte automáticamente una tabla de costos en categorías de calidad ni se sobrescribe un ejercicio de otro método. Volver a desarrollar recalcula el resultado. El selector **Ejemplo** muestra únicamente ejemplos compatibles; se desactiva su botón si no hay ninguno. **Nuevo problema** limpia solo el método activo, previa confirmación cuando corresponde. Al cerrar se avisa también de borradores en opciones no visibles.

En **Inicio → Banco de práctica** hay **1 000 ejercicios sintéticos: 100 por cada uno de los 10 métodos**. Filtra por método y abre el caso para resolverlo. Solo se incorpora a tu biblioteca personal al desarrollarlo. Los casos varían producciones, recursos, defectos en cantidades y porcentajes, costos directos o unitarios, número de insumos y alternativas, monedas, unidades, períodos, crecimientos negativos y plantillas opcionales. Los resultados de referencia se calculan de forma independiente con fracciones racionales, no copiando la salida del módulo que se evalúa.

**Planteamiento** presenta el caso en prosa; **Datos** agrupa los campos editables por tema y conserva las tablas de insumos y categorías. **Identificación** y **Desarrollo** muestran fracciones apiladas y notación matemática sin instalar LaTeX. Usa **Ctrl+C** sobre una fórmula enfocada para copiar su versión en texto.

Las fórmulas y expresiones tienen recuadros que explican variables, términos y operaciones. Se sitúan a la derecha cuando hay espacio y debajo en ventanas estrechas. El componente se comparte entre método, pasos y detalles auxiliares; las explicaciones de los términos se mantienen en `src/dirope/leyendas.py`. Una fórmula futura con símbolos nuevos debe añadir sus descripciones y pruebas: no se interpreta automáticamente el significado de variables desconocidas.

`python generar_banco.py` escribe los enunciados, datos y respuestas de referencia en `ejemplos/banco_generado.json`. La semilla fija permite repetir exactamente las pruebas y no modifica la biblioteca personal.

Al final de **Resultados → Informe completo**, puedes leer el ejercicio de corrido, o usar **Exportar** para guardar PDF o HTML. El HTML se adapta al ancho de la pantalla y muestra fórmula, sustitución y resultado en cada paso, sin una tabla de procedimiento. Para generar PDF A4 directamente, instala la dependencia opcional ReportLab una vez:

```text
python -m pip install -r requirements.txt
```

La aplicación y la exportación funcionan localmente después de instalarla. Los cálculos, el historial, la copia y la exportación HTML funcionan con Python y Tcl/Tk.

HTML y PDF separan fórmula y sustitución de sus explicaciones en dos columnas, con resultados independientes. Las exportaciones se escriben primero en un archivo temporal junto al destino y solo reemplazan el anterior si la operación termina correctamente.

## Si aparece un error en otro equipo

Los avisos que aparecen junto a los campos se corrigen en **Datos**. Si aparece «No se pudo completar la operación», copia el detalle técnico de la ventana y abre **Ajustes → Información y diagnóstico**. Si la ventana no abre, desde la carpeta extraída ejecuta:

```text
Abrir_programa.bat --diagnostico
```

Alternativa: `python iniciar.py --diagnostico` en Windows o `python3 iniciar.py --diagnostico` en macOS y Linux. La huella distingue copias del código, incluso sin Git. Para comprobar el arranque de una ventana de Tk en ese mismo intérprete, ejecuta `python -m tkinter` (o `py -3 -m tkinter` si el diagnóstico muestra que el lanzador usa ese Python).

Comparte el diagnóstico, el método, el paso exacto y las últimas líneas de `registro.log` relacionadas con el error. En Windows puedes abrir `%LOCALAPPDATA%\DIROPE Calc` desde el Explorador. No compartas toda la carpeta: contiene ejercicios personales. El diagnóstico no lee esos ejercicios, pero las rutas pueden mostrar tu nombre de usuario.

## Verificación

```text
python -m unittest discover -s pruebas -v
python iniciar.py --comprobar-interfaz
python pruebas/comprobar_banco_interfaz.py
python pruebas/comprobar_navegacion.py
python verificar_contraste.py
```

La comprobación de interfaz recorre nueve ejemplos, datos propios, cambios de módulo, edición, duplicación de insumos, acceso directo a resultados, guardado y reapertura, informes y gráficos. Consulta los [requisitos pendientes para la versión 1.0](docs/VIABILIDAD.md).

Consulta la [última verificación](docs/VERIFICACION.md) y sus limitaciones.

La prueba intensiva recorre los 1 000 ejercicios por la interfaz real, con acceso directo y desarrollo guiado, escritura y lectura en una carpeta temporal, cambios Claro/Oscuro y pares de métodos con borradores guardados o sin guardar. Las pruebas del núcleo añaden miles de mutaciones inválidas: vacíos, texto, negativos, NaN/Infinity, booleanos, denominadores nulos, monedas incompatibles, filas contradictorias, porcentajes fuera de dominio, sobreflujo y límites decimales de personal. No se afirma cobertura exhaustiva de todos los errores posibles ni validación de otros sistemas operativos.

Las pruebas de recuadros verifican anchos grandes y pequeños, ambos temas, escala aumentada y funcionamiento sin Pillow. Las pruebas PDF requieren ReportLab; si no está instalado se omiten explícitamente. Las pruebas Tk se omiten si el entorno no tiene pantalla disponible. La integración continua incluye una ejecución Windows con ReportLab, comprobación de interfaz y contraste, además de la matriz sin dependencias opcionales.

Los ejemplos 1.14 y 1.17 usan los datos de Heizer y Render, *Principios de administración de operaciones*, 7.ª edición, capítulo 1. [Enunciados del capítulo](https://matrixeducacion.com/wp-content/uploads/2023/07/Libro-5-Heizer-and-Render-Principios-de-Operaciones.pdf)

Consulta `CONTRIBUTING.md` para colaborar. Conserva los documentos privados del curso fuera de las publicaciones del proyecto.
