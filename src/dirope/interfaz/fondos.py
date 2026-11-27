"""Degradado ambiental compartido, sin transparencias ni descargas externas."""

import math
import tkinter as tk
from tkinter import ttk

from . import redondeado
from .temas import paleta


def color_ambiental(x, y, esquinas):
    """Interpolación bilineal de colores RGB; coordenadas normalizadas y acotadas."""
    x, y = max(0, min(1, x)), max(0, min(1, y))
    pesos = ((1 - x) * (1 - y), x * (1 - y), (1 - x) * y, x * y)
    canales = [round(sum(int(color[i:i + 2], 16) * peso for color, peso in zip(esquinas, pesos)))
               for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(canales)


class LienzoAmbiental(tk.Canvas):
    """Fondo de baja resolución interpolado; guarda una sola imagen por superficie."""

    def __init__(self, padre, *, titulo=None, **opciones):
        super().__init__(padre, highlightthickness=0, borderwidth=0, takefocus=False, **opciones)
        self.titulo = titulo
        self.imagen = None
        self.firma = None
        self.tarea = None
        self.es_grafico_tematizado = True
        self.bind("<Configure>", self.programar, add="+")
        self.bind("<Map>", self.programar, add="+")
        self.bind("<Destroy>", self.cancelar, add="+")

    def cancelar(self, evento=None):
        if evento is not None and evento.widget is not self:
            return
        if self.tarea is not None:
            self.after_cancel(self.tarea)
            self.tarea = None

    def programar(self, evento=None):
        if self.tarea is None:
            self.tarea = self.after_idle(self.dibujar)

    def dibujar(self):
        self.cancelar()
        if not self.winfo_viewable():
            return
        colores = paleta(self)
        ancho, alto = self.winfo_width(), self.winfo_height()
        if min(ancho, alto) < 2:
            return
        raiz = self._root()
        total_x, total_y = max(1, raiz.winfo_width()), max(1, raiz.winfo_height())
        origen_x = self.winfo_rootx() - raiz.winfo_rootx()
        origen_y = self.winfo_rooty() - raiz.winfo_rooty()
        esquinas = colores.get("fondo_ambiental")
        motor = redondeado.usa_pillow()
        firma = (ancho, alto, total_x, total_y, origen_x, origen_y, esquinas,
                 colores["fondo"], colores["texto"], motor, self.tk.call("tk", "scaling"))
        if firma == self.firma:
            return
        self.firma = firma
        self.configure(background=colores["fondo"])
        self.delete("ambiente")
        self.imagen = None
        if esquinas:
            # Una malla pequeña evita calcular millones de píxeles en Python al redimensionar.
            columnas, filas = min(96, ancho), min(64, alto)
            datos = bytearray()
            for fila in range(filas):
                y = (origen_y + fila / max(1, filas - 1) * (alto - 1)) / total_y
                for columna in range(columnas):
                    x = (origen_x + columna / max(1, columnas - 1) * (ancho - 1)) / total_x
                    color = color_ambiental(x, y, esquinas)
                    datos.extend(bytes.fromhex(color[1:]))
            if motor:
                imagen = redondeado.Image.frombytes("RGB", (columnas, filas), bytes(datos))
                imagen = imagen.resize((ancho, alto), redondeado.Image.Resampling.BILINEAR)
                self.imagen = redondeado.ImageTk.PhotoImage(imagen, master=self)
            else:
                ppm = f"P6\n{columnas} {filas}\n255\n".encode("ascii") + datos
                original = tk.PhotoImage(master=self, data=ppm, format="PPM")
                self.imagen = original.zoom(math.ceil(ancho / columnas), math.ceil(alto / filas))
            self.create_image(0, 0, anchor="nw", image=self.imagen, tags="ambiente")
        if self.titulo is not None:
            fuente = ttk.Style(self).lookup("Title.TLabel", "font")
            self.create_text(0, alto / 2, text=self.titulo, anchor="w", fill=colores["texto"],
                             font=fuente, tags="ambiente")


class FondoAmbiental(ttk.Frame):
    """Contenedor con degradado visible en los espacios libres entre tarjetas opacas."""

    def __init__(self, padre, **opciones):
        super().__init__(padre, **opciones)
        self.es_grafico_tematizado = True
        self.fondo = LienzoAmbiental(self)
        self.bind("<Configure>", self.actualizar_fondo, add="+")
        self.bind("<Map>", self.actualizar_fondo, add="+")

    def actualizar_fondo(self, evento=None):
        if paleta(self).get("fondo_ambiental"):
            self.fondo.place(x=0, y=0, relwidth=1, relheight=1, bordermode="outside")
            # Canvas.lower() ordena trazos; el comando Tk ordena el widget completo.
            self.tk.call("lower", str(self.fondo))
            self.fondo.programar()
        else:
            self.fondo.place_forget()
            self.fondo.cancelar()
            self.fondo.imagen = None
            self.fondo.firma = None

    def dibujar(self):
        self.actualizar_fondo()
