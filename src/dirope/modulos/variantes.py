"""Comparaciones y despejes sobre los modelos de productividad y capacidad."""

from decimal import Decimal
from fractions import Fraction
from math import ceil

from .. import nucleo as n
from ..formato import numero
from ..modelos import Paso, Resultado
from .campos import MODOS


def validar_modo(datos, modulo):
    modo = datos.get("modo")
    if not isinstance(modo, str) or modo not in MODOS[modulo]:
        raise ValueError("Selecciona un cálculo disponible.")
    return modo


def texto(datos, clave, etiqueta):
    valor = str(datos.get(clave, "")).strip()
    if not valor:
        raise ValueError(f"Indica {etiqueta}.")
    return valor


def diferencias(titulo, antes, despues, unidad, *, auxiliar=False):
    delta = despues - antes
    pasos = [Paso(f"Diferencia de {titulo}", "", "Δ = final − inicial",
                  f"{numero(despues, 8)} − {numero(antes, 8)}", delta, unidad, auxiliar)]
    if antes > 0:
        pasos.append(Paso(f"Cambio de {titulo}", "", "Δ% = (final − inicial) / inicial × 100",
                          f"({numero(despues, 8)} − {numero(antes, 8)}) / {numero(antes, 8)} × 100",
                          n.cambio_pct(antes, despues), "%", auxiliar))
    return pasos


def factor_flexible(datos):
    modo = validar_modo(datos, "un_factor")
    salida = texto(datos, "unidad_salida", "la unidad de producción")
    recurso = texto(datos, "unidad_recurso", "la unidad del recurso")
    unidad = f"{salida}/{recurso}"
    if modo == "Comparar conformidad":
        return comparar_conformidad(datos, salida, recurso)
    if modo in ("Producción requerida", "Recurso requerido"):
        p = n.validar_numero(datos.get("ritmo", ""), f"Productividad ({unidad})", modo == "Recurso requerido")
        if modo == "Producción requerida":
            i = n.validar_numero(datos.get("insumo_antes", ""), "Recurso", True)
            paso = Paso(modo, "", "Q = P × I", f"{numero(p, 8)} × {numero(i, 8)}", n.finito(p * i), salida)
        else:
            q = n.validar_numero(datos.get("antes", ""), "Producción")
            paso = Paso(modo, "", "I = Q / P", f"{numero(q, 8)} / {numero(p, 8)}", n.productividad(q, p), recurso)
        return Resultado((paso,), "El resultado usa la productividad indicada.", (paso,), principal=paso)
    comparar = modo == "Comparar escenarios"
    pasos = []
    valores = []
    for sufijo, nombre in (("antes", "Inicial"), ("despues", "Final")) if comparar else (("antes", "Único"),):
        q = n.validar_numero(datos.get(sufijo, ""), f"Producción · {nombre}")
        i = n.validar_numero(datos.get(f"insumo_{sufijo}", ""), f"Recurso · {nombre}", True)
        p = n.productividad(q, i)
        valores.append((q, i, p))
        pasos.append(Paso(f"Productividad · {nombre}", "", "P = Q / I",
                          f"{numero(q, 8)} / {numero(i, 8)}", p, unidad))
    if comparar:
        for indice, titulo, medida in ((2, "productividad", unidad), (0, "producción", salida), (1, "recurso", recurso)):
            pasos.extend(diferencias(titulo, valores[0][indice], valores[1][indice], medida, auxiliar=indice != 2))
    mensaje = "Productividad por unidad del recurso."
    if comparar and 0 in valores[0]:
        mensaje += " La variación porcentual de una magnitud con base cero queda indefinida."
    return Resultado(tuple(pasos), mensaje, tuple(pasos[:4]),
                     tuple((nombre, valor[2]) for nombre, valor in zip(("Inicial", "Final"), valores)) if comparar else (),
                     unidad, "Productividad por escenario", principal=pasos[min(3, len(pasos) - 1)])


