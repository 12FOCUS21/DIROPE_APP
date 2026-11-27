"""Significado de los elementos de las fórmulas, sin dependencias de interfaz."""

import re


ELEMENTOS = {
    "Q": "Cantidad producida; en capacidad, producción actual del período.",
    "Q conforme": "Cantidad producida que cumple los requisitos de calidad.",
    "Q actual": "Producción actual del período de referencia.",
    "P": "Productividad: producción por unidad de recurso; en capacidad, por hora-persona.",
    "I": "Cantidad del recurso o insumo utilizado.",
    "PM": "Productividad multifactor: producción por unidad monetaria del costo total.",
    "PL": "Productividad laboral: producción por unidad del insumo laboral indicado.",
    "PL$": "Producción por unidad monetaria de costo laboral.",
    "C": "Costo total de los insumos, en una moneda común; en una partida, costo de ese recurso.",
    "Cᵢ": "Costo del insumo i, expresado en la misma moneda que los demás.",
    "V": "Valor monetario de la producción; en una categoría, valor de esa categoría.",
    "Vᵢ": "Valor monetario de la categoría i.",
    "Meta": "Producción objetivo para el período considerado.",
    "demanda": "Cantidad de producción requerida para el período.",
    "g": "Crecimiento de la producción, expresado como porcentaje.",
    "H": "Total de horas-persona requeridas para alcanzar la meta.",
    "N": "Número de personas necesarias.",
    "N necesario": "Número entero de personas requeridas para cubrir la meta.",
    "N disponible": "Número de personas de la plantilla disponible.",
    "jornada": "Horas de trabajo por persona en el período considerado.",
    "h por persona": "Horas de trabajo disponibles por persona en el período.",
    "horas-persona": "Suma de las horas trabajadas por todas las personas.",
    "horas": "Horas-persona de trabajo utilizadas.",
    "insumo laboral": "Horas-persona o costo laboral, según el título y la unidad del cálculo.",
    "costo laboral": "Costo monetario total del trabajo.",
    "cantidad": "Cantidad de unidades del recurso o de la categoría indicada.",
    "precio": "Costo por unidad del recurso.",
    "precio unitario": "Costo monetario de una unidad del recurso.",
    "horas laborales": "Total de horas-persona de las filas identificadas como trabajo.",
    "horas por persona": "Horas de trabajo disponibles para cada persona en el período.",
    "producción": "Cantidad de unidades producidas en el escenario y período considerados.",
    "productividad laboral": "Cantidad producida por cada hora-persona de trabajo.",
    "valor unitario": "Valor monetario de una unidad de la categoría.",
    "directo": "Costo total introducido directamente, sin multiplicar cantidad por precio.",
    "defectos": "Unidades no conformes; si se divide entre 100, porcentaje de no conformes.",
    "Participación": "Porcentaje del costo total correspondiente al insumo i.",
    "Δ": "Cambio con signo: valor final menos valor inicial de la magnitud comparada.",
    "Δ%": "Variación porcentual respecto del valor inicial, que debe ser distinto de cero.",
    "ΔP": "Diferencia entre la productividad final y la inicial.",
    "ΔH": "Cambio de horas-persona respecto de la producción actual.",
    "final": "Valor de la magnitud comparada en el escenario final.",
    "inicial": "Valor de esa misma magnitud en el escenario inicial.",
    "Tasa final": "Porcentaje de producción conforme en el escenario final.",
    "tasa inicial": "Porcentaje de producción conforme en el escenario inicial.",
    "producción actual": "Cantidad producida en el período de referencia.",
    "ritmo indicado": "Productividad laboral introducida, en unidades por hora-persona.",
    "Adicional": "Diferencia entre el personal entero necesario y el personal entero actual.",
    "Σ": "Sumatoria: sumar todas las partidas o categorías indicadas por el índice i.",
    "100": "Factor de conversión entre una proporción y un porcentaje.",
    "1": "Unidad completa (100 %): base a la que se suma o resta una proporción.",
    "techo": "Redondeo hacia arriba al menor entero mayor o igual que el valor calculado.",
    "ajuste": "Regla del modelo original: entero más próximo si la distancia es como máximo 0.01; en otro caso, techo.",
}
for simbolo, descripcion in (("Q", "Producción"), ("I", "Cantidad del recurso"),
                              ("P", "Productividad"), ("H", "Horas-persona"),
                              ("N", "Personal calculado, antes del ajuste a personas enteras")):
    for subindice, escenario in (("₀", "inicial"), ("₁", "final")):
        ELEMENTOS[simbolo + subindice] = f"{descripcion} del escenario {escenario}."
for subindice, escenario in (("₀", "actual"), ("₁", "necesario")):
    ELEMENTOS[f"N{subindice} entero"] = f"Personal {escenario} después de aplicar la regla de ajuste del modelo original."

_PATRON = re.compile(r"(?<![\w$])(?:" + "|".join(
    re.escape(clave) for clave in sorted(ELEMENTOS, key=len, reverse=True)) + r")(?![\w$])")

OPERADORES = {
    "=": "Igualdad: ambos lados representan el mismo valor.",
    "+": "Suma de los valores indicados.",
    "−": "Resta: al primer valor se le quita el segundo; el resultado puede ser negativo.",
    "×": "Multiplicación de los factores indicados.",
    "/": "División: el numerador se divide entre el denominador, que no puede ser cero.",
    "(…)": "Agrupación: resolver primero la operación contenida entre paréntesis.",
    "%": "Porcentaje: cantidad por cada cien unidades.",
}


def elementos_formula(formula):
    """Devuelve solo los elementos presentes, sin duplicados y en orden de lectura."""
    claves = dict.fromkeys(coincidencia.group() for coincidencia in _PATRON.finditer(formula))
    elementos = []
    for clave in claves:
        descripcion = ELEMENTOS[clave]
        if clave == "defectos":
            descripcion = ("Porcentaje de producción no conforme, expresado entre 0 y 100."
                           if "defectos / 100" in formula else "Cantidad de unidades no conformes.")
        elementos.append((clave, descripcion))
    return tuple(elementos)


def operadores_expresion(expresion):
    """Explica operaciones también cuando los símbolos se sustituyen por números."""
    claves = dict.fromkeys("(…)" if c in "()" else c for c in expresion if c in "=+−×/()%")
    return tuple((clave, OPERADORES[clave]) for clave in claves)


def leyenda_formula(formula):
    """Texto compartido por pantalla, copia e informes exportados."""
    elementos = (*elementos_formula(formula), *operadores_expresion(formula))
    if not elementos:
        return ""
    return "Elementos de la fórmula\n" + "\n".join(f"{clave}: {texto}" for clave, texto in elementos)


def elementos_sustitucion(expresion):
    """Solo funciones y operaciones: las cifras son los datos del ejercicio."""
    funciones = tuple((clave, ELEMENTOS[clave]) for clave in ("techo", "ajuste")
                      if re.search(r"\b" + clave + r"\(", expresion))
    return (*funciones, *operadores_expresion(expresion))


def leyenda_sustitucion(expresion):
    """No atribuye a las cifras sustituidas el significado de constantes simbólicas."""
    elementos = elementos_sustitucion(expresion)
    if not elementos:
        return ""
    return "Elementos de la expresión\n" + "\n".join(f"{clave}: {texto}" for clave, texto in elementos)
