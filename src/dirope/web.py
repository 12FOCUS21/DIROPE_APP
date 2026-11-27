"""Adaptador JSON de la edición web; las reglas y los informes son los de escritorio."""

import json

from .analisis import analizar_datos, describir_ejemplo
from .banco import TAREAS, generar_banco
from .entradas import ESCENARIOS, FORMATO, NOTA_NO_CONFORMES, TEXTOS, ayuda_campo, ayuda_insumo, errores_entrada
from .informe import informe_html, valor_paso
from .modulos import MODULOS
from .modulos.campos import CAMPOS_COMUNES, MODOS, grupos_datos
from .practica_inicial import casos_practica


def _campo(clave, modo):
    campo = CAMPOS_COMUNES[clave]
    return dict(clave=clave, etiqueta=campo.etiqueta, valor=campo.valor,
                tipo="opciones" if clave == "medida_calidad" else "texto" if clave in TEXTOS else "numero",
                opciones=["Cantidad", "%"] if clave == "medida_calidad" else [],
                ayuda=ayuda_campo(clave, {"modo": modo}),
                ayuda_porcentaje=ayuda_campo(clave, {"modo": modo, "medida_calidad": "%"})
                if clave.startswith("defecto_") else None)


def _tabla(modulo, modo):
    if not modulo.tabla_insumos:
        return None
    calidad = modo == "Valor por calidad"
    comparar = modo == "Comparar alternativas"
    campos = []
    if comparar:
        campos.append(dict(clave="escenario", etiqueta="Escenario", tipo="opciones",
                           opciones=ESCENARIOS))
    campos.extend((dict(clave="nombre", etiqueta="Nombre de la categoría" if calidad else "Nombre del recurso", tipo="texto"),
                   dict(clave="cantidad", etiqueta="Cantidad", tipo="numero"),
                   dict(clave="precio", etiqueta="Valor unitario" if calidad else "Costo unitario", tipo="numero")))
    if not calidad:
        campos.extend((dict(clave="directo", etiqueta="Costo directo (opcional)", tipo="numero"),
                       dict(clave="unidad", etiqueta="Unidad del insumo (opcional)", tipo="texto"),
                       dict(clave="es_laboral", etiqueta="Es trabajo (cantidad en horas-persona)", tipo="casilla")))
    ayuda = ("Indica la cantidad y el valor unitario de cada categoría." if calidad else
             "Usa cantidad × costo unitario, o deja vacío el costo unitario e indica un costo directo. "
             "Si marcas trabajo, la cantidad debe ser la de horas-persona. Todos los costos usan la moneda común.")
    if comparar:
        ayuda += " Registra insumos para Inicial y Alternativa. Si usas Alternativa 2, indica también su producción."
    for campo in campos:
        campo["ayuda"] = ayuda_insumo(campo["clave"], calidad=calidad)
    return dict(titulo="Categorías de calidad" if calidad else "Insumos", campos=campos, ayuda=ayuda,
                filas=[{"escenario": "Inicial"}, {"escenario": "Alternativa"}] if comparar else [{}])


def _ejemplos(modulo, modo, caso):
    ejemplos = []
    for nombre, datos in modulo.ejemplos.items():
        if datos.get("modo", next(iter(MODOS[modulo.clave]))) != modo:
            continue
        campos = {clave: datos.get(clave, CAMPOS_COMUNES[clave].valor) for clave in MODOS[modulo.clave][modo]}
        ejemplos.append(dict(nombre=nombre, enunciado=describir_ejemplo(modulo.clave, datos),
                             datos=dict(campos, modo=modo, insumos=datos.get("insumos", []))))
    ejemplos.append({clave: caso[clave] for clave in ("nombre", "enunciado", "datos")})
    return ejemplos


def catalogo():
    """Devuelve las definiciones de formulario y ejemplos de los diez modos."""
    banco = {(caso["modulo"], caso["datos"]["modo"]): caso for caso in generar_banco(1)}
    modulos = []
    for modulo in MODULOS:
        modos = []
        for modo in MODOS[modulo.clave]:
            grupos = [dict(titulo=titulo, campos=[_campo(clave, modo) for clave in claves])
                      for titulo, claves in grupos_datos(modulo.clave, modo)]
            modos.append(dict(nombre=modo, ayuda=TAREAS[modo], grupos=grupos, tabla=_tabla(modulo, modo),
                              nota=NOTA_NO_CONFORMES if modo == "Comparar conformidad" else "",
                              ejemplos=_ejemplos(modulo, modo, banco[modulo.clave, modo])))
        modulos.append(dict(clave=modulo.clave, nombre=modulo.nombre, modos=modos))
    return json.dumps(dict(modulos=modulos, formato=FORMATO, practica=casos_practica()), ensure_ascii=False)


def resolver(solicitud):
    """Valida las entradas y devuelve el resumen y el mismo informe HTML del núcleo."""
    peticion = json.loads(solicitud)
    clave, datos = peticion["modulo"], peticion["datos"]
    errores = errores_entrada(clave, datos)
    if errores:
        return json.dumps(dict(errores=errores), ensure_ascii=False)
    modulo = next(m for m in MODULOS if m.clave == clave)
    try:
        resultado = modulo.calcular(datos)
        analisis = analizar_datos(clave, datos, resultado=resultado)
    except ValueError as error:
        return json.dumps(dict(mensaje=str(error)), ensure_ascii=False)

    titulo = peticion["titulo"].strip() or datos["modo"]
    decimales = 6
    principal = resultado.principal
    return json.dumps(dict(
        principal=dict(titulo=principal.titulo, valor=valor_paso(principal, decimales)) if principal else None,
        interpretacion=resultado.interpretacion,
        html=informe_html(titulo, peticion["enunciado"].strip(), analisis, resultado, decimales),
    ), ensure_ascii=False)


def revisar(solicitud):
    """Devuelve avisos de entrada sin volver a calcular ni producir un informe."""
    peticion = json.loads(solicitud)
    return json.dumps(errores_entrada(peticion["modulo"], peticion["datos"]), ensure_ascii=False)
