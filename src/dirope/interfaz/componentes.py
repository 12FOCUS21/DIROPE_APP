"""Sistema visual y gráficos locales sin dependencias externas."""

import tkinter as tk
from tkinter import ttk, font

from ..formato import numero
from .temas import paleta, vincular_colores, gestor, PALETAS
from .tokens import TIPOGRAFIA
from .redondeado import configurar_bordes
from .fondos import FondoAmbiental

_CLARO = PALETAS["Claro"]
FONDO, SUPERFICIE, TEXTO, SECUNDARIO, PRIMARIO, PRIMARIO_HOVER, ACENTO, SUAVE, BORDE, ERROR = (
    _CLARO[k] for k in ("fondo", "superficie", "texto", "secundario", "primario", "hover", "acento", "suave", "borde", "error"))
NOCHE = PALETAS["Oscuro"]["superficie"]
TEXTO_SOBRE_OSCURO = PALETAS["Oscuro"]["texto_secundario"]

DESCRIPCIONES = {
    "un_factor": ("Productividad de un factor", "Rendimiento por recurso"),
    "multifactor": ("Productividad multifactor", "Costos y alternativas"),
    "capacidad": ("Capacidad y personal", "Demanda, horas y plantilla"),
}


def habilitar_desplazamiento(widget, lienzo):
    """Rueda local y desplazamiento al foco, sin capturar eventos de otras pantallas."""
    def rueda(evento):
        if getattr(evento, "num", None) in (4, 5):
            pasos = -1 if evento.num == 4 else 1
        else:
            delta = evento.delta
            if not delta:
                return None
            pasos = -max(1, abs(delta) // 120) if delta > 0 else max(1, abs(delta) // 120)
        lienzo.yview_scroll(pasos, "units")
        return "break"

    def revelar(evento):
        control = evento.widget
        if not control.winfo_viewable():
            return
        superior = control.winfo_rooty() - lienzo.winfo_rooty()
        inferior = superior + control.winfo_height()
        alto = lienzo.winfo_height()
        region = lienzo.bbox("all")
        if not region:
            return
        desplazamiento = superior - 12 if superior < 0 else (inferior - alto + 12 if inferior > alto else 0)
        if desplazamiento:
            lienzo.yview_moveto(max(0, (lienzo.canvasy(0) + desplazamiento) / max(region[3], 1)))

    if getattr(widget, "_lienzo_desplazamiento", None) is not lienzo:
        widget._lienzo_desplazamiento = lienzo
        # Los selectores y el texto conservan sus comportamientos de rueda nativos.
        if not isinstance(widget, (ttk.Combobox, tk.Text)):
            widget.bind("<MouseWheel>", rueda)
            widget.bind("<Button-4>", rueda)
            widget.bind("<Button-5>", rueda)
        widget.bind("<FocusIn>", revelar, add="+")
    for hijo in widget.winfo_children():
        habilitar_desplazamiento(hijo, lienzo)


def configurar_estilos(raiz):
    """Estilos con estados de teclado, puntero y desactivación explícitos."""
    colores = paleta(raiz)
    FONDO, SUPERFICIE, TEXTO, SECUNDARIO = (colores[k] for k in ("fondo", "superficie", "texto", "secundario"))
    PRIMARIO, PRIMARIO_HOVER, NOCHE, ACENTO = (colores[k] for k in ("primario", "hover", "noche", "acento"))
    TEXTO_SOBRE_OSCURO, SUAVE, BORDE, ERROR = (colores[k] for k in ("lateral", "suave", "borde", "error"))
    gestor(raiz).preparar()
    destacado = colores["blanco"]
    enlace = colores["enlace"]
    if not hasattr(raiz, "familias_disponibles"):
        raiz.familias_disponibles = set(font.families(raiz))
    familias = raiz.familias_disponibles
    familia = next((f for f in TIPOGRAFIA["texto"] if f in familias), "TkDefaultFont")
    display = next((f for f in TIPOGRAFIA["titulos"] if f in familias), familia)
    mono = next((f for f in TIPOGRAFIA["cifras"] if f in familias), familia)
    semibold = next((f for f in ("Segoe UI Variable Text Semibold", "Segoe UI Semibold") if f in familias), familia)
    boton = (semibold, -TIPOGRAFIA["boton_px"])
    estilo = ttk.Style(raiz)
    estilo.theme_use("clam")
    estilo.configure(".", font=(familia, -TIPOGRAFIA["base_px"]), background=FONDO, foreground=TEXTO)
    estilo.configure("TFrame", background=FONDO)
    estilo.configure("Card.TFrame", background=SUPERFICIE)
    estilo.configure("Header.TFrame", background=colores["cabecera"])
    estilo.configure("HeaderTitle.TLabel", background=colores["cabecera"], font=("Segoe UI", 15, "bold"))
    estilo.configure("HeaderMuted.TLabel", background=colores["cabecera"], foreground=SECUNDARIO)
    estilo.configure("Data.TFrame", background=SUAVE)
    estilo.configure("DataKey.TLabel", background=SUAVE, foreground=SECUNDARIO, font=("Segoe UI", 10))
    estilo.configure("DataValue.TLabel", background=SUAVE, font=("Segoe UI", 11, "bold"))
    estilo.configure("Note.TFrame", background=colores["fondo_nota"])
    estilo.configure("NoteTitle.TLabel", background=colores["fondo_nota"], foreground=colores["nota"],
                     font=("Segoe UI", 12, "bold"))
    estilo.configure("Note.TLabel", background=colores["fondo_nota"], foreground=colores["nota"],
                     font=("Segoe UI", 11, "italic"))
    estilo.configure("Assumption.TLabel", background=SUPERFICIE, foreground=colores["nota"],
                     font=("Segoe UI", 11, "italic"))
    estilo.configure("ResultTitle.TLabel", background=colores["fondo_resultado"], foreground=colores["resultado"],
                     font=("Segoe UI", 14, "bold"))
    estilo.configure("ResultValue.TLabel", background=colores["fondo_resultado"], foreground=colores["resultado"],
                     font=("Segoe UI", 20, "bold"))
    estilo.configure("Panel.TFrame", background=SUPERFICIE, bordercolor=BORDE, borderwidth=1, relief="solid")
    estilo.configure("TLabel", background=FONDO, foreground=TEXTO)
    estilo.configure("Card.TLabel", background=SUPERFICIE)
    estilo.configure("Muted.TLabel", foreground=SECUNDARIO)
    estilo.configure("CardMuted.TLabel", background=SUPERFICIE, foreground=SECUNDARIO)
    estilo.configure("InputHint.TLabel", background=SUPERFICIE, foreground=SECUNDARIO, font=(familia, -12))
    estilo.configure("InputError.TLabel", background=SUPERFICIE, foreground=ERROR, font=(familia, -12))
    estilo.configure("Title.TLabel", font=(display, -32, "bold"))
    estilo.configure("Subtitle.TLabel", font=("Segoe UI", 16, "bold"))
    estilo.configure("CardTitle.TLabel", background=SUPERFICIE, font=("Segoe UI", 15, "bold"))
    estilo.configure("CardSection.TLabel", background=SUPERFICIE, font=("Segoe UI", 12, "bold"))
    estilo.configure("Kpi.TLabel", background=SUPERFICIE, foreground=enlace, font=(mono, -26))
    estilo.configure("ResultValue.TLabel", font=(mono, -26, "bold"))
    estilo.configure("Accent.TLabel", background=SUPERFICIE, foreground=ACENTO, font=("Segoe UI", 12, "bold"))
    estilo.configure("TButton", font=boton, padding=(14, 8), background=SUPERFICIE, foreground=enlace,
                     bordercolor=BORDE, focuscolor=PRIMARIO, focusthickness=2)
    estilo.map("TButton", background=[("disabled", FONDO), ("pressed", SUAVE), ("active", SUAVE)],
               foreground=[("disabled", colores["texto_deshabilitado"])])
    estilo.configure("Primary.TButton", background=PRIMARIO, foreground=destacado, bordercolor=PRIMARIO,
                     focuscolor=destacado)
    estilo.configure("Compact.TButton", padding=(8, 7), font=boton)
    estilo.configure("Primary.TButton", padding=(16, 12), font=boton)
    estilo.configure("CardPrimary.TButton", padding=(16, 12), font=boton, foreground=destacado)
    estilo.map("CardPrimary.TButton", foreground=[("disabled", colores["texto_deshabilitado"]), ("!disabled", destacado)])
    for nombre in ("HeaderMenu.TButton", "ReportMenu.TButton", "Popup.TButton", "PopupSelected.TButton"):
        estilo.configure(nombre, font=boton, padding=(10, 6), anchor="w")
    estilo.configure("Popup.TButton", foreground=TEXTO)
    estilo.configure("PopupSelected.TButton", foreground=enlace)
    estilo.configure("Danger.TButton", foreground=colores["texto_destructivo"])
    estilo.map("Primary.TButton", background=[("disabled", SECUNDARIO), ("pressed", PRIMARIO_HOVER), ("active", PRIMARIO_HOVER)],
                 foreground=[("disabled", colores["texto_deshabilitado"]), ("!disabled", destacado)])
    estilo.configure("Nav.TButton", background=NOCHE, foreground=TEXTO_SOBRE_OSCURO,
                     bordercolor=NOCHE, focuscolor=SUPERFICIE, anchor="w")
    estilo.map("Nav.TButton", foreground=[("disabled", colores["texto_deshabilitado"]), ("active", TEXTO)])
    estilo.configure("NavActive.TButton", background=PRIMARIO, foreground=destacado,
                       bordercolor=PRIMARIO, focuscolor=destacado, anchor="w")
    estilo.map("NavActive.TButton", background=[("active", PRIMARIO_HOVER), ("pressed", PRIMARIO_HOVER)])
    estilo.configure("TEntry", padding=(10, 8), fieldbackground=SUPERFICIE, foreground=TEXTO, insertcolor=TEXTO, bordercolor=BORDE,
                     lightcolor=BORDE, darkcolor=BORDE, selectbackground=PRIMARIO, selectforeground=destacado)
    estilo.map("TEntry", bordercolor=[("focus", PRIMARIO)], lightcolor=[("focus", PRIMARIO)], darkcolor=[("focus", PRIMARIO)],
                fieldbackground=[("disabled", colores["relleno_deshabilitado"])], foreground=[("disabled", colores["texto_deshabilitado"])])
    estilo.configure("TCombobox", padding=(8, 5), fieldbackground=SUPERFICIE, background=colores["campo"], foreground=TEXTO,
                     bordercolor=colores["campo"], lightcolor=colores["campo"], darkcolor=colores["campo"],
                     arrowcolor=TEXTO, arrowsize=13)
    estilo.map("TCombobox", fieldbackground=[("disabled", SUAVE), ("readonly", SUPERFICIE)],
               foreground=[("disabled", SECUNDARIO), ("readonly", TEXTO)],
               selectbackground=[("readonly", SUAVE)], selectforeground=[("readonly", TEXTO)])
    estilo.configure("Header.TCombobox", background=colores["campo"], fieldbackground=colores["campo"],
                     bordercolor=colores["campo"], darkcolor=colores["campo"], lightcolor=colores["campo"],
                     arrowsize=13, padding=(9, 6), font=boton)
    estilo.map("Header.TCombobox", fieldbackground=[("readonly", colores["campo"])],
               selectbackground=[("readonly", colores["campo"])], selectforeground=[("readonly", TEXTO)])
    estilo.configure("TPanedwindow", background=FONDO)
    estilo.configure("TCheckbutton", padding=5)
    estilo.configure("Error.TLabel", foreground=ERROR, background=FONDO)
    estilo.configure("Step.TButton", padding=(8, 11), font=boton)
    estilo.configure("StepActive.TButton", padding=(8, 11), background=PRIMARIO, foreground=destacado,
                     bordercolor=PRIMARIO, focuscolor=destacado)
    estilo.map("StepActive.TButton", foreground=[("disabled", colores["texto_deshabilitado"]), ("!disabled", destacado)])
    estilo.configure("Table.TLabel", background=SUAVE, font=("Segoe UI", 10, "bold"))
    estilo.configure("ModuleIcon.TLabel", background=SUAVE, foreground=enlace, font=("Segoe UI", 21, "bold"))
    estilo.configure("TMenubutton", background=SUPERFICIE, foreground=TEXTO, padding=(12, 9))
    estilo.configure("Primary.TMenubutton", background=PRIMARIO, foreground=destacado, arrowcolor=destacado)
    estilo.map("Primary.TMenubutton", background=[("active", PRIMARIO_HOVER)])
    raiz.configure(background=FONDO)
    raiz.option_add("*TCombobox*Listbox.font", ("Segoe UI", 12))
    raiz.option_add("*TCombobox*Listbox.background", SUPERFICIE)
    raiz.option_add("*TCombobox*Listbox.foreground", TEXTO)
    raiz.option_add("*TCombobox*Listbox.selectBackground", PRIMARIO)
    raiz.option_add("*TCombobox*Listbox.selectForeground", destacado)
    estilo.configure("Treeview", background=SUPERFICIE, fieldbackground=SUPERFICIE, foreground=TEXTO,
                     rowheight=32, bordercolor=BORDE)
    estilo.map("Treeview", background=[("selected", PRIMARIO)], foreground=[("selected", destacado)])
    estilo.configure("Treeview.Heading", background=SUAVE, foreground=TEXTO, padding=8)
    estilo.map("Treeview.Heading", background=[("active", BORDE)])
    estilo.configure("TScrollbar", background=SUAVE, troughcolor=FONDO, arrowcolor=TEXTO,
                     bordercolor=BORDE, lightcolor=BORDE, darkcolor=BORDE)
    estilo.map("TScrollbar", background=[("active", BORDE), ("pressed", BORDE)])
    estilo.configure("TCheckbutton", indicatorbackground=SUPERFICIE, indicatorforeground=TEXTO)
    estilo.map("TCheckbutton", background=[("active", SUAVE)],
               indicatorbackground=[("disabled", SUAVE), ("selected", PRIMARIO), ("!selected", SUPERFICIE)])
    estilo.map("TMenubutton", background=[("active", SUAVE)])
    estilo.configure("Header.TMenubutton", font=boton, foreground=enlace, arrowcolor=TEXTO, padding=(12, 7))
    estilo.configure("Report.TMenubutton", font=boton, foreground=enlace, arrowcolor=TEXTO, padding=(12, 7))
    configurar_bordes(raiz, estilo, colores)


def mostrar_informe(padre, titulo, informe, copiar=None):
    """Visor desplazable con jerarquía tipográfica para informes nuevos y guardados."""
    ventana = tk.Toplevel(padre)
    ventana.title(titulo)
    ventana.geometry("880x660")
    ventana.minsize(460, 360)
    vincular_colores(ventana, background="fondo")
    pie = ttk.Frame(ventana, padding=(16, 8))
    pie.pack(side="bottom", fill="x")
    ttk.Button(pie, text="Cerrar", command=ventana.destroy).pack(side="right")
    if copiar:
        ttk.Button(pie, text="Copiar informe", command=copiar).pack(side="left")
    texto = tk.Text(ventana, wrap="word", font=("Segoe UI", 11), padx=22, pady=18, relief="flat",
                    spacing2=3)
    vincular_colores(texto, background="superficie", foreground="texto", selectbackground="primario", selectforeground="blanco")
    barra = ttk.Scrollbar(ventana, command=texto.yview)
    barra.pack(side="right", fill="y")
    texto.configure(yscrollcommand=barra.set)
    texto.pack(fill="both", expand=True)
    texto.tag_configure("titulo", font=("Segoe UI", 18, "bold"), spacing3=9)
    texto.tag_configure("seccion", font=("Segoe UI", 14, "bold"), spacing1=12, spacing3=6)
    texto.tag_configure("paso", font=("Segoe UI", 12, "bold"), spacing1=7, spacing3=4)
    texto.tag_configure("operacion", font=("Cambria", 12), lmargin1=14, lmargin2=14)
    texto.tag_configure("resultado", font=("Segoe UI", 11, "bold"), spacing1=5)
    texto.tag_configure("supuesto", font=("Segoe UI", 11, "italic"))
    texto.etiquetas_tema = {"seccion": "enlace", "paso": "acento", "resultado": "resultado", "supuesto": "nota"}
    for etiqueta, rol in texto.etiquetas_tema.items():
        texto.tag_configure(etiqueta, foreground=paleta(texto)[rol])
    for i, linea in enumerate(informe.split("\n")):
        marca = "titulo" if i == 0 else (
            "seccion" if linea[:3] in ("1. ", "2. ", "3. ", "4. ", "5. ") and linea[3:].isupper() else
            "paso" if linea.startswith("Paso ") else "resultado" if linea.startswith("Resultado:") else
            "supuesto" if linea.startswith("• ") else
            "operacion" if linea.startswith(("Fórmula:", "Sustitución:")) else "normal")
        texto.insert("end", linea + "\n", marca)
        if linea == "4. DESARROLLO":
            texto.mark_set("desarrollo", f"{i + 1}.0")
    texto.configure(state="disabled")
    if "desarrollo" in texto.mark_names():
        ttk.Button(pie, text="Ir al desarrollo", command=lambda: texto.yview("desarrollo")).pack(side="left", padx=8)
    texto.yview_moveto(0)
    ventana.bind("<Escape>", lambda _: ventana.destroy())
    return ventana


class TransicionPaginas(FondoAmbiental):
    """Deslizamiento breve entre páginas; cancelar una transición no pierde el estado."""

    def __init__(self, padre, movimiento):
        super().__init__(padre)
        self.movimiento = movimiento
        self.actual = None
        self.tarea = None
        self.bind("<Destroy>", self.cancelar)

    def cancelar(self, evento=None):
        if evento is not None and evento.widget is not self:
            return
        if self.tarea is not None:
            self.after_cancel(self.tarea)
            self.tarea = None
        if self.actual is not None and self.actual.winfo_exists():
            self.actual.place_configure(x=0)

    def mostrar(self, pagina):
        if self.actual is pagina:
            pagina.tkraise()
            return
        self.cancelar()
        if self.actual is not None:
            self.actual.place_forget()
        self.actual = pagina
        pagina.place(x=0, y=0, relwidth=1, relheight=1)
        pagina.tkraise()
        if self.movimiento.get():
            self.animar(0)

    def animar(self, cuadro):
        self.tarea = None
        desplazamiento = round(28 * (1 - cuadro / 12) ** 3) if self.movimiento.get() else 0
        self.actual.place_configure(x=desplazamiento)
        if cuadro < 12 and self.movimiento.get():
            self.tarea = self.after(16, self.animar, cuadro + 1)


class Indicadores(ttk.Frame):
    """Tarjetas compactas que se reorganizan según el ancho disponible."""

    def __init__(self, padre):
        super().__init__(padre)
        self.tarjetas = []
        self.columnas = 0
        self.presentacion = None
        self.bind("<Configure>", lambda e: self.organizar(e.width))

    def presentar(self, pasos, decimales):
        pasos = tuple(pasos)
        presentacion = pasos, decimales
        if self.presentacion == presentacion:
            return
        self.presentacion = presentacion
        for tarjeta in self.tarjetas:
            tarjeta.destroy()
        self.tarjetas = []
        self.columnas = 0
        for paso in pasos:
            tarjeta = ttk.Frame(self, style="Rounded.TFrame", padding=18)
            precision = 0 if paso.unidad == "personas" else decimales
            valor = numero(paso.resultado, precision)
            if paso.unidad == "$":
                valor = "$" + valor
            ttk.Label(tarjeta, text=paso.titulo, style="CardMuted.TLabel", wraplength=170).pack(anchor="w")
            ttk.Label(tarjeta, text=valor, style="Kpi.TLabel", wraplength=240).pack(anchor="w", pady=(8, 2))
            ttk.Label(tarjeta, text=paso.unidad if paso.unidad != "$" else "costo total ($)",
                      style="CardMuted.TLabel", wraplength=170).pack(anchor="w")
            self.tarjetas.append(tarjeta)
        self.organizar(self.winfo_width())

    def organizar(self, ancho):
        columnas = min(3, len(self.tarjetas), max(1, ancho // 225))
        if not columnas or columnas == self.columnas:
            return
        self.columnas = columnas
        for indice in range(3):
            self.columnconfigure(indice, weight=1 if indice < columnas else 0,
                                 minsize=0, uniform="kpis" if indice < columnas else "")
        for indice, tarjeta in enumerate(self.tarjetas):
            tarjeta.grid(row=indice // columnas, column=indice % columnas, sticky="nsew", padx=(0, 8), pady=(0, 8))


def resumen_resultado(modulo, resultado):
    """Selecciona indicadores y series con unidades comparables, sin recalcular."""
    if resultado.indicadores:
        return resultado.indicadores, resultado.serie, resultado.unidad_grafico, resultado.titulo_grafico
    pasos = resultado.pasos
    if modulo == "un_factor":
        indicadores = (pasos[0], pasos[1], pasos[3])
        serie = [("Antes", pasos[0].resultado), ("Después", pasos[1].resultado)]
        return indicadores, serie, pasos[0].unidad, "Comparación de productividad"
    if modulo == "capacidad":
        indicadores = (pasos[0], pasos[6], pasos[7])
        serie = [("Actual", pasos[5].resultado), ("Necesario", pasos[6].resultado)]
        return indicadores, serie, "personas", "Personal calculado · con ajuste a enteros"
    costos = [p for p in pasos if p.titulo.startswith("Costo:")]
    total = next(p for p in pasos if p.titulo == "Costo total")
    laboral = next((p for p in pasos if p.titulo == "Productividad laboral por hora"), None)
    indicadores = (total, pasos[-1]) if laboral is None else (total, pasos[-1], laboral)
    # Agrupar los menores evita un gráfico ilegible con decenas de insumos.
    ordenados = sorted(costos, key=lambda p: p.resultado, reverse=True)
    serie = [(p.titulo.removeprefix("Costo: "), p.resultado) for p in ordenados[:4]]
    if len(ordenados) > 4:
        serie.append(("Otros insumos", sum(p.resultado for p in ordenados[4:])))
    return indicadores, serie, "$", "Distribución de costos por insumo"


class GraficoBarras(tk.Canvas):
    """Barras con etiquetas legibles y animación breve opcional, no espera artificial."""

    def __init__(self, padre, movimiento):
        super().__init__(padre, background=SUPERFICIE, width=270, height=190, highlightthickness=0)
        vincular_colores(self, background="superficie")
        self.es_grafico_tematizado = True
        self.movimiento = movimiento
        self.serie = []
        self.unidad = ""
        self.decimales = 3
        self.tipo = "barras"
        self.tarea = None
        self.bind("<Configure>", lambda e: self.dibujar())
        self.bind("<Destroy>", self.cancelar)

    def cancelar(self, evento=None):
        if self.tarea is not None:
            self.after_cancel(self.tarea)
            self.tarea = None

    def presentar(self, serie, unidad, decimales, tipo="barras"):
        self.cancelar()
        self.serie, self.unidad, self.decimales = serie, unidad, decimales
        self.tipo = tipo
        self.configure(height=max(160, len(serie) * 42 + 35))
        if self.movimiento.get():
            self.animar(0)
        else:
            self.dibujar()

    def animar(self, cuadro):
        self.tarea = None
        if not self.movimiento.get():
            self.dibujar()
            return
        self.dibujar(1 - (1 - cuadro / 10) ** 3)
        if cuadro < 10:
            self.tarea = self.after(16, self.animar, cuadro + 1)

    def dibujar(self, progreso=1):
        colores = paleta(self)
        TEXTO, SUAVE, PRIMARIO, ACENTO, SECUNDARIO = (colores[k] for k in ("texto", "suave", "primario", "acento", "secundario"))
        self.delete("all")
        if not self.serie:
            return
        if self.tipo == "composicion":
            self.dibujar_composicion()
            return
        if len(self.serie) <= 3:
            self.dibujar_comparacion(progreso)
            return
        ancho = max(self.winfo_width(), 300)
        inicio = min(155, ancho * 0.3)
        disponible = max(20, ancho - inicio - 140)
        maximo = max(v for _, v in self.serie) or 1
        for indice, (nombre, valor) in enumerate(self.serie):
            y = 24 + indice * 42
            etiqueta = nombre if len(nombre) <= 17 else nombre[:16] + "…"
            self.create_text(12, y + 10, text=etiqueta, anchor="w", fill=TEXTO, font=("Segoe UI", 12))
            self.create_rectangle(inicio, y, inicio + disponible, y + 22, fill=SUAVE, outline="")
            largo = disponible * (valor / maximo) * progreso
            self.create_rectangle(inicio, y, inicio + largo, y + 22,
                                  fill=PRIMARIO if indice == 0 else ACENTO, outline="")
            valor_texto = numero(valor, self.decimales)
            self.create_text(inicio + disponible + 10, y + 10, text=valor_texto,
                             anchor="w", fill=TEXTO, font=("Segoe UI", 12))
        self.create_text(12, 24 + len(self.serie) * 42, text=f"Unidad: {self.unidad}",
                         anchor="w", fill=SECUNDARIO, font=("Segoe UI", 12))

    def dibujar_comparacion(self, progreso):
        colores = paleta(self)
        BORDE, PRIMARIO, ACENTO, TEXTO, SECUNDARIO = (colores[k] for k in ("borde", "primario", "acento", "texto", "secundario"))
        ancho = max(100, self.winfo_width())
        origen, base, alto = 18, 118, 72
        derecha = ancho - origen
        for nivel in range(4):
            y = base - nivel * alto / 3
            self.create_line(origen, y, derecha, y, fill=BORDE)
        espacio = (derecha - origen) / len(self.serie)
        mitad = min(48, espacio * 0.3)
        maximo = max(valor for _, valor in self.serie) or 1
        for indice, (nombre, valor) in enumerate(self.serie):
            centro = origen + espacio * (indice + 0.5)
            y = base - (valor / maximo) * alto * progreso
            if valor:
                self.create_rectangle(centro - mitad, y, centro + mitad, base, outline="",
                                      fill=colores["graficos"][indice])
            etiqueta = nombre if len(nombre) <= 16 else nombre[:15] + "…"
            self.create_text(centro, base + 13, text=etiqueta, fill=TEXTO, font=("Segoe UI", 9))
            self.create_text(centro, y - 11, text=numero(valor, self.decimales),
                             width=max(20, int(espacio) - 4), fill=TEXTO, font=("Segoe UI", 9))
        self.create_text(origen, 151, text=self.unidad, anchor="w", fill=SECUNDARIO, font=("Segoe UI", 9))

    def dibujar_composicion(self):
        colores_tema = paleta(self)
        PRIMARIO, ACENTO, TEXTO, SUPERFICIE = (colores_tema[k] for k in ("primario", "acento", "texto", "superficie"))
        ancho = self.winfo_width()
        total = sum(valor for _, valor in self.serie)
        if total <= 0:
            return
        colores = colores_tema["graficos"]
        diametro = min(126, max(65, ancho // 4))
        inicio = 90
        for indice, (nombre, valor) in enumerate(self.serie):
            fraccion = valor / total
            color = colores[indice % len(colores)]
            y = 22 + indice * 26
            if fraccion == 1:
                self.create_oval(16, 12, 16 + diametro, 12 + diametro, fill=color, outline="")
            elif fraccion:
                self.create_arc(16, 12, 16 + diametro, 12 + diametro,
                                start=inicio, extent=-360 * fraccion, fill=color, outline="")
            inicio -= 360 * fraccion
            izquierda = diametro + 36
            self.create_rectangle(izquierda, y - 5, izquierda + 10, y + 5, fill=color, outline="")
            self.create_text(izquierda + 16, y, text=nombre, anchor="w", fill=TEXTO,
                             width=max(30, ancho - izquierda - 112), font=("Segoe UI", 10))
            self.create_text(ancho - 14, y, text=f"{numero(fraccion * 100, self.decimales)} %",
                             anchor="e", fill=TEXTO, font=("Segoe UI", 10))
        margen = diametro * 0.26
        self.create_oval(16 + margen, 12 + margen, 16 + diametro - margen, 12 + diametro - margen,
                         fill=SUPERFICIE, outline="")
