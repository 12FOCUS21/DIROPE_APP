"""Banco reproducible de ejercicios con oráculos independientes de los módulos."""

from fractions import Fraction
from math import ceil
from random import Random

from .modulos.campos import MODOS


TAREAS = {
    "Comparar escenarios": "La jefatura quiere saber si el cambio de proceso mejoró el rendimiento. Compara la productividad inicial y final, su diferencia y su variación porcentual.",
    "Productividad individual": "La jefatura necesita una medida del rendimiento del período. Calcula cuánta producción se obtuvo por cada unidad del recurso utilizado.",
    "Producción requerida": "El equipo conoce el recurso disponible y el rendimiento que se espera alcanzar. Determina cuánto tendría que producir para cumplir ese objetivo.",
    "Recurso requerido": "El equipo tiene una cantidad que debe entregar y un rendimiento objetivo. Determina cuánto recurso necesitará para completar la entrega.",
    "Comparar conformidad": "No todo lo producido cumple la especificación. Compara los dos escenarios usando solo la producción conforme y explica cómo cambió el rendimiento.",
    "Escenario individual": "La administración quiere evaluar el rendimiento del proceso incluyendo sus costos. Calcula el costo total y la producción obtenida por unidad monetaria.",
    "Comparar alternativas": "Antes de cambiar de proceso, la administración quiere comparar el plan actual con las propuestas. Calcula la productividad de cada escenario a partir de su producción y el costo de sus insumos.",
    "Valor por calidad": "La producción se clasifica en categorías con distinto valor unitario. Calcula el valor total y el valor generado por hora-persona.",
    "Crecimiento porcentual": "El próximo período se espera un cambio de demanda respecto de la producción actual. Calcula la nueva meta, las horas de trabajo y el número entero de personas necesarias.",
    "Meta directa": "La jefatura ya fijó la cantidad que debe entregar en el período. Calcula las horas de trabajo y el número entero de personas necesarias para lograr la meta.",
}

CONTEXTOS = {
    "cajas": "Una planta de empaque revisa la operación de su línea de cajas.",
    "placas": "Un taller industrial revisa el desempeño de su línea de placas.",
    "kg": "Una procesadora evalúa una operación cuyo volumen se mide en kilogramos.",
    "servicios": "Un centro de atención revisa su capacidad para completar servicios.",
}


