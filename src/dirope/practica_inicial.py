"""Ejercicios de DIROPE.01 en su orden original y casos complementarios."""

from dataclasses import asdict
from uuid import NAMESPACE_URL, uuid5

from .analisis import analizar_datos
from .formato import numero
from .leyendas import leyenda_formula, leyenda_sustitucion
from .modulos import MODULOS
from .modulos.campos import CAMPOS_COMUNES, MODOS
from .modulos.productividad import CAPACIDAD, MULTIFACTOR, UN_FACTOR
from .nucleo import unidades_buenas


def casos_practica():
    """Devuelve los siete ejercicios de DIROPE.01, en el orden del documento."""
    seleccion = [
        ("T1", UN_FACTOR, "Chuck Sox (T1)", "1.1", "Chuck Sox", "Cajas de madera de Chuck Sox",
         "Chuck Sox y sus tres empleados invierten 40 horas-persona al día para fabricar 120 cajas de madera. "
         "Con un rediseño podrían fabricar 125 cajas con las mismas horas. Calcula la productividad inicial y nueva, "
         "el incremento unitario por hora y el cambio porcentual."),
        ("T2", UN_FACTOR, "Lori Cook (T2)", "1.5", "Lori Cook", "Paquetes para exámenes de Lori Cook",
         "Lori Cook produce 100 paquetes para los exámenes finales en cinco horas diarias. Con un rediseño espera "
         "producir 133 paquetes al día sin variar el tiempo. Calcula la productividad actual, la nueva y su incremento porcentual."),
        ("T3", MULTIFACTOR, "Kleen Karpet (T3)", "1.8", "Kleen Karpet", "Limpieza de alfombras de Kleen Karpet",
         "Kleen Karpet limpió 65 alfombras en octubre. Utilizó 520 horas de mano de obra a $13/hora, "
         "100 galones de solvente a $5/galón y 20 días de maquinaria a $50/día. "
         "Calcula la productividad laboral por dólar y la productividad multifactor."),
        ("T4", MULTIFACTOR, "Lakefront · ahorro de energía (T4)", "1.9", "Lakefront", "Ahorro energético en Lakefront Manufacturing",
         "Lakefront produce 1 000 llantas al día con 400 horas de mano de obra a $12.50/hora, 20 000 libras de "
         "materia prima a $1/libra, $5 000 de energía y $10 000 de capital diarios. Calcula la productividad laboral, "
         "la multifactor y su cambio porcentual si se ahorran $1 000 diarios de energía."),
        ("T5", CAPACIDAD, "Lackey (T5)", "1.13", "Lackey: personal", "Personal adicional en la panadería de Charles Lackey",
         "La panadería fabrica 1 500 hogazas mensuales y prevé un aumento de demanda del 25 %. Su productividad es "
         "2.344 hogazas por hora-persona y cada trabajador labora 160 horas al mes. ¿Cuántos trabajadores adicionales se requieren?"),
        ("1.17", MULTIFACTOR, "Susan Williams · valor por calidad (1.17)", "1.17", "Susan Williams",
         "Prendas de distinta calidad de Susan Williams (adicional)",
         "Ocho trabajadores trabajaron 45 horas cada uno en la semana. De las 132 prendas producidas, 80 de primera "
         "se vendieron a $198 cada una y 52 de segunda a $90. Calcula las ventas en dólares por hora-persona."),
        ("1.14", MULTIFACTOR, "Lackey · contratación e inversión (1.14)", "1.14", "Lackey: batidora",
         "Contratación o batidora nueva (adicional)",
         "Charles Lackey debe pasar de 1 500 a 1 875 hogazas mensuales. Con un pago de $8 por hora, compara aumentar "
         "la mano de obra de 640 a 800 horas o mantener 640 horas y gastar $100 adicionales al mes en una batidora. "
         "Calcula la productividad actual y la de cada alternativa, y compáralas en porcentaje."),
    ]
    return [_preparar_caso(codigo, modulo.clave, f"{orden} · {corto} ({referencia})",
                           f"{orden} · {titulo} · Problema {referencia}", enunciado, modulo.ejemplos[ejemplo])
            for orden, (codigo, modulo, ejemplo, referencia, corto, titulo, enunciado) in enumerate(seleccion, 1)]


