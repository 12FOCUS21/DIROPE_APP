"""Formularios generados desde el registro de módulos."""

import logging
import tkinter as tk
from tkinter import messagebox, ttk

from ..formato import numero
from ..modulos import MODULOS
from ..nucleo import validar_numero


class Panel(ttk.Frame):
    def __init__(self, padre, modulo, decimales):
        super().__init__(padre, padding=12)
        self.modulo = modulo
        self.decimales = decimales
        self.variables = {}
        self.filas = []
        self.resultado = None
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        division = ttk.Panedwindow(self, orient="horizontal")
        division.grid(row=0, column=0, sticky="nsew")
        izquierda = ttk.Frame(division)
        derecha = ttk.Frame(division)
        division.add(izquierda, weight=1)
        division.add(derecha, weight=2)

        # Desplazamiento para que las tablas largas no oculten los botones.
        lienzo = tk.Canvas(izquierda, highlightthickness=0, width=460)
        barra = ttk.Scrollbar(izquierda, orient="vertical", command=lienzo.yview)
        lienzo.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        lienzo.pack(side="left", fill="both", expand=True)
        formulario = ttk.Frame(lienzo, padding=6)
        ventana = lienzo.create_window((0, 0), window=formulario, anchor="nw")
        formulario.bind("<Configure>", lambda e: lienzo.configure(scrollregion=lienzo.bbox("all")))
        lienzo.bind("<Configure>", lambda e: lienzo.itemconfigure(ventana, width=e.width))
        formulario.columnconfigure(0, weight=1)
        ttk.Label(formulario, text="Usa punto decimal. Todas las cantidades son del mismo período.",
                  wraplength=420).grid(row=0, column=0, sticky="w", pady=(0, 12))
        fila = 1
        for campo in modulo.campos:
            ttk.Label(formulario, text=campo.etiqueta).grid(row=fila, column=0, sticky="w")
            variable = tk.StringVar(value=campo.valor)
            self.variables[campo.clave] = variable
            ttk.Entry(formulario, textvariable=variable).grid(row=fila + 1, column=0, sticky="ew", pady=(0, 10))
            fila += 2
        if modulo.tabla_insumos:
            ttk.Label(formulario, text="Insumos: marca Horas solo para mano de obra medida en horas.\n"
                      "Para un costo global, usa cantidad 1 y el costo como precio.",
                      wraplength=420).grid(row=fila, column=0, sticky="w")
            self.tabla = ttk.Frame(formulario)
            self.tabla.grid(row=fila + 1, column=0, sticky="ew", pady=8)
            ttk.Button(formulario, text="Añadir insumo", command=self.agregar_fila).grid(row=fila + 2, column=0, sticky="w")
            fila += 3
            self.agregar_fila()

        ttk.Label(formulario, text="Ejemplos disponibles").grid(row=fila, column=0, sticky="w", pady=(14, 0))
        self.ejemplo = ttk.Combobox(formulario, state="readonly", values=list(modulo.ejemplos))
        self.ejemplo.current(0)
        self.ejemplo.grid(row=fila + 1, column=0, sticky="ew")
        ttk.Button(formulario, text="Cargar ejemplo", command=self.cargar_ejemplo).grid(row=fila + 2, column=0, sticky="ew", pady=6)
        ttk.Button(formulario, text="Calcular (Enter)", command=self.calcular).grid(row=fila + 3, column=0, sticky="ew", pady=6)
        ttk.Button(formulario, text="Limpiar", command=self.limpiar).grid(row=fila + 4, column=0, sticky="ew")

        ttk.Label(derecha, text="Procedimiento y resultados").pack(anchor="w", pady=(0, 8))
        ttk.Label(derecha, text="Los cálculos conservan precisión; los valores mostrados se redondean.",
                  wraplength=550).pack(anchor="w", pady=(0, 8))
        texto_marco = ttk.Frame(derecha)
        texto_marco.pack(fill="both", expand=True)
        self.texto = tk.Text(texto_marco, wrap="word", font=("Segoe UI", 12), padx=12, pady=12, state="disabled")
        scroll = ttk.Scrollbar(texto_marco, orient="vertical", command=self.texto.yview)
        self.texto.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.texto.pack(fill="both", expand=True)
        ttk.Button(derecha, text="Copiar procedimiento", command=self.copiar).pack(anchor="w", pady=10)

    def agregar_fila(self, valores=None):
        valores = valores or dict(nombre="", cantidad="", precio="", es_laboral=False)
        marco = ttk.Frame(self.tabla, padding=(0, 5))
        marco.pack(fill="x")
        variables = {c: tk.StringVar(value=str(valores[c])) for c in ("nombre", "cantidad", "precio")}
        variables["es_laboral"] = tk.BooleanVar(value=valores.get("es_laboral", False))
        for columna, (clave, etiqueta) in enumerate((("nombre", "Nombre"), ("cantidad", "Cantidad"), ("precio", "Precio ($)"))):
            ttk.Label(marco, text=etiqueta).grid(row=0, column=columna, sticky="w")
            ttk.Entry(marco, textvariable=variables[clave], width=14 if columna == 0 else 9).grid(row=1, column=columna, sticky="ew", padx=(0, 4))
            marco.columnconfigure(columna, weight=1)
        ttk.Checkbutton(marco, text="Horas", variable=variables["es_laboral"]).grid(row=2, column=0, sticky="w")
        registro = (marco, variables)
        ttk.Button(marco, text="Quitar", command=lambda: self.quitar_fila(registro)).grid(row=2, column=2, sticky="e")
        self.filas.append(registro)

    def quitar_fila(self, registro):
        self.filas.remove(registro)
        registro[0].destroy()

    def cargar_ejemplo(self):
        datos = self.modulo.ejemplos[self.ejemplo.get()]
        for clave, variable in self.variables.items():
            variable.set(str(datos[clave]))
        if self.modulo.tabla_insumos:
            for registro in self.filas[:]:
                self.quitar_fila(registro)
            for insumo in datos["insumos"]:
                self.agregar_fila(insumo)
        self.resultado = None
        self.mostrar_texto("Ejemplo cargado. Pulsa Calcular para obtener el procedimiento.")

    def recoger_datos(self):
        datos = {c: v.get() for c, v in self.variables.items()}
        if self.modulo.tabla_insumos:
            datos["insumos"] = []
            for _, variables in self.filas:
                nombre = variables["nombre"].get()
                datos["insumos"].append(dict(
                    nombre=nombre,
                    cantidad=validar_numero(variables["cantidad"].get(), f"Cantidad de {nombre or 'insumo'}"),
                    precio=validar_numero(variables["precio"].get(), f"Precio de {nombre or 'insumo'}"),
                    es_laboral=variables["es_laboral"].get()))
        return datos

    def calcular(self):
        # Un error nunca deja un resultado anterior que pueda confundirse con el nuevo.
        self.resultado = None
        self.mostrar_texto("")
        try:
            self.resultado = self.modulo.calcular(self.recoger_datos())
            self.renderizar()
        except ValueError as error:
            messagebox.showwarning("Revisa los datos", str(error), parent=self)
            return False
        return True

    def renderizar(self):
        if self.resultado is None:
            return
        lineas = [self.modulo.nombre.upper(), ""]
        for indice, paso in enumerate(self.resultado.pasos, 1):
            decimales = 2 if paso.unidad in ("%", "$") else self.decimales.get()
            valor = numero(paso.resultado, decimales)
            mostrado = f"${valor}" if paso.unidad == "$" else f"{valor} {paso.unidad}"
            lineas.extend([f"{indice}. {paso.titulo}", paso.explicacion, paso.formula,
                           f"Sustitución: {paso.sustitucion}", f"Resultado: {mostrado}", ""])
        lineas.extend(["INTERPRETACIÓN", self.resultado.interpretacion])
        self.mostrar_texto("\n".join(lineas))

    def mostrar_texto(self, texto):
        self.texto.configure(state="normal")
        self.texto.delete("1.0", "end")
        self.texto.insert("1.0", texto)
        self.texto.configure(state="disabled")

    def limpiar(self):
        for campo in self.modulo.campos:
            self.variables[campo.clave].set(campo.valor)
        for registro in self.filas[:]:
            self.quitar_fila(registro)
        if self.modulo.tabla_insumos:
            self.agregar_fila()
        self.resultado = None
        self.mostrar_texto("")

    def copiar(self):
        if self.resultado is None:
            messagebox.showinfo("Sin resultado", "Primero calcula un problema válido.", parent=self)
            return
        self.clipboard_clear()
        self.clipboard_append(self.texto.get("1.0", "end-1c"))


