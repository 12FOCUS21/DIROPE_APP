"""Ayuda y validación de campos editables, sin dependencias de la interfaz."""

from .modulos.campos import CAMPOS_COMUNES, MODOS
from .nucleo import decimal_exacto, validar_numero


TEXTOS = {"unidad_salida", "unidad_recurso", "recurso", "moneda", "periodo"}
FORMATO = "Usa punto decimal (2.5) y espacios de miles (1 500). No uses coma, NaN ni infinito."
NOTA_NO_CONFORMES = (
    "Son las unidades producidas que no cumplen los requisitos de calidad (por ejemplo, piezas dañadas "
    "o fuera de especificación). No son las unidades buenas ni la diferencia entre escenarios.\n"
    "• Cantidad: de 125 unidades, 5 no conformes → escribe 5; quedan 120 conformes.\n"
    "• Porcentaje (%): de 125 unidades, 4 % no conformes → escribe 4, no 0.04; quedan 120 conformes.\n"
    "Usa la misma medida en ambos escenarios y el mismo período que la producción. "
    "Si no hubo no conformes, escribe 0. No dejes el campo vacío: vacío significa dato sin indicar."
)


def regla_campo(clave, datos):
    """Regla contextual: (opcional, positivo, mínimo, máximo, entero)."""
    modo = datos.get("modo")
    opcional = clave in ("plantilla", "produccion_otra") or (clave == "actual" and modo == "Meta directa")
    positivo = clave in ("insumo_antes", "insumo_despues", "productividad", "horas", "horas_calidad")
    positivo |= clave == "ritmo" and modo == "Recurso requerido"
    positivo |= clave in ("antes", "despues") and modo == "Comparar conformidad"
    minimo = -100 if clave == "crecimiento" else 0
    maximo = 100 if clave.startswith("defecto_") and datos.get("medida_calidad") == "%" else None
    return opcional, positivo, minimo, maximo, clave == "plantilla"


def ayuda_campo(clave, datos):
    """Describe el tipo y el dominio admitidos, incluidos los campos opcionales."""
    ejemplos = {"unidad_salida": "cajas", "unidad_recurso": "h-persona", "recurso": "Trabajo",
                "moneda": "USD o $", "periodo": "mes"}
    if clave in TEXTOS:
        return f"Texto obligatorio. Ejemplo: {ejemplos[clave]}."
    if clave == "medida_calidad":
        return "Selecciona Cantidad o %. En cantidad, no superes la producción; en %, usa de 0 a 100."
    if clave.startswith("defecto_"):
        medida = datos.get("medida_calidad", "Cantidad")
        return ("Obligatorio: porcentaje de unidades que no cumplen calidad, entre 0 y 100. "
                "Ejemplo: para 4 %, escribe 4. Si no hubo, escribe 0." if medida == "%" else
                "Obligatorio: cantidad de unidades que no cumplen calidad; no puede superar la producción "
                "del escenario. Ejemplo: de 125, 5 no conformes → escribe 5. Si no hubo, escribe 0.")
    opcional, positivo, minimo, maximo, entero = regla_campo(clave, datos)
    dominio = "entero ≥ 0" if entero else "número > 0" if positivo else f"número ≥ {minimo}"
    if maximo is not None:
        dominio = "porcentaje entre 0 y 100"
    return f"{'Opcional; vacío = no indicado' if opcional else 'Obligatorio'}: {dominio}. {FORMATO}"


def errores_entrada(modulo, datos):
    """Devuelve todos los errores de campo; el motor comprueba además las relaciones globales."""
    errores = {}
    modo = datos.get("modo")
    if modo not in MODOS.get(modulo, {}):
        return {"modo": "Selecciona un cálculo disponible."}
    valores = {}
    for clave in MODOS[modulo][modo]:
        valor = datos.get(clave, "")
        nombre = CAMPOS_COMUNES[clave].etiqueta
        if clave in TEXTOS:
            if not str(valor).strip():
                errores[clave] = f"{nombre}: {ayuda_campo(clave, datos)}"
            continue
        if clave == "medida_calidad":
            if valor not in ("Cantidad", "%"):
                errores[clave] = "Selecciona Cantidad o %."
            continue
        opcional, positivo, minimo, maximo, entero = regla_campo(clave, datos)
        if opcional and not str(valor).strip():
            continue
        try:
            if clave.startswith("defecto_") and not str(valor).strip():
                medida = "el porcentaje" if datos.get("medida_calidad") == "%" else "la cantidad"
                raise ValueError(f"{nombre}: el campo está vacío. Indica {medida} de unidades no conformes. "
                                 "Si no hubo, escribe 0.")
            validar_numero(valor, nombre, positivo, admitir_negativo=clave == "crecimiento")
            exacto = decimal_exacto(valor, nombre)
            if exacto < minimo or (maximo is not None and exacto > maximo):
                raise ValueError(f"{nombre}: debe estar entre {minimo} y {maximo}." if maximo is not None
                                 else f"{nombre}: no puede ser inferior a {minimo}.")
            if entero and exacto != exacto.to_integral_value():
                raise ValueError(f"{nombre}: escribe un número entero de personas (0, 1, 2…).")
            valores[clave] = exacto
        except ValueError as error:
            errores[clave] = str(error)
    if modo == "Comparar conformidad" and datos.get("medida_calidad") == "Cantidad":
        for escenario in ("antes", "despues"):
            clave = f"defecto_{escenario}"
            if clave in valores and escenario in valores and valores[clave] > valores[escenario]:
                errores[clave] = "Los no conformes no pueden superar la producción del mismo escenario."
    for indice, fila in enumerate(datos.get("insumos", ())):
        prefijo = f"insumos.{indice}."
        if not str(fila.get("nombre", "")).strip():
            errores[prefijo + "nombre"] = "Escribe el nombre del recurso o categoría."
        directo = modo != "Valor por calidad" and bool(str(fila.get("directo", "")).strip())
        for clave in ("cantidad", "precio", "directo"):
            valor = fila.get(clave, "")
            if clave == "directo" and (modo == "Valor por calidad" or not directo):
                continue
            if directo and clave in ("cantidad", "precio") and not str(valor).strip():
                continue
            try:
                validar_numero(valor, f"Fila {indice + 1} · {clave}")
            except ValueError as error:
                errores[prefijo + clave] = str(error)
        if directo and str(fila.get("precio", "")).strip():
            errores[prefijo + "precio"] = "Usa costo directo o cantidad × costo unitario, no ambos."
        if modo != "Valor por calidad" and fila.get("es_laboral"):
            unidad = str(fila.get("unidad", "")).strip().casefold()
            if unidad and unidad not in ("h", "hora", "horas", "h-persona", "horas-persona"):
                errores[prefijo + "unidad"] = "Para trabajo usa h-persona (o h, hora, horas, horas-persona)."
            try:
                validar_numero(fila.get("cantidad", ""), "Horas-persona")
            except ValueError as error:
                errores[prefijo + "cantidad"] = str(error)
    return errores