def comparar_conformidad(datos, salida, recurso):
    pasos, valores = [], []
    unidad = f"{salida} conformes/{recurso}"
    medida = datos.get("medida_calidad", "Cantidad")
    if medida not in ("%", "Cantidad"):
        raise ValueError("Selecciona Cantidad o % como medida de no conformes.")
    es_porcentaje = medida == "%"
    for clave, nombre in (("antes", "Inicial"), ("despues", "Final")):
        cantidad = n.validar_numero(datos.get(clave, ""), f"Producción · {nombre}", True)
        defecto = n.validar_numero(datos.get(f"defecto_{clave}", ""), f"No conformes · {nombre}")
        insumo = n.validar_numero(datos.get(f"insumo_{clave}", ""), f"Recurso · {nombre}", True)
        if es_porcentaje:
            conformes = n.unidades_buenas(cantidad, defecto)
            formula = "Q conforme = Q × (1 − defectos / 100)"
            sustitucion = f"{numero(cantidad, 8)} × (1 − {numero(defecto, 8)} / 100)"
        else:
            if defecto > cantidad:
                raise ValueError(f"Los no conformes superan la producción del escenario {nombre.lower()}.")
            conformes = cantidad - defecto
            formula = "Q conforme = Q − defectos"
            sustitucion = f"{numero(cantidad, 8)} − {numero(defecto, 8)}"
        tasa = conformes / cantidad * 100
        productividad = n.productividad(conformes, insumo)
        pasos.extend((
            Paso(f"Producción conforme · {nombre}", "", formula, sustitucion, conformes, salida),
            Paso(f"Conformidad · {nombre}", "", "Q conforme / Q × 100",
                 f"{numero(conformes, 8)} / {numero(cantidad, 8)} × 100", tasa, "%"),
            Paso(f"Productividad conforme · {nombre}", "", "P = Q conforme / I",
                 f"{numero(conformes, 8)} / {numero(insumo, 8)}", productividad, unidad),
        ))
        valores.append((nombre, tasa, productividad))
    _, tasa_antes, p_antes = valores[0]
    _, tasa_despues, p_despues = valores[1]
    puntos = Paso("Cambio de conformidad", "", "Tasa final − tasa inicial",
                  f"{numero(tasa_despues, 8)} − {numero(tasa_antes, 8)}",
                  tasa_despues - tasa_antes, "puntos porcentuales")
    pasos.append(puntos)
    pasos.extend(diferencias("productividad conforme", p_antes, p_despues, unidad))
    mensaje = "La productividad se calcula con la producción conforme."
    if p_antes == 0:
        mensaje += " Su variación porcentual queda indefinida porque la base es cero."
    return Resultado(tuple(pasos), mensaje,
                     (pasos[2], pasos[5], puntos, pasos[-1]),
                     tuple((nombre, p) for nombre, _, p in valores), unidad, "Productividad conforme", principal=pasos[-1])


def fraccion_decimal(valor):
    """Representa exactamente una entrada numérica ya validada."""
    decimal = Decimal(str(valor).strip().replace(" ", "").replace("\u00a0", ""))
    return Fraction(decimal) if float(decimal) else Fraction(0)


