"""Resolución guiada: planteamiento, datos, identificación, desarrollo y resultados."""

import tkinter as tk
from tkinter import ttk

from ..analisis import PERFILES, analizar_datos, describir_ejemplo, validar_planteamiento
from ..formato import numero
from ..nucleo import validar_numero
from .componentes import (
    ACENTO, FONDO, PRIMARIO, SECUNDARIO, SUPERFICIE, TEXTO,
    GraficoBarras, Indicadores, TransicionPaginas, habilitar_desplazamiento, resumen_resultado,
)

ETAPAS = ("Planteamiento", "Datos", "Identificación", "Desarrollo", "Resultados")


def pagina_desplazable(padre):
    """Crea un área de contenido desplazable independiente para una etapa."""
    exterior = ttk.Frame(padre)
    lienzo = tk.Canvas(exterior, background=FONDO, highlightthickness=0)
    barra = ttk.Scrollbar(exterior, orient="vertical", command=lienzo.yview)
    lienzo.configure(yscrollcommand=barra.set)
    barra.pack(side="right", fill="y")
    lienzo.pack(fill="both", expand=True)
    contenido = ttk.Frame(lienzo, padding=(8, 8, 24, 20))
    identificador = lienzo.create_window((0, 0), window=contenido, anchor="nw")
    contenido.bind("<Configure>", lambda e: lienzo.configure(scrollregion=lienzo.bbox("all")))
    lienzo.bind("<Configure>", lambda e: lienzo.itemconfigure(identificador, width=e.width))
    return exterior, contenido, lienzo


