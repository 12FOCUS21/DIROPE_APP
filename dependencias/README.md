# Paquetes incluidos para DIROPE Calc

`wheels/` contiene los archivos oficiales sin modificar de PyPI, para instalaciones sin internet en Windows x64 con CPython estándar 3.10–3.14. Los hashes SHA-256 se fijan en `requirements-windows-x64.txt` y pip los comprueba antes de instalar. Los paquetes son:

| Paquete | Versión | Uso / licencia incluida en el archivo |
|---|---|---|
| [Pillow](https://pypi.org/project/Pillow/) | 12.3.0 (Python 3.10), 13.0.0 (3.11–3.14) | Renderizado de controles y fondos; MIT-CMU y avisos de bibliotecas incluidas. |
| [ReportLab](https://pypi.org/project/reportlab/4.5.1/) | 4.5.1 | Exportación PDF; BSD y avisos de fuentes incluidas. |
| [charset-normalizer](https://pypi.org/project/charset-normalizer/3.5.3/) | 3.5.3 | Dependencia de ReportLab; MIT. Se incluye la rueda universal de Python. |

Los avisos de terceros viajan dentro de cada archivo `.whl`, que se puede abrir como un ZIP. No se incluyen Python o Tcl/Tk, ni un entorno virtual ya creado. El lanzador crea `.venv-dirope/` solo tras autorización. Fuera de la combinación indicada puede solicitar permiso para descargar las versiones de `../requirements.txt` desde PyPI; requiere una rueda compatible. Los cálculos y la exportación HTML funcionan sin estos paquetes opcionales.
