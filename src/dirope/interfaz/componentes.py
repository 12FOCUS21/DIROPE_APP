"""Sistema visual y gráficos locales sin dependencias externas."""

import tkinter as tk
from tkinter import ttk

from ..formato import numero

FONDO = "#EAF1FB"
SUPERFICIE = "#FFFFFF"
TEXTO = "#112039"
SECUNDARIO = "#526176"
PRIMARIO = "#164CCA"
PRIMARIO_HOVER = "#1942AA"
NOCHE = "#112138"
ACENTO = "#087F8C"
TEXTO_SOBRE_OSCURO = "#BCCBDF"
SUAVE = "#EAF0FD"
BORDE = "#D5DEEB"
ERROR = "#9B302B"

DESCRIPCIONES = {
    "un_factor": ("▥", "Productividad de un factor", "Rendimiento por recurso"),
    "multifactor": ("◇", "Productividad multifactor", "Costos y alternativas"),
    "capacidad": ("♙", "Capacidad y personal", "Demanda, horas y plantilla"),
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
    estilo = ttk.Style(raiz)
    estilo.theme_use("clam")
    estilo.configure(".", font=("Segoe UI", 11), background=FONDO, foreground=TEXTO)
    estilo.configure("TFrame", background=FONDO)
    estilo.configure("Card.TFrame", background=SUPERFICIE)
    estilo.configure("Panel.TFrame", background=SUPERFICIE, bordercolor=BORDE, borderwidth=1, relief="solid")
    estilo.configure("TLabel", background=FONDO, foreground=TEXTO)
    estilo.configure("Card.TLabel", background=SUPERFICIE)
    estilo.configure("Muted.TLabel", foreground=SECUNDARIO)
    estilo.configure("CardMuted.TLabel", background=SUPERFICIE, foreground=SECUNDARIO)
    estilo.configure("Title.TLabel", font=("Segoe UI", 25, "bold"))
    estilo.configure("Subtitle.TLabel", font=("Segoe UI", 16, "bold"))
    estilo.configure("CardTitle.TLabel", background=SUPERFICIE, font=("Segoe UI", 15, "bold"))
    estilo.configure("Kpi.TLabel", background=SUPERFICIE, foreground=PRIMARIO, font=("Segoe UI", 20, "bold"))
    estilo.configure("Accent.TLabel", background=SUPERFICIE, foreground=ACENTO, font=("Segoe UI", 12, "bold"))
    estilo.configure("TButton", padding=(14, 10), background=SUPERFICIE, foreground=PRIMARIO,
                     bordercolor=BORDE, focuscolor=PRIMARIO, focusthickness=2)
    estilo.map("TButton", background=[("disabled", FONDO), ("pressed", SUAVE), ("active", SUAVE)],
               foreground=[("disabled", SECUNDARIO)])
    estilo.configure("Primary.TButton", background=PRIMARIO, foreground=SUPERFICIE, bordercolor=PRIMARIO,
                     focuscolor=SUPERFICIE)
    estilo.configure("Compact.TButton", padding=(6, 5), font=("Segoe UI", 10))
    estilo.map("Primary.TButton", background=[("disabled", SECUNDARIO), ("pressed", PRIMARIO_HOVER), ("active", PRIMARIO_HOVER)],
               foreground=[("disabled", SUPERFICIE), ("!disabled", SUPERFICIE)])
    estilo.configure("Nav.TButton", background=NOCHE, foreground=TEXTO_SOBRE_OSCURO,
                     bordercolor=NOCHE, focuscolor=SUPERFICIE, anchor="w")
    estilo.map("Nav.TButton", background=[("active", "#223650"), ("pressed", PRIMARIO_HOVER)],
               foreground=[("active", SUPERFICIE)])
    estilo.configure("NavActive.TButton", background=PRIMARIO, foreground=SUPERFICIE,
                      bordercolor=PRIMARIO, focuscolor=SUPERFICIE, anchor="w")
    estilo.map("NavActive.TButton", background=[("active", PRIMARIO_HOVER), ("pressed", PRIMARIO_HOVER)])
    estilo.configure("TEntry", padding=8, fieldbackground=SUPERFICIE, bordercolor=BORDE,
                     lightcolor=BORDE, darkcolor=BORDE)
    estilo.map("TEntry", bordercolor=[("focus", PRIMARIO)], lightcolor=[("focus", PRIMARIO)], darkcolor=[("focus", PRIMARIO)])
    estilo.configure("TCombobox", padding=7, fieldbackground=SUPERFICIE, arrowsize=16)
    estilo.map("TCombobox", fieldbackground=[("readonly", SUPERFICIE)])
    estilo.configure("TPanedwindow", background=FONDO)
    estilo.configure("TCheckbutton", padding=5)
    estilo.configure("Error.TLabel", foreground=ERROR, background=FONDO)
    estilo.configure("Step.TButton", padding=(8, 8), font=("Segoe UI", 11))
    estilo.configure("StepActive.TButton", padding=(8, 8), background=PRIMARIO, foreground=SUPERFICIE,
                     bordercolor=PRIMARIO, focuscolor=SUPERFICIE)
    estilo.map("StepActive.TButton", background=[("active", PRIMARIO_HOVER)], foreground=[("!disabled", SUPERFICIE)])
    estilo.configure("Table.TLabel", background=SUAVE, font=("Segoe UI", 10, "bold"))
    estilo.configure("ModuleIcon.TLabel", background=SUAVE, foreground=PRIMARIO, font=("Segoe UI", 21, "bold"))
    estilo.configure("TMenubutton", background=SUPERFICIE, foreground=TEXTO, padding=(12, 9))
    estilo.configure("Primary.TMenubutton", background=PRIMARIO, foreground=SUPERFICIE, arrowcolor=SUPERFICIE)
    estilo.map("Primary.TMenubutton", background=[("active", PRIMARIO_HOVER)])
    raiz.configure(background=FONDO)
    raiz.option_add("*TCombobox*Listbox.font", ("Segoe UI", 12))


class TransicionPaginas(ttk.Frame):
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
        self.bind("<Configure>", lambda e: self.organizar(e.width))

    def presentar(self, pasos, decimales):
        for tarjeta in self.tarjetas:
            tarjeta.destroy()
        self.tarjetas = []
        self.columnas = 0
        for paso in pasos:
            tarjeta = ttk.Frame(self, style="Card.TFrame", padding=14)
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
                                      fill=("#75A7F5", PRIMARIO, ACENTO)[indice])
            etiqueta = nombre if len(nombre) <= 16 else nombre[:15] + "…"
            self.create_text(centro, base + 13, text=etiqueta, fill=TEXTO, font=("Segoe UI", 9))
            self.create_text(centro, y - 11, text=numero(valor, self.decimales),
                             width=max(20, int(espacio) - 4), fill=TEXTO, font=("Segoe UI", 9))
        self.create_text(origen, 151, text=self.unidad, anchor="w", fill=SECUNDARIO, font=("Segoe UI", 9))

    def dibujar_composicion(self):
        ancho = self.winfo_width()
        total = sum(valor for _, valor in self.serie)
        if total <= 0:
            return
        colores = (PRIMARIO, "#388FE0", ACENTO, "#79BEA7", "#535EAB")
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
