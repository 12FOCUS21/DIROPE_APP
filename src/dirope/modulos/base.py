"""Contrato de formulario y cálculo, independiente de Tkinter."""

from dataclasses import dataclass
from typing import Callable

from ..modelos import Resultado


@dataclass(frozen=True)
class Campo:
    clave: str
    etiqueta: str
    valor: str = ""


@dataclass(frozen=True)
class Modulo:
    clave: str
    nombre: str
    campos: tuple[Campo, ...]
    calcular: Callable[[dict], Resultado]
    ejemplos: dict[str, dict]
    tabla_insumos: bool = False
