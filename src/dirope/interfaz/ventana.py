"""Inicio, navegación global y acceso a los asistentes de resolución."""

import logging
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

from ..historial import Historial, carpeta_local
from ..modulos import MODULOS
from .asistente import Panel, pagina_desplazable
from .componentes import (
    BORDE, DESCRIPCIONES, NOCHE, SUPERFICIE, TransicionPaginas, configurar_estilos, habilitar_desplazamiento,
)


class Aplicacion(tk.Tk):
    def __init__(self, carpeta=None):
        super().__init__()
        self.title("DIROPE Calc | Dirección de Operaciones")
        ancho, alto = min(1400, self.winfo_screenwidth() - 60), min(940, self.winfo_screenheight() - 90)
        self.geometry(f"{ancho}x{alto}")
        self.minsize(min(960, ancho), min(580, alto))
        configurar_estilos(self)
        self.decimales = tk.IntVar(value=6)
        self.movimiento = tk.BooleanVar(value=False)
        self.activo = None
        self.historial = Historial(carpeta or carpeta_local())
        self.botones_nav = {}
        cabecera = ttk.Frame(self, style="Card.TFrame", padding=(26, 10))
        cabecera.pack(fill="x")
        ttk.Label(cabecera, text="▥  DIROPE", style="CardTitle.TLabel").pack(side="left")
        ttk.Label(cabecera, text="Calc / Operaciones", style="CardMuted.TLabel").pack(side="left", padx=18)
        cuerpo = ttk.Frame(self)
        cuerpo.pack(fill="both", expand=True)
        lateral = self.lateral = tk.Frame(cuerpo, background=NOCHE, width=168)
        lateral.pack_propagate(False)
        for clave, etiqueta in ((None, "Inicio"), ("un_factor", "Un factor"),
                                ("multifactor", "Multifactor"), ("capacidad", "Capacidad y personal")):
            icono = DESCRIPCIONES[clave][0] if clave else "⌂"
            boton = ttk.Button(lateral, text=f"{icono}   {etiqueta}", style="Nav.TButton",
                               command=lambda c=clave: self.mostrar(c))
            boton.pack(fill="x", padx=10, pady=4)
            self.botones_nav[clave] = boton
        zona = ttk.Frame(cuerpo)
        zona.pack(fill="both", expand=True)
        self.zona = zona
        ajustes = ttk.Frame(cabecera, style="Card.TFrame")
        ajustes.pack(side="right")
        ttk.Label(ajustes, text="Decimales", style="Card.TLabel").pack(side="left", padx=(0, 6))
        selector = ttk.Combobox(ajustes, textvariable=self.decimales, state="readonly", values=list(range(9)), width=3)
        selector.pack(side="left")
        selector.bind("<<ComboboxSelected>>", lambda e: self.actualizar_formato())
        menu_ajustes = ttk.Menubutton(ajustes, text="Ajustes")
        opciones = tk.Menu(menu_ajustes, tearoff=False)
        opciones.add_checkbutton(label="Animación", variable=self.movimiento, command=self.cambiar_movimiento)
        menu_ajustes.configure(menu=opciones)
        menu_ajustes.pack(side="left", padx=(12, 0))
        self.contenido = TransicionPaginas(zona, self.movimiento)
        self.contenido.pack(fill="both", expand=True)
        self.inicio = self.construir_inicio()
        self.paneles = [Panel(self.contenido, modulo, self.decimales, self.movimiento) for modulo in MODULOS]
        self.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.bind("<Return>", self.avanzar_activo)
        self.bind("<Alt-Home>", lambda e: self.mostrar(None))
        self.mostrar(None)

    def construir_inicio(self):
        contenedor, pagina, lienzo = pagina_desplazable(self.contenido)
        pagina.configure(padding=(28, 24, 28, 24))
        tk.Frame(pagina, background="#1669FA", width=58, height=5).pack(anchor="w", pady=(0, 12))
        ttk.Label(pagina, text="Inicio", style="Title.TLabel").pack(anchor="w", pady=(0, 18))
        tarjetas = ttk.Frame(pagina)
        tarjetas.pack(fill="x")
        for indice, modulo in enumerate(MODULOS):
            simbolo, titulo, descripcion = DESCRIPCIONES[modulo.clave]
            tarjeta = tk.Frame(tarjetas, background=SUPERFICIE, padx=14, pady=16,
                               highlightbackground=BORDE, highlightthickness=1)
            tarjeta.grid(row=0, column=indice, sticky="nsew", padx=(0, 10 if indice < 2 else 0))
            tarjetas.columnconfigure(indice, weight=1, uniform="tarjetas")
            encabezado_tarjeta = ttk.Frame(tarjeta, style="Card.TFrame")
            encabezado_tarjeta.pack(fill="x")
            ttk.Label(encabezado_tarjeta, text=simbolo, style="ModuleIcon.TLabel",
                      padding=(10, 6)).pack(side="left", anchor="n")
            textos = ttk.Frame(encabezado_tarjeta, style="Card.TFrame")
            textos.pack(side="left", fill="x", expand=True, padx=(12, 0))
            nombre = ttk.Label(textos, text=titulo, style="CardTitle.TLabel", wraplength=185)
            nombre.pack(anchor="w")
            subtitulo = ttk.Label(textos, text=descripcion, style="CardMuted.TLabel", wraplength=185)
            subtitulo.pack(anchor="w", pady=(3, 0))
            def ajustar_textos(evento, etiquetas=(nombre, subtitulo)):
                for etiqueta in etiquetas:
                    etiqueta.configure(wraplength=max(90, evento.width))

            textos.bind("<Configure>", ajustar_textos)
            ttk.Button(tarjeta, text="Abrir →", command=lambda c=modulo.clave: self.mostrar(c)).pack(
                side="bottom", anchor="e", pady=(14, 0))
        bloque = ttk.Frame(pagina, style="Panel.TFrame", padding=16)
        bloque.pack(fill="x", pady=(22, 0))
        cabecera = ttk.Frame(bloque, style="Card.TFrame")
        cabecera.pack(fill="x")
        ttk.Label(cabecera, text="Cálculos recientes", style="CardTitle.TLabel").pack(side="left")
        ttk.Button(cabecera, text="Administrar →", command=self.administrar).pack(side="right")
        self.recientes = ttk.Frame(bloque, style="Card.TFrame")
        self.recientes.pack(fill="x", pady=(8, 0))
        self.lienzo_inicio = lienzo
        habilitar_desplazamiento(contenedor, lienzo)
        return contenedor

    def abrir_ejemplo(self, clave, nombre):
        panel = next(p for p in self.paneles if p.modulo.clave == clave)
        if panel.confirmar_reemplazo():
            panel.ejemplo.set(nombre)
            panel.cargar_ejemplo(confirmar=False)
            self.mostrar(clave)

    def mostrar(self, clave):
        self.activo = clave
        for identificador, boton in self.botones_nav.items():
            boton.configure(style="NavActive.TButton" if identificador == clave else "Nav.TButton")
        for panel in self.paneles:
            panel.grafico.cancelar()
            panel.transicion.cancelar()
        if clave is None:
            self.lateral.pack_forget()
            self.refrescar_historial()
            self.contenido.mostrar(self.inicio)
        else:
            if not self.lateral.winfo_manager():
                self.lateral.pack(side="left", fill="y", before=self.zona)
            panel = next(p for p in self.paneles if p.modulo.clave == clave)
            self.contenido.mostrar(panel)
            panel.mostrar_etapa(panel.etapa)

    def listar_calculos(self):
        try:
            return self.historial.listar()
        except OSError:
            return [], 1

    def refrescar_historial(self):
        for hijo in self.recientes.winfo_children():
            hijo.destroy()
        registros, errores = self.listar_calculos()
        if not registros:
            ttk.Label(self.recientes, text="Todavía no hay cálculos guardados.",
                      style="CardMuted.TLabel").pack(anchor="w", pady=4)
        for registro in registros[:3]:
            fila = ttk.Frame(self.recientes, style="Card.TFrame")
            fila.pack(fill="x", pady=3)
            modulo = next((m.nombre for m in MODULOS if m.clave == registro["modulo"]), registro["modulo"])
            fecha = datetime.fromisoformat(registro["modificado"]).astimezone().strftime("%d/%m/%Y %H:%M")
            ttk.Label(fila, text=f'{registro["nombre"]} · {modulo} · {fecha}', style="Card.TLabel",
                      wraplength=580).pack(side="left", fill="x", expand=True)
            ttk.Button(fila, text="Continuar", command=lambda r=registro: self.abrir_guardado(r["id"])).pack(side="right")
        if errores:
            ttk.Label(self.recientes, text="Algunos cálculos guardados no se pudieron leer.",
                      style="CardMuted.TLabel").pack(anchor="w")
        habilitar_desplazamiento(self.recientes, self.lienzo_inicio)

    def administrar(self):
        ventana = tk.Toplevel(self)
        ventana.title("Cálculos guardados")
        ventana.transient(self)
        ventana.geometry("720x340")
        marco = ttk.Frame(ventana, padding=14)
        marco.pack(fill="both", expand=True)
        lista = ttk.Treeview(marco, columns=("nombre", "modo", "fecha"), show="headings", selectmode="browse")
        for campo, etiqueta in (("nombre", "Ejercicio"), ("modo", "Tipo"), ("fecha", "Modificado")):
            lista.heading(campo, text=etiqueta)
        barra = ttk.Scrollbar(marco, orient="vertical", command=lista.yview)
        lista.configure(yscrollcommand=barra.set)
        marco.columnconfigure(0, weight=1)
        marco.rowconfigure(0, weight=1)
        lista.grid(row=0, column=0, sticky="nsew")
        barra.grid(row=0, column=1, sticky="ns")
        aviso = ttk.Label(marco, style="Muted.TLabel")
        aviso.grid(row=1, column=0, sticky="w")
        acciones = ttk.Frame(marco)
        acciones.grid(row=2, column=0, sticky="w", pady=(8, 0))

        def actualizar():
            for fila in lista.get_children():
                lista.delete(fila)
            registros, errores = self.listar_calculos()
            for r in registros:
                fecha = datetime.fromisoformat(r["modificado"]).astimezone().strftime("%d/%m/%Y %H:%M")
                lista.insert("", "end", iid=r["id"], values=(r["nombre"], r["datos"].get("modo", ""), fecha))
            aviso.configure(text="Algunos registros no se pudieron leer." if errores else
                            ("" if registros else "Todavía no hay cálculos guardados."))

        def abrir():
            if lista.selection() and self.abrir_guardado(lista.selection()[0], ventana):
                ventana.destroy()

        def eliminar():
            if lista.selection() and messagebox.askyesno("Eliminar cálculo", "¿Eliminar el cálculo seleccionado?", parent=ventana):
                identificador = lista.selection()[0]
                try:
                    self.historial.eliminar(identificador)
                except (OSError, ValueError) as error:
                    messagebox.showerror("No se pudo eliminar", str(error), parent=ventana)
                    return
                for panel in self.paneles:
                    if panel.identificador == identificador:
                        panel.identificador = None
                        panel.borrador = True
                actualizar()
                self.refrescar_historial()

        ttk.Button(acciones, text="Abrir cálculo", command=abrir).pack(side="left")
        ttk.Button(acciones, text="Eliminar", command=eliminar).pack(side="left", padx=8)
        lista.bind("<Double-1>", lambda _: abrir())
        lista.bind("<Return>", lambda _: abrir())
        actualizar()

    def abrir_guardado(self, identificador, padre=None):
        try:
            registro = self.historial.abrir(identificador)
            panel = next((p for p in self.paneles if p.modulo.clave == registro["modulo"]), None)
            datos = registro["datos"]
            if panel is None or datos.get("modo") not in panel.modos:
                raise ValueError("El cálculo guardado usa un modo desconocido.")
            filas = datos.get("insumos", [])
            if (any(not isinstance(datos.get(clave), str) for clave in panel.modos[datos["modo"]])
                    or not isinstance(filas, list) or any(
                        not isinstance(fila, dict) or
                        any(not isinstance(valor, bool if clave == "es_laboral" else str)
                            for clave, valor in fila.items()) for fila in filas)
                    or (panel.modulo.tabla_insumos and "insumos" not in datos)):
                raise ValueError("El cálculo guardado contiene entradas dañadas.")
        except (OSError, ValueError, TypeError, RecursionError) as error:
            messagebox.showerror("No se pudo abrir el cálculo", str(error), parent=padre or self)
            return False
        if not panel.confirmar_reemplazo():
            return False
        panel.cargar_datos(registro["nombre"], registro["enunciado"], datos, identificador)
        self.mostrar(panel.modulo.clave)
        panel.ver_resultado()
        return True

    def guardar_calculo(self, panel):
        if panel.resultado is None or panel.etapa != 4:
            return False
        try:
            registro = self.historial.guardar(panel.modulo.clave, panel.titulo.get().strip() or panel.objetivo.get(),
                                              panel.texto_enunciado(), panel.recoger_datos(), panel.identificador)
        except (OSError, ValueError) as error:
            panel.estado.set(f"No se pudo guardar el cálculo. {error}")
            return False
        panel.identificador = registro["id"]
        panel.borrador = False
        panel.estado.set("Cálculo guardado.")
        return True

    def abrir_demo(self):
        self.abrir_ejemplo("un_factor", next(iter(self.paneles[0].modulo.ejemplos)))

    def cerrar(self):
        if any(panel.borrador for panel in self.paneles):
            if not messagebox.askyesno("Cerrar DIROPE Calc", "¿Cerrar y descartar los cálculos de esta sesión?", parent=self):
                return
        self.destroy()

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
            for registro in panel.filas:
                panel.actualizar_costo(registro)
            if panel.actualizar_vista is None:
                panel.actualizar_vista = panel.after_idle(panel.previsualizar)
            panel.renderizar()

    def report_callback_exception(self, tipo, valor, traza):
        logging.error("Error inesperado en la interfaz", exc_info=(tipo, valor, traza))
        messagebox.showerror("No se pudo completar la operación",
                             "Ocurrió un error inesperado. Revisa registro.log en la carpeta de datos de DIROPE Calc.", parent=self)
