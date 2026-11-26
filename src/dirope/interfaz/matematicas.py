"""Composición matemática local: fracciones apiladas y delimitadores, sin LaTeX externo."""

import tkinter as tk
from tkinter import font as tkfont

from ..notacion import componer
from .temas import paleta, vincular_colores


class Formula(tk.Canvas):
    """Fórmula vectorial adaptable; conserva el texto original para copiar e informes."""

    def __init__(self, padre, text="", **opciones):
        super().__init__(padre, highlightthickness=0, height=60, width=160, takefocus=True, **opciones)
        self.texto = text
        raiz = self._root()
        if not hasattr(raiz, "fuentes_formula"):
            raiz.fuentes_formula = [tkfont.Font(raiz, family="Cambria", size=tamano) for tamano in range(18, 9, -1)]
        self.fuentes = raiz.fuentes_formula
        self.ultima_vista = None
        self.es_grafico_tematizado = True
        vincular_colores(self, background="superficie")
        self.bind("<Configure>", lambda _: self.dibujar())
        self.bind("<Control-c>", self.copiar)
        self.bind("<Button-1>", lambda _: self.focus_set())
        self.bind("<Shift-MouseWheel>", lambda e: self.desplazar(-1 if e.delta > 0 else 1))
        self.bind("<Left>", lambda _: self.desplazar(-1))
        self.bind("<Right>", lambda _: self.desplazar(1))
        for evento in ("<FocusIn>", "<FocusOut>"):
            self.bind(evento, lambda _: self.dibujar(), add="+")
        self.dibujar()

    def presentar(self, texto):
        self.texto = texto
        self.xview_moveto(0)
        self.dibujar()

    def desplazar(self, direccion):
        self.xview_scroll(direccion, "units")
        return "break"

    def copiar(self, evento=None):
        self.clipboard_clear()
        self.clipboard_append(self.texto)
        return "break"

    def caja(self, nodo, fuente):
        tipo = nodo[0]
        alto = fuente.metrics("linespace")
        if tipo == "texto":
            return fuente.measure(nodo[1]), alto, [("texto", 0, alto / 2, nodo[1])]
        if tipo == "fraccion":
            a, b = self.caja(nodo[1], fuente), self.caja(nodo[2], fuente)
            ancho = max(a[0], b[0]) + 16
            y = a[1] + 5
            trazos = [("linea", 1, y, ancho - 1)]
            for caja, superior in ((a, 0), (b, y + 6)):
                trazos.extend(self.mover(caja[2], (ancho - caja[0]) / 2, superior))
            return ancho, a[1] + b[1] + 12, trazos
        if tipo == "grupo":
            ancho, altura, marcas = self.caja(nodo[2], fuente)
            if altura > alto and nodo[1] == "⌈":
                # Los signos de techo abarcan el numerador y el denominador.
                return ancho + 22, altura, [*self.mover(marcas, 11, 0),
                                            ("techo", 3, 1, (1, altura - 2)),
                                            ("techo", ancho + 19, 1, (-1, altura - 2))]
            nodo = ("fila", ("texto", nodo[1]), nodo[2], ("texto", nodo[3]))
        cajas = [self.caja(hijo, fuente) for hijo in nodo[1:]]
        altura = max(c[1] for c in cajas)
        x, trazos = 0, []
        for ancho, alto_hijo, marcas in cajas:
            trazos.extend(self.mover(marcas, x, (altura - alto_hijo) / 2))
            x += ancho
        return x, altura, trazos

    @staticmethod
    def mover(trazos, x, y):
        return [(tipo, a + x, b + y, valor + x if tipo == "linea" else
                 (valor[0], valor[1] + y) if tipo == "techo" else valor) for tipo, a, b, valor in trazos]

    def dibujar(self):
        disponible = self.winfo_width() - 16 if self.winfo_width() > 1 else 484
        colores = paleta(self)
        tiene_foco = self.focus_get() == self
        vista = (self.texto, disponible, colores["texto"], tiene_foco, self.tk.call("tk", "scaling"))
        if vista == self.ultima_vista:
            return
        self.ultima_vista = vista
        self.delete("all")
        nodo = componer(self.texto)
        for fuente in self.fuentes:
            ancho, alto, trazos = self.caja(nodo, fuente)
            if ancho <= disponible:
                break
        self.fuente = fuente
        if int(self.cget("height")) != int(alto + 20):
            self.configure(height=int(alto + 20))
        color = colores["texto"]
        for tipo, x, y, valor in trazos:
            if tipo == "linea":
                self.create_line(x + 8, y + 10, valor + 8, y + 10, fill=color, width=1.4)
            elif tipo == "techo":
                direccion, base = valor
                self.create_line(x + 8 + direccion * 6, y + 10, x + 8, y + 10, x + 8, base + 10,
                                 fill=color, width=1.4)
            else:
                self.create_text(x + 8, y + 10, text=valor, anchor="w", font=fuente, fill=color)
        self.configure(scrollregion=(0, 0, ancho + 16, alto + 20))
        if tiene_foco:
            self.create_line(8, alto + 16, min(ancho + 8, disponible + 8), alto + 16, fill=colores["acento"], width=2)
