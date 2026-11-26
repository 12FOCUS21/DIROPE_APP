"""Preferencias locales separadas de los ejercicios guardados."""

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile


class Preferencias:
    def __init__(self, carpeta):
        self.ruta = Path(carpeta) / "ajustes" / "preferencias.json"

    def leer_tema(self):
        try:
            datos = json.loads(self.ruta.read_text(encoding="utf-8"))
            tema = datos.get("tema") if isinstance(datos, dict) else None
            return tema if tema in ("Claro", "Oscuro") else "Claro"
        except (OSError, ValueError, RecursionError):
            return "Claro"

    def guardar_tema(self, tema):
        if tema not in ("Claro", "Oscuro"):
            raise ValueError("Selecciona el tema Claro u Oscuro.")
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        temporal = None
        try:
            with NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.ruta.parent,
                                    suffix=".tmp", delete=False) as archivo:
                temporal = Path(archivo.name)
                json.dump({"tema": tema}, archivo)
                archivo.flush()
                os.fsync(archivo.fileno())
            temporal.replace(self.ruta)
        finally:
            if temporal is not None:
                temporal.unlink(missing_ok=True)
