"""Análisis estructurado de problemas; no interpreta automáticamente lenguaje natural."""

from dataclasses import dataclass

from .modelos import Insumo, Resultado
from .modulos import MODULOS
from .modulos.campos import CAMPOS_COMUNES, MODOS
from .nucleo import costo_total, validar_numero


@dataclass(frozen=True)
class PerfilProblema:
    tipo: str
    objetivo: str
    criterio: str
    incognitas: tuple[str, ...]
    formulas: tuple[str, ...]
    supuestos: tuple[str, ...]


PERFILES = {
    "un_factor": PerfilProblema(
        "Productividad de un factor con comparación",
        "Comparar productividad, diferencia unitaria y cambio porcentual entre dos escenarios.",
        "Se dispone de producción y de un mismo tipo de insumo en dos escenarios comparables.",
        ("Productividad inicial y final", "Incremento unitario", "Cambio porcentual"),
        ("P₀ = Q₀ / I₀", "P₁ = Q₁ / I₁", "ΔP = P₁ − P₀", "Δ% = (P₁ − P₀) / P₀ × 100"),
        ("El insumo debe representar la misma magnitud en ambos escenarios.",
         "Producción e insumo deben corresponder a períodos y unidades comparables.",
         "Si se indican trabajadores y horas por trabajador, convierte primero a horas-persona.")),
    "multifactor": PerfilProblema(
        "Productividad multifactor por costo",
        "Calcular costos y productividad respecto al conjunto de insumos.",
        "Hay una producción y uno o más insumos que pueden expresarse en una moneda común.",
        ("Costo de cada insumo y costo total", "Productividad multifactor",
         "Productividad laboral si se registran horas"),
        ("Cᵢ = cantidad × precio unitario", "C = Σ Cᵢ", "PM = Q / C", "PL = Q / horas laborales"),
        ("Todos los precios deben usar la misma moneda; esta versión presenta el símbolo $.",
         "Marca Horas solo si la cantidad de esa fila está expresada en horas-persona.",
         "Un costo global se registra como cantidad 1 y precio igual al costo.",
         "La producción se presenta como unidades; no se realizan conversiones automáticas.")),
    "capacidad": PerfilProblema(
        "Planeación de capacidad y personal",
        "Determinar la meta, las horas y el personal para un crecimiento de producción.",
        "Se conocen producción actual, crecimiento, productividad laboral y horas por persona.",
        ("Meta de producción", "Horas actuales y necesarias", "Personal total y adicional"),
        ("Meta = Q × (1 + g / 100)", "H = producción / productividad laboral", "N = H / horas por persona"),
        ("La productividad laboral se mantiene constante al aumentar la producción.",
         "Producción y horas por persona corresponden al mismo período.",
         "El personal actual se estima a partir de los datos; no es una plantilla observada.",
         "Se aplica tolerancia de 0.01 cerca de un entero; supone productividad publicada redondeada.")),
}


@dataclass(frozen=True)
class AnalisisProblema:
    perfil: PerfilProblema
    datos: tuple[tuple[str, str], ...]


def validar_planteamiento(enunciado: str, objetivo: str) -> None:
    """El usuario redacta el problema y el objetivo; no se extraen cifras del texto."""
    if not enunciado.strip():
        raise ValueError("Escribe el planteamiento del problema antes de continuar.")
    if not objetivo.strip():
        raise ValueError("Indica qué necesitas encontrar en este problema.")


