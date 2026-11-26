"""Casos del documento inicial y los dos adicionales del Word del curso."""

from copy import deepcopy
from dataclasses import asdict
from uuid import NAMESPACE_URL, uuid5

from .analisis import analizar_datos
from .formato import numero
from .modulos import MODULOS
from .modulos.campos import CAMPOS_COMUNES, MODOS
from .modulos.productividad import CAPACIDAD, MULTIFACTOR, UN_FACTOR
from .nucleo import unidades_buenas


def casos_practica():
    """Prepara entradas editables, sin modificar los ejemplos originales."""
    seleccion = [
        ("T1", UN_FACTOR, "Chuck Sox (T1)", "1.1 · Chuck Sox · Cajas de madera"),
        ("T2", UN_FACTOR, "Lori Cook (T2)", "1.5 · Lori Cook · Paquetes"),
        ("T3", MULTIFACTOR, "Kleen Karpet (T3)", "1.8 · Kleen Karpet · Alfombras"),
        ("T4", MULTIFACTOR, "Lakefront · ahorro de energía (T4)", "1.9 · Lakefront · Ahorro energético"),
        ("T5", CAPACIDAD, "Lackey (T5)", "1.13 · Charles Lackey · Personal adicional"),
        ("1.17", MULTIFACTOR, "Susan Williams · valor por calidad (1.17)", "1.17 · Susan Williams · Valor por calidad"),
        ("1.14", MULTIFACTOR, "Lackey · contratación e inversión (1.14)", "1.14 · Charles Lackey · Contratación o batidora"),
    ]
    casos = []
    for codigo, modulo, ejemplo, nombre in seleccion:
        datos = deepcopy(modulo.ejemplos[ejemplo])
        casos.append(dict(codigo=codigo, modulo=modulo.clave, nombre=nombre,
                          enunciado=datos.pop("enunciado"), datos=datos))
    base = dict(modo="Comparar conformidad", unidad_salida="placas", unidad_recurso="h-persona",
                recurso="Mano de obra", medida_calidad="%", antes=800, despues=800,
                insumo_antes=160, insumo_despues=160, defecto_antes=6, defecto_despues=2)
    enunciado = ("Caso hipotético del documento inicial: se producen 800 placas antes y después de una mejora. "
                 "Los defectos bajan del 6 % al 2 %. En cada escenario se usan 160 horas a $10/h, "
                 "$12 000 de componentes y $400 de energía. La depreciación e inspección pasa de $1 000 "
                 "a $1 300. Calcular unidades buenas, productividad laboral y multifactor y sus cambios. "
                 "Las cantidades corresponden al mismo período. Véase también el otro registro Placas.")
    casos.append(dict(codigo="T6-laboral", modulo="un_factor", nombre="T6 · Placas · Calidad y productividad laboral",
                      enunciado=enunciado, datos=base))
    insumos = []
    for escenario, inspeccion in (("Inicial", 1000), ("Alternativa", 1300)):
        insumos.extend([
            dict(nombre="Mano de obra", cantidad=160, precio=10, unidad="h-persona", es_laboral=True, escenario=escenario),
            dict(nombre="Componentes", directo=12000, escenario=escenario),
            dict(nombre="Energía", directo=400, escenario=escenario),
            dict(nombre="Depreciación e inspección", directo=inspeccion, escenario=escenario),
        ])
    casos.append(dict(codigo="T6-multifactor", modulo="multifactor", nombre="T6 · Placas · Costos y productividad multifactor",
                      enunciado=enunciado + " Para el numerador se usan 800 × (1 − 6/100) = 752 y "
                      "800 × (1 − 2/100) = 784 placas buenas, no las 800 fabricadas.",
                      datos=dict(modo="Comparar alternativas", unidad_salida="placas buenas", moneda="$",
                                 produccion=unidades_buenas(800, 6), produccion_final=unidades_buenas(800, 2), insumos=insumos)))
    for caso in casos:
        clave = caso["modulo"]
        entrada = caso["datos"]
        modo = entrada.get("modo", next(iter(MODOS[clave])))
        datos = {campo: str(entrada.get(campo, CAMPOS_COMUNES[campo].valor)) for campo in MODOS[clave][modo]}
        datos["modo"] = modo
        if "insumos" in entrada:
            datos["insumos"] = [
                {campo: bool(fila.get(campo, False)) if campo == "es_laboral" else
                 str(fila.get(campo, "Inicial" if campo == "escenario" else ""))
                 for campo in ("nombre", "cantidad", "unidad", "precio", "directo", "escenario", "es_laboral")}
                for fila in entrada["insumos"]
            ]
        caso["datos"] = datos
    return casos


def resolver_caso(caso):
    """Calcula con los mismos módulos de la interfaz y genera el informe conservado."""
    modulo = next(m for m in MODULOS if m.clave == caso["modulo"])
    resultado = modulo.calcular(caso["datos"])
    analisis = analizar_datos(caso["modulo"], caso["datos"], resultado=resultado)
    lineas = [caso["nombre"], "", "1. PLANTEAMIENTO", caso["enunciado"], "", "2. ANÁLISIS DE DATOS"]
    lineas.extend(f"{k}: {v}" for k, v in analisis.datos)
    lineas.extend(["", "3. IDENTIFICACIÓN", analisis.perfil.tipo, *analisis.perfil.supuestos, "", "4. DESARROLLO"])
    for indice, paso in enumerate(resultado.pasos, 1):
        lineas.extend([f"{indice}. {paso.titulo}", paso.explicacion, paso.formula, paso.sustitucion,
                       f"Resultado: {numero(paso.resultado, 6)} {paso.unidad}", ""])
    lineas.extend(["5. RESULTADOS", resultado.interpretacion])
    return {"resultado": asdict(resultado), "informe": "\n".join(lineas), "decimales": 6}


def guardar_practica(historial):
    """Carga una vez por código; nunca sobrescribe ejercicios existentes ni variantes."""
    registros = []
    for caso in casos_practica():
        identificador = str(uuid5(NAMESPACE_URL, "dirope:practica-inicial:" + caso["codigo"]))
        try:
            registro = historial.abrir(identificador)
        except FileNotFoundError:
            registro = historial.guardar(caso["modulo"], caso["nombre"], caso["enunciado"], caso["datos"],
                                         identificador, resolucion=resolver_caso(caso))
        registros.append(registro)
    return registros
