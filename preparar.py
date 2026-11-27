"""Lanzador de DIROPE: comprueba primero y pide permiso antes de instalar."""

import os
from pathlib import Path
import subprocess
import sys
import sysconfig

RAIZ = Path(__file__).resolve().parent
PAQUETES = (
    ("Pillow", "12.3.0" if sys.version_info[:2] == (3, 10) else "13.0.0", "dibuja los controles y fondos"),
    ("reportlab", "4.5.1", "exporta informes a PDF"),
    ("charset-normalizer", "3.5.3", "es una dependencia de ReportLab para manejar codificaciones de texto"),
)
CONSULTA = """
from importlib.metadata import version
import sys
try:
    if any(version(n) != v for n, v in zip(sys.argv[1::2], sys.argv[2::2])):
        sys.exit(1)
    from PIL import Image, ImageTk, _imaging
    from reportlab.pdfgen import canvas
    import charset_normalizer
except Exception:
    sys.exit(1)
"""


def entorno_local(raiz):
    version = f"{sys.implementation.name}-{sys.version_info.major}.{sys.version_info.minor}"
    plataforma = sysconfig.get_platform()
    abi = "t" if sysconfig.get_config_var("Py_GIL_DISABLED") else getattr(sys, "abiflags", "")
    entorno = raiz / ".venv-dirope" / f"{version}-{plataforma}{abi}"
    ejecutable = entorno / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    return entorno, ejecutable


def paquetes_disponibles(ejecutable):
    if not Path(ejecutable).is_file():
        return False
    argumentos = [dato for nombre, version, _ in PAQUETES for dato in (nombre, version)]
    try:
        return subprocess.run([str(ejecutable), "-I", "-c", CONSULTA, *argumentos],
                              capture_output=True, timeout=15).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def origen_paquetes(raiz):
    carpeta = raiz / "dependencias" / "wheels"
    bloqueo = raiz / "dependencias" / "requirements-windows-x64.txt"
    if (sysconfig.get_platform() == "win-amd64" and sys.implementation.name == "cpython"
            and (3, 10) <= sys.version_info[:2] <= (3, 14) and not sysconfig.get_config_var("Py_GIL_DISABLED")):
        abi = f"cp{sys.version_info.major}{sys.version_info.minor}"
        nombres = (f"pillow-{PAQUETES[0][1]}-{abi}-{abi}-win_amd64.whl",
                   "reportlab-4.5.1-py3-none-any.whl", "charset_normalizer-3.5.3-py3-none-any.whl")
        if bloqueo.is_file() and all((carpeta / nombre).is_file() for nombre in nombres):
            return bloqueo, carpeta, True
        if bloqueo.is_file():
            return bloqueo, None, True
    return raiz / "requirements.txt", None, False


def motivo_instalacion(carpeta, ruedas):
    lista = "\n".join(f"• {nombre} {version}: {motivo}." for nombre, version, motivo in PAQUETES)
    origen = ("Se usarán los paquetes incluidos en la descarga, sin internet."
              if ruedas else "Se descargarán los paquetes desde PyPI (pypi.org). Se necesita internet.")
    return ("No se encontró un entorno con todos los paquetes en las versiones comprobadas. "
            "Para habilitar el aspecto completo y la exportación directa a PDF se instalará este conjunto:\n\n"
            f"{lista}\n\n{origen}\n\nSe creará un entorno de Python con pip para instalar y verificar los paquetes solo en:\n{carpeta}\n\n"
            "No se requiere acceso de administrador ni se cambiará tu Python global. "
            "Si eliges No, podrás abrir la aplicación y exportar HTML.\n\n¿Autorizar la instalación?")


