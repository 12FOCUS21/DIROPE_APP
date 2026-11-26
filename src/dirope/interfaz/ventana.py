"""Inicio, navegación global y acceso a los asistentes de resolución."""

import logging
from dataclasses import asdict
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, ttk

from ..historial import Historial, carpeta_local
from ..preferencias import Preferencias
from ..banco import generar_banco
from ..modulos import MODULOS
from .asistente import Panel, pagina_desplazable
from .temas import actualizar_controles, vincular_colores
from .componentes import (
    BORDE, DESCRIPCIONES, NOCHE, SUPERFICIE, TransicionPaginas, configurar_estilos, habilitar_desplazamiento, mostrar_informe,
)


from .iconos import vincular_icono
from .opciones import MenuRedondeado, SelectorRedondeado
from .redondeado import SuperficieCanvas
from .tokens import ALTURAS


class Aplicacion(tk.Tk):
    def __init__(self, carpeta=None):
        super().__init__()
        self.title("DIROPE Calc | Dirección de Operaciones")
        ancho, alto = min(1400, self.winfo_screenwidth() - 60), min(940, self.winfo_screenheight() - 90)
        self.geometry(f"{ancho}x{alto}")
        self.minsize(min(960, ancho), min(580, alto))
        self.historial = Historial(carpeta or carpeta_local())
        self.preferencias = Preferencias(self.historial.carpeta)
        self.nombre_tema = self.preferencias.leer_tema()
        self.tema = tk.StringVar(value=self.nombre_tema)
        configurar_estilos(self)
        self.decimales = tk.IntVar(value=6)
        self.movimiento = tk.BooleanVar(value=False)
        self.activo = None
        self.botones_nav = {}
        self.cabecera = SuperficieCanvas(self, "cabecera", ALTURAS["cabecera"])
        self.cabecera.pack(fill="x")
        identidad = ttk.Frame(self.cabecera, style="Header.TFrame")
        self.cabecera.create_window(24, ALTURAS["cabecera"] // 2, window=identidad, anchor="w")
        marca = ttk.Label(identidad, text="  DIROPE", compound="left", style="HeaderTitle.TLabel")
        vincular_icono(marca, "un_factor", "acento")
        marca.pack(side="left")
        ttk.Label(identidad, text="Calc / Operaciones", style="HeaderMuted.TLabel").pack(side="left", padx=16)
        cuerpo = ttk.Frame(self)
        cuerpo.pack(fill="both", expand=True)
        lateral = self.lateral = tk.Frame(cuerpo, background=NOCHE, width=168)
        vincular_colores(lateral, background="noche")
        lateral.pack_propagate(False)
        for clave, etiqueta in ((None, "Inicio"), ("un_factor", "Un factor"),
                                ("multifactor", "Multifactor"), ("capacidad", "Capacidad y\npersonal")):
            boton = ttk.Button(lateral, text=etiqueta, compound="left", style="Nav.TButton",
                               command=lambda c=clave: self.mostrar(c))
            vincular_icono(boton, clave, "lateral", 20)
            boton.pack(fill="x", padx=10, pady=4)
            self.botones_nav[clave] = boton
        zona = ttk.Frame(cuerpo)
        zona.pack(fill="both", expand=True)
        self.zona = zona
        ajustes = ttk.Frame(self.cabecera, style="Header.TFrame")
        controles = self.cabecera.create_window(0, ALTURAS["cabecera"] // 2, window=ajustes, anchor="e")
        self.cabecera.bind("<Configure>", lambda e: self.cabecera.coords(controles, e.width - 24,
                                                                         ALTURAS["cabecera"] // 2), add="+")
        ttk.Label(ajustes, text="Tema", style="HeaderMuted.TLabel").pack(side="left", padx=(0, 6))
        self.selector_tema = SelectorRedondeado(ajustes, textvariable=self.tema, values=("Claro", "Oscuro"),
                                           state="readonly", width=8, style="Header.TCombobox")
        self.selector_tema.pack(side="left", padx=(0, 16))
        self.selector_tema.bind("<<ComboboxSelected>>", self.cambiar_tema)
        ttk.Label(ajustes, text="Decimales", style="HeaderMuted.TLabel").pack(side="left", padx=(0, 6))
        selector = SelectorRedondeado(ajustes, textvariable=self.decimales, state="readonly", values=list(range(9)),
                                width=3, style="Header.TCombobox")
        selector.pack(side="left")
        selector.bind("<<ComboboxSelected>>", lambda e: self.actualizar_formato())
        def alternar_animacion():
            self.movimiento.set(not self.movimiento.get())
            self.cambiar_movimiento()

        menu_ajustes = MenuRedondeado(ajustes, "Ajustes", lambda: [
            ("Desactivar animación" if self.movimiento.get() else "Activar animación", alternar_animacion),
        ], style="HeaderMenu.TButton")
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
        acento = tk.Frame(pagina, width=58, height=5)
        vincular_colores(acento, background="acento").pack(anchor="w", pady=(0, 12))
        ttk.Label(pagina, text="Inicio", style="Title.TLabel").pack(anchor="w", pady=(0, 18))
        tarjetas = ttk.Frame(pagina)
        tarjetas.pack(fill="x")
        for indice, modulo in enumerate(MODULOS):
            titulo, descripcion = DESCRIPCIONES[modulo.clave]
            tarjeta = ttk.Frame(tarjetas, style="Panel.TFrame", padding=(16, 18))
            tarjeta.grid(row=0, column=indice, sticky="nsew", padx=(0, 10 if indice < 2 else 0))
            tarjetas.columnconfigure(indice, weight=1, uniform="tarjetas")
            encabezado_tarjeta = ttk.Frame(tarjeta, style="Card.TFrame")
            encabezado_tarjeta.pack(fill="x")
            insignia = ttk.Label(encabezado_tarjeta, style="ModuleIcon.TLabel", padding=(8, 6))
            vincular_icono(insignia, modulo.clave, "acento", 26)
            insignia.pack(side="left", anchor="n")
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
            ttk.Button(tarjeta, text="Abrir →", style="Card.TButton", command=lambda c=modulo.clave: self.mostrar(c)).pack(
                side="bottom", anchor="e", pady=(14, 0))
        bloque = ttk.Frame(pagina, style="Panel.TFrame", padding=16)
        bloque.pack(fill="x", pady=(22, 0))
        cabecera = ttk.Frame(bloque, style="Card.TFrame")
        cabecera.pack(fill="x")
        ttk.Label(cabecera, text="Mi biblioteca de ejercicios", style="CardTitle.TLabel").pack(side="left")
        ttk.Button(cabecera, text="Ver todos / Buscar →", style="Card.TButton", command=self.administrar).pack(side="right")
        ttk.Button(cabecera, text="Banco de práctica", style="Card.TButton", command=self.abrir_banco).pack(side="right", padx=8)
        ttk.Label(bloque, text="Guardado automático al desarrollar o ver resultados. Al editar se actualiza el mismo ejercicio.",
                  style="CardMuted.TLabel", wraplength=650).pack(anchor="w", pady=(8, 0))
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
            vincular_icono(boton, identificador, "blanco" if identificador == clave else "lateral", 20)
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

    def listar_calculos(self, busqueda="", modulo=""):
        try:
            return self.historial.listar(busqueda, modulo)
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
            fila = ttk.Frame(self.recientes, style="Exercise.TFrame", padding=(14, 10))
            fila.pack(fill="x", pady=5)
            modulo = next((m.nombre for m in MODULOS if m.clave == registro["modulo"]), registro["modulo"])
            fecha = datetime.fromisoformat(registro["modificado"]).astimezone().strftime("%d/%m/%Y %H:%M")
            ttk.Button(fila, text="Continuar", style="Exercise.TButton",
                       command=lambda r=registro: self.abrir_guardado(r["id"])).pack(side="right", padx=(10, 0))
            texto = ttk.Frame(fila, style="Data.TFrame")
            texto.pack(side="left", fill="x", expand=True)
            nombre = ttk.Label(texto, text=registro["nombre"], style="DataValue.TLabel", wraplength=420)
            nombre.pack(anchor="w")
            detalle = ttk.Label(texto, text=f"{modulo} · {fecha}", style="DataKey.TLabel", wraplength=420)
            detalle.pack(anchor="w", pady=(3, 0))
            def ajustar(evento, etiquetas=(nombre, detalle)):
                for control in etiquetas:
                    ancho = max(80, evento.width - 2)
                    if int(control.cget("wraplength")) != ancho:
                        control.configure(wraplength=ancho)
            texto.bind("<Configure>", ajustar)
        if errores:
            ttk.Label(self.recientes, text="Algunos cálculos guardados no se pudieron leer.",
                      style="CardMuted.TLabel").pack(anchor="w")
        habilitar_desplazamiento(self.recientes, self.lienzo_inicio)

    def administrar(self):
        ventana = tk.Toplevel(self)
        vincular_colores(ventana, background="fondo")
        ventana.title("Mi biblioteca de ejercicios")
        ventana.transient(self)
        ventana.geometry("850x480")
        ventana.minsize(660, 380)
        filtros = ttk.Frame(ventana, padding=(14, 14, 14, 0))
        filtros.pack(fill="x")
        busqueda = tk.StringVar()
        tipo = tk.StringVar(value="Todos")
        ttk.Label(filtros, text="Buscar:").pack(side="left")
        ttk.Entry(filtros, textvariable=busqueda).pack(side="left", fill="x", expand=True, padx=8)
        tipos = {"Todos": "", **{m.nombre: m.clave for m in MODULOS}}
        SelectorRedondeado(filtros, textvariable=tipo, values=list(tipos), state="readonly", width=24).pack(side="left")
        ttk.Label(ventana, text=f"Almacenamiento local: {self.historial.carpeta}",
                  style="Muted.TLabel", wraplength=780).pack(fill="x", padx=14, pady=(8, 0))
        marco = ttk.Frame(ventana, padding=14)
        marco.pack(fill="both", expand=True)
        lista = ttk.Treeview(marco, columns=("nombre", "modo", "fecha"), show="headings", selectmode="browse")
        for campo, etiqueta in (("nombre", "Ejercicio"), ("modo", "Tipo"), ("fecha", "Modificado")):
            lista.heading(campo, text=etiqueta)
            lista.column(campo, width=230 if campo != "fecha" else 145, minwidth=90)
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
            registros, errores = self.listar_calculos(busqueda.get(), tipos[tipo.get()])
            for r in registros:
                fecha = datetime.fromisoformat(r["modificado"]).astimezone().strftime("%d/%m/%Y %H:%M")
                lista.insert("", "end", iid=r["id"], values=(r["nombre"], r["datos"].get("modo", ""), fecha))
            aviso.configure(text=f"{len(registros)} ejercicio(s)." +
                            (f" {errores} registro(s) no se pudieron leer." if errores else ""))

        def ver_informe():
            if not lista.selection():
                return
            try:
                registro = self.historial.abrir(lista.selection()[0])
            except (OSError, ValueError) as error:
                messagebox.showerror("No se pudo leer", str(error), parent=ventana)
                return
            informe = registro.get("resolucion", {}).get("informe")
            if not informe:
                messagebox.showinfo("Ejercicio antiguo", "Abre el ejercicio una vez para guardar su resolución completa.", parent=ventana)
                return
            mostrar_informe(ventana, "Resolución guardada · " + registro["nombre"], informe)

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
                    for modo, estado in list(panel.borradores_modo.items()):
                        if estado[3] == identificador:
                            panel.borradores_modo[modo] = (*estado[:3], None, True)
                actualizar()
                self.refrescar_historial()

        ttk.Button(acciones, text="Abrir cálculo", command=abrir).pack(side="left")
        ttk.Button(acciones, text="Ver resolución guardada", command=ver_informe).pack(side="left", padx=8)
        ttk.Button(acciones, text="×  Eliminar", style="Danger.TButton", command=eliminar).pack(side="left", padx=8)
        lista.bind("<Double-1>", lambda _: abrir())
        lista.bind("<Return>", lambda _: abrir())
        busqueda.trace_add("write", lambda *_: actualizar())
        tipo.trace_add("write", lambda *_: actualizar())
        actualizar()
        return ventana

    def abrir_banco(self):
        ventana = tk.Toplevel(self)
        vincular_colores(ventana, background="fondo")
        ventana.title("Banco de práctica · 100 ejercicios por método")
        ventana.geometry("900x500")
        ventana.minsize(660, 380)
        casos = generar_banco()
        marco = ttk.Frame(ventana, padding=16)
        marco.pack(fill="both", expand=True)
        ttk.Label(marco, text="1 000 ejercicios sintéticos · 100 por método", style="Subtitle.TLabel").pack(anchor="w")
        ttk.Label(marco, text="Se guardan en tu biblioteca solo cuando los desarrollas. No reemplazan tus ejercicios.",
                  style="Muted.TLabel", wraplength=800).pack(anchor="w", pady=(6, 12))
        filtro = tk.StringVar(value="Todos")
        modos = ["Todos", *dict.fromkeys(c["datos"]["modo"] for c in casos)]
        selector = SelectorRedondeado(marco, textvariable=filtro, values=modos, state="readonly")
        selector.pack(fill="x", pady=(0, 12))
        zona = ttk.Frame(marco)
        zona.pack(fill="both", expand=True)
        lista = ttk.Treeview(zona, columns=("caso", "modulo"), show="headings", selectmode="browse")
        lista.heading("caso", text="Ejercicio")
        lista.heading("modulo", text="Herramienta")
        lista.column("caso", width=530, minwidth=250)
        lista.column("modulo", width=200, minwidth=120)
        barra = ttk.Scrollbar(zona, command=lista.yview)
        barra.pack(side="right", fill="y")
        lista.configure(yscrollcommand=barra.set)
        lista.pack(fill="both", expand=True)

        def filtrar(*_):
            lista.delete(*lista.get_children())
            for indice, caso in enumerate(casos):
                if filtro.get() == "Todos" or caso["datos"]["modo"] == filtro.get():
                    modulo = next(m.nombre for m in MODULOS if m.clave == caso["modulo"])
                    lista.insert("", "end", iid=str(indice), values=(caso["nombre"], modulo))

        def abrir():
            if not lista.selection():
                return
            caso = casos[int(lista.selection()[0])]
            panel = next(p for p in self.paneles if p.modulo.clave == caso["modulo"])
            if panel.confirmar_reemplazo():
                panel.cargar_datos(caso["nombre"], caso["enunciado"], caso["datos"])
                self.mostrar(caso["modulo"])
                ventana.destroy()

        ttk.Button(marco, text="Abrir ejercicio para resolver", command=abrir).pack(anchor="e", pady=(12, 0))
        lista.bind("<Double-1>", lambda _: abrir())
        lista.bind("<Return>", lambda _: abrir())
        filtro.trace_add("write", filtrar)
        filtrar()
        return ventana

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

    def guardar_calculo(self, panel, *, copia=False):
        if panel.resultado is None or panel.etapa not in (3, 4):
            return False
        try:
            registro = self.historial.guardar(panel.modulo.clave, panel.titulo.get().strip() or panel.objetivo.get(),
                                              panel.texto_enunciado(), panel.recoger_datos(),
                                              None if copia else panel.identificador,
                                              resolucion={"resultado": asdict(panel.resultado),
                                                          "informe": panel.informe_completo(),
                                                          "decimales": self.decimales.get()})
        except (OSError, ValueError, TypeError) as error:
            panel.estado.set(f"No se pudo guardar el cálculo. {error}")
            return False
        panel.identificador = registro["id"]
        panel.borrador = False
        panel.estado.set("Ejercicio guardado en tu biblioteca local." if not copia else "Copia guardada como otro ejercicio.")
        return True

    def abrir_demo(self):
        self.abrir_ejemplo("un_factor", next(iter(self.paneles[0].modulo.ejemplos)))

    def cerrar(self):
        if any(panel.tiene_borradores for panel in self.paneles):
            if not messagebox.askyesno("Cerrar DIROPE Calc", "¿Cerrar y descartar los cálculos de esta sesión?", parent=self):
                return
        self.destroy()

    def destroy(self):
        # Cancelar las vistas diferidas antes de destruir sus controles.
        for tarea in self.tk.call("after", "info"):
            self.tk.call("after", "cancel", tarea)
        super().destroy()

    def cambiar_movimiento(self):
        self.contenido.cancelar()
        for panel in self.paneles:
            panel.transicion.cancelar()
            panel.grafico.cancelar()
            panel.grafico.dibujar()

    def cambiar_tema(self, evento=None):
        tema = self.tema.get()
        if tema not in ("Claro", "Oscuro"):
            self.tema.set(self.nombre_tema)
            return False
        if tema == self.nombre_tema and self.preferencias.leer_tema() == tema:
            return True
        self.nombre_tema = tema
        configurar_estilos(self)
        actualizar_controles(self)
        try:
            self.preferencias.guardar_tema(tema)
        except OSError:
            messagebox.showwarning("Preferencia no guardada", "El tema se aplicó, pero no se pudo guardar la preferencia para el próximo inicio.", parent=self)
            return False
        return True

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
