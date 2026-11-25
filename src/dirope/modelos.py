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
    auxiliar: bool = False


@dataclass(frozen=True)
class Resultado:
    pasos: tuple[Paso, ...]
    interpretacion: str
    indicadores: tuple[Paso, ...] = ()
    serie: tuple[tuple[str, float], ...] = ()
    unidad_grafico: str = ""
    titulo_grafico: str = ""
    tipo_grafico: str = "barras"
    principal: Paso | None = None

    @property
    def procedimiento(self):
        return tuple(paso for paso in self.pasos if not paso.auxiliar)

    @property
    def detalles(self):
        return tuple(paso for paso in self.pasos if paso.auxiliar)
