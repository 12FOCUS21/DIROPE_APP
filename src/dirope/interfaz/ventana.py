"""Inicio, navegación global y acceso a los asistentes de resolución."""

import logging
import tkinter as tk
from tkinter import messagebox, ttk

from ..modulos import MODULOS
from .asistente import Panel
from .componentes import (
    ACENTO, BORDE, DESCRIPCIONES, FONDO, NOCHE, PRIMARIO, SECUNDARIO, SUPERFICIE,
    TEXTO, TEXTO_SOBRE_OSCURO, TransicionPaginas, configurar_estilos, habilitar_desplazamiento,
)


class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DIROPE Calc | Dirección de Operaciones")
        ancho, alto = min(1400, self.winfo_screenwidth() - 60), min(940, self.winfo_screenheight() - 90)
        self.geometry(f"{ancho}x{alto}")
        self.minsize(min(1100, ancho), min(660, alto))
        configurar_estilos(self)
        self.decimales = tk.IntVar(value=6)
        self.movimiento = tk.BooleanVar(value=True)
        self.activo = None
        self.botones_nav = {}
        lateral = tk.Frame(self, background=NOCHE, width=210)
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)
        tk.Label(lateral, text="DIROPE", background=NOCHE, foreground=SUPERFICIE,
                 font=("Segoe UI", 24, "bold"), anchor="w").pack(fill="x", padx=20, pady=(28, 0))
        tk.Label(lateral, text="CALC / OPERACIONES", background=NOCHE, foreground=TEXTO_SOBRE_OSCURO,
                 font=("Segoe UI", 12), anchor="w").pack(fill="x", padx=20, pady=(0, 30))
        for clave, etiqueta in [(None, "Inicio"), *[(m.clave, m.nombre) for m in MODULOS]]:
            boton = ttk.Button(lateral, text=etiqueta, style="Nav.TButton", command=lambda c=clave: self.mostrar(c))
            boton.pack(fill="x", padx=10, pady=4)
            self.botones_nav[clave] = boton
        tk.Label(lateral, text="ESPACIO LOCAL\nSin conexión necesaria\n\nResolución guiada\n5 etapas · 3 herramientas",
                 background=NOCHE, foreground=TEXTO_SOBRE_OSCURO, justify="left", font=("Segoe UI", 12),
                 anchor="w").pack(side="bottom", fill="x", padx=20, pady=24)
        zona = ttk.Frame(self)
        zona.pack(fill="both", expand=True)
        cabecera = ttk.Frame(zona, padding=(24, 14))
        cabecera.pack(fill="x")
        self.ruta = ttk.Label(cabecera, text="Espacio de trabajo / Inicio", style="Muted.TLabel")
        self.ruta.pack(side="left")
        ajustes = ttk.Frame(cabecera)
        ajustes.pack(side="right")
        ttk.Checkbutton(ajustes, text="Efectos", variable=self.movimiento, command=self.cambiar_movimiento).pack(side="left", padx=10)
        ttk.Label(ajustes, text="Decimales").pack(side="left", padx=(0, 6))
        selector = ttk.Combobox(ajustes, textvariable=self.decimales, state="readonly", values=list(range(9)), width=3)
        selector.pack(side="left")
        selector.bind("<<ComboboxSelected>>", lambda e: self.actualizar_formato())
        self.contenido = TransicionPaginas(zona, self.movimiento)
        self.contenido.pack(fill="both", expand=True)
        self.inicio = self.construir_inicio()
        self.paneles = [Panel(self.contenido, modulo, self.decimales, self.movimiento) for modulo in MODULOS]
        self.bind("<Return>", self.avanzar_activo)
        self.bind("<Alt-Home>", lambda e: self.mostrar(None))
        self.mostrar(None)

    def construir_inicio(self):
        contenedor = ttk.Frame(self.contenido)
        lienzo = tk.Canvas(contenedor, background=FONDO, highlightthickness=0)
        barra = ttk.Scrollbar(contenedor, orient="vertical", command=lienzo.yview)
        lienzo.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        lienzo.pack(fill="both", expand=True)
        pagina = ttk.Frame(lienzo, padding=24)
        identificador = lienzo.create_window((0, 0), window=pagina, anchor="nw")
        pagina.bind("<Configure>", lambda e: lienzo.configure(scrollregion=lienzo.bbox("all")))
        lienzo.bind("<Configure>", lambda e: lienzo.itemconfigure(identificador, width=e.width))
        hero = tk.Frame(pagina, background=SUPERFICIE, padx=26, pady=24,
                        highlightbackground=BORDE, highlightthickness=1)
        hero.pack(fill="x")
        tk.Label(hero, text="COMPRENDE · RESUELVE · PRESENTA", background=SUPERFICIE,
                 foreground=ACENTO, font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x")
        tk.Label(hero, text="Cada problema tiene un proceso.", background=SUPERFICIE,
                 foreground=TEXTO, font=("Segoe UI", 28, "bold"), anchor="w", wraplength=850,
                 justify="left").pack(fill="x", pady=(10, 8))
        tk.Label(hero, text="Plantea el caso, organiza los datos, confirma el método y explica tu solución.",
                 background=SUPERFICIE, foreground=SECUNDARIO, font=("Segoe UI", 12),
                 anchor="w", wraplength=800, justify="left").pack(fill="x")
        ttk.Button(hero, text="Explorar un ejemplo guiado →", style="Primary.TButton", command=self.abrir_demo).pack(anchor="w", pady=(18, 0))
        ttk.Label(pagina, text="Elige qué necesitas resolver", style="Subtitle.TLabel").pack(anchor="w", pady=(24, 6))
        ttk.Label(pagina, text="Las herramientas admiten datos propios. Los ejemplos solo sirven como referencia.",
                  style="Muted.TLabel", wraplength=850).pack(anchor="w", pady=(0, 16))
        tarjetas = ttk.Frame(pagina)
        tarjetas.pack(fill="x")
        for indice, modulo in enumerate(MODULOS):
            codigo, titulo, descripcion = DESCRIPCIONES[modulo.clave]
            tarjeta = tk.Frame(tarjetas, background=SUPERFICIE, padx=18, pady=18,
                               highlightbackground=BORDE, highlightthickness=1)
            tarjeta.grid(row=0, column=indice, sticky="nsew", padx=(0, 12 if indice < 2 else 0))
            tarjetas.columnconfigure(indice, weight=1, uniform="tarjetas")
            tk.Label(tarjeta, text=f"HERRAMIENTA {codigo}", font=("Segoe UI", 12, "bold"),
                     background=SUPERFICIE, foreground=ACENTO, anchor="w").pack(fill="x")
            tk.Label(tarjeta, text=titulo, font=("Segoe UI", 16, "bold"), background=SUPERFICIE,
                     foreground=TEXTO, wraplength=220, justify="left", anchor="nw", height=3).pack(fill="x", pady=(10, 0))
            tk.Label(tarjeta, text=descripcion, font=("Segoe UI", 12), background=SUPERFICIE,
                     foreground=SECUNDARIO, wraplength=220, justify="left", anchor="nw", height=4).pack(fill="x", pady=(4, 12))
            ttk.Button(tarjeta, text="Abrir herramienta →", command=lambda c=modulo.clave: self.mostrar(c)).pack(fill="x")
            tarjeta.bind("<Enter>", lambda e, t=tarjeta: t.configure(highlightbackground=PRIMARIO))
            tarjeta.bind("<Leave>", lambda e, t=tarjeta: t.configure(highlightbackground=BORDE))
        ttk.Label(pagina, text="Alcance actual: productividad y personal. Calidad, escenarios y otros capítulos aún no están disponibles.",
                  style="Muted.TLabel", wraplength=850).pack(anchor="w", pady=22)
        habilitar_desplazamiento(contenedor, lienzo)
        return contenedor

    def mostrar(self, clave):
        self.activo = clave
        for identificador, boton in self.botones_nav.items():
            boton.configure(style="NavActive.TButton" if identificador == clave else "Nav.TButton")
        for panel in self.paneles:
            panel.grafico.cancelar()
            panel.transicion.cancelar()
        if clave is None:
            self.contenido.mostrar(self.inicio)
            self.ruta.configure(text="Espacio de trabajo / Inicio")
        else:
            panel = next(p for p in self.paneles if p.modulo.clave == clave)
            self.contenido.mostrar(panel)
            self.ruta.configure(text=f"Inicio / {panel.modulo.nombre}")
            panel.mostrar_etapa(panel.etapa)

    def abrir_demo(self):
        self.mostrar("un_factor")
        self.paneles[0].cargar_ejemplo()

    def cambiar_movimiento(self):
        self.contenido.cancelar()
        for panel in self.paneles:
            panel.transicion.cancelar()
            panel.grafico.cancelar()
            panel.grafico.dibujar()

    def avanzar_activo(self, evento=None):
        foco = self.focus_get()
        if isinstance(foco, ttk.Button):
            foco.invoke()
            return "break"
        if self.activo is None or isinstance(foco, (ttk.Combobox, ttk.Checkbutton, tk.Text)):
            return None
        next(p for p in self.paneles if p.modulo.clave == self.activo).avanzar()
        return "break"

    def actualizar_formato(self):
        for panel in self.paneles:
            panel.renderizar()

    def report_callback_exception(self, tipo, valor, traza):
        logging.error("Error inesperado en la interfaz", exc_info=(tipo, valor, traza))
        messagebox.showerror("No se pudo completar la operación",
                             "Ocurrió un error inesperado. Revisa registro.log en la carpeta de datos de DIROPE Calc.", parent=self)
