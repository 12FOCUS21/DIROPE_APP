"""Cálculos puros. Sin ventanas ni redondeo de productividades."""

import math

from .modelos import Insumo

TOLERANCIA_PERSONAL = 0.01


def validar_numero(valor: object, nombre: str, positivo: bool = False) -> float:
    """Admite números con punto decimal y espacios de miles, no valores infinitos."""
    if isinstance(valor, bool):
        raise ValueError(f"{nombre}: ingresa un número, no un valor lógico.")
    texto = str(valor).strip().replace("\u00a0", " ")
    if not texto:
        raise ValueError(f"{nombre}: el campo está vacío.")
    # Si hay separadores de miles, exigimos agrupaciones de tres cifras.
    if " " in texto:
        entero, _, fraccion = texto.partition(".")
        grupos = entero.lstrip("+-").split(" ")
        if (not 1 <= len(grupos[0]) <= 3 or not grupos[0].isdigit()
                or any(len(g) != 3 or not g.isdigit() for g in grupos[1:])
                or " " in fraccion):
            raise ValueError(f"{nombre}: usa espacios solo para agrupar miles, por ejemplo 1 500.")
        texto = texto.replace(" ", "")
    try:
        numero = float(texto)
    except (TypeError, ValueError):
        raise ValueError(f"{nombre}: ingresa un número con punto decimal (por ejemplo, 2.5).") from None
    if not math.isfinite(numero):
        raise ValueError(f"{nombre}: el número debe ser finito.")
    if numero < 0 or (positivo and numero == 0):
        condicion = "mayor que cero" if positivo else "mayor o igual que cero"
        raise ValueError(f"{nombre}: debe ser {condicion}.")
    return numero


def finito(valor: float) -> float:
    """Evita propagar desbordamientos aritméticos a los resultados."""
    if not math.isfinite(valor):
        raise ValueError("Los valores son demasiado grandes para calcular. Reduce su magnitud.")
    return valor


def productividad(salida: float, insumo: float) -> float:
    return finito(validar_numero(salida, "Producción") / validar_numero(insumo, "Insumo", True))


def cambio_pct(antes: float, despues: float) -> float:
    base = validar_numero(antes, "Productividad inicial", True)
    nuevo = validar_numero(despues, "Productividad final")
    return finito((nuevo - base) / base * 100)


def costo_total(insumos: list[Insumo]) -> float:
    if not insumos:
        raise ValueError("Agrega al menos un insumo.")
    costos = []
    for insumo in insumos:
        if not insumo.nombre.strip():
            raise ValueError("Cada insumo debe tener un nombre.")
        cantidad = validar_numero(insumo.cantidad, f"Cantidad de {insumo.nombre}")
        precio = validar_numero(insumo.precio, f"Precio de {insumo.nombre}")
        costos.append(finito(cantidad * precio))
    total = finito(sum(costos))
    if total <= 0:
        raise ValueError("El costo total debe ser mayor que cero.")
    return total


def multifactor(salida: float, insumos: list[Insumo]) -> float:
    return productividad(salida, costo_total(insumos))


def horas_necesarias(meta: float, productividad_laboral: float) -> float:
    return productividad(meta, productividad_laboral)


def personas_necesarias(horas: float, horas_por_persona: float) -> float:
    return productividad(horas, horas_por_persona)


def personal_entero(personas: float) -> int:
    """Ajusta al entero más próximo si dista <= 0.01; en otro caso aplica techo.

    Supuesto explícito para productividad publicada con redondeo: 5.0001 -> 5.
    No es una garantía de capacidad cuando los datos son exactos.
    """
    personas = validar_numero(personas, "Personal")
    cercano = round(personas)
    if cercano > 0 and abs(personas - cercano) <= TOLERANCIA_PERSONAL + 1e-12:
        return cercano
    return math.ceil(personas)


def unidades_buenas(produccion: float, pct_defectos: float) -> float:
    cantidad = validar_numero(produccion, "Producción")
    defectos = validar_numero(pct_defectos, "Defectos")
    if defectos > 100:
        raise ValueError("El porcentaje de defectos no puede superar 100 %.")
    return finito(cantidad * (1 - defectos / 100))
