"""Guarda los ejercicios resueltos de los documentos iniciales en la biblioteca local."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from dirope.historial import Historial, carpeta_local
from dirope.practica_inicial import guardar_practica


if __name__ == "__main__":
    historial = Historial(carpeta_local())
    registros = guardar_practica(historial)
    print(f"Biblioteca: {historial.carpeta}")
    for registro in registros:
        print(f"Guardado: {registro['nombre']}")
    print(f"{len(registros)} registros disponibles; los ejercicios existentes no se sobrescriben.")
