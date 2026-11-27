"""Fórmulas y leyendas en recuadros, con distribución adaptable al espacio real."""

from tkinter import ttk, font

from ..leyendas import elementos_formula, elementos_sustitucion, operadores_expresion
from .matematicas import Formula


class FormulaExplicada(ttk.Frame):
    """Fórmula a la izquierda y explicación a la derecha, o debajo en anchos pequeños."""

    def __init__(self, padre, texto="", *, sustitucion=False, zona_leyenda=None):
        super().__init__(padre, style="Card.TFrame")
        self.sustitucion = sustitucion
        self.zona_leyenda = zona_leyenda
        self.texto = None
        self.distribucion = None
        self.etiquetas = []
        self.izquierda = ttk.Frame(self, style="Card.TFrame")
        ttk.Label(self.izquierda, text="SUSTITUCIÓN" if sustitucion else "FÓRMULA",
                  style="Accent.TLabel").pack(anchor="w", pady=(0, 8))
        self.formula = Formula(self.izquierda)
        self.formula.pack(fill="x")
        self.leyenda = ttk.Frame(zona_leyenda if zona_leyenda is not None else self, style="Card.TFrame")
        self.bind("<Configure>", self.organizar, add="+")
        self.leyenda.bind("<Configure>", self.ajustar_textos, add="+")
        self.presentar(texto)

    def presentar(self, texto):
        if texto == self.texto:
            return
        self.texto = texto
        self.formula.presentar(texto)
        for hijo in self.leyenda.winfo_children():
            hijo.destroy()
        self.etiquetas = []
        if self.sustitucion:
            grupos = (("Cómo leer la operación", elementos_sustitucion(texto)),)
        else:
            grupos = (("Elementos de la fórmula", elementos_formula(texto)),
                      ("Operaciones", operadores_expresion(texto)))
        for titulo, elementos in grupos:
            if not elementos:
                continue
            ttk.Label(self.leyenda, text=titulo, style="CardSection.TLabel").pack(
                anchor="w", pady=(0, 6))
            for simbolo, descripcion in elementos:
                recuadro = ttk.Frame(self.leyenda, style="DataBlock.TFrame", padding=(12, 9))
                recuadro.pack(fill="x", pady=(0, 6))
                recuadro.columnconfigure(1, weight=1)
                clave = ttk.Label(recuadro, text=simbolo, style="DataKey.TLabel", justify="left", wraplength=80)
                clave.grid(row=0, column=0, sticky="nw", padx=(0, 14))
                detalle = ttk.Label(recuadro, text=descripcion, style="DataValue.TLabel",
                                     justify="left", wraplength=260)
                detalle.grid(row=0, column=1, sticky="nw")
                self.etiquetas.append((clave, detalle))
        self.ajustar_textos()
        self.organizar()

    def organizar(self, evento=None):
        if self.zona_leyenda is not None:
            self.izquierda.grid(row=0, column=0, sticky="ew")
            self.columnconfigure(0, weight=1)
            if self.etiquetas:
                self.leyenda.pack(fill="x", pady=(4, 8))
            else:
                self.leyenda.pack_forget()
            return
        ancho = self.winfo_width()
        # El umbral sigue el tamaño real de la fuente, incluido el escalado de Tk.
        unidad = font.nametofont("TkDefaultFont").measure("0")
        lateral = ancho >= max(720, unidad * 85)
        distribucion = lateral, bool(self.etiquetas)
        if self.distribucion == distribucion:
            return
        self.distribucion = distribucion
        self.izquierda.grid_forget()
        self.leyenda.grid_forget()
        uniforme = "explicacion" if lateral and self.etiquetas else ""
        self.columnconfigure(0, weight=2 if lateral and self.etiquetas else 1, minsize=0, uniform=uniforme)
        self.columnconfigure(1, weight=3 if lateral and self.etiquetas else 0, minsize=0, uniform=uniforme)
        self.izquierda.grid(row=0, column=0, sticky="new", padx=(0, 24) if lateral else 0)
        if self.etiquetas:
            self.leyenda.grid(row=0 if lateral else 1, column=1 if lateral else 0,
                              sticky="new", pady=0 if lateral else (10, 0))

    def ajustar_textos(self, evento=None):
        ancho = evento.width if evento is not None else self.leyenda.winfo_width()
        ancho_clave = min(125, max(58, int(ancho * .23)))
        ancho_detalle = max(80, ancho - ancho_clave - 42)
        for clave, detalle in self.etiquetas:
            clave.master.columnconfigure(0, minsize=ancho_clave)
            if int(clave.cget("wraplength")) != ancho_clave:
                clave.configure(wraplength=ancho_clave, width=0)
            if int(detalle.cget("wraplength")) != ancho_detalle:
                detalle.configure(wraplength=ancho_detalle)