class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DIROPE Calc — versión local inicial")
        self.geometry("1200x780")
        self.minsize(960, 620)
        estilo = ttk.Style(self)
        estilo.configure(".", font=("Segoe UI", 12))
        self.option_add("*TCombobox*Listbox.font", ("Segoe UI", 12))
        cabecera = ttk.Frame(self, padding=12)
        cabecera.pack(fill="x")
        ttk.Label(cabecera, text="DIROPE Calc | Uso local, sin internet").pack(side="left")
        ttk.Label(cabecera, text="Decimales:").pack(side="left", padx=(24, 6))
        self.decimales = tk.IntVar(value=6)
        selector = ttk.Combobox(cabecera, textvariable=self.decimales, state="readonly", values=list(range(9)), width=3)
        selector.pack(side="left")
        selector.bind("<<ComboboxSelected>>", lambda e: self.actualizar_formato())
        self.pestanas = ttk.Notebook(self)
        self.pestanas.pack(fill="both", expand=True)
        self.paneles = []
        for modulo in MODULOS:
            panel = Panel(self.pestanas, modulo, self.decimales)
            self.pestanas.add(panel, text=modulo.nombre)
            self.paneles.append(panel)
        self.bind("<Return>", self.calcular_activo)

    def calcular_activo(self, evento=None):
        self.paneles[self.pestanas.index("current")].calcular()
        return "break"

    def actualizar_formato(self):
        for panel in self.paneles:
            panel.renderizar()

    def report_callback_exception(self, tipo, valor, traza):
        logging.error("Error inesperado en la interfaz", exc_info=(tipo, valor, traza))
        messagebox.showerror("No se pudo completar la operación",
                             "Ocurrió un error inesperado. Revisa registro.log en la carpeta de datos de DIROPE Calc.", parent=self)