def capacidad_flexible(datos):
    modo = validar_modo(datos, "capacidad")
    entrada_actual = datos.get("actual", "")
    actual = (n.validar_numero(entrada_actual, "Producción actual")
              if modo != "Meta directa" or str(entrada_actual).strip() else None)
    p = n.validar_numero(datos.get("productividad", ""), "Productividad laboral", True)
    jornada = n.validar_numero(datos.get("horas", ""), "Horas por persona", True)
    unidad = texto(datos, "unidad_salida", "la unidad de producción")
    periodo = texto(datos, "periodo", "el período")
    medida = f"{unidad}/{periodo}"
    actual_exacto = fraccion_decimal(entrada_actual) if actual is not None else None
    if modo == "Meta directa":
        meta = n.validar_numero(datos.get("meta", ""), "Meta")
        meta_exacta = fraccion_decimal(datos["meta"])
        paso_meta = Paso("Meta de producción", "", "Meta = demanda", numero(meta, 8), meta, medida)
    else:
        g = n.validar_numero(datos.get("crecimiento", ""), "Crecimiento (%)", admitir_negativo=True)
        crecimiento_exacto = fraccion_decimal(datos["crecimiento"])
        if crecimiento_exacto < -100:
            raise ValueError("El crecimiento no puede ser inferior a −100 %.")
        meta_exacta = actual_exacto * (1 + crecimiento_exacto / 100)
        meta = n.finito(actual * (1 + g / 100))
        paso_meta = Paso("Meta de producción", "", "Meta = Q × (1 + g / 100)",
                         f"{numero(actual, 8)} × (1 + {numero(g, 8)} / 100)", meta, medida)
    h = n.horas_necesarias(meta, p)
    n.personas_necesarias(h, jornada)
    capacidad_persona = fraccion_decimal(datos["productividad"]) * fraccion_decimal(datos["horas"])
    necesarios = ceil(meta_exacta / capacidad_persona)
    horas = Paso("Horas-persona requeridas", "", "H = Meta / P", f"{numero(meta, 8)} / {numero(p, 8)}", h, "h-persona")
    personal = Paso("Personal necesario", "", "N = techo(H / jornada)",
                    f"techo({numero(h, 8)} / {numero(jornada, 8)})", necesarios, "personas")
    pasos = []
    if actual is not None:
        pasos.append(Paso("Producción de referencia", "", "Q = producción actual", numero(actual, 8), actual, medida))
    pasos.extend((paso_meta, Paso("Productividad laboral", "", "P = ritmo indicado", numero(p, 8),
                                 p, f"{unidad}/h-persona"), horas, personal))
    indicadores = [paso_meta, horas, personal]
    equipo = str(datos.get("plantilla", "")).strip()
    serie = ()
    if equipo:
        plantilla = n.validar_numero(equipo, "Plantilla disponible")
        plantilla_exacta = fraccion_decimal(equipo)
        if plantilla_exacta.denominator != 1:
            raise ValueError("La plantilla disponible debe ser un número entero.")
        disponible = n.finito(plantilla * jornada * p)
        saldo = necesarios - int(plantilla_exacta)
        paso_saldo = Paso("Personal adicional (+) o excedente (−)", "Respecto de la plantilla indicada.",
                          "N necesario − N disponible", f"{necesarios} − {int(plantilla_exacta)}", saldo, "personas")
    elif actual is not None:
        disponible = actual
        n.finito((meta - actual) / p / jornada)
        saldo = ceil((meta_exacta - actual_exacto) / capacidad_persona)
        paso_saldo = Paso("Personal adicional (+) o excedente (−)", "Respecto de la producción actual, a ritmo constante.",
                          "techo((Meta − Q) / P / jornada)",
                          f"({numero(meta, 8)} − {numero(actual, 8)}) / {numero(p, 8)} / {numero(jornada, 8)}",
                          saldo, "personas")
    if equipo or actual is not None:
        base = Paso("Capacidad disponible" if equipo else "Producción de referencia", "",
                    "N disponible × jornada × P" if equipo else "Q actual",
                    f"{equipo} × {numero(jornada, 8)} × {numero(p, 8)}" if equipo else numero(actual, 8),
                    disponible, medida)
        if equipo:
            pasos.append(base)
        pasos.append(paso_saldo)
        indicadores.append(paso_saldo)
        serie = ((base.titulo, disponible), ("Demanda", meta))
    if actual is not None:
        h_adicionales = n.finito((meta - actual) / p)
        pasos.append(Paso("Cambio de horas-persona", "Respecto de la producción actual.",
                          "ΔH = (Meta − Q) / P", f"({numero(meta, 8)} − {numero(actual, 8)}) / {numero(p, 8)}",
                          h_adicionales, "h-persona", auxiliar=True))
    if modo == "Meta directa" and actual is not None and actual > 0:
        pasos.extend(diferencias("producción", actual, meta, medida, auxiliar=True))
    return Resultado(tuple(pasos), "El personal necesario se expresa en trabajadores enteros suficientes.",
                     tuple(indicadores), serie, medida, "Capacidad y demanda", principal=paso_saldo if equipo or actual is not None else personal)
