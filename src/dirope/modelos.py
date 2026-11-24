"""Modelos independientes de la interfaz gráfica."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Insumo:
    nombre: str
    cantidad: float
    precio: float
    es_laboral: bool = False


@dataclass(frozen=True)
class Paso:
    titulo: str
    explicacion: str
    formula: str
    sustitucion: str
    resultado: float
    unidad: str


@dataclass(frozen=True)
class Resultado:
    pasos: tuple[Paso, ...]
    interpretacion: str
