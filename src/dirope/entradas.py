"""Ayuda y validación de campos editables, sin dependencias de la interfaz."""

from .modulos.campos import CAMPOS_COMUNES, MODOS
from .nucleo import decimal_exacto, validar_numero


TEXTOS = {"unidad_salida", "unidad_recurso", "recurso", "moneda", "periodo"}
FORMATO = "En los campos numéricos, escribe solo el número: 12, 2.5 o 1 500 son ejemplos. Usa punto decimal (2.5, no 2,5). No agregues unidades, signos de moneda ni % al número."
NOTA_NO_CONFORMES = (
    "Son las unidades producidas que no cumplen los requisitos de calidad (por ejemplo, piezas dañadas "
    "o fuera de especificación). No son las unidades buenas ni la diferencia entre escenarios.\n"
    "• Cantidad: de 125 unidades, 5 no conformes → escribe 5; quedan 120 conformes.\n"
    "• Porcentaje (%): de 125 unidades, 4 % no conformes → escribe 4, no 0.04; quedan 120 conformes.\n"
    "Usa la misma medida en ambos escenarios y el mismo período que la producción. "
    "Si no hubo no conformes, escribe 0. No dejes el campo vacío: vacío significa dato sin indicar."
)

GUIAS = {
    "unidad_salida": "Escribe qué se produce. Ejemplo: cajas.",
    "unidad_recurso": "Escribe cómo se mide el recurso. Ejemplo: h-persona, kg o kWh.",
    "recurso": "Ponle nombre a lo que se usa para producir. Ejemplo: Trabajo.",
    "moneda": "Escribe la moneda que usarás para todos los costos. Ejemplo: USD o $.",
    "periodo": "Escribe el tiempo que abarca el ejercicio. Ejemplo: semana o mes.",
    "antes": "Cantidad producida al inicio. Ejemplo: 120.",
    "despues": "Cantidad producida al final. Ejemplo: 150.",
    "insumo_antes": "Cuánto recurso se usó al inicio, en la unidad elegida. Ejemplo: 40.",
    "insumo_despues": "Cuánto recurso se usó al final, en la misma unidad. Ejemplo: 45.",
    "ritmo": "Cuánto se espera producir por cada unidad de recurso. Si son 3 cajas por hora-persona, escribe 3.",
    "produccion": "Total producido al inicio o en el único escenario. Ejemplo: 120.",
    "produccion_final": "Total producido con la primera opción. Ejemplo: 150.",
    "produccion_otra": "Total con la segunda opción. Ejemplo: 160. Déjalo vacío si no comparas una segunda opción.",
    "horas_calidad": "Horas de trabajo de todas las personas juntas. Si 3 personas trabajan 8 horas cada una, escribe 24.",
    "actual": "Total que se produce ahora en el período elegido. Ejemplo: 100.",
    "crecimiento": "Si esperas subir 25 %, escribe 25; para bajar 10 %, escribe -10. Sin cambios, escribe 0.",
    "meta": "Cantidad que se necesita producir en ese período. Ejemplo: 125.",
    "productividad": "Cuánto produce una persona en una hora. Si produce 2.5 cajas, escribe 2.5.",
    "horas": "Horas que trabaja una sola persona en el período. Si trabaja 8 horas al día, para un día escribe 8.",
    "plantilla": "Personas con las que ya cuentas. Ejemplo: 4. Escribe 0 si no hay ninguna; vacío si no lo sabes.",
}

ESCENARIOS = ("Inicial", "Alternativa", "Alternativa 2")


