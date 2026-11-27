"""Información técnica local para soporte; no lee ejercicios ni envía datos a internet."""

from hashlib import sha256
from importlib import metadata
from pathlib import Path
import platform
import sys

from .historial import carpeta_local


def huella_codigo(carpeta):
    """Identifica copias del código aunque se descarguen como ZIP, sin requerir Git."""
    carpeta = Path(carpeta)
    rutas = [carpeta / "iniciar.py", *sorted((carpeta / "src" / "dirope").rglob("*.py"))]
    rutas.extend(carpeta / nombre for nombre in ("preparar.py", "requirements.txt") if (carpeta / nombre).is_file())
    huella = sha256()
    try:
        for ruta in rutas:
            huella.update(ruta.relative_to(carpeta).as_posix().encode("utf-8"))
            huella.update(b"\0")
            # La misma descarga puede tener finales de línea diferentes en cada sistema.
            huella.update(ruta.read_bytes().replace(b"\r\n", b"\n"))
            huella.update(b"\0")
    except OSError:
        return "No disponible: no se pudieron leer todos los archivos del programa."
    return huella.hexdigest()[:16]


def informacion_entorno(raiz=None, *, carpeta_programa=None, carpeta_datos=None):
    """Texto copiable: versiones, rutas y huella; no incluye entradas ni resoluciones."""
    programa = Path(carpeta_programa) if carpeta_programa is not None else Path(__file__).resolve().parents[2]
    datos = Path(carpeta_datos) if carpeta_datos is not None else carpeta_local()

    def version(nombre):
        try:
            return metadata.version(nombre)
        except metadata.PackageNotFoundError:
            return "No instalado (opcional)"
        except (OSError, ValueError):
            return "No se pudo consultar"

    try:
        if raiz is not None:
            tk = f'Tcl {raiz.tk.call("info", "patchlevel")} / Tk {raiz.tk.call("set", "tk_patchLevel")}'
        else:
            import tkinter
            tk = f"Tcl {tkinter.TclVersion} / Tk {tkinter.TkVersion} (módulo disponible; ventana no probada)"
    except Exception as error:
        # El diagnóstico debe seguir disponible incluso si Tk no se instaló o ya se cerró.
        tk = f"No disponible: {error}"

    return "\n".join((
        "DIROPE Calc · Diagnóstico local", "",
        f"Código (huella): {huella_codigo(programa)}",
        f"Python: {platform.python_version()}", f"Ejecutable Python: {sys.executable}",
        f"Sistema: {platform.platform()}", f"Tcl/Tk: {tk}",
        f"Pillow: {version('Pillow')}", f"ReportLab: {version('reportlab')}",
        f"Carpeta del programa: {programa}", f"Carpeta de datos: {datos}",
        f"Registro de errores: {carpeta_local() / 'registro.log'}", "",
        "Reproducción: anota qué botón pulsaste, el método y la hora del error.",
        "Para soporte, adjunta este diagnóstico y el fragmento reciente de registro.log.",
        "No se han leído ejercicios ni enviado datos por internet. Las rutas pueden incluir tu nombre de usuario.",
    ))