class Panel(ttk.Frame):
    def __init__(self, padre, modulo, decimales, movimiento):
        super().__init__(padre, padding=(24, 4, 24, 16))
        self.modulo, self.decimales, self.movimiento = modulo, decimales, movimiento
        self.variables, self.filas, self.entradas = {}, [], []
        self.resultado = None
        self.analisis = None
        self.etapa = 0
        self.habilitada = 0
        self.paso_actual = 0
        self.actualizando = True
        self.estado = tk.StringVar(value="Comienza con un problema nuevo o carga un ejemplo opcional.")
        self.titulo = tk.StringVar()
        self.objetivo = tk.StringVar(value=PERFILES[modulo.clave].objetivo)
        self.titulo.trace_add("write", self.contexto_modificado)
        self.objetivo.trace_add("write", self.contexto_modificado)

        ttk.Label(self, text=modulo.nombre, style="Subtitle.TLabel").pack(anchor="w", pady=(0, 10))
        navegacion = ttk.Frame(self)
        navegacion.pack(fill="x")
        self.botones_etapas = []
        for indice, nombre in enumerate(ETAPAS):
            boton = ttk.Button(navegacion, text=f"{indice + 1:02}\n{nombre}", style="Step.TButton",
                               command=lambda i=indice: self.mostrar_etapa(i))
            boton.grid(row=0, column=indice, sticky="ew", padx=(0, 4))
            navegacion.columnconfigure(indice, weight=1, uniform="etapas")
            self.botones_etapas.append(boton)
        self.progreso = ttk.Progressbar(self, maximum=5, value=1)
        self.progreso.pack(fill="x", pady=(10, 14))
        self.transicion = TransicionPaginas(self, movimiento)
        self.transicion.pack(fill="both", expand=True)
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

        pie = ttk.Frame(self)
        pie.pack(fill="x", pady=(12, 0))
        self.aviso = ttk.Label(pie, textvariable=self.estado, style="Muted.TLabel", wraplength=650)
        self.aviso.pack(anchor="w", pady=(0, 10))
        self.anterior = ttk.Button(pie, text="← Anterior", command=self.retroceder)
        self.anterior.pack(side="left")
        self.siguiente = ttk.Button(pie, style="Primary.TButton", command=self.avanzar)
        self.siguiente.pack(side="right")
        for pagina, lienzo in zip(self.paginas, self.lienzos):
            habilitar_desplazamiento(pagina, lienzo)
        self.actualizando = False
        self.mostrar_etapa(0)

    def encabezado(self, etapa, titulo, descripcion):
        contenido = self.contenidos[etapa]
        ttk.Label(contenido, text=titulo, style="Title.TLabel", wraplength=850).pack(anchor="w", pady=(2, 8))
        ttk.Label(contenido, text=descripcion, style="Muted.TLabel", wraplength=850).pack(anchor="w", pady=(0, 20))
        return contenido

    def construir_planteamiento(self):
        pagina = self.encabezado(0, "Primero, comprende el problema.",
            "Escribe el caso del profesor con tus propias palabras. No necesitas usar un ejercicio precargado.")
        ttk.Label(pagina, text="Título del caso (opcional)").pack(anchor="w")
        self.entrada_titulo = ttk.Entry(pagina, textvariable=self.titulo)
        self.entrada_titulo.pack(fill="x", pady=(4, 12))
        ttk.Label(pagina, text="Planteamiento / enunciado").pack(anchor="w")
        self.enunciado = tk.Text(pagina, height=6, wrap="word", font=("Segoe UI", 12), relief="flat",
                                 background=SUPERFICIE, foreground=TEXTO, insertbackground=PRIMARIO, padx=14, pady=12,
                                 highlightthickness=1, highlightbackground="#D5DEEB", highlightcolor=PRIMARIO)
        self.enunciado.pack(fill="x", pady=(4, 12))
        self.enunciado.bind("<<Modified>>", self.enunciado_modificado)
        ttk.Label(pagina, text="¿Qué necesitas encontrar?").pack(anchor="w")
        ttk.Entry(pagina, textvariable=self.objetivo).pack(fill="x", pady=(4, 12))
        ttk.Label(pagina, text="El enunciado es contexto: tú registras las cifras en Datos. "
                  "La aplicación no extrae datos ni decide el método leyendo el texto.",
                  style="Muted.TLabel", wraplength=850).pack(anchor="w", pady=8)
        ejemplo = ttk.Frame(pagina, style="Card.TFrame", padding=16)
        ejemplo.pack(fill="x", pady=12)
        ttk.Label(ejemplo, text="¿Quieres explorar antes?", style="CardTitle.TLabel").pack(anchor="w")
        self.ejemplo = ttk.Combobox(ejemplo, state="readonly", values=list(self.modulo.ejemplos))
        if self.modulo.ejemplos:
            self.ejemplo.current(0)
        self.ejemplo.pack(side="left", fill="x", expand=True, pady=(10, 0))
        ttk.Button(ejemplo, text="Cargar ejemplo", command=self.cargar_ejemplo).pack(side="left", padx=(12, 0), pady=(10, 0))
        ttk.Button(pagina, text="Nuevo problema / limpiar", command=self.limpiar).pack(anchor="w", pady=8)

    def construir_datos(self):
        pagina = self.encabezado(1, "Organiza lo que conoces.",
            "Traslada los datos del enunciado. Usa punto decimal, unidades compatibles y el mismo período.")
        self.formulario = ttk.Frame(pagina)
        self.formulario.pack(fill="x")
        for indice, campo in enumerate(self.modulo.campos):
            columna = indice % 2
            marco = ttk.Frame(self.formulario, padding=(0, 0, 20, 14))
            marco.grid(row=indice // 2, column=columna, sticky="nsew")
            self.formulario.columnconfigure(columna, weight=1, uniform="datos")
            ttk.Label(marco, text=campo.etiqueta, wraplength=350).pack(anchor="w")
            variable = tk.StringVar(value=campo.valor)
            self.variables[campo.clave] = variable
            entrada = ttk.Entry(marco, textvariable=variable)
            entrada.pack(fill="x", pady=(6, 0))
            self.entradas.append(entrada)
            variable.trace_add("write", self.datos_modificados)
        if self.modulo.tabla_insumos:
            ttk.Label(pagina, text="Tabla de insumos", style="Subtitle.TLabel").pack(anchor="w", pady=(12, 8))
            ttk.Label(pagina, text="Añade todos los insumos del problema. Para costos globales: cantidad 1. "
                      "Marca Horas solo para mano de obra medida en horas-persona.",
                      style="Muted.TLabel", wraplength=850).pack(anchor="w", pady=(0, 12))
            self.tabla = ttk.Frame(pagina)
            self.tabla.pack(fill="x")
            self.agregar_fila()
            ttk.Button(pagina, text="+ Añadir insumo", command=self.agregar_fila).pack(anchor="w", pady=12)
        ttk.Label(pagina, text="Antes de continuar: revisa qué representa cada cantidad. "
                  "No hay conversiones automáticas de monedas, períodos o unidades.",
                  style="Muted.TLabel", wraplength=850).pack(anchor="w", pady=12)

    def construir_identificacion(self):
        pagina = self.encabezado(2, "Elige el método con criterio.",
            "Revisa los datos, las incógnitas y los supuestos antes de iniciar el desarrollo.")
        self.metodo = ttk.Frame(pagina, style="Card.TFrame", padding=22)
        self.metodo.pack(fill="x")
        self.revision = ttk.Frame(pagina)
        self.revision.pack(fill="x", pady=16)

    def construir_desarrollo(self):
        pagina = self.encabezado(3, "Resuelve, un paso a la vez.",
            "Comprende la fórmula, observa la sustitución y verifica cada resultado intermedio.")
        self.contador_paso = ttk.Label(pagina, style="Muted.TLabel")
        self.contador_paso.pack(anchor="w", pady=(0, 12))
        self.tarjeta_paso = ttk.Frame(pagina, style="Card.TFrame", padding=24)
        self.tarjeta_paso.pack(fill="x")
        self.titulo_paso = ttk.Label(self.tarjeta_paso, style="CardTitle.TLabel", wraplength=800)
        self.titulo_paso.pack(anchor="w", pady=(0, 12))
        self.explicacion_paso = ttk.Label(self.tarjeta_paso, style="CardMuted.TLabel", wraplength=800)
        self.explicacion_paso.pack(anchor="w", pady=(0, 18))
        ttk.Label(self.tarjeta_paso, text="FÓRMULA", style="Accent.TLabel").pack(anchor="w")
        self.formula_paso = ttk.Label(self.tarjeta_paso, style="CardTitle.TLabel", wraplength=800)
        self.formula_paso.pack(anchor="w", pady=(6, 18))
        ttk.Label(self.tarjeta_paso, text="SUSTITUCIÓN", style="Accent.TLabel").pack(anchor="w")
        self.sustitucion_paso = ttk.Label(self.tarjeta_paso, style="Card.TLabel", wraplength=800)
        self.sustitucion_paso.pack(anchor="w", pady=(6, 18))
        self.valor_paso = ttk.Label(self.tarjeta_paso, style="Kpi.TLabel", wraplength=800)
        self.valor_paso.pack(anchor="w")

    def construir_resultados(self):
        pagina = self.encabezado(4, "Presenta una conclusión clara.",
            "Síntesis final del caso. El desarrollo permanece en su propia etapa.")
        self.caso_final = ttk.Label(pagina, style="Subtitle.TLabel", wraplength=850)
        self.caso_final.pack(anchor="w", pady=(0, 12))
        self.resumen = ttk.Frame(pagina)
        self.resumen.pack(fill="x")
        self.kpis = Indicadores(self.resumen)
        self.kpis.pack(fill="x")
        self.interpretacion = ttk.Label(self.resumen, style="Card.TLabel", padding=18, wraplength=820)
        self.interpretacion.pack(fill="x", pady=12)
        self.titulo_grafico = ttk.Label(self.resumen, style="CardTitle.TLabel", padding=12, wraplength=820)
        self.titulo_grafico.pack(fill="x")
        self.grafico = GraficoBarras(self.resumen, self.movimiento)
        self.grafico.pack(fill="x")
        ttk.Label(pagina, text="Precisión conservada · redondeo solo al presentar · revisa los supuestos de Identificación",
                  style="Muted.TLabel", wraplength=850).pack(anchor="w", pady=12)
        ttk.Button(pagina, text="Copiar informe completo", command=self.copiar).pack(anchor="w", pady=8)

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
        self.resultado = None
        self.analisis = None
        self.paso_actual = 0
        self.habilitada = min(self.habilitada, desde)
        self.grafico.cancelar()
        self.grafico.serie = []
        self.grafico.dibujar()
        self.estado.set("Cambios pendientes. Revisa el análisis antes de volver a desarrollar.")
        self.aviso.configure(style="Muted.TLabel")
        if self.etapa > desde:
            self.mostrar_etapa(desde)
        self.actualizar_navegacion()

    def agregar_fila(self, valores=None):
        valores = valores or dict(nombre="", cantidad="", precio="", es_laboral=False)
        marco = ttk.Frame(self.tabla, padding=(0, 0, 0, 12))
        marco.pack(fill="x")
        variables = {clave: tk.StringVar(value=str(valores[clave])) for clave in ("nombre", "cantidad", "precio")}
        variables["es_laboral"] = tk.BooleanVar(value=valores.get("es_laboral", False))
        for columna, (clave, etiqueta) in enumerate((("nombre", "Insumo"), ("cantidad", "Cantidad"), ("precio", "Precio unitario ($)"))):
            ttk.Label(marco, text=etiqueta).grid(row=0, column=columna, sticky="w")
            ttk.Entry(marco, textvariable=variables[clave], width=16).grid(row=1, column=columna, sticky="ew", padx=(0, 10))
            marco.columnconfigure(columna, weight=1)
        ttk.Checkbutton(marco, text="Horas laborales", variable=variables["es_laboral"]).grid(row=2, column=0, sticky="w")
        registro = (marco, variables)
        ttk.Button(marco, text="Quitar", command=lambda: self.quitar_fila(registro)).grid(row=2, column=2, sticky="e", pady=6)
        for variable in variables.values():
            variable.trace_add("write", self.datos_modificados)
        self.filas.append(registro)
        habilitar_desplazamiento(marco, self.lienzos[1])
        self.datos_modificados()

    def quitar_fila(self, registro):
        self.filas.remove(registro)
        registro[0].destroy()
        self.datos_modificados()

    def cargar_ejemplo(self):
        datos = self.modulo.ejemplos[self.ejemplo.get()]
        self.actualizando = True
        try:
            self.titulo.set(self.ejemplo.get())
            self.objetivo.set(PERFILES[self.modulo.clave].objetivo)
            self.enunciado.delete("1.0", "end")
            self.enunciado.insert("1.0", describir_ejemplo(self.modulo.clave, datos))
            self.enunciado.edit_modified(False)
            for clave, variable in self.variables.items():
                variable.set(str(datos[clave]))
            if self.modulo.tabla_insumos:
                for registro in self.filas[:]:
                    self.quitar_fila(registro)
                for fila in datos["insumos"]:
                    self.agregar_fila(fila)
        finally:
            self.actualizando = False
        self.invalidar(0)
        self.mostrar_etapa(0)
        self.estado.set("Ejemplo cargado como punto de partida. Puedes modificar el enunciado y todas sus cifras.")

    def recoger_datos(self):
        datos = {clave: variable.get() for clave, variable in self.variables.items()}
        if self.modulo.tabla_insumos:
            datos["insumos"] = []
            for _, variables in self.filas:
                nombre = variables["nombre"].get()
                datos["insumos"].append(dict(nombre=nombre,
                    cantidad=validar_numero(variables["cantidad"].get(), f"Cantidad de {nombre or 'insumo'}"),
                    precio=validar_numero(variables["precio"].get(), f"Precio de {nombre or 'insumo'}"),
                    es_laboral=variables["es_laboral"].get()))
        return datos

    def actualizar_identificacion(self):
        for contenedor in (self.metodo, self.revision):
            for hijo in contenedor.winfo_children():
                hijo.destroy()
        perfil = self.analisis.perfil
        ttk.Label(self.metodo, text="MÉTODO PROPUESTO · SEGÚN LA HERRAMIENTA ELEGIDA", style="Accent.TLabel", wraplength=800).pack(anchor="w")
        ttk.Label(self.metodo, text=perfil.tipo, style="CardTitle.TLabel", wraplength=800).pack(anchor="w", pady=10)
        ttk.Label(self.metodo, text=perfil.criterio, style="CardMuted.TLabel", wraplength=800).pack(anchor="w")
        secciones = (("Datos registrados", tuple(f"{k}: {v}" for k, v in self.analisis.datos)),
                     ("Incógnitas que resolveremos", perfil.incognitas), ("Fórmulas del método", perfil.formulas),
                     ("Supuestos y condiciones que debes confirmar", perfil.supuestos))
        for titulo, lineas in secciones:
            ttk.Label(self.revision, text=titulo, style="Subtitle.TLabel").pack(anchor="w", pady=(18, 8))
            for linea in lineas:
                ttk.Label(self.revision, text=f"• {linea}", wraplength=850).pack(anchor="w", pady=3)
        ttk.Label(self.revision, text="¿No coincide con lo pedido? Corrige los datos o elige otra herramienta en el menú. "
                  "La app no resuelve automáticamente cualquier tema de Dirección de Operaciones.",
                  style="Muted.TLabel", wraplength=850).pack(anchor="w", pady=16)
        habilitar_desplazamiento(self.paginas[2], self.lienzos[2])

    def mostrar_etapa(self, etapa):
        if not 0 <= etapa <= self.habilitada:
            return False
        self.etapa = etapa
        self.transicion.mostrar(self.paginas[etapa])
        self.progreso.configure(value=etapa + 1)
        if etapa == 3:
            self.renderizar_paso()
        elif etapa == 4:
            self.renderizar()
        self.actualizar_navegacion()
        if etapa == 0:
            self.entrada_titulo.focus_set()
        elif etapa == 1:
            self.entradas[0].focus_set()
        else:
            self.siguiente.focus_set()
        return True

    def actualizar_navegacion(self):
        for indice, boton in enumerate(self.botones_etapas):
            boton.configure(state="normal" if indice <= self.habilitada else "disabled",
                            style="StepActive.TButton" if indice == self.etapa else "Step.TButton")
        self.anterior.configure(state="disabled" if self.etapa == 0 else "normal",
                                text="← Paso anterior" if self.etapa == 3 and self.paso_actual > 0 else "← Anterior")
        textos = ("Continuar a datos →", "Analizar datos →", "Confirmar método y desarrollar →", "Siguiente paso →", "Volver al planteamiento")
        texto = textos[self.etapa]
        if self.etapa == 3 and self.resultado and self.paso_actual == len(self.resultado.pasos) - 1:
            texto = "Presentar resultados →"
        self.siguiente.configure(text=texto)

    def avanzar(self):
        try:
            if self.etapa == 0:
                validar_planteamiento(self.texto_enunciado(), self.objetivo.get())
                self.habilitada = max(self.habilitada, 1)
                self.mostrar_etapa(1)
                self.estado.set("Registra los datos conocidos; después revisaremos el método.")
            elif self.etapa == 1:
                self.analisis = analizar_datos(self.modulo.clave, self.recoger_datos())
                self.actualizar_identificacion()
                self.habilitada = max(self.habilitada, 2)
                self.mostrar_etapa(2)
                self.estado.set("Datos validados. Confirma que el método y sus supuestos corresponden al problema.")
            elif self.etapa == 2:
                # El cálculo solo comienza después de confirmar el método propuesto.
                self.resultado = self.modulo.calcular(self.recoger_datos())
                self.paso_actual = 0
                self.habilitada = 3
                self.mostrar_etapa(3)
                self.estado.set("Desarrollo iniciado. Recorre las fórmulas y sus sustituciones antes de la síntesis final.")
            elif self.etapa == 3:
                if self.paso_actual < len(self.resultado.pasos) - 1:
                    self.paso_actual += 1
                    self.lienzos[3].yview_moveto(0)
                    self.transicion.mostrar(self.paginas[3])
                    self.renderizar_paso()
                    self.actualizar_navegacion()
                else:
                    self.habilitada = 4
                    self.mostrar_etapa(4)
                    self.estado.set("Resolución completada. Puedes copiar el informe o volver para revisar cualquier etapa.")
            else:
                self.mostrar_etapa(0)
        except ValueError as error:
            self.estado.set(f"Revisa los datos: {error}")
            self.aviso.configure(style="Error.TLabel")
            return False
        self.aviso.configure(style="Muted.TLabel")
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
        paso = self.resultado.pasos[self.paso_actual]
        self.contador_paso.configure(text=f"PASO {self.paso_actual + 1:02} DE {len(self.resultado.pasos):02}")
        self.titulo_paso.configure(text=paso.titulo)
        self.explicacion_paso.configure(text=paso.explicacion)
        self.formula_paso.configure(text=paso.formula)
        self.sustitucion_paso.configure(text=paso.sustitucion)
        self.valor_paso.configure(text=self.valor_mostrado(paso))

    def valor_mostrado(self, paso):
        precision = 2 if paso.unidad in ("%", "$") else self.decimales.get()
        valor = numero(paso.resultado, precision)
        return f"${valor}" if paso.unidad == "$" else f"{valor} {paso.unidad}"

    def renderizar(self):
        if self.resultado is None:
            return
        if self.etapa == 3:
            self.renderizar_paso()
        if self.etapa != 4:
            return
        self.caso_final.configure(text=self.titulo.get().strip() or "Resolución del problema")
        indicadores, serie, unidad, titulo = resumen_resultado(self.modulo.clave, self.resultado)
        self.kpis.presentar(indicadores, self.decimales.get())
        for tarjeta in self.kpis.tarjetas:
            habilitar_desplazamiento(tarjeta, self.lienzos[4])
        self.interpretacion.configure(text=self.resultado.interpretacion)
        self.titulo_grafico.configure(text=titulo)
        self.grafico.presentar(serie, unidad, self.decimales.get())

    def informe_completo(self):
        if self.resultado is None or self.habilitada < 4:
            return ""
        lineas = [self.titulo.get().strip() or "Problema de Dirección de Operaciones", "", "1. PLANTEAMIENTO",
                  self.texto_enunciado(), "Objetivo: " + self.objetivo.get(), "", "2. ANÁLISIS DE DATOS"]
        lineas.extend(f"{clave}: {valor}" for clave, valor in self.analisis.datos)
        lineas.extend(["", "3. IDENTIFICACIÓN", self.analisis.perfil.tipo, self.analisis.perfil.criterio, "Supuestos:"])
        lineas.extend("• " + supuesto for supuesto in self.analisis.perfil.supuestos)
        lineas.extend(["", "4. DESARROLLO"])
        for indice, paso in enumerate(self.resultado.pasos, 1):
            lineas.extend([f"{indice}. {paso.titulo}", paso.explicacion, paso.formula,
                           paso.sustitucion, "Resultado: " + self.valor_mostrado(paso), ""])
        lineas.extend(["5. RESULTADOS", self.resultado.interpretacion])
        return "\n".join(lineas)

    def copiar(self):
        informe = self.informe_completo()
        if informe:
            self.clipboard_clear()
            self.clipboard_append(informe)
            self.estado.set("Informe copiado con planteamiento, datos, método, desarrollo y conclusión.")

    def limpiar(self):
        self.actualizando = True
        try:
            self.titulo.set("")
            self.objetivo.set(PERFILES[self.modulo.clave].objetivo)
            self.enunciado.delete("1.0", "end")
            self.enunciado.edit_modified(False)
            for campo in self.modulo.campos:
                self.variables[campo.clave].set(campo.valor)
            for registro in self.filas[:]:
                self.quitar_fila(registro)
            if self.modulo.tabla_insumos:
                self.agregar_fila()
        finally:
            self.actualizando = False
        self.invalidar(0)
        self.mostrar_etapa(0)
        self.estado.set("Nuevo problema. No hay datos ni resultados de los ejemplos anteriores.")