def generar_banco(cantidad=100, semilla=20261125):
    """Genera la cantidad indicada por modo, con resultados de referencia racionales."""
    if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad < 1:
        raise ValueError("La cantidad de ejercicios debe ser un entero positivo.")
    azar = Random(semilla)
    casos = []
    for modulo, modos in MODOS.items():
        for modo in modos:
            for indice in range(cantidad):
                q = Fraction(azar.randint(1, 50000), 10)
                i = Fraction(azar.randint(1, 10000), 10)
                q1 = Fraction(azar.randint(0, 50000), 10)
                i1 = Fraction(azar.randint(1, 10000), 10)
                salida = ("cajas", "placas", "kg", "servicios")[indice % 4]
                recurso = ("h-persona", "kWh", "kg", "h-máquina")[indice % 4]
                datos = dict(modo=modo, unidad_salida=salida, unidad_recurso=recurso, recurso="Recurso de producción")
                esperado = {}
                if modulo == "un_factor":
                    if indice % 10 == 0:
                        q = Fraction(0)
                    datos.update(antes=float(q), despues=float(q1), insumo_antes=float(i), insumo_despues=float(i1))
                    if modo == "Comparar escenarios":
                        if indice % 10 == 0:
                            q = Fraction(0)
                            datos["antes"] = 0
                        p0, p1 = q / i, q1 / i1
                        esperado.update({"Productividad · Inicial": p0, "Productividad · Final": p1,
                                         "Diferencia de productividad": p1 - p0})
                        if p0:
                            esperado["Cambio de productividad"] = (p1 / p0 - 1) * 100
                    elif modo == "Productividad individual":
                        esperado["Productividad · Único"] = q / i
                    elif modo == "Producción requerida":
                        ritmo = Fraction(0) if indice % 10 == 0 else Fraction(azar.randint(0, 10000), 100)
                        datos["ritmo"] = float(ritmo)
                        esperado[modo] = ritmo * i
                    elif modo == "Recurso requerido":
                        ritmo = Fraction(azar.randint(1, 10000), 100)
                        datos["ritmo"] = float(ritmo)
                        esperado[modo] = q / ritmo
                    else:
                        porcentajes = indice % 2 == 0
                        # Producciones enteras cuando el defecto se cuenta por unidades.
                        q, q1 = Fraction(azar.randint(1, 2000)), Fraction(azar.randint(1, 2000))
                        d0 = azar.choice((0, 100, azar.randint(1, 99))) if porcentajes else azar.randint(0, int(q))
                        d1 = azar.choice((0, 100, azar.randint(1, 99))) if porcentajes else azar.randint(0, int(q1))
                        datos.update(antes=int(q), despues=int(q1), medida_calidad="%" if porcentajes else "Cantidad",
                                     defecto_antes=d0, defecto_despues=d1)
                        buenas0 = q * (1 - Fraction(d0, 100)) if porcentajes else q - d0
                        buenas1 = q1 * (1 - Fraction(d1, 100)) if porcentajes else q1 - d1
                        p0, p1 = buenas0 / i, buenas1 / i1
                        esperado.update({"Producción conforme · Inicial": buenas0, "Producción conforme · Final": buenas1,
                                         "Productividad conforme · Inicial": p0, "Productividad conforme · Final": p1,
                                         "Cambio de conformidad": (buenas1 / q1 - buenas0 / q) * 100,
                                         "Diferencia de productividad conforme": p1 - p0})
                        if p0:
                            esperado["Cambio de productividad conforme"] = (p1 / p0 - 1) * 100
                elif modulo == "multifactor":
                    datos.update(moneda=("$", "PEN", "EUR")[indice % 3], insumos=[])
                    if modo == "Valor por calidad":
                        total = Fraction(0)
                        for fila in range(1 + indice % 8):
                            cantidad_fila = 0 if indice % 10 == 0 else azar.randint(0, 2000)
                            precio = Fraction(azar.randint(0, 50000), 100)
                            datos["insumos"].append(dict(nombre=f"Categoría {fila + 1}", cantidad=cantidad_fila, precio=float(precio)))
                            total += cantidad_fila * precio
                        datos["horas_calidad"] = float(i)
                        esperado.update({"Valor total": total, "Productividad económica": total / i})
                    else:
                        datos["produccion"] = 0 if indice % 10 == 0 else float(q)
                        escenarios = [("Base", "produccion")] if modo == "Escenario individual" else [
                            ("Inicial", "produccion"), ("Alternativa", "produccion_final")]
                        if modo == "Comparar alternativas":
                            datos["produccion_final"] = float(q1)
                            if indice % 2:
                                datos["produccion_otra"] = float(q / 2)
                                escenarios.append(("Alternativa 2", "produccion_otra"))
                        productividades = []
                        for escenario, campo in escenarios:
                            total = Fraction(0)
                            horas_laborales = costo_laboral = Fraction(0)
                            for fila in range(1 + indice % 7):
                                cantidad_fila = azar.randint(1, 1000)
                                precio = Fraction(azar.randint(1, 10000), 100)
                                costo = cantidad_fila * precio
                                entrada = dict(nombre=f"Insumo {fila + 1}", escenario="Inicial" if escenario == "Base" else escenario)
                                laboral = fila == 0 and indice % 3 == 0
                                if (indice + fila) % 2 and not laboral:
                                    entrada["directo"] = float(costo)
                                else:
                                    entrada.update(cantidad=cantidad_fila, precio=float(precio),
                                                   unidad="h-persona" if laboral else "kg", es_laboral=laboral)
                                if laboral:
                                    horas_laborales += cantidad_fila
                                    costo_laboral += costo
                                datos["insumos"].append(entrada)
                                total += costo
                            produccion = Fraction(str(datos[campo]))
                            productividad = produccion / total
                            esperado.update({f"Costo total · {escenario}": total, f"Productividad · {escenario}": productividad})
                            if horas_laborales:
                                esperado.update({f"Productividad laboral por hora · {escenario}": produccion / horas_laborales,
                                                 f"Productividad por costo laboral · {escenario}": produccion / costo_laboral})
                            productividades.append(productividad)
                        for posicion, (escenario, _) in enumerate(escenarios[1:], 1):
                            if productividades[0]:
                                esperado[f"Cambio de productividad · {escenario}"] = (productividades[posicion] / productividades[0] - 1) * 100
                else:
                    p = Fraction(azar.randint(1, 10000), 100)
                    jornada = Fraction(azar.choice((1, 8, 40, 160, 192)))
                    actual = Fraction(azar.randint(0, 100000), 10)
                    crecimiento = azar.choice((-100, -50, 0, 25, 100, 250))
                    meta = actual * (1 + Fraction(crecimiento, 100)) if modo == "Crecimiento porcentual" else q
                    datos.update(unidad_salida=salida, periodo=("día", "semana", "mes")[indice % 3],
                                 actual=float(actual), productividad=float(p), horas=int(jornada))
                    if modo == "Crecimiento porcentual":
                        datos["crecimiento"] = crecimiento
                    else:
                        datos["meta"] = float(meta)
                        if indice % 5 == 0:
                            datos["actual"] = ""
                    necesarios = ceil(meta / p / jornada)
                    esperado.update({"Meta de producción": meta, "Horas-persona requeridas": meta / p, "Personal necesario": necesarios})
                    if indice % 2:
                        plantilla = azar.randint(0, 100)
                        datos["plantilla"] = plantilla
                        esperado["Personal adicional (+) o excedente (−)"] = necesarios - plantilla
                    elif str(datos["actual"]).strip():
                        esperado["Personal adicional (+) o excedente (−)"] = ceil((meta - actual) / p / jornada)
                # Solo campos visibles: permite verificar guardado y reapertura sin datos ocultos.
                datos = {k: str(datos.get(k, "")) for k in MODOS[modulo][modo]} | {
                    "modo": modo, **({"insumos": datos["insumos"]} if "insumos" in datos else {})}
                nombre = f"{modo} · Caso {indice + 1:03}"
                enunciado = f"{CONTEXTOS[salida]} {TAREAS[modo]}"
                casos.append(dict(modulo=modulo, nombre=nombre, enunciado=enunciado, datos=datos,
                                  esperados={k: float(v) for k, v in esperado.items()}))
    return casos
