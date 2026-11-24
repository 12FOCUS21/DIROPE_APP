"""Primeros tres módulos y sus ejemplos de aceptación."""

from .. import nucleo as n
from ..formato import numero
from ..modelos import Insumo, Paso, Resultado
from .base import Campo, Modulo


def un_factor(datos: dict) -> Resultado:
    a = n.validar_numero(datos["antes"], "Producción antes", True)
    b = n.validar_numero(datos["despues"], "Producción después")
    h0 = n.validar_numero(datos["insumo_antes"], "Insumo antes", True)
    h1 = n.validar_numero(datos["insumo_despues"], "Insumo después", True)
    unidad = str(datos["unidad"]).strip()
    if not unidad:
        raise ValueError("Escribe la unidad de productividad (por ejemplo, cajas/h).")
    p0, p1 = n.productividad(a, h0), n.productividad(b, h1)
    cambio = n.cambio_pct(p0, p1)
    pasos = (
        Paso("Productividad inicial", "Dividimos la producción entre el insumo inicial.",
             "P₀ = Q₀ / I₀", f"{numero(a)} / {numero(h0)}", p0, unidad),
        Paso("Productividad final", "Dividimos la producción entre el insumo final.",
             "P₁ = Q₁ / I₁", f"{numero(b)} / {numero(h1)}", p1, unidad),
        Paso("Incremento unitario", "Restamos las productividades.", "ΔP = P₁ − P₀",
             f"{numero(p1, 6)} − {numero(p0, 6)}", p1 - p0, unidad),
        Paso("Cambio porcentual", "Comparamos el cambio con la productividad inicial.",
             "Δ% = (P₁ − P₀) / P₀ × 100",
             f"({numero(p1, 6)} − {numero(p0, 6)}) / {numero(p0, 6)} × 100", cambio, "%"),
    )
    return Resultado(pasos, f"La productividad cambia {numero(cambio, 2)} %; "
                     f"la diferencia es {numero(p1 - p0)} {unidad}.")


def multifactor(datos: dict) -> Resultado:
    produccion = n.validar_numero(datos["produccion"], "Producción")
    insumos = [Insumo(**fila) for fila in datos["insumos"]]
    total = n.costo_total(insumos)
    pasos = [Paso(f"Costo: {i.nombre}", "Multiplicamos cantidad por precio unitario.",
                  "Cᵢ = cantidad × precio", f"{numero(i.cantidad)} × ${numero(i.precio, 2)}",
                  i.cantidad * i.precio, "$") for i in insumos]
    pasos.append(Paso("Costo total", "Sumamos los costos de todos los insumos.",
                      "C = Σ Cᵢ", " + ".join(numero(i.cantidad * i.precio, 2) for i in insumos), total, "$"))
    laboral = [i for i in insumos if i.es_laboral]
    if laboral:
        horas = sum(i.cantidad for i in laboral)
        costo_laboral = sum(i.cantidad * i.precio for i in laboral)
        pasos.append(Paso("Productividad laboral por hora", "Solo las filas marcadas como horas laborales.",
                          "PL = Q / horas", f"{numero(produccion)} / {numero(horas)}",
                          n.productividad(produccion, horas), "unidades/h"))
        if costo_laboral > 0:
            pasos.append(Paso("Productividad por costo laboral", "No confundir con unidades por hora.",
                              "PL$ = Q / costo laboral", f"{numero(produccion)} / {numero(costo_laboral, 2)}",
                              n.productividad(produccion, costo_laboral), "unidades/$ laboral"))
    pm = n.multifactor(produccion, insumos)
    pasos.append(Paso("Productividad multifactor", "Dividimos la producción entre el costo total.",
                      "PM = Q / C", f"{numero(produccion)} / {numero(total, 2)}", pm, "unidades/$"))
    return Resultado(tuple(pasos), f"Por cada dólar de insumos se obtienen {numero(pm, 6)} unidades. "
                     "Todos los precios deben estar expresados en la misma moneda.")