def ayuda_insumo(clave, *, calidad=False):
    """Guía común para las columnas de gastos y categorías."""
    guias = {
        "escenario": "Elige a qué opción pertenece esta fila: Inicial es antes del cambio.",
        "nombre": "Texto obligatorio. Ejemplo: Primera calidad." if calidad else "Texto obligatorio. Ejemplo: Madera.",
        "cantidad": "Número de piezas de esta categoría. Ejemplo: 12." if calidad else
                    "Número usado. Ejemplo: 12. Si usas costo directo, puede quedar vacío salvo en trabajo.",
        "precio": "Valor de una pieza. Ejemplo: 2.5." if calidad else
                  "Costo de una unidad. Ejemplo: 2.5. Déjalo vacío si llenas costo directo.",
        "directo": "Costo total de esta fila. Ejemplo: 30. Déjalo vacío si indicaste el costo unitario.",
        "unidad": "Texto opcional. Ejemplo: kg. Si marcas trabajo, usa h-persona.",
        "es_laboral": "Marca solo si esta fila mide trabajo. Escribe las horas totales en Cantidad.",
    }
    return guias[clave]


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
    if clave in TEXTOS:
        return f"Texto obligatorio. {GUIAS[clave]}"
    if clave == "medida_calidad":
        return "Selecciona Cantidad o %. En cantidad, no superes la producción; en %, usa de 0 a 100."
    if clave.startswith("defecto_"):
        medida = datos.get("medida_calidad", "Cantidad")
        return ("Obligatorio: porcentaje de unidades que no cumplen calidad, entre 0 y 100. "
                "Ejemplo: para 4 %, escribe 4. Si no hubo, escribe 0." if medida == "%" else
                "Obligatorio: cantidad de unidades que no cumplen calidad; no puede superar la producción "
                "del escenario. Ejemplo: de 125, 5 no conformes → escribe 5. Si no hubo, escribe 0.")
    opcional, positivo, minimo, maximo, entero = regla_campo(clave, datos)
    guia = GUIAS[clave]
    if clave == "antes" and datos.get("modo") == "Recurso requerido":
        guia = "Cuánto necesitas producir. Ejemplo: 120."
    if clave == "insumo_antes" and datos.get("modo") == "Producción requerida":
        guia = "Cuánto recurso tienes disponible. Ejemplo: 40."
    if clave in ("antes", "despues") and datos.get("modo") == "Comparar conformidad":
        guia += " Incluye lo que salió bien y lo que no cumplió."
    dominio = ("Número entero, sin decimales" if entero else "Número mayor que 0" if positivo else
               "Número desde -100" if minimo < 0 else "Número desde 0")
    tipo = "Opcional" if opcional else "Obligatorio"
    return f"{tipo}. {guia} {dominio}."


def errores_entrada(modulo, datos):
    """Devuelve todos los errores de campo; el motor comprueba además las relaciones globales."""
    errores = {}
    modo = datos.get("modo")
    if not isinstance(modo, str) or modo not in MODOS.get(modulo, {}):
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
    filas = datos.get("insumos", ())
    if modo == "Comparar alternativas":
        escenarios = {fila.get("escenario", "Inicial") for fila in filas}
        tercera = bool(str(datos.get("produccion_otra", "")).strip())
        if "Alternativa 2" in escenarios and not tercera:
            errores["produccion_otra"] = "Escribe la producción de Alternativa 2 o quita las filas de esa opción."
        requeridos = ESCENARIOS if tercera else ESCENARIOS[:2]
        faltantes = [escenario for escenario in requeridos if escenario not in escenarios]
        if faltantes:
            errores["insumos"] = "Añade al menos una fila de insumos para: " + ", ".join(faltantes) + "."
    elif modulo == "multifactor" and not filas:
        errores["insumos"] = ("Añade al menos una categoría y escribe su cantidad y su valor unitario."
                               if modo == "Valor por calidad" else "Añade al menos una fila de insumos.")
    for indice, fila in enumerate(filas):
        prefijo = f"insumos.{indice}."
        calidad = modo == "Valor por calidad"
        if modo == "Comparar alternativas" and fila.get("escenario", "Inicial") not in ESCENARIOS:
            errores[prefijo + "escenario"] = "Elige Inicial, Alternativa o Alternativa 2."
        if not str(fila.get("nombre", "")).strip():
            errores[prefijo + "nombre"] = ayuda_insumo("nombre", calidad=calidad)
        directo = not calidad and bool(str(fila.get("directo", "")).strip())
        for clave in ("cantidad", "precio", "directo"):
            valor = fila.get(clave, "")
            if clave == "directo" and not directo:
                continue
            if directo and clave in ("cantidad", "precio") and not str(valor).strip():
                continue
            try:
                etiqueta = {"cantidad": "Cantidad", "precio": "Valor unitario" if calidad else "Costo unitario",
                            "directo": "Costo directo"}[clave]
                validar_numero(valor, etiqueta)
            except ValueError as error:
                errores[prefijo + clave] = str(error)
        if directo and str(fila.get("precio", "")).strip():
            errores[prefijo + "precio"] = "Usa costo directo o cantidad × costo unitario, no ambos."
        if not calidad and fila.get("es_laboral"):
            unidad = str(fila.get("unidad", "")).strip().casefold()
            if unidad and unidad not in ("h", "hora", "horas", "h-persona", "horas-persona"):
                errores[prefijo + "unidad"] = "Para trabajo usa h-persona (o h, hora, horas, horas-persona)."
            try:
                validar_numero(fila.get("cantidad", ""), "Horas-persona")
            except ValueError as error:
                errores[prefijo + "cantidad"] = str(error)
        moneda = str(fila.get("moneda", "")).strip()
        if not calidad and moneda and moneda.casefold() != str(datos.get("moneda", "")).strip().casefold():
            errores[prefijo + "moneda"] = f"Usa la moneda común del ejercicio: {datos.get('moneda', '')}."
    return errores