def preparar_entorno(raiz, carpeta, ejecutable, origen):
    requisitos, ruedas, hashes = origen
    if not requisitos.is_file():
        raise OSError("Falta el archivo de requisitos. Extrae la carpeta completa antes de continuar.")
    base = str(Path(getattr(sys, "_base_executable", None) or sys.executable))
    if not ejecutable.is_file():
        subprocess.run([base, "-I", "-m", "venv", str(carpeta)], check=True, timeout=120)
    if subprocess.run([str(ejecutable), "-I", "-m", "pip", "--version"], capture_output=True, timeout=15).returncode != 0:
        subprocess.run([str(ejecutable), "-I", "-m", "ensurepip", "--upgrade"], check=True, timeout=120)
    comando = [str(ejecutable), "-I", "-m", "pip", "--isolated", "--disable-pip-version-check",
               "--no-input", "install", "--only-binary=:all:", "--force-reinstall", "-r", str(requisitos)]
    if hashes:
        comando.append("--require-hashes")
    if ruedas:
        comando.extend(("--no-index", "--find-links", str(ruedas)))
    else:
        comando.extend(("--index-url", "https://pypi.org/simple", "--timeout", "20"))
    env = dict(os.environ, PIP_CONFIG_FILE=os.devnull)
    subprocess.run(comando, cwd=raiz, env=env, check=True, timeout=360)
    subprocess.run([str(ejecutable), "-I", "-m", "pip", "check"], cwd=raiz, env=env, check=True, timeout=30)
    if not paquetes_disponibles(ejecutable):
        raise RuntimeError("Los paquetes se copiaron, pero no se pudieron cargar con este Python.")


def elegir_python(raiz, base, confirmar, avisar):
    """Devuelve el intérprete y si se debe iniciar sin paquetes de terceros."""
    carpeta, ejecutable = entorno_local(raiz)
    if paquetes_disponibles(ejecutable):
        return ejecutable, False
    if paquetes_disponibles(base):
        return base, False
    try:
        import venv  # noqa: F401
        import ensurepip  # noqa: F401
    except ImportError:
        avisar("Este Python no incluye venv/ensurepip. Se abrirá el modo básico. "
               "Para preparar el entorno instala Python con soporte de entornos virtuales.")
        return base, True
    origen = origen_paquetes(raiz)
    if not origen[0].is_file():
        avisar("Falta el archivo de requisitos. Extrae todo el ZIP de GitHub. Se abrirá el modo básico.")
        return base, True
    if not confirmar(motivo_instalacion(carpeta, origen[1])):
        return base, True
    print("Preparando los paquetes de DIROPE…", flush=True)
    try:
        preparar_entorno(raiz, carpeta, ejecutable, origen)
    except (OSError, subprocess.SubprocessError, RuntimeError) as error:
        print(f"No se pudieron preparar los paquetes: {error}", file=sys.stderr)
        avisar("No se completó la instalación. Se abrirá DIROPE en modo básico. "
               "Consulta el mensaje de la consola; no se modificaron tus ejercicios.")
        return base, True
    return ejecutable, False


def main(argumentos=None):
    argumentos = list(sys.argv[1:] if argumentos is None else argumentos)
    base = Path(sys.executable)
    if sys.version_info < (3, 10):
        print("Se necesita Python 3.10 o superior con Tcl/Tk. No se instaló nada.", file=sys.stderr)
        return 1
    if not (RAIZ / "src" / "dirope" / "interfaz" / "ventana.py").is_file():
        print("Faltan archivos de DIROPE. Extrae todo el ZIP de GitHub.", file=sys.stderr)
        return 1
    if any(a in argumentos for a in ("--diagnostico", "--help", "-h", "--comprobar-interfaz")):
        _, preparado = entorno_local(RAIZ)
        elegido = preparado if paquetes_disponibles(preparado) else base
        basico = False
    else:
        try:
            import tkinter as tk
            from tkinter import messagebox

            ventana = tk.Tk()
        except (ImportError, RuntimeError) as error:
            print(f"No se pudo iniciar Tkinter: {error}. Instala Python con Tcl/Tk; no se instaló nada.", file=sys.stderr)
            return 1
        except Exception as error:
            print(f"No se pudo abrir una ventana Tk: {error}. No se instaló nada.", file=sys.stderr)
            return 1
        ventana.withdraw()
        try:
            elegido, basico = elegir_python(
                RAIZ, base,
                lambda texto: messagebox.askyesno("Preparar DIROPE Calc", texto, parent=ventana, default="no"),
                lambda texto: messagebox.showwarning("DIROPE Calc · Modo básico", texto, parent=ventana),
            )
        finally:
            ventana.destroy()
    opciones = ["-I", "-S"] if basico else ["-I"]
    return subprocess.call([str(elegido), *opciones, str(RAIZ / "iniciar.py"), *argumentos], cwd=RAIZ)


if __name__ == "__main__":
    raise SystemExit(main())