def capacidad(datos: dict) -> Resultado:
    actual = n.validar_numero(datos["actual"], "Producción actual", True)
    crecimiento = n.validar_numero(datos["crecimiento"], "Crecimiento")
    prod = n.validar_numero(datos["productividad"], "Productividad laboral", True)
    jornada = n.validar_numero(datos["horas"], "Horas por persona", True)
    meta = n.finito(actual * (1 + crecimiento / 100))
    h0, h1 = n.horas_necesarias(actual, prod), n.horas_necesarias(meta, prod)
    p0, p1 = n.personas_necesarias(h0, jornada), n.personas_necesarias(h1, jornada)
    e0, e1 = n.personal_entero(p0), n.personal_entero(p1)
    pasos = (
        Paso("Meta de producción", "Aplicamos el crecimiento al mismo período.", "Meta = Q × (1 + g / 100)",
             f"{numero(actual)} × (1 + {numero(crecimiento, 2)} / 100)", meta, "unidades"),
        Paso("Horas actuales", "Usamos la productividad laboral publicada.", "H₀ = Q / PL",
             f"{numero(actual)} / {numero(prod, 6)}", h0, "h"),
        Paso("Horas necesarias", "Dividimos la meta entre la productividad.", "H₁ = Meta / PL",
             f"{numero(meta)} / {numero(prod, 6)}", h1, "h"),
        Paso("Personal actual calculado", "Equivalentes de tiempo completo, no una plantilla observada.",
             "N₀ = H₀ / h por persona", f"{numero(h0, 6)} / {numero(jornada)}", p0, "personas"),
        Paso("Personal necesario calculado", "Equivalentes antes del ajuste a personas enteras.",
             "N₁ = H₁ / h por persona", f"{numero(h1, 6)} / {numero(jornada)}", p1, "personas"),
        Paso("Personal actual entero", "Tolerancia de 0.01 al entero más próximo; fuera de ella, techo.",
             "N₀ entero = ajuste(N₀)", f"Valor sin ajuste: {numero(p0, 8)}; se toma {e0}", e0, "personas"),
        Paso("Personal necesario entero", "Supone productividad de entrada redondeada, no datos exactos.",
             "N₁ entero = ajuste(N₁)", f"Valor sin ajuste: {numero(p1, 8)}; se toma {e1}", e1, "personas"),
        Paso("Personal adicional", "Restamos las plantillas calculadas.", "Adicional = N₁ entero − N₀ entero",
             f"{e1} − {e0}", e1 - e0, "personas"),
    )
    return Resultado(pasos, f"Se requieren {e1} personas en total y {e1 - e0} adicionales. "
                     "Producción y horas por persona deben corresponder al mismo período. "
                     "La tolerancia de 0.01 es un supuesto pendiente de confirmar.")


UN_FACTOR = Modulo("un_factor", "Un factor", (
    Campo("antes", "Producción antes"), Campo("despues", "Producción después"),
    Campo("insumo_antes", "Cantidad del insumo antes"), Campo("insumo_despues", "Cantidad del insumo después"),
    Campo("unidad", "Unidad del resultado", "unidades/h")), un_factor, {
        "Chuck Sox (T1)": dict(antes=120, despues=125, insumo_antes=40, insumo_despues=40, unidad="cajas/h"),
        "Lori Cook (T2)": dict(antes=100, despues=133, insumo_antes=5, insumo_despues=5, unidad="paquetes/h"),
    })

MULTIFACTOR = Modulo("multifactor", "Multifactor", (Campo("produccion", "Producción"),), multifactor, {
    "Kleen Karpet (T3)": dict(produccion=65, insumos=[
        dict(nombre="Mano de obra", cantidad=520, precio=13, es_laboral=True),
        dict(nombre="Limpieza (gal)", cantidad=100, precio=5, es_laboral=False),
        dict(nombre="Equipo (días)", cantidad=20, precio=50, es_laboral=False)]),
    "Lakefront inicial (T4)": dict(produccion=1000, insumos=[
        dict(nombre="Mano de obra", cantidad=400, precio=12.5, es_laboral=True),
        dict(nombre="Materia prima", cantidad=1, precio=20000, es_laboral=False),
        dict(nombre="Energía", cantidad=1, precio=5000, es_laboral=False),
        dict(nombre="Capital", cantidad=1, precio=10000, es_laboral=False)]),
}, tabla_insumos=True)

CAPACIDAD = Modulo("capacidad", "Capacidad y personal", (
    Campo("actual", "Producción actual del período"), Campo("crecimiento", "Crecimiento (%)"),
    Campo("productividad", "Productividad (unidades/h)"), Campo("horas", "Horas por persona en el período")), capacidad, {
        "Lackey (T5)": dict(actual=1500, crecimiento=25, productividad=2.344, horas=160),
    })
