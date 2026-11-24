"""Presentación de números sin alterar la precisión del cálculo."""

import math


def numero(valor: float, decimales: int = 3) -> str:
    """Usa punto decimal y espacio sin salto para los miles."""
    if not 0 <= decimales <= 8:
        raise ValueError("Los decimales deben estar entre 0 y 8.")
    if not math.isfinite(valor):
        raise ValueError("El resultado debe ser un número finito.")
    return f"{valor:,.{decimales}f}".replace(",", "\u00a0")