def casos_complementarios():
    """Devuelve los casos de práctica extra que no forman parte de DIROPE.01."""
    base = dict(modo="Comparar conformidad", unidad_salida="placas", unidad_recurso="h-persona",
                recurso="Mano de obra", medida_calidad="%", antes=800, despues=800,
                insumo_antes=160, insumo_despues=160, defecto_antes=6, defecto_despues=2)
    enunciado = ("Caso hipotético del documento inicial: se producen 800 placas antes y después de una mejora. "
                 "Los defectos bajan del 6 % al 2 %. En cada escenario se usan 160 horas a $10/h, "
                 "$12 000 de componentes y $400 de energía. La depreciación e inspección pasa de $1 000 "
                 "a $1 300. Las cantidades corresponden al mismo período.")
    insumos = []
    for escenario, inspeccion in (("Inicial", 1000), ("Alternativa", 1300)):
        insumos.extend([
            dict(nombre="Mano de obra", cantidad=160, precio=10, unidad="h-persona", es_laboral=True, escenario=escenario),
            dict(nombre="Componentes", directo=12000, escenario=escenario),
            dict(nombre="Energía", directo=400, escenario=escenario),
            dict(nombre="Depreciación e inspección", directo=inspeccion, escenario=escenario),
        ])
    mesa = UN_FACTOR.ejemplos["Mesa de ayuda · conformidad (T6)"]
    return [
        _preparar_caso("T6-laboral", "un_factor", "8A · Placas: calidad laboral",
                       "8A · Placas · Calidad y productividad laboral",
                       enunciado + " Calcula las placas buenas, la productividad laboral y su cambio. "
                       "Continúa con los costos en el 8B.", base),
        _preparar_caso("T6-multifactor", "multifactor", "8B · Placas: costos multifactor",
                       "8B · Placas · Costos y productividad multifactor",
                       enunciado + " Calcula la productividad multifactor y su cambio. "
                       "Usa las 752 y 784 placas buenas calculadas en el 8A, no las 800 fabricadas.",
                       dict(modo="Comparar alternativas", unidad_salida="placas buenas", moneda="$",
                            produccion=unidades_buenas(800, 6), produccion_final=unidades_buenas(800, 2), insumos=insumos)),
        _preparar_caso("mesa-ayuda", "un_factor", "9 · Mesa de ayuda", "9 · Mesa de ayuda · Conformidad",
                       mesa["enunciado"] + " Compara la productividad usando solo los cierres conformes.", mesa),
    ]


def _preparar_caso(codigo, modulo, etiqueta, nombre, enunciado, entrada):
    modo = entrada.get("modo", next(iter(MODOS[modulo])))
    datos = {campo: str(entrada.get(campo, CAMPOS_COMUNES[campo].valor)) for campo in MODOS[modulo][modo]}
    datos["modo"] = modo
    if "insumos" in entrada:
        datos["insumos"] = [
            {campo: bool(fila.get(campo, False)) if campo == "es_laboral" else
             str(fila.get(campo, "Inicial" if campo == "escenario" else ""))
             for campo in ("nombre", "cantidad", "unidad", "precio", "directo", "escenario", "es_laboral")}
            for fila in entrada["insumos"]
        ]
    return dict(codigo=codigo, modulo=modulo, etiqueta=etiqueta, nombre=nombre, enunciado=enunciado, datos=datos)


def resolver_caso(caso):
    """Calcula con los mismos módulos de la interfaz y genera el informe conservado."""
    modulo = next(m for m in MODULOS if m.clave == caso["modulo"])
    resultado = modulo.calcular(caso["datos"])
    analisis = analizar_datos(caso["modulo"], caso["datos"], resultado=resultado)
    lineas = [caso["nombre"], "", "1. PLANTEAMIENTO", caso["enunciado"], "", "2. ANÁLISIS DE DATOS"]
    lineas.extend(f"{k}: {v}" for k, v in analisis.datos)
    lineas.extend(["", "3. IDENTIFICACIÓN", analisis.perfil.tipo, *analisis.perfil.supuestos])
    for formula in analisis.perfil.formulas:
        lineas.extend([formula, leyenda_formula(formula), ""])
    lineas.extend(["", "4. DESARROLLO"])
    for indice, paso in enumerate(resultado.pasos, 1):
        lineas.extend([f"{indice}. {paso.titulo}", paso.explicacion, paso.formula, leyenda_formula(paso.formula),
                       paso.sustitucion, leyenda_sustitucion(paso.sustitucion),
                       f"Resultado: {numero(paso.resultado, 6)} {paso.unidad}", ""])
    lineas.extend(["5. RESULTADOS", resultado.interpretacion])
    return {"resultado": asdict(resultado), "informe": "\n".join(lineas), "decimales": 6}


def guardar_practica(historial):
    """Carga una vez por código; nunca sobrescribe ejercicios existentes ni variantes."""
    registros = []
    for caso in casos_practica() + casos_complementarios():
        identificador = str(uuid5(NAMESPACE_URL, "dirope:practica-inicial:" + caso["codigo"]))
        try:
            registro = historial.abrir(identificador)
        except FileNotFoundError:
            registro = historial.guardar(caso["modulo"], caso["nombre"], caso["enunciado"], caso["datos"],
                                         identificador, resolucion=resolver_caso(caso))
        registros.append(registro)
    return registros