def multifactor_flexible(datos):
    modo = validar_modo(datos, "multifactor")
    salida = texto(datos, "unidad_salida", "la unidad de producción")
    moneda = texto(datos, "moneda", "la moneda común")
    filas = datos.get("insumos", ())
    if modo == "Valor por calidad":
        horas = n.validar_numero(datos.get("horas_calidad", ""), "Horas-persona", True)
        if not filas:
            raise ValueError("Añade al menos una categoría.")
        pasos = []
        for fila in filas:
            nombre = texto(fila, "nombre", "el nombre de la categoría")
            q = n.validar_numero(fila.get("cantidad", ""), f"Cantidad de {nombre}")
            precio = n.validar_numero(fila.get("precio", ""), f"Valor unitario de {nombre}")
            pasos.append(Paso(f"Valor · {nombre}", f"{numero(q, 8)} {salida}", "V = cantidad × valor unitario",
                              f"{numero(q, 8)} × {numero(precio, 8)}", n.finito(q * precio), moneda))
        total = n.finito(sum(paso.resultado for paso in pasos))
        valor = Paso("Valor total", "", "V = Σ Vᵢ", " + ".join(numero(p.resultado, 8) for p in pasos), total, moneda)
        productividad = Paso("Productividad económica", "", "P = V / horas-persona",
                             f"{numero(total, 8)} / {numero(horas, 8)}", n.productividad(total, horas), moneda + "/h-persona")
        return Resultado(tuple([*pasos, valor, productividad]), "Rendimiento medido en valor de producción.",
                         (valor, productividad), principal=productividad)
    comparar = modo == "Comparar alternativas"
    escenarios = [("Inicial", "produccion"), ("Alternativa", "produccion_final")] if comparar else [("Base", "produccion")]
    if comparar and (str(datos.get("produccion_otra", "")).strip()
                     or any(fila.get("escenario") == "Alternativa 2" for fila in filas)):
        escenarios.append(("Alternativa 2", "produccion_otra"))
    pasos, indicadores, productividades, costos, composicion = [], [], [], [], []
    for escenario, campo in escenarios:
        q = n.validar_numero(datos.get(campo, ""), f"Producción · {escenario}")
        recursos = [fila for fila in filas if not comparar or fila.get("escenario", "Inicial") == escenario]
        if not recursos:
            raise ValueError(f"Añade insumos al escenario {escenario}.")
        partidas, horas, costo_laboral = [], [], []
        for fila in recursos:
            nombre = texto(fila, "nombre", "el nombre del recurso")
            moneda_fila = str(fila.get("moneda", "")).strip()
            if moneda_fila and moneda_fila.casefold() != moneda.casefold():
                raise ValueError(f"{nombre}: usa la moneda común {moneda}.")
            costo, sustitucion = costo_fila(fila)
            partidas.append((nombre, costo))
            pasos.append(Paso(f"Costo · {escenario} · {nombre}", "", "C = directo o cantidad × precio",
                              sustitucion, costo, moneda, auxiliar=True))
            if fila.get("es_laboral"):
                unidad_laboral = str(fila.get("unidad", "")).strip().casefold()
                if unidad_laboral and unidad_laboral not in ("h", "hora", "horas", "h-persona", "horas-persona"):
                    raise ValueError(f"{nombre}: las filas laborales deben usar horas-persona.")
                horas.append(n.validar_numero(fila.get("cantidad", ""), f"Horas-persona de {nombre}"))
                costo_laboral.append(costo)
        total = n.finito(sum(costo for _, costo in partidas))
        productividad = n.productividad(q, total)
        costos.append(total)
        productividades.append(productividad)
        pasos.append(Paso(f"Costo total · {escenario}", "", "C = Σ Cᵢ",
                          " + ".join(numero(c, 8) for _, c in partidas), total, moneda))
        indicadores.append(pasos[-1])
        pasos.append(Paso(f"Productividad · {escenario}", "", "PM = Q / C",
                          f"{numero(q, 8)} / {numero(total, 8)}", productividad, f"{salida}/{moneda}"))
        indicadores.append(pasos[-1])
        for nombre, costo in partidas:
            pasos.append(Paso(f"Participación · {escenario} · {nombre}", "", "Participación = Cᵢ / C × 100",
                              f"{numero(costo, 8)} / {numero(total, 8)} × 100", costo / total * 100, "%", auxiliar=True))
        composicion = partidas
        if horas:
            for etiqueta, denominador, unidad in (
                ("Productividad laboral por hora", sum(horas), f"{salida}/h-persona"),
                ("Productividad por costo laboral", sum(costo_laboral), f"{salida}/{moneda} laboral"),
            ):
                if denominador > 0 or etiqueta == "Productividad laboral por hora":
                    pasos.append(Paso(f"{etiqueta} · {escenario}", "", "PL = Q / insumo laboral",
                                      f"{numero(q, 8)} / {numero(denominador, 8)}", n.productividad(q, denominador), unidad, auxiliar=comparar))
                    if not comparar:
                        indicadores.append(pasos[-1])
    if comparar:
        for indice, (nombre, _) in enumerate(escenarios[1:], 1):
            pasos.extend(diferencias(f"costo · {nombre}", costos[0], costos[indice], moneda, auxiliar=True))
            cambios = diferencias(f"productividad · {nombre}", productividades[0], productividades[indice], f"{salida}/{moneda}")
            pasos.extend(cambios)
            indicadores.append(cambios[-1])
        mayor = max(productividades)
        mejores = [nombre for (nombre, _), p in zip(escenarios, productividades) if p == mayor]
        mensaje = "Mayor productividad con los costos incluidos: " + ", ".join(mejores) + "."
        if productividades[0] == 0:
            mensaje += " La variación porcentual de productividad queda indefinida porque la base es cero."
        return Resultado(tuple(pasos), mensaje, tuple(indicadores),
                         tuple((e[0], p) for e, p in zip(escenarios, productividades)), f"{salida}/{moneda}",
                         "Productividad por escenario",
                         principal=indicadores[-1] if len(escenarios) == 2 else None)
    composicion.sort(key=lambda partida: partida[1], reverse=True)
    if len(composicion) > 5:
        composicion = [*composicion[:4], ("Otros insumos", sum(c for _, c in composicion[4:]))]
    return Resultado(tuple(pasos), "La composición muestra cuánto representa cada recurso en el costo total.",
                     tuple(indicadores), tuple(composicion), moneda, "Composición de insumos", "composicion",
                     principal=indicadores[1])


def costo_fila(fila):
    directo = str(fila.get("directo", "")).strip()
    if directo:
        if str(fila.get("precio", "")).strip():
            raise ValueError("Indica costo directo o precio unitario en cada fila.")
        if str(fila.get("cantidad", "")).strip():
            n.validar_numero(fila["cantidad"], "Cantidad")
        costo = n.validar_numero(directo, "Costo directo")
        return costo, numero(costo, 8)
    cantidad = n.validar_numero(fila.get("cantidad", ""), "Cantidad")
    precio = n.validar_numero(fila.get("precio", ""), "Costo unitario")
    return n.finito(cantidad * precio), f"{numero(cantidad, 8)} × {numero(precio, 8)}"
