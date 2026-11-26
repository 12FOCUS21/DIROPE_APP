"""Opciones desplegables con botones redondeados y navegación por teclado."""

import tkinter as tk
from tkinter import ttk

from .temas import vincular_colores


class Opciones(tk.Toplevel):
    def __init__(self, origen, opciones, elegido=None):
        self.origen = origen
        raiz = origen._root()
        anterior = getattr(raiz, "opciones_abiertas", None)
        if anterior is not None:
            anterior.cerrar()
        super().__init__(origen)
        raiz.opciones_abiertas = self
        self.withdraw()
        self.overrideredirect(True)
        self.transient(origen.winfo_toplevel())
        vincular_colores(self, background="fondo")
        marco = ttk.Frame(self, style="Panel.TFrame", padding=7)
        marco.pack(fill="both", expand=True)
        self.lienzo = tk.Canvas(marco, highlightthickness=0, borderwidth=0, width=1, height=1)
        vincular_colores(self.lienzo, background="superficie")
        self.lienzo.pack(side="left", fill="both", expand=True)
        lista = ttk.Frame(self.lienzo, style="Card.TFrame")
        interior = self.lienzo.create_window(0, 0, window=lista, anchor="nw")
        self.lienzo.bind("<Configure>", lambda e: self.lienzo.itemconfigure(interior, width=e.width))
        lista.bind("<Configure>", lambda _: self.lienzo.configure(scrollregion=self.lienzo.bbox(interior)))
        self.botones = []
        for indice, (texto, accion) in enumerate(opciones):
            seleccionado = indice == elegido
            boton = ttk.Button(lista, text=("✓  " if seleccionado else "     ") + str(texto),
                               style="PopupSelected.TButton" if seleccionado else "Popup.TButton",
                               command=lambda f=accion: self.elegir(f))
            boton.pack(fill="x", pady=1)
            boton.bind("<FocusIn>", lambda e: self.revelar(e.widget), add="+")
            self.botones.append(boton)
        self.bind("<Escape>", lambda _: self.cancelar())
        for tecla, destino in (("Up", -1), ("Down", 1), ("Tab", 1), ("ISO_Left_Tab", -1),
                               ("Shift-Tab", -1), ("Home", "inicio"), ("End", "fin")):
            self.bind(f"<{tecla}>", lambda _, paso=destino: self.mover(paso))
        self.bind("<Return>", self.activar_foco)
        self.bind("<MouseWheel>", self.rueda)
        self.bind("<Button-4>", self.rueda)
        self.bind("<Button-5>", self.rueda)
        self.bind("<ButtonPress-1>", self.clic_exterior, add="+")
        self.bind("<Destroy>", self.liberar, add="+")
        self.update_idletasks()
        x, y0 = origen.winfo_rootx(), origen.winfo_rooty()
        y = y0 + origen.winfo_height() + 4
        fondo = self.winfo_screenheight() - 34
        alto = min(lista.winfo_reqheight() + 14, max(fondo - y, y0 - 4, 1))
        barra_ancho = 0
        if lista.winfo_reqheight() + 14 > alto:
            barra = ttk.Scrollbar(marco, orient="vertical", command=self.lienzo.yview)
            barra.pack(side="right", fill="y")
            self.lienzo.configure(yscrollcommand=barra.set, yscrollincrement=12)
            barra_ancho = barra.winfo_reqwidth()
        ancho = min(self.winfo_screenwidth(), max(origen.winfo_width(), lista.winfo_reqwidth() + 14 + barra_ancho))
        if y + alto > fondo:
            y = max(0, min(y0 - alto - 4, fondo - alto))
        self.geometry(f"{ancho}x{alto}+{max(0, min(x, self.winfo_screenwidth() - ancho))}+{y}")
        self.deiconify()
        self.grab_set()
        inicial = self.botones[elegido if elegido is not None else 0]
        self.update_idletasks()
        self.revelar(inicial)
        inicial.focus_set()

    def revelar(self, boton):
        alto = self.lienzo.winfo_height()
        total = boton.master.winfo_height()
        if alto < total:
            inicio = self.lienzo.canvasy(0)
            arriba, abajo = boton.winfo_y(), boton.winfo_y() + boton.winfo_height()
            if arriba < inicio or abajo > inicio + alto:
                posicion = arriba if arriba < inicio else abajo - alto
                self.lienzo.yview_moveto(max(0, posicion) / total)

    def rueda(self, evento):
        direccion = -1 if evento.num == 4 or evento.delta > 0 else 1
        self.lienzo.yview_scroll(3 * direccion, "units")
        return "break"

    def mover(self, paso):
        foco = self.focus_get()
        actual = self.botones.index(foco) if foco in self.botones else 0
        indice = 0 if paso == "inicio" else len(self.botones) - 1 if paso == "fin" else (actual + paso) % len(self.botones)
        self.botones[indice].focus_set()
        return "break"

    def activar_foco(self, evento):
        if evento.widget in self.botones:
            evento.widget.invoke()
        return "break"

    def clic_exterior(self, evento):
        x, y = evento.x_root - self.winfo_rootx(), evento.y_root - self.winfo_rooty()
        if not (0 <= x < self.winfo_width() and 0 <= y < self.winfo_height()):
            return self.cancelar()

    def elegir(self, accion):
        self.cerrar()
        accion()

    def cancelar(self):
        self.cerrar()
        return "break"

    def cerrar(self, restaurar=True):
        if self.winfo_exists():
            self.destroy()
        if restaurar and self.origen.winfo_exists() and self.origen.winfo_viewable():
            self.origen.focus_set()

    def liberar(self, evento):
        if evento.widget is self:
            raiz = self._root()
            if getattr(raiz, "opciones_abiertas", None) is self:
                raiz.opciones_abiertas = None


class SelectorRedondeado(ttk.Combobox):
    """Conserva StringVar, current() y ComboboxSelected sin mostrar la lista nativa."""

    def __init__(self, padre, **opciones):
        super().__init__(padre, **opciones)
        for secuencia in ("<ButtonPress-1>", "<Down>", "<Alt-Down>", "<F4>", "<space>", "<Return>"):
            self.bind(secuencia, self.abrir)
        self.bind("<Unmap>", self.cerrar_al_ocultar, add="+")

    def abrir(self, evento=None):
        valores = self.tk.splitlist(self.cget("values"))
        if valores and not self.instate(("disabled",)) and self.winfo_viewable():
            indice = self.current()
            Opciones(self, [(valor, lambda i=i: self.seleccionar(i)) for i, valor in enumerate(valores)],
                     indice if indice >= 0 else None)
        return "break"

    def seleccionar(self, indice):
        if self.current() != indice:
            self.current(indice)
            self.event_generate("<<ComboboxSelected>>", when="tail")

    def cerrar_al_ocultar(self, evento=None):
        actual = getattr(self._root(), "opciones_abiertas", None)
        if actual is not None and actual.origen is self:
            actual.cerrar(restaurar=False)


class MenuRedondeado(ttk.Button):
    def __init__(self, padre, titulo, opciones, **kwargs):
        self.opciones = opciones
        super().__init__(padre, text=f"{titulo}  ▾", command=self.abrir, **kwargs)
        self.bind("<Down>", self.abrir)
        self.bind("<Unmap>", lambda evento: SelectorRedondeado.cerrar_al_ocultar(self, evento), add="+")

    def abrir(self, evento=None):
        if self.winfo_viewable() and not self.instate(("disabled",)):
            opciones = self.opciones() if callable(self.opciones) else self.opciones
            if opciones:
                Opciones(self, opciones)
        return "break"
