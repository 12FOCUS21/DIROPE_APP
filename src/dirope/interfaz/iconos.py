"""Iconos de línea en una cuadrícula común, con fondo transparente y etiqueta aparte."""

import tkinter as tk


TRAZOS = {
    None: (((2, 10), (10, 3), (18, 10)), ((4, 9), (4, 17), (8, 17), (8, 12), (12, 12), (12, 17), (16, 17), (16, 9))),
    "un_factor": (((3, 4), (3, 17), (17, 17)), ((7, 13), (7, 10)), ((11, 13), (11, 7)), ((15, 13), (15, 4))),
    "multifactor": (((3, 6), (10, 3), (17, 6), (10, 9), (3, 6)), ((3, 10), (10, 13), (17, 10)),
                    ((3, 14), (10, 17), (17, 14))),
    "capacidad": (((7, 5), (9, 3), (11, 3), (13, 5), (13, 7), (11, 9), (9, 9), (7, 7), (7, 5)),
                  ((4, 17), (4, 15), (7, 12), (13, 12), (16, 15), (16, 17), (4, 17))),
}


def distancia2(x, y, a, b):
    ax, ay = a
    dx, dy = b[0] - ax, b[1] - ay
    t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
    return (x - ax - t * dx) ** 2 + (y - ay - t * dy) ** 2


def icono(widget, clave, color, tamano):
    raiz = widget._root()
    cache = getattr(raiz, "imagenes_iconos", {})
    datos = (clave, color, tamano)
    if datos not in cache:
        imagen = tk.PhotoImage(master=raiz, width=tamano, height=tamano)
        segmentos = [par for linea in TRAZOS[clave] for par in zip(linea, linea[1:])]
        for y in range(tamano):
            for x in range(tamano):
                if any(distancia2((x + .5) * 20 / tamano, (y + .5) * 20 / tamano, a, b) < .85
                       for a, b in segmentos):
                    imagen.put(color, to=(x, y))
        cache[datos] = imagen
        raiz.imagenes_iconos = cache
    return cache[datos]


def vincular_icono(widget, clave, rol, tamano=24):
    widget.icono_tema = clave, rol, tamano
    from .temas import paleta
    widget.configure(image=icono(widget, clave, paleta(widget)[rol], tamano))