def analizar_datos(clave: str, datos: dict, *, resultado: Resultado | None = None) -> AnalisisProblema:
    """Valida y documenta el método elegido a partir de datos estructurados."""
    if clave not in PERFILES:
        raise ValueError("Este tipo de problema todavía no está disponible.")
    if "modo" in datos:
        if resultado is None:
            modulo = next(m for m in MODULOS if m.clave == clave)
            resultado = modulo.calcular(datos)
        modo = datos["modo"]
        supuestos = ["Las cantidades de cada escenario corresponden al mismo período."]
        if clave == "multifactor":
            supuestos.append("Todos los valores monetarios usan la moneda seleccionada.")
        elif clave == "capacidad":
            supuestos.append("La productividad laboral por hora se mantiene constante.")
        else:
            supuestos.append("La producción y el recurso usan las mismas unidades en ambos escenarios.")
        perfil = PerfilProblema(
            modo, modo, "Método seleccionado con los datos registrados.",
            tuple(paso.titulo for paso in resultado.indicadores),
            tuple(dict.fromkeys(paso.formula for paso in resultado.pasos)), tuple(supuestos),
        )
        filas = [(CAMPOS_COMUNES[campo].etiqueta, str(datos[campo]))
                 for campo in MODOS[clave][modo] if str(datos.get(campo, "")).strip()]
        for fila in datos.get("insumos", ()):
            campos = (("escenario", ""), ("cantidad", "Cantidad "), ("unidad", ""),
                      ("precio", "Valor unitario " if modo == "Valor por calidad" else "Costo unitario "),
                      ("directo", "Costo directo "))
            detalle = [f"{etiqueta}{fila[campo]}" for campo, etiqueta in campos if str(fila.get(campo, "")).strip()]
            if fila.get("es_laboral"):
                detalle.append("Horas-persona")
            filas.append((fila["nombre"], " · ".join(detalle)))
        return AnalisisProblema(perfil, tuple(filas))
    filas = []
    if clave == "un_factor":
        campos = (("antes", "Producción antes", True), ("despues", "Producción después", False),
                  ("insumo_antes", "Insumo antes", True), ("insumo_despues", "Insumo después", True))
    elif clave == "capacidad":
        campos = (("actual", "Producción actual", True), ("crecimiento", "Crecimiento (%)", False),
                  ("productividad", "Productividad (unidades/h)", True), ("horas", "Horas por persona", True))
    else:
        campos = (("produccion", "Producción", False),)
    for campo, etiqueta, positivo in campos:
        valor = validar_numero(datos.get(campo, ""), etiqueta, positivo)
        filas.append((etiqueta, str(valor)))
    if clave == "un_factor":
        unidad = str(datos.get("unidad", "")).strip()
        if not unidad:
            raise ValueError("Indica la unidad del resultado, por ejemplo cajas/h.")
        filas.append(("Unidad de productividad", unidad))
    if clave == "multifactor":
        insumos = []
        for fila in datos.get("insumos", []):
            nombre = str(fila.get("nombre", "")).strip()
            cantidad = validar_numero(fila.get("cantidad", ""), f"Cantidad de {nombre or 'insumo'}")
            precio = validar_numero(fila.get("precio", ""), f"Precio de {nombre or 'insumo'}")
            laboral = fila.get("es_laboral", False)
            if not isinstance(laboral, bool):
                raise ValueError("La marca Horas debe ser un valor lógico.")
            insumos.append(Insumo(nombre, cantidad, precio, laboral))
            filas.append((nombre, f"Cantidad: {cantidad}; precio: ${precio}" + ("; horas laborales" if laboral else "")))
        costo_total(insumos)
        if any(i.es_laboral for i in insumos) and sum(i.cantidad for i in insumos if i.es_laboral) <= 0:
            raise ValueError("Las filas marcadas como Horas deben sumar más de cero.")
    return AnalisisProblema(PERFILES[clave], tuple(filas))


def describir_ejemplo(clave: str, datos: dict) -> str:
    """Describe los valores reales del ejemplo, sin depender del nombre del ejercicio."""
    if clave in PERFILES and datos.get("enunciado"):
        return datos["enunciado"]
    if clave == "un_factor":
        return (f"Se producen {datos['antes']} unidades con {datos['insumo_antes']} de insumo. "
                f"En el segundo escenario se producen {datos['despues']} unidades con {datos['insumo_despues']} de insumo. "
                f"La productividad se expresará en {datos['unidad']}. Compara ambos escenarios.")
    if clave == "multifactor":
        detalle = "; ".join(f"{i['nombre']}: {i['cantidad']} × ${i['precio']}" for i in datos["insumos"])
        return f"La producción es {datos['produccion']} unidades. Insumos: {detalle}. Determina costos y productividad."
    if clave == "capacidad":
        return (f"La producción actual es {datos['actual']} unidades por período y se busca crecer {datos['crecimiento']} %. "
                f"La productividad es {datos['productividad']} unidades/h y cada persona trabaja {datos['horas']} h por período. "
                "Determina la capacidad y el personal requeridos.")
    raise ValueError("No hay una descripción disponible para este tipo de problema.")
