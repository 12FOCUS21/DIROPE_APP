"""Estructura de las fórmulas de DIROPE, independiente del medio de presentación."""


def componer(texto):
    """Transforma la notación de los módulos sin evaluar sus cálculos."""
    texto = texto.strip()
    if not texto:
        return ("texto", "")
    for operadores in ("=", "+−", "×", "/"):
        profundidad = 0
        posiciones = []
        for i, caracter in enumerate(texto):
            if caracter == "(":
                profundidad += 1
            elif caracter == ")":
                profundidad -= 1
            elif (profundidad == 0 and caracter in operadores and i > 0
                  and not (caracter in "+−" and texto[i - 1] in "eE" and texto[i + 1:i + 2].isdigit())):
                posiciones.append(i)
        if posiciones:
            if operadores == "/":
                i = posiciones[-1]
                return ("fraccion", componer(texto[:i]), componer(texto[i + 1:]))
            partes, inicio = [], 0
            for i in posiciones:
                partes.extend((componer(texto[inicio:i]), ("texto", f" {texto[i]} ")))
                inicio = i + 1
            partes.append(componer(texto[inicio:]))
            return ("fila", *partes)
    inicio = texto.find("(")
    if inicio >= 0 and texto.endswith(")"):
        profundidad = 0
        for i in range(inicio, len(texto)):
            profundidad += (texto[i] == "(") - (texto[i] == ")")
            if profundidad == 0:
                break
        if i == len(texto) - 1:
            prefijo = texto[:inicio].strip()
            interior = componer(texto[inicio + 1:-1])
            if prefijo == "techo":
                return ("grupo", "⌈", interior, "⌉")
            grupo = ("grupo", "(", interior, ")")
            return ("fila", ("texto", prefijo), grupo) if prefijo else grupo
    return ("texto", texto)
