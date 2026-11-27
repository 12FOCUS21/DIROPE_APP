"""Crea el ZIP para usuarios a partir de un commit, sin archivos locales o del curso."""

import argparse
from hashlib import sha256
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

RAIZ = Path(__file__).resolve().parents[1]
NOMBRE = "DIROPE-Calc.zip"
INCLUIR = (
    "Abrir_programa.bat", "Abrir_programa.command", "iniciar.py", "preparar.py",
    "requirements.txt", "dependencias", "src", "cargar_practica.py", "docs/INICIO_RAPIDO.md",
)


def empaquetar(ref, salida):
    """Exporta solo los archivos de ejecución y escribe su SHA-256."""
    commit = subprocess.check_output(
        ["git", "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}"],
        cwd=RAIZ, text=True,
    ).strip()
    salida = Path(salida).resolve()
    salida.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=salida) as temporal:
        archivo = Path(temporal) / NOMBRE
        subprocess.run(
            ["git", "archive", "--format=zip", "--prefix=DIROPE Calc/", f"--output={archivo}",
             commit, "--", *INCLUIR], cwd=RAIZ, check=True,
        )
        with archivo.open("rb") as contenido:
            huella = sha256()
            for bloque in iter(lambda: contenido.read(1024 * 1024), b""):
                huella.update(bloque)
        suma = archivo.with_suffix(".zip.sha256")
        suma.write_text(f"{huella.hexdigest()}  {NOMBRE}\n", encoding="ascii")
        archivo.replace(salida / archivo.name)
        suma.replace(salida / suma.name)
    return salida / NOMBRE, commit


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default="HEAD", help="Commit o etiqueta que se va a publicar")
    parser.add_argument("--salida", type=Path, default=RAIZ / "dist", help="Carpeta para el ZIP y su hash")
    opciones = parser.parse_args()
    zip_final, revision = empaquetar(opciones.ref, opciones.salida)
    print(f"{zip_final} (commit {revision})")
