"""Minibase local de ejercicios y resoluciones, sin dependencias externas."""
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import UUID, uuid4


def carpeta_local():
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    return base / "DIROPE Calc"


class Historial:
    def __init__(self, carpeta):
        self.carpeta = Path(carpeta)

    def ruta(self, identificador):
        return self.carpeta / (str(UUID(identificador)) + ".json")

    def guardar(self, modulo, nombre, enunciado, datos, identificador=None, *, resolucion=None):
        identificador = identificador or str(uuid4())
        registro = dict(version=1, id=identificador, modulo=modulo, nombre=nombre,
                        enunciado=enunciado, datos=datos,
                        modificado=datetime.now().astimezone().isoformat(timespec="microseconds"))
        if resolucion is not None:
            registro["resolucion"] = resolucion
        # Validar antes de crear archivos y rechazar también NaN/Infinity anidados.
        registro = json.loads(json.dumps(registro, allow_nan=False))
        self.validar(registro, identificador)
        try:
            anterior = self.abrir(identificador)
        except FileNotFoundError:
            anterior = None
        if anterior is not None:
            if all(anterior.get(k) == v for k, v in registro.items() if k != "modificado"):
                return anterior
        self.carpeta.mkdir(parents=True, exist_ok=True)
        destino = self.ruta(identificador)
        temporal = None
        try:
            with NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.carpeta,
                                    suffix=".tmp", delete=False) as archivo:
                temporal = Path(archivo.name)
                json.dump(registro, archivo, ensure_ascii=False, allow_nan=False, indent=2)
                archivo.flush()
                os.fsync(archivo.fileno())
            temporal.replace(destino)
        finally:
            if temporal is not None:
                temporal.unlink(missing_ok=True)
        return registro

    def abrir(self, identificador):
        ruta = self.ruta(identificador)
        registro = json.loads(ruta.read_text(encoding="utf-8"))
        self.validar(registro, identificador)
        return registro

    @staticmethod
    def validar(registro, identificador):
        if (not isinstance(registro, dict) or registro.get("version") != 1
                or registro.get("id") != identificador
                or any(not isinstance(registro.get(k), str)
                       for k in ("modulo", "nombre", "enunciado", "modificado"))
                or not isinstance(registro.get("datos"), dict)):
            raise ValueError("Formato de cálculo guardado inválido.")
        fecha = datetime.fromisoformat(registro["modificado"])
        if fecha.tzinfo is None:
            raise ValueError("La fecha del cálculo guardado no incluye zona horaria.")
        resolucion = registro.get("resolucion")
        if resolucion is not None and (not isinstance(resolucion, dict)
                or not isinstance(resolucion.get("resultado"), dict)
                or not isinstance(resolucion.get("informe"), str)):
            raise ValueError("La resolución guardada no tiene un formato válido.")
        json.dumps(registro, allow_nan=False)

    def listar(self, busqueda="", modulo=""):
        registros, errores = [], 0
        for ruta in self.carpeta.glob("*.json"):
            try:
                registro = self.abrir(ruta.stem)
                texto = " ".join((registro["nombre"], registro["enunciado"],
                                  json.dumps(registro["datos"], ensure_ascii=False))).casefold()
                if (not modulo or registro["modulo"] == modulo) and busqueda.strip().casefold() in texto:
                    registros.append(registro)
            except (OSError, ValueError, RecursionError):
                errores += 1
        registros.sort(key=lambda r: datetime.fromisoformat(r["modificado"]), reverse=True)
        return registros, errores

    def eliminar(self, identificador):
        self.ruta(identificador).unlink()
