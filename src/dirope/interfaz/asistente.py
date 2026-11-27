"""Resolución guiada: planteamiento, datos, identificación, desarrollo y resultados."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from .temas import vincular_colores
from .formula_explicada import FormulaExplicada
from .fondos import FondoAmbiental, LienzoAmbiental
from ..entradas import ayuda_campo, errores_entrada, FORMATO
from .opciones import MenuRedondeado, SelectorRedondeado

from ..analisis import analizar_datos, describir_ejemplo
from ..formato import numero
from ..informe import PDFNoDisponible, guardar_informe_html, informe_html, informe_pdf, secciones_informe
from ..modulos.variantes import costo_fila
from ..modulos.campos import CAMPOS_COMUNES, MODOS, GRUPOS_DATOS, grupos_datos
from .componentes import (
    BORDE, FONDO, PRIMARIO, SUPERFICIE, TEXTO,
    GraficoBarras, Indicadores, TransicionPaginas, habilitar_desplazamiento, resumen_resultado, mostrar_informe,
)

ETAPAS = ("Planteamiento", "Datos", "Identificación", "Desarrollo", "Resultados")


def pagina_desplazable(padre):
    """Crea un área de contenido desplazable independiente para una etapa."""
    exterior = FondoAmbiental(padre)
    lienzo = tk.Canvas(exterior, background=FONDO, highlightthickness=0)
    vincular_colores(lienzo, background="fondo")
    barra = ttk.Scrollbar(exterior, orient="vertical", command=lienzo.yview)
    lienzo.configure(yscrollcommand=barra.set)
    barra.pack(side="right", fill="y")
    lienzo.pack(fill="both", expand=True)
    contenido = FondoAmbiental(lienzo, padding=(8, 8, 24, 20))
    identificador = lienzo.create_window((0, 0), window=contenido, anchor="nw")
    contenido.bind("<Configure>", lambda e: lienzo.configure(scrollregion=lienzo.bbox(identificador)), add="+")
    lienzo.bind("<Configure>", lambda e: lienzo.itemconfigure(identificador, width=e.width), add="+")
    return exterior, contenido, lienzo


class Panel(FondoAmbiental):
    def __init__(self, padre, modulo, decimales, movimiento):
        super().__init__(padre, padding=(24, 4, 24, 16))
        self.modulo, self.decimales, self.movimiento = modulo, decimales, movimiento
        self.variables, self.filas, self.entradas = {}, [], []
        self.borrador = False
        self.identificador = None
        self.preparado = None
        self.datos_calculados = None
        self.error_calculo = None
        self.actualizar_vista = None
        self.resultado = None
        self.analisis = None
        self.etapa = 0
        self.habilitada = 0
        self.paso_actual = 0
        self.actualizando = True
        self.borradores_modo = {}
        self.modo_actual = None
        self.estado = tk.StringVar()
        self.titulo = tk.StringVar()
        self.modos = MODOS[modulo.clave]
        self.objetivo = tk.StringVar(value=next(iter(self.modos)))
        self.titulo.trace_add("write", self.contexto_modificado)

        LienzoAmbiental(self, titulo=modulo.nombre, height=50, width=1).pack(fill="x", pady=(0, 14))
        navegacion = FondoAmbiental(self)
        navegacion.pack(fill="x")
        self.botones_etapas = []
        for indice, nombre in enumerate(ETAPAS):
            boton = ttk.Button(navegacion, text=nombre, style="Step.TButton",
                               command=lambda i=indice: self.mostrar_etapa(i))
            boton.grid(row=0, column=indice, sticky="ew", padx=(0, 4))
            navegacion.columnconfigure(indice, weight=1, uniform="etapas")
            self.botones_etapas.append(boton)
        self.transicion = TransicionPaginas(self, movimiento)
        self.transicion.pack(fill="both", expand=True, pady=(14, 0))
        self.paginas, self.contenidos, self.lienzos = [], [], []
        for _ in ETAPAS:
            pagina, contenido, lienzo = pagina_desplazable(self.transicion)
            self.paginas.append(pagina)
            self.contenidos.append(contenido)
            self.lienzos.append(lienzo)

        self.construir_planteamiento()
        self.construir_datos()
        self.construir_identificacion()
        self.construir_desarrollo()
        self.construir_resultados()

        pie = FondoAmbiental(self)
        pie.pack(fill="x", pady=(12, 0))
        self.aviso = ttk.Label(pie, textvariable=self.estado, style="Muted.TLabel", wraplength=650, padding=(8, 4))
        self.aviso.pack(anchor="w", pady=(0, 10))
        self.anterior = ttk.Button(pie, text="← Anterior", command=self.retroceder)
        self.anterior.pack(side="left")
        ttk.Button(pie, text="+ Nuevo problema", command=self.limpiar).pack(side="left", padx=8)
        self.siguiente = ttk.Button(pie, style="Primary.TButton", command=self.avanzar)
        self.siguiente.pack(side="right")
        self.directo = ttk.Button(pie, text="Ver resultado", command=self.ver_resultado)
        self.directo.pack(side="right", padx=8)
        self.estado.trace_add("write", self.actualizar_aviso)
        self.actualizar_aviso()
        for pagina, lienzo in zip(self.paginas, self.lienzos):
            habilitar_desplazamiento(pagina, lienzo)
        self.actualizando = False
        self.mostrar_etapa(0)
        self.actualizar_vista = self.after_idle(self.previsualizar)

    def actualizar_aviso(self, *args):
        if self.estado.get():
            self.aviso.pack(anchor="w", pady=(0, 10), before=self.anterior)
        else:
            self.aviso.pack_forget()

    def construir_planteamiento(self):
        zona = self.contenidos[0]
        pagina = ttk.Frame(zona, style="Panel.TFrame", padding=20)
        pagina.pack(fill="x")
        ttk.Label(pagina, text="Lee el planteamiento", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(pagina, text="Primero lee el caso. Después podrás revisar los datos por secciones.",
                  style="CardMuted.TLabel", wraplength=490).pack(anchor="w", pady=(4, 14))
        ttk.Label(pagina, text="Título del caso (opcional)", style="CardSection.TLabel").pack(anchor="w")
        self.entrada_titulo = ttk.Entry(pagina, textvariable=self.titulo)
        self.entrada_titulo.pack(fill="x", pady=(6, 14))
        ttk.Label(pagina, text="Enunciado (opcional)", style="CardSection.TLabel").pack(anchor="w")
        bloque_enunciado = ttk.Frame(pagina, style="DataBlock.TFrame", padding=(10, 7))
        bloque_enunciado.pack(fill="x", pady=(6, 14))
        self.enunciado = tk.Text(bloque_enunciado, height=6, width=18, wrap="word", font=("Segoe UI", 12), relief="flat",
                                 spacing2=3, spacing3=6,
                                 background=SUPERFICIE, foreground=TEXTO, insertbackground=PRIMARIO,
                                 padx=8, pady=5, highlightthickness=0, highlightbackground=BORDE,
                                 highlightcolor=PRIMARIO)
        self.enunciado.pack(fill="x")
        vincular_colores(self.enunciado, background="suave", foreground="texto", insertbackground="texto",
                         highlightbackground="borde", highlightcolor="primario", selectbackground="primario")
        vincular_colores(self.enunciado, **self.enunciado.colores_tema, selectforeground="blanco")
        self.enunciado.bind("<<Modified>>", self.enunciado_modificado)
        ttk.Label(pagina, text="¿Qué calcular?", style="CardSection.TLabel").pack(anchor="w")
        selector = self.selector_modo = SelectorRedondeado(pagina, textvariable=self.objetivo, state="readonly",
                                values=list(self.modos), width=16)
        selector.pack(fill="x", pady=(6, 14))
        selector.bind("<<ComboboxSelected>>", self.cambiar_modo)
        ttk.Label(pagina, text="Ejemplo", style="CardSection.TLabel").pack(anchor="w")
        ejemplo = ttk.Frame(pagina, style="Card.TFrame")
        ejemplo.pack(fill="x", pady=(6, 0))
        self.ejemplo = SelectorRedondeado(ejemplo, state="readonly", values=list(self.modulo.ejemplos), width=12)
        self.ejemplo.current(0)
        self.ejemplo.pack(side="left", fill="x", expand=True)
        self.boton_ejemplo = ttk.Button(ejemplo, text="Cargar ejemplo", command=self.cargar_ejemplo)
        self.boton_ejemplo.pack(side="left", padx=(8, 0))

    def construir_datos(self):
        pagina = self.contenidos[1]
        pagina.columnconfigure(0, weight=1)
        editor = ttk.Frame(pagina)
        editor.grid(row=0, column=0, sticky="nsew")
        self.formulario = ttk.Frame(editor, style="Panel.TFrame", padding=16)
        self.formulario.pack(fill="x")
        ttk.Label(self.formulario, text="Datos del ejercicio", style="CardTitle.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 4))
        self.encabezados_datos = {titulo: ttk.Label(self.formulario, text=titulo, style="CardSection.TLabel")
                                  for titulo, _ in GRUPOS_DATOS}
        activas = {clave for campos in self.modos.values() for clave in campos}
        claves = (clave for _, campos in GRUPOS_DATOS for clave in campos if clave in activas)
        self.marcos = {}
        self.ayudas_campos = {}
        self.campos_revisados = set()
        self.filas_revisadas = False
        for clave in claves:
            campo = CAMPOS_COMUNES[clave]
            marco = ttk.Frame(self.formulario, style="Card.TFrame", padding=(0, 0, 12, 10))
            etiqueta = ttk.Label(marco, text=campo.etiqueta, style="Card.TLabel", wraplength=180)
            etiqueta.pack(anchor="w")
            marco.bind("<Configure>", lambda e, control=etiqueta: self.ajustar_ayuda(e, control))
            variable = tk.StringVar(value=campo.valor)
            self.variables[clave] = variable
            if clave == "medida_calidad":
                entrada = SelectorRedondeado(marco, textvariable=variable, state="readonly",
                                        values=("Cantidad", "%"), width=14)
            else:
                entrada = ttk.Entry(marco, textvariable=variable, width=14)
            entrada.pack(fill="x", pady=(5, 0))
            ayuda = ttk.Label(marco, style="InputHint.TLabel", wraplength=220, justify="left", width=1)
            ayuda.pack(fill="x", pady=(5, 0))
            self.ayudas_campos[clave] = ayuda
            entrada.bind("<FocusOut>", lambda evento, campo=clave: self.revisar_campo(campo), add="+")
            marco.bind("<Configure>", lambda evento, control=ayuda: self.ajustar_ayuda(evento, control), add="+")
            variable.trace_add("write", self.datos_modificados)
            self.marcos[clave] = (marco, entrada)
        for columna in range(2):
            self.formulario.columnconfigure(columna, weight=1, uniform="datos")
        if self.modulo.tabla_insumos:
            zona = ttk.Frame(editor, style="Panel.TFrame", padding=16)
            zona.pack(fill="x", pady=(12, 0))
            cabecera = ttk.Frame(zona, style="Card.TFrame")
            cabecera.pack(fill="x", pady=(0, 10))
            self.titulo_tabla = ttk.Label(cabecera, text="Insumos", style="CardTitle.TLabel")
            self.titulo_tabla.pack(side="left")
            ttk.Label(zona, text=f"{FORMATO}\nIndica cantidad y costo unitario, o un costo directo. "
                      "En categorías: cantidad y valor unitario. Marca Horas solo para trabajo en h-persona.",
                      style="InputHint.TLabel", wraplength=650, justify="left", width=1).pack(fill="x", pady=(0, 8))
            ttk.Button(cabecera, text="+ Añadir fila", command=self.agregar_fila).pack(side="right")
            self.duplicar = ttk.Button(cabecera, text="Duplicar inicial", command=self.duplicar_escenario)
            self.escenario = tk.StringVar(value="Inicial")
            self.selector_escenario = SelectorRedondeado(cabecera, textvariable=self.escenario, state="readonly",
                                                    values=("Inicial", "Alternativa", "Alternativa 2"), width=13)
            self.selector_escenario.bind("<<ComboboxSelected>>", lambda _: self.organizar_tabla())
            self.lienzo_tabla = tk.Canvas(zona, background=SUPERFICIE, highlightthickness=0)
            vincular_colores(self.lienzo_tabla, background="superficie")
            self.lienzo_tabla.pack(fill="x")
            self.barra_tabla = ttk.Scrollbar(zona, orient="horizontal", command=self.lienzo_tabla.xview)
            self.lienzo_tabla.configure(xscrollcommand=self.barra_tabla.set)
            self.tabla = ttk.Frame(self.lienzo_tabla, style="Card.TFrame")
            self.ventana_tabla = self.lienzo_tabla.create_window(0, 0, window=self.tabla, anchor="nw")
            self.tabla.bind("<Configure>", self.ajustar_tabla)
            self.lienzo_tabla.bind("<Configure>", self.ajustar_tabla)
            self.tabla.columnconfigure(0, weight=1)
            self.cabecera_tabla = ttk.Frame(self.tabla, style="Card.TFrame")
            self.cabecera_tabla.grid(row=0, column=0, sticky="ew")
            self.agregar_fila()
        self.vista = ttk.Frame(pagina, style="Panel.TFrame", padding=14)
        ttk.Label(self.vista, text="Vista previa", style="CardTitle.TLabel").pack(anchor="w")
        self.vista_datos = ttk.Label(self.vista, style="CardMuted.TLabel", wraplength=240)
        self.vista_datos.pack(fill="x", pady=(8, 0))
        self.vista_grafico = GraficoBarras(self.vista, tk.BooleanVar(value=False))
        pagina.bind("<Configure>", self.distribuir_datos, add="+")
        self.cambiar_modo()

    def ajustar_tabla(self, evento=None):
        ancho = max(self.tabla.winfo_reqwidth(), self.lienzo_tabla.winfo_width())
        alto = self.tabla.winfo_reqheight()
        self.lienzo_tabla.itemconfigure(self.ventana_tabla, width=ancho)
        self.lienzo_tabla.configure(height=alto, scrollregion=(0, 0, ancho, alto))
        if ancho > self.lienzo_tabla.winfo_width():
            self.barra_tabla.pack(fill="x")
        else:
            self.barra_tabla.pack_forget()
            self.lienzo_tabla.xview_moveto(0)

    def revelar_columna(self, evento):
        control = evento.widget
        ancho = self.tabla.winfo_width()
        visible = self.lienzo_tabla.winfo_width()
        izquierda = control.winfo_rootx() - self.lienzo_tabla.winfo_rootx()
        derecha = izquierda + control.winfo_width()
        if izquierda < 0 or derecha > visible:
            ajuste = izquierda if izquierda < 0 else derecha - visible
            self.lienzo_tabla.xview_moveto((self.lienzo_tabla.canvasx(0) + ajuste) / max(1, ancho))

    def obtener_resultado(self):
        datos = self.recoger_datos()
        if datos != self.datos_calculados:
            self.datos_calculados = datos
            self.preparado = None
            self.error_calculo = None
            try:
                errores = errores_entrada(self.modulo.clave, datos)
                if errores:
                    raise ValueError(next(iter(errores.values())))
                self.preparado = self.modulo.calcular(datos)
            except ValueError as error:
                self.error_calculo = str(error)
        if self.error_calculo is not None:
            raise ValueError(self.error_calculo)
        return self.preparado

    def revisar_campo(self, clave):
        if not self.actualizando:
            self.campos_revisados.add(clave)
            self.revisar_entradas()

    @staticmethod
    def ajustar_ayuda(evento, control):
        # Una página oculta aún no tiene un ancho asignado: no realimentar su tamaño solicitado.
        if not control.winfo_viewable():
            return
        ancho = max(80, evento.width - 12)
        if int(control.cget("wraplength")) != ancho:
            control.configure(wraplength=ancho)

    def revisar_fila(self, evento=None):
        if not self.actualizando:
            self.filas_revisadas = True
            self.revisar_entradas()

    def revisar_entradas(self, *, mostrar_todos=False, enfocar=False):
        """Ayuda contextual y errores junto al control; nunca bloquea la edición o el pegado."""
        datos = self.recoger_datos()
        errores = errores_entrada(self.modulo.clave, datos)
        if mostrar_todos:
            self.campos_revisados.update(self.modos[self.objetivo.get()])
            self.filas_revisadas = True
        primero = None
        for clave, (marco, entrada) in self.marcos.items():
            activo = clave in self.modos[self.objetivo.get()]
            visible = mostrar_todos or clave in self.campos_revisados or bool(str(datos.get(clave, "")).strip())
            error = errores.get(clave) if activo and visible else None
            entrada.state(["invalid"] if error else ["!invalid"])
            self.ayudas_campos[clave].configure(text=(f"Revisa: {error}" if error else ayuda_campo(clave, datos)),
                                              style="InputError.TLabel" if error else "InputHint.TLabel")
            if error and primero is None:
                primero = entrada
        if self.modulo.tabla_insumos:
            calidad = datos["modo"] == "Valor por calidad"
            filas = [registro for registro in self.filas if registro[3] == calidad and
                     (datos["modo"] != "Escenario individual" or registro[1]["escenario"].get() == "Inicial")]
            for indice, (_, variables, controles, _) in enumerate(filas):
                mensajes = []
                for clave in ("nombre", "cantidad", "precio", "directo", "unidad"):
                    error = errores.get(f"insumos.{indice}.{clave}")
                    mostrar = self.filas_revisadas or bool(variables[clave].get().strip())
                    controles[clave].state(["invalid"] if error and mostrar else ["!invalid"])
                    if error and mostrar:
                        mensajes.append(error)
                        if primero is None:
                            primero = controles[clave]
                controles["aviso"].configure(text=" · ".join(mensajes))
        if enfocar and primero is not None:
            if self.modulo.tabla_insumos:
                for _, variables, controles, _ in self.filas:
                    if primero in controles.values() and datos["modo"] == "Comparar alternativas":
                        self.escenario.set(variables["escenario"].get())
                        self.organizar_tabla()
            primero.focus_set()
            primero.event_generate("<FocusIn>")
        return errores

    def preparar(self):
        resultado = self.obtener_resultado()
        if self.analisis is None:
            self.analisis = analizar_datos(self.modulo.clave, self.datos_calculados, resultado=resultado)
            self.actualizar_identificacion()
        return resultado

    def ver_resultado(self):
        try:
            self.resultado = self.preparar()
        except ValueError as error:
            self.habilitada = max(self.habilitada, 1)
            self.mostrar_etapa(1)
            self.estado.set(f"Revisa los datos: {error}")
            self.aviso.configure(style="Error.TLabel")
            self.revisar_entradas(mostrar_todos=True, enfocar=True)
            return False
        self.estado.set("")
        self.habilitada = 4
        self.mostrar_etapa(4)
        self.winfo_toplevel().guardar_calculo(self)
        return True

    def distribuir_datos(self, evento):
        if evento.width >= 1050:
            self.vista.grid(row=0, column=1, sticky="new", padx=(12, 0))
        else:
            self.vista.grid(row=1, column=0, sticky="ew", padx=0, pady=(12, 0))

    def previsualizar(self):
        self.actualizar_vista = None
        self.revisar_entradas()
        try:
            resultado = self.obtener_resultado()
        except ValueError as error:
            self.directo.state(["disabled"])
            self.vista_datos.configure(text=str(error))
            self.vista_grafico.pack_forget()
            self.vista_grafico.presentar((), "", self.decimales.get())
            return
        self.directo.configure(state="normal" if self.etapa != 4 else "disabled")
        indicadores, serie, unidad, _ = resumen_resultado(self.modulo.clave, resultado)
        self.vista_datos.configure(text="\n\n".join(
            f"{paso.titulo}\n{self.valor_mostrado(paso)}" for paso in indicadores))
        if serie:
            self.vista_grafico.pack(fill="x", pady=(8, 0))
        else:
            self.vista_grafico.pack_forget()
        self.vista_grafico.presentar(serie, unidad, self.decimales.get(), resultado.tipo_grafico)

    def cambiar_modo(self, evento=None):
        nuevo = self.objetivo.get()
        if nuevo not in self.modos:
            self.objetivo.set(self.modo_actual or next(iter(self.modos)))
            self.estado.set("Selecciona un cálculo disponible.")
            return False
        if evento is not None and self.modo_actual and nuevo != self.modo_actual:
            anterior = self.modo_actual
            self.borradores_modo[anterior] = (
                self.titulo.get(), self.texto_enunciado(), self.datos_del_modo(anterior),
                self.identificador, self.borrador)
            guardado = self.borradores_modo.pop(nuevo, None)
            if guardado is None:
                datos = {clave: CAMPOS_COMUNES[clave].valor for clave in self.modos[nuevo]}
                datos.update(modo=nuevo, insumos=[])
                guardado = ("", "", datos, None, False)
            titulo, enunciado, datos, identificador, borrador = guardado
            self.cargar_datos(titulo, enunciado, datos, identificador)
            self.borrador = borrador
            self.estado.set("Método cambiado. Cada opción conserva su propio borrador durante esta sesión.")
            return True
        self.modo_actual = nuevo
        self.campos_revisados.clear()
        self.filas_revisadas = False
        for marco, _ in self.marcos.values():
            marco.grid_remove()
        for encabezado in self.encabezados_datos.values():
            encabezado.grid_remove()
        self.entradas.clear()
        fila = 1
        for titulo, campos in grupos_datos(self.modulo.clave, nuevo):
            self.encabezados_datos[titulo].grid(row=fila, column=0, columnspan=2, sticky="w", pady=(8, 6))
            for indice, clave in enumerate(campos):
                marco, entrada = self.marcos[clave]
                marco.grid(row=fila + 1 + indice // 2, column=indice % 2, sticky="ew")
                self.entradas.append(entrada)
            fila += 1 + (len(campos) + 1) // 2
        if self.modulo.clave == "capacidad":
            etiqueta = CAMPOS_COMUNES["actual"].etiqueta
            if self.objetivo.get() == "Meta directa":
                etiqueta = "Producción actual (opcional)"
            self.marcos["actual"][0].winfo_children()[0].configure(text=etiqueta)
        if self.modulo.tabla_insumos:
            calidad = self.objetivo.get() == "Valor por calidad"
            self.titulo_tabla.configure(text="Categorías de calidad" if calidad else "Insumos")
            if self.objetivo.get() == "Comparar alternativas":
                self.selector_escenario.pack(side="left", padx=10)
                self.duplicar.pack(side="right", padx=8)
            else:
                self.selector_escenario.pack_forget()
                self.duplicar.pack_forget()
            self.organizar_tabla()
        ejemplos = [nombre for nombre, datos in self.modulo.ejemplos.items()
                    if datos.get("modo", next(iter(self.modos))) == nuevo]
        self.ejemplo.configure(values=ejemplos)
        if self.ejemplo.get() not in ejemplos:
            self.ejemplo.set(ejemplos[0] if ejemplos else "")
        self.boton_ejemplo.configure(state="normal" if ejemplos else "disabled")
        if evento is not None:
            self.contexto_modificado()
        self.revisar_entradas()
        return True

    def construir_identificacion(self):
        pagina = self.contenidos[2]
        self.metodo = ttk.Frame(pagina, style="Panel.TFrame", padding=22)
        self.metodo.pack(fill="x")
        self.revision = ttk.Frame(pagina, style="Panel.TFrame", padding=18)
        self.revision.pack(fill="x", pady=16)

    def construir_desarrollo(self):
        pagina = self.contenidos[3]
        self.contador_paso = ttk.Label(pagina, style="Muted.TLabel")
        self.contador_paso.pack(anchor="w", pady=(0, 12))
        self.tarjeta_paso = ttk.Frame(pagina, style="Panel.TFrame", padding=24)
        self.tarjeta_paso.pack(fill="x")
        self.titulo_paso = ttk.Label(self.tarjeta_paso, style="CardTitle.TLabel", wraplength=560)
        self.titulo_paso.pack(anchor="w", pady=(0, 12))
        self.explicacion_paso = ttk.Label(self.tarjeta_paso, style="CardMuted.TLabel", wraplength=560)
        self.explicacion_paso.pack(anchor="w", pady=(0, 18))
        self.formula_paso = FormulaExplicada(self.tarjeta_paso)
        self.formula_paso.pack(fill="x", pady=(0, 18))
        self.sustitucion_paso = FormulaExplicada(self.tarjeta_paso, sustitucion=True)
        self.sustitucion_paso.pack(fill="x", pady=(0, 18))
        self.valor_paso = ttk.Label(self.tarjeta_paso, style="Kpi.TLabel", wraplength=560)
        self.valor_paso.pack(anchor="w")
        self.boton_detalle = ttk.Button(pagina, text="Detalle del cálculo", command=self.mostrar_detalle)
        self.boton_detalle.pack(anchor="w", pady=8)
        self.detalle = ttk.Frame(pagina, style="Panel.TFrame", padding=12)

    def pasos_principales(self):
        return self.resultado.procedimiento

    def mostrar_detalle(self):
        if self.detalle.winfo_manager():
            self.detalle.pack_forget()
            return
        self.renderizar_detalle()
        self.detalle.pack(fill="x")

    def renderizar_detalle(self):
        for hijo in self.detalle.winfo_children():
            hijo.destroy()
        for paso in self.resultado.detalles:
            ttk.Label(self.detalle, text=paso.titulo, style="CardSection.TLabel").pack(anchor="w", pady=(12, 6))
            FormulaExplicada(self.detalle, paso.formula).pack(fill="x", pady=(0, 12))
            FormulaExplicada(self.detalle, paso.sustitucion, sustitucion=True).pack(fill="x", pady=(0, 8))
            ttk.Label(self.detalle, text=f"Resultado · {self.valor_mostrado(paso)}",
                      style="Card.TLabel").pack(anchor="w", pady=(0, 12))
        habilitar_desplazamiento(self.detalle, self.lienzos[3])

    def construir_resultados(self):
        pagina = self.contenidos[4]
        self.caso_final = ttk.Label(pagina, style="Subtitle.TLabel", wraplength=560)
        self.caso_final.pack(anchor="w", pady=(0, 12))
        self.resumen = ttk.Frame(pagina)
        self.resumen.pack(fill="x")
        self.principal = ttk.Frame(self.resumen, style="Result.TFrame", padding=(16, 12))
        self.titulo_principal = ttk.Label(self.principal, style="ResultTitle.TLabel", wraplength=540)
        self.titulo_principal.pack(anchor="w")
        self.valor_principal = ttk.Label(self.principal, style="ResultValue.TLabel", wraplength=540)
        self.valor_principal.pack(anchor="w")
        self.kpis = Indicadores(self.resumen)
        self.kpis.pack(fill="x")
        nota = ttk.Frame(self.resumen, style="Note.TFrame", padding=18)
        nota.pack(fill="x", pady=12)
        ttk.Label(nota, text="Interpretación", style="NoteTitle.TLabel").pack(anchor="w", pady=(0, 4))
        self.interpretacion = ttk.Label(nota, style="Note.TLabel", wraplength=560)
        self.interpretacion.pack(fill="x")
        self.tarjeta_grafico = ttk.Frame(self.resumen, style="Rounded.TFrame", padding=14)
        self.titulo_grafico = ttk.Label(self.tarjeta_grafico, style="CardTitle.TLabel", wraplength=560)
        self.titulo_grafico.pack(fill="x")
        self.grafico = GraficoBarras(self.tarjeta_grafico, self.movimiento)
        self.grafico.pack(fill="x")
        acciones = ttk.Frame(pagina, style="Panel.TFrame", padding=18)
        acciones.pack(fill="x", pady=(16, 4))
        ttk.Label(acciones, text="Informe completo", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(acciones, text="Del planteamiento a los resultados, con el desarrollo paso a paso.",
                  style="CardMuted.TLabel", wraplength=490).pack(anchor="w", pady=(2, 10))
        ttk.Button(acciones, text="Leer informe completo", style="CardPrimary.TButton", command=self.ver_informe_completo).pack(anchor="w")
        fila = ttk.Frame(acciones, style="Card.TFrame")
        fila.pack(fill="x", pady=(12, 0))
        for columna, (titulo, opciones) in enumerate((
            ("Exportar", (("Exportar PDF", self.exportar_pdf), ("Exportar HTML", self.exportar))),
            ("Biblioteca", (("Guardar cálculo", lambda: self.winfo_toplevel().guardar_calculo(self)),
                            ("Guardar copia", lambda: self.winfo_toplevel().guardar_calculo(self, copia=True)))),
            ("Más opciones", (("Volver al desarrollo", lambda: self.mostrar_etapa(3)), ("Copiar informe", self.copiar))),
        )):
            menu = MenuRedondeado(fila, titulo, opciones, style="ReportMenu.TButton")
            menu.grid(row=0, column=columna, sticky="ew", padx=(0, 8))
            fila.columnconfigure(columna, weight=1)

    def texto_enunciado(self):
        return self.enunciado.get("1.0", "end-1c").strip()

    def enunciado_modificado(self, evento=None):
        if self.enunciado.edit_modified():
            self.enunciado.edit_modified(False)
            self.contexto_modificado()

    def contexto_modificado(self, *args):
        self.invalidar(0)

    def datos_modificados(self, *args):
        self.invalidar(1)

    def invalidar(self, desde):
        if self.actualizando:
            return
        self.borrador = True
        self.resultado = None
        self.analisis = None
        self.paso_actual = 0
        self.detalle.pack_forget()
        self.habilitada = min(self.habilitada, desde)
        self.grafico.cancelar()
        self.grafico.serie = []
        self.grafico.dibujar()
        if self.actualizar_vista is None:
            self.actualizar_vista = self.after_idle(self.previsualizar)
        self.estado.set("")
        self.aviso.configure(style="Muted.TLabel")
        if self.etapa > desde:
            self.mostrar_etapa(desde)
        self.actualizar_navegacion()

    def agregar_fila(self, valores=None):
        valores = valores or {}
        marco = ttk.Frame(self.tabla, style="Card.TFrame")
        calidad = self.objetivo.get() == "Valor por calidad"
        variables = {clave: tk.StringVar(value=str(valores.get(clave, defecto))) for clave, defecto in (
            ("nombre", ""), ("cantidad", ""), ("unidad", ""), ("precio", ""),
            ("directo", ""), ("escenario", self.escenario.get() if self.objetivo.get() == "Comparar alternativas" else "Inicial"),
        )}
        variables["es_laboral"] = tk.BooleanVar(value=valores.get("es_laboral", False))
        controles = {
            clave: ttk.Entry(marco, textvariable=variables[clave], width=ancho)
            for clave, ancho in (("nombre", 8), ("cantidad", 5), ("unidad", 5), ("precio", 6), ("directo", 6))
        }
        controles["es_laboral"] = ttk.Checkbutton(marco, variable=variables["es_laboral"], text="Horas")
        controles["total"] = ttk.Label(marco, style="Card.TLabel", width=8)
        controles["aviso"] = ttk.Label(marco, style="InputError.TLabel", wraplength=650, justify="left", width=1)
        registro = (marco, variables, controles, calidad)
        controles["quitar"] = ttk.Button(marco, text="Quitar", style="Compact.TButton",
                                        command=lambda: self.quitar_fila(registro))
        for variable in variables.values():
            variable.trace_add("write", lambda *_: self.fila_modificada(registro))
        self.filas.append(registro)
        if not self.actualizando:
            self.organizar_tabla()
        self.actualizar_costo(registro)
        habilitar_desplazamiento(marco, self.lienzos[1])
        for control in controles.values():
            control.bind("<FocusIn>", self.revelar_columna, add="+")
        for clave in ("nombre", "cantidad", "precio", "directo", "unidad"):
            controles[clave].bind("<FocusOut>", self.revisar_fila, add="+")
        self.datos_modificados()

    def organizar_tabla(self):
        calidad = self.objetivo.get() == "Valor por calidad"
        comparar = self.objetivo.get() == "Comparar alternativas"
        columnas = [("nombre", "Categoría" if calidad else "Recurso"), ("cantidad", "Cantidad")]
        if not calidad:
            columnas.append(("unidad", "Unidad"))
        columnas.append(("precio", "Valor unit." if calidad else "Costo unit."))
        if not calidad:
            columnas.append(("directo", "Costo directo"))
        columnas.append(("total", "Total"))
        if not calidad:
            columnas.append(("es_laboral", "Laboral"))
        columnas.append(("quitar", ""))
        for encabezado in self.cabecera_tabla.winfo_children():
            encabezado.destroy()
        for columna in range(8):
            self.cabecera_tabla.columnconfigure(columna, weight=0, minsize=0)
        anchos = []
        for columna, (clave, etiqueta) in enumerate(columnas):
            encabezado = ttk.Label(self.cabecera_tabla, text=etiqueta, style="Table.TLabel", padding=(4, 5))
            encabezado.grid(row=0, column=columna, sticky="ew")
            ancho_control = self.filas[0][2][clave].winfo_reqwidth() + 4 if self.filas else 0
            ancho = max(encabezado.winfo_reqwidth(), ancho_control)
            anchos.append(ancho)
            self.cabecera_tabla.columnconfigure(columna, weight=int(clave == "nombre"), minsize=ancho)
        presentes = 0
        for marco, variables, controles, es_calidad in self.filas:
            marco.grid_remove()
            for control in controles.values():
                control.grid_remove()
            if es_calidad != calidad:
                continue
            escenario = self.escenario.get() if comparar else "Inicial"
            if not calidad and variables["escenario"].get() != escenario:
                continue
            presentes += 1
            marco.grid(row=presentes, column=0, sticky="ew", pady=(3, 0))
            for columna in range(8):
                marco.columnconfigure(columna, weight=0, minsize=0)
            for columna, ((clave, _), ancho) in enumerate(zip(columnas, anchos)):
                control = controles[clave]
                marco.columnconfigure(columna, weight=int(clave == "nombre"), minsize=ancho)
                control.grid(row=0, column=columna, sticky="ew", padx=(0, 4))
            controles["aviso"].grid(row=1, column=0, columnspan=len(columnas), sticky="ew", pady=(2, 4))

    def fila_modificada(self, registro):
        self.actualizar_costo(registro)
        self.datos_modificados()

    def actualizar_costo(self, registro):
        _, variables, controles, _ = registro
        try:
            valor, _ = costo_fila({clave: variable.get() for clave, variable in variables.items()})
            texto = numero(valor, self.decimales.get())
        except ValueError:
            texto = "—"
        controles["total"].configure(text=texto)

    def quitar_fila(self, registro):
        self.filas.remove(registro)
        registro[0].destroy()
        if not self.actualizando:
            self.organizar_tabla()
        self.datos_modificados()

    def duplicar_escenario(self):
        destino = self.escenario.get()
        if destino == "Inicial":
            self.estado.set("Selecciona una alternativa para duplicar el escenario inicial.")
            return
        filas = self.recoger_datos()["insumos"]
        inicial = [fila for fila in filas if fila["escenario"] == "Inicial"]
        if not inicial:
            self.estado.set("Añade insumos al escenario inicial.")
            return
        if any(fila["escenario"] == destino for fila in filas):
            self.estado.set("Ya hay insumos en la alternativa.")
            return
        for fila in inicial:
            self.agregar_fila(dict(fila, escenario=destino))
        campo = "produccion_final" if destino == "Alternativa" else "produccion_otra"
        if not self.variables[campo].get():
            self.variables[campo].set(self.variables["produccion"].get())

    def confirmar_reemplazo(self):
        return not self.borrador or messagebox.askyesno(
            "Reemplazar cálculo", "¿Descartar los datos del cálculo actual?", parent=self)

    @property
    def tiene_borradores(self):
        return self.borrador or any(estado[4] for estado in self.borradores_modo.values())

    def cargar_ejemplo(self, *, confirmar=True):
        if self.ejemplo.get() not in self.modulo.ejemplos:
            self.estado.set("No hay un ejemplo seleccionado para este método.")
            return False
        if confirmar and not self.confirmar_reemplazo():
            return False
        datos = self.modulo.ejemplos[self.ejemplo.get()]
        self.cargar_datos(self.ejemplo.get(), describir_ejemplo(self.modulo.clave, datos), datos)
        return True

    def cargar_datos(self, titulo, enunciado, datos, identificador=None):
        self.identificador = identificador
        self.datos_calculados = None
        self.actualizando = True
        try:
            self.titulo.set(titulo)
            self.objetivo.set(datos.get("modo", next(iter(self.modos))))
            self.enunciado.delete("1.0", "end")
            self.enunciado.insert("1.0", enunciado)
            self.enunciado.edit_modified(False)
            for clave, variable in self.variables.items():
                variable.set(str(datos.get(clave, CAMPOS_COMUNES[clave].valor)))
            if "unidad" in datos and "unidad_salida" not in datos:
                salida, recurso = datos["unidad"].split("/", 1)
                self.variables["unidad_salida"].set(salida)
                self.variables["unidad_recurso"].set(recurso)
            if self.modulo.tabla_insumos:
                self.escenario.set("Inicial")
                for registro in self.filas[:]:
                    self.quitar_fila(registro)
                for fila in datos["insumos"]:
                    self.agregar_fila(fila)
            self.cambiar_modo()
        finally:
            self.actualizando = False
        self.invalidar(0)
        self.mostrar_etapa(0)
        self.borrador = identificador is None

    def recoger_datos(self):
        return self.datos_del_modo(self.objetivo.get())

    def datos_del_modo(self, modo):
        datos = {clave: self.variables[clave].get() for clave in self.modos[modo]}
        datos["modo"] = modo
        if self.modulo.tabla_insumos:
            calidad = modo == "Valor por calidad"
            datos["insumos"] = [
                {clave: variable.get() for clave, variable in variables.items()}
                for _, variables, _, es_calidad in self.filas
                if es_calidad == calidad and (modo != "Escenario individual" or variables["escenario"].get() == "Inicial")
            ]
        return datos

    def actualizar_identificacion(self):
        perfil = self.analisis.perfil
        for contenedor in (self.metodo, self.revision):
            for hijo in contenedor.winfo_children():
                hijo.destroy()
        ttk.Label(self.metodo, text=perfil.tipo, style="CardTitle.TLabel").pack(anchor="w")
        for formula in perfil.formulas:
            FormulaExplicada(self.metodo, formula).pack(fill="x", pady=(16, 12))
        for supuesto in perfil.supuestos:
            ttk.Label(self.metodo, text=supuesto, style="Assumption.TLabel", wraplength=510).pack(anchor="w", pady=(6, 0))
        habilitar_desplazamiento(self.metodo, self.lienzos[2])
        ttk.Label(self.revision, text="Datos utilizados", style="CardTitle.TLabel").pack(anchor="w")
        cantidad = len(self.analisis.datos)
        ttk.Label(self.revision, text=f"{cantidad} {'entrada' if cantidad == 1 else 'entradas'} del cálculo, agrupadas por sección",
                  style="CardMuted.TLabel").pack(anchor="w", pady=(3, 10))
        for nombre, filas in self.analisis.grupos:
            ttk.Label(self.revision, text=nombre, style="CardSection.TLabel").pack(anchor="w", pady=(10, 4))
            for etiqueta, valor in filas:
                fila = ttk.Frame(self.revision, style="DataBlock.TFrame", padding=(10, 6))
                fila.pack(fill="x", pady=2)
                fila.columnconfigure(0, weight=2, uniform="dato")
                fila.columnconfigure(1, weight=3, uniform="dato")
                k = ttk.Label(fila, text=etiqueta, style="DataKey.TLabel", wraplength=155)
                v = ttk.Label(fila, text=valor, style="DataValue.TLabel", wraplength=235)
                k.grid(row=0, column=0, sticky="nw", padx=(0, 6))
                v.grid(row=0, column=1, sticky="nw")
                def ajustar(evento, clave=k, dato=v):
                    for control, fraccion in ((clave, .4), (dato, .6)):
                        ancho = max(60, int((evento.width - 32) * fraccion))
                        if int(control.cget("wraplength")) != ancho:
                            control.configure(wraplength=ancho)
                fila.bind("<Configure>", ajustar)
        habilitar_desplazamiento(self.revision, self.lienzos[2])

    def mostrar_etapa(self, etapa):
        if not 0 <= etapa <= self.habilitada:
            return False
        self.etapa = etapa
        self.transicion.mostrar(self.paginas[etapa])
        if etapa == 3:
            self.renderizar_paso()
        elif etapa == 4:
            self.renderizar()
        self.actualizar_navegacion()
        if etapa == 0:
            self.entrada_titulo.focus_set()
        elif etapa == 1:
            self.entradas[0].focus_set()
            if self.actualizar_vista is None:
                self.actualizar_vista = self.after_idle(self.previsualizar)
        else:
            self.siguiente.focus_set()
        return True

    def actualizar_navegacion(self):
        for indice, boton in enumerate(self.botones_etapas):
            boton.configure(state="normal" if indice <= self.habilitada else "disabled",
                             style="StepActive.TButton" if indice == self.etapa else "Step.TButton",
                             text=("✓ " if indice == self.etapa else "") + ETAPAS[indice])
        self.anterior.configure(state="disabled" if self.etapa == 0 else "normal",
                                text="← Paso anterior" if self.etapa == 3 and self.paso_actual > 0 else "← Anterior")
        textos = ("Continuar →", "Revisar método →", "Desarrollar →", "Siguiente paso →", "Volver al planteamiento")
        texto = textos[self.etapa]
        if self.etapa == 3 and self.resultado and self.paso_actual == len(self.pasos_principales()) - 1:
            texto = "Presentar resultados →"
        self.siguiente.configure(text=texto)
        valido = self.preparado is not None and self.datos_calculados == self.recoger_datos()
        self.directo.configure(state="normal" if valido and self.etapa != 4 else "disabled")

    def avanzar(self):
        try:
            if self.etapa == 0:
                self.habilitada = max(self.habilitada, 1)
                self.mostrar_etapa(1)
                self.estado.set("")
            elif self.etapa == 1:
                self.preparar()
                self.habilitada = max(self.habilitada, 2)
                self.mostrar_etapa(2)
                self.estado.set("")
            elif self.etapa == 2:
                self.resultado = self.preparado
                self.paso_actual = 0
                self.habilitada = 3
                self.mostrar_etapa(3)
                self.estado.set("")
            elif self.etapa == 3:
                if self.paso_actual < len(self.pasos_principales()) - 1:
                    self.paso_actual += 1
                    self.lienzos[3].yview_moveto(0)
                    self.transicion.mostrar(self.paginas[3])
                    self.renderizar_paso()
                    self.actualizar_navegacion()
                else:
                    self.habilitada = 4
                    self.mostrar_etapa(4)
                    self.estado.set("")
            else:
                self.mostrar_etapa(0)
        except ValueError as error:
            self.estado.set(f"Revisa los datos: {error}")
            self.revisar_entradas(mostrar_todos=True, enfocar=True)
            self.aviso.configure(style="Error.TLabel")
            return False
        self.aviso.configure(style="Muted.TLabel")
        if self.etapa in (3, 4):
            self.winfo_toplevel().guardar_calculo(self)
        return True

    def retroceder(self):
        if self.etapa == 3 and self.paso_actual > 0:
            self.paso_actual -= 1
            self.transicion.mostrar(self.paginas[3])
            self.renderizar_paso()
            self.actualizar_navegacion()
        elif self.etapa > 0:
            self.mostrar_etapa(self.etapa - 1)

    def renderizar_paso(self):
        if self.resultado is None:
            return
        self.boton_detalle.configure(state="normal" if self.resultado.detalles else "disabled")
        paso = self.pasos_principales()[self.paso_actual]
        self.contador_paso.configure(text=f"PASO {self.paso_actual + 1:02} DE {len(self.pasos_principales()):02}")
        self.titulo_paso.configure(text=paso.titulo)
        if paso.explicacion:
            self.explicacion_paso.configure(text=paso.explicacion)
            self.explicacion_paso.pack(anchor="w", pady=(0, 12), after=self.titulo_paso)
        else:
            self.explicacion_paso.pack_forget()
        self.formula_paso.presentar(paso.formula)
        self.sustitucion_paso.presentar(paso.sustitucion)
        self.valor_paso.configure(text=self.valor_mostrado(paso))

    def valor_mostrado(self, paso):
        precision = 0 if paso.unidad == "personas" else self.decimales.get()
        valor = numero(paso.resultado, precision)
        return f"${valor}" if paso.unidad == "$" else f"{valor} {paso.unidad}"

    def renderizar(self):
        if self.resultado is None:
            return
        if self.etapa == 3:
            self.renderizar_paso()
            if self.detalle.winfo_manager():
                self.renderizar_detalle()
        if self.etapa != 4:
            return
        self.caso_final.configure(text=self.titulo.get().strip() or "Resolución del problema")
        indicadores, serie, unidad, titulo = resumen_resultado(self.modulo.clave, self.resultado)
        principal = self.resultado.principal
        if principal is not None:
            self.titulo_principal.configure(text=principal.titulo)
            self.valor_principal.configure(text=self.valor_mostrado(principal))
            self.principal.pack(fill="x", before=self.kpis, pady=(0, 10))
            indicadores = tuple(paso for paso in indicadores if paso is not principal)
        else:
            self.principal.pack_forget()
        self.kpis.presentar(indicadores, self.decimales.get())
        for tarjeta in self.kpis.tarjetas:
            habilitar_desplazamiento(tarjeta, self.lienzos[4])
        self.interpretacion.configure(text=self.resultado.interpretacion)
        if serie:
            self.titulo_grafico.configure(text=titulo)
            self.tarjeta_grafico.pack(fill="x")
        else:
            self.tarjeta_grafico.pack_forget()
        self.grafico.presentar(serie, unidad, self.decimales.get(), self.resultado.tipo_grafico)

    def informe_completo(self):
        if self.resultado is None:
            return ""
        lineas = [self.titulo.get().strip() or "Problema de Dirección de Operaciones"]
        secciones = secciones_informe(self.texto_enunciado(), self.analisis, self.resultado, self.decimales.get())
        for indice, (nombre, contenido) in enumerate(secciones, 1):
            lineas.extend(["", f"{indice}. {nombre}", *contenido])
        return "\n".join(lineas)

    def ver_informe_completo(self):
        if self.resultado is not None and self.etapa == 4:
            return mostrar_informe(self, "Informe completo", self.informe_completo(), self.copiar)

    def copiar(self):
        informe = self.informe_completo()
        if informe:
            self.clipboard_clear()
            self.clipboard_append(informe)
            self.estado.set("Informe copiado.")

    def exportar(self):
        if self.resultado is None or self.etapa != 4:
            return
        ruta = filedialog.asksaveasfilename(parent=self, title="Exportar informe",
                                             defaultextension=".html", filetypes=[("Informe HTML", "*.html")])
        if not ruta:
            return
        titulo = self.titulo.get().strip() or "Informe de cálculo"
        html = informe_html(titulo, self.texto_enunciado(), self.analisis, self.resultado, self.decimales.get())
        try:
            guardar_informe_html(ruta, html)
        except OSError as error:
            self.estado.set(f"No se pudo exportar el informe: {error.strerror or error}.")
            self.aviso.configure(style="Error.TLabel")
        else:
            self.estado.set("Informe exportado.")
            self.aviso.configure(style="Muted.TLabel")

    def exportar_pdf(self):
        if self.resultado is None or self.etapa != 4:
            return
        ruta = filedialog.asksaveasfilename(parent=self, title="Exportar PDF",
                                            defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if not ruta:
            return
        try:
            informe_pdf(ruta, self.titulo.get().strip() or "Informe de cálculo",
                         self.texto_enunciado(), self.analisis, self.resultado, self.decimales.get())
        except PDFNoDisponible as error:
            if messagebox.askyesno("Exportar como HTML", f"{error}\n\n¿Guardar el informe HTML? "
                                   "Puedes abrirlo y elegir Imprimir → Guardar como PDF.", parent=self):
                self.exportar()
        except (OSError, ValueError, RuntimeError) as error:
            self.estado.set(f"No se pudo exportar el PDF. {error}")
            self.aviso.configure(style="Error.TLabel")
        else:
            self.estado.set("PDF exportado.")
            self.aviso.configure(style="Muted.TLabel")

    def limpiar(self, *, confirmar=True):
        if confirmar and not self.confirmar_reemplazo():
            return False
        self.actualizando = True
        try:
            self.titulo.set("")
            self.enunciado.delete("1.0", "end")
            self.enunciado.edit_modified(False)
            for clave, variable in self.variables.items():
                variable.set(CAMPOS_COMUNES[clave].valor)
            for registro in self.filas[:]:
                self.quitar_fila(registro)
            if self.modulo.tabla_insumos:
                self.escenario.set("Inicial")
                self.agregar_fila()
            self.cambiar_modo()
        finally:
            self.actualizando = False
        self.invalidar(0)
        self.mostrar_etapa(0)
        self.borrador = False
        self.identificador = None
        return True
