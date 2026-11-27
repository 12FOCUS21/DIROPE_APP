"""Empaqueta el sitio estático y exactamente los módulos Python que importa."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
from urllib.request import urlopen
from zipfile import ZIP_DEFLATED, ZipFile


RAIZ = Path(__file__).resolve().parents[1]
WEB = RAIZ / "web"
MODULOS = (
    "__init__.py", "analisis.py", "banco.py", "entradas.py", "formato.py", "informe.py",
    "leyendas.py", "modelos.py", "notacion.py", "nucleo.py", "practica_inicial.py", "web.py", "modulos/__init__.py",
    "modulos/base.py", "modulos/campos.py", "modulos/productividad.py", "modulos/variantes.py",
)
PUBLICOS = ("index.html", "estilos.css", "app.js", "motor.js")
RUNTIME = ("pyodide.js", "pyodide.js.map", "pyodide.asm.js", "pyodide.asm.wasm",
           "pyodide-lock.json", "python_stdlib.zip")
LICENCIAS = {
    "Pyodide": ("pyodide/pyodide/0.29.3/LICENSE", "1f256ecad192880510e84ad60474eab7589218784b9a50bc7ceee34c2b91f1d5"),
    "CPython": ("python/cpython/v3.13.2/LICENSE", "78b12c3a81360b357002334f0e70ea0e92eebf7a9b358805c03c48484945f3bb"),
    "Emscripten": ("emscripten-core/emscripten/4.0.9/LICENSE", "620a78084fc7ca97c0b5dea9abf891f3ffcadfdbf305276f099c9c4e12fc1d86"),
}


def empaquetar_nucleo(archivo):
    with ZipFile(archivo, "w", compression=ZIP_DEFLATED) as zip_web:
        for nombre in MODULOS:
            zip_web.write(RAIZ / "src" / "dirope" / nombre, f"dirope/{nombre}")


def copiar_licencias(motor):
    for nombre, (ruta, huella) in LICENCIAS.items():
        destino = motor / f"LICENCIA-{nombre}.txt"
        if destino.is_file() and sha256(destino.read_bytes()).hexdigest() == huella:
            continue
        with urlopen(f"https://raw.githubusercontent.com/{ruta}", timeout=30) as respuesta:
            texto = respuesta.read(100_000)
        if sha256(texto).hexdigest() != huella:
            raise ValueError(f"El contenido de la licencia de {nombre} no coincide con su SHA-256.")
        destino.write_bytes(texto)


def preparar(salida):
    runtime = WEB / "node_modules" / "pyodide"
    esperada = json.loads((WEB / "package.json").read_text(encoding="utf-8"))["devDependencies"]["pyodide"]
    instalada = json.loads((runtime / "package.json").read_text(encoding="utf-8"))["version"]
    if instalada != esperada:
        raise ValueError(f"Pyodide {instalada} no coincide con {esperada}. Ejecuta npm ci en web/.")
    salida = salida.resolve()
    if salida == WEB or salida == RAIZ:
        raise ValueError("Usa una carpeta de salida separada, como build/web.")
    motor = salida / "runtime"
    motor.mkdir(parents=True, exist_ok=True)
    for nombre in PUBLICOS:
        shutil.copyfile(WEB / nombre, salida / nombre)
    for nombre in RUNTIME:
        shutil.copyfile(runtime / nombre, motor / nombre)
    copiar_licencias(motor)
    empaquetar_nucleo(salida / "dirope.zip")
    (salida / ".nojekyll").touch()
    return salida


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=RAIZ / "build" / "web")
    print(f"Sitio preparado en {preparar(parser.parse_args().salida)}")
