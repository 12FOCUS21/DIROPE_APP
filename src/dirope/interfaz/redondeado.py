"""Bordes redondeados ttk mediante imágenes locales, conservando controles nativos."""

from math import sqrt
import tkinter as tk
from os import environ

from .temas import gestor, paleta, vincular_colores
from .tokens import RADIOS, SUPERMUESTREO

try:
    from PIL import Image, ImageColor, ImageDraw, ImageFilter, ImageTk
except ImportError:
    Image = None


def usa_pillow():
    return Image is not None and environ.get("DIROPE_SIN_PILLOW") != "1"


def tono(inicio, fin, proporcion):
    canales = [round(int(inicio[i:i+2], 16) * (1-proporcion) + int(fin[i:i+2], 16) * proporcion)
               for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(canales)


def dibujar_piel(widget, ancho, alto, radio, inicio, fin, borde=None, grosor=1, sombra=False, exterior=None):
    escala = SUPERMUESTREO
    tamano = (ancho * escala, alto * escala)
    # En Windows, ttk no siempre compone las esquinas transparentes con el padre real.
    imagen = Image.new("RGBA", tamano, exterior or (0, 0, 0, 0))
    margen = 4 * escala if sombra else 0
    caja = (margen, margen, tamano[0] - margen - 1, tamano[1] - margen - 1)
    if sombra:
        rgba = paleta(widget)["sombra_rgba"]
        for desplazamiento, radio_sombra, opacidad in ((2, 2, .55), (1, 1, .7)):
            capa = Image.new("RGBA", tamano)
            y = desplazamiento * escala
            ImageDraw.Draw(capa).rounded_rectangle((caja[0], caja[1] + y, caja[2], caja[3] + y),
                                                   radio * escala, fill=(*rgba[:3], round(255 * rgba[3] * opacidad)))
            imagen.alpha_composite(capa.filter(ImageFilter.GaussianBlur(radio_sombra * escala)))
    mascara = Image.new("L", tamano)
    ImageDraw.Draw(mascara).rounded_rectangle(caja, radio * escala, fill=255)
    if inicio == fin:
        cara = Image.new("RGBA", tamano, inicio)
    else:
        # Generar la rampa en código nativo, no una llamada Python por cada franja.
        rampa = Image.new("RGB", (1, 2))
        rampa.putdata((ImageColor.getrgb(inicio), ImageColor.getrgb(fin)))
        cara = rampa.resize(tamano, Image.Resampling.BILINEAR).convert("RGBA")
    cara.putalpha(mascara)
    if borde:
        ImageDraw.Draw(cara).rounded_rectangle(caja, radio * escala, outline=borde, width=grosor * escala)
    imagen.alpha_composite(cara)
    return ImageTk.PhotoImage(imagen.resize((ancho, alto), Image.Resampling.LANCZOS), master=widget)


class SuperficieCanvas(tk.Canvas):
    """Superficie a tamaño real; no interviene en la semántica de los controles."""

    def __init__(self, padre, variante, alto, radio=0, **opciones):
        super().__init__(padre, height=alto, highlightthickness=0, borderwidth=0, **opciones)
        self.variante, self.radio = variante, radio
        self.es_grafico_tematizado = True
        vincular_colores(self, background="fondo")
        self.bind("<Configure>", lambda _: self.dibujar(), add="+")

    def dibujar(self):
        ancho, alto = self.winfo_width(), self.winfo_height()
        if min(ancho, alto) <= 1:
            return
        colores = paleta(self)
        inicio, fin = colores[self.variante + "_inicio"], colores[self.variante]
        sombra = self.radio > 0 and min(ancho, alto) >= 20
        motor = usa_pillow()
        manager = gestor(self)
        manager.preparar()
        clave = (ancho, alto, self.radio, self.variante, "normal", manager.tema, motor)
        self.delete("piel")
        if motor:
            if clave not in manager.imagenes:
                if len(manager.imagenes) >= 12:
                    manager.imagenes.pop(next(iter(manager.imagenes)))
                manager.imagenes[clave] = dibujar_piel(self, ancho, alto, self.radio, inicio, fin, sombra=sombra)
            self.imagen = manager.imagenes[clave]
            self.create_image(0, 0, anchor="nw", image=self.imagen, tags="piel")
        else:
            self.imagen = None
            r = min(self.radio, ancho // 2, alto // 2)
            if r:
                self.create_polygon(1, r, 1, 1, r, 1, ancho-r, 1, ancho-1, 1, ancho-1, r,
                                    ancho-1, alto-r, ancho-1, alto-1, ancho-r, alto-1, r, alto-1,
                                    1, alto-1, 1, alto-r, smooth=True, fill=fin,
                                    outline=colores["borde_decorativo"], tags="piel")
            for y in range(0, alto, 2):
                margen = r if y < r or y >= alto-r else int(bool(r))
                self.create_rectangle(margen, y, ancho-margen, min(alto, y+2), outline="",
                                      fill=tono(inicio, fin, y / alto), tags="piel")
        self.tag_lower("piel")


def imagen_borde(raiz, relleno, borde, exterior, radio=12, grosor=1, sombra=False):
    """Crea un mosaico de nueve zonas estirables con esquinas circulares."""
    # Un centro amplio evita miles de mosaicos diminutos al pintar paneles grandes en Tk.
    lado = 96
    inicio, fin = relleno if isinstance(relleno, tuple) else (relleno, relleno)
    if usa_pillow():
        return dibujar_piel(raiz, lado, lado, radio, inicio, fin, borde, grosor, sombra=sombra, exterior=exterior)
    imagen = tk.PhotoImage(master=raiz, width=lado, height=lado)
    if exterior:
        imagen.put(exterior, to=(0, 0, lado, lado))
    for y in range(lado):
        dy = max(radio - y - 0.5, y + 0.5 - (lado - radio), 0)
        margen = round(radio - sqrt(max(0, radio * radio - dy * dy))) if dy else 0
        imagen.put(borde, to=(margen, y, lado - margen, y + 1))
        if grosor <= y < lado - grosor:
            interior = grosor + round((radio - grosor) - sqrt(max(0, (radio - grosor) ** 2 - dy ** 2)))
            imagen.put(tono(inicio, fin, y / (lado-1)), to=(interior, y, lado - interior, y + 1))
    return imagen


def configurar_bordes(raiz, estilo, colores):
    """Recrea los recursos al cambiar de tema, sin sustituir widgets ni sus eventos."""
    # Los elementos no se pueden redefinir: cada paleta usa nombres propios.
    tema = getattr(raiz, "nombre_tema", "Claro")
    cache = getattr(raiz, "imagenes_redondeadas", {})
    if tema not in cache:
        cache[tema] = []
    imagenes = cache[tema]
    existentes = estilo.element_names()

    def elemento(nombre, estados, exterior=None, radio=12, minimo=None, sombra=False):
        clave = f"Dirope.{tema}.{nombre}"
        if clave not in existentes:
            recursos = cache.setdefault("recursos_" + tema, {})
            fotos = []
            for estado, fondo, borde in estados:
                grosor = 2 if "focus" in estado else 1
                con_sombra = sombra and estado != "disabled"
                firma = (fondo, borde, exterior, radio, grosor, con_sombra)
                if firma not in recursos:
                    recursos[firma] = imagen_borde(raiz, fondo, borde, exterior, radio, grosor, con_sombra)
                fotos.append(recursos[firma])
            imagenes.extend(fotos)
            medida = {} if minimo is None else dict(width=minimo, height=minimo)
            estilo.element_create(clave, "image", fotos[0],
                                  *[(estado, foto) for (estado, _, _), foto in zip(estados[1:], fotos[1:])],
                                   border=radio + (4 if sombra and usa_pillow() else 0), padding=0, sticky="nsew", **medida)
        return clave

    fondo, superficie, borde = (colores[c] for c in ("fondo", "superficie", "borde"))
    for nombre, relleno, exterior in (("Panel.TFrame", superficie, fondo), ("Rounded.TFrame", superficie, fondo),
                                     ("Exercise.TFrame", colores["suave"], superficie),
                                     ("DataBlock.TFrame", colores["suave"], superficie)):
        elem = elemento(nombre, [("", relleno, colores["borde_decorativo"])], exterior, RADIOS["tarjeta"], 28)
        estilo.configure(nombre, background=exterior, relief="flat", borderwidth=0)
        estilo.layout(nombre, [(elem, {"sticky": "nsew"})])
    for nombre, fondo_rol in (("Note.TFrame", "fondo_nota"), ("Result.TFrame", "fondo_resultado")):
        relleno = colores[fondo_rol]
        contorno = colores["nota"] if nombre == "Note.TFrame" else colores["resultado"]
        elem = elemento(nombre, [("", relleno, contorno)], fondo, minimo=24)
        estilo.configure(nombre, background=fondo, relief="flat", borderwidth=0)
        estilo.layout(nombre, [(elem, {"sticky": "nsew"})])

    for nombre in ("TButton", "Primary.TButton", "CardPrimary.TButton", "Compact.TButton", "Nav.TButton", "NavActive.TButton",
                   "Step.TButton", "StepActive.TButton", "Card.TButton", "Popup.TButton", "PopupSelected.TButton",
                   "HeaderMenu.TButton", "ReportMenu.TButton", "Exercise.TButton", "Danger.TButton"):
        activo = nombre in ("Primary.TButton", "CardPrimary.TButton", "NavActive.TButton", "StepActive.TButton")
        nav = nombre.startswith("Nav")
        base = ((colores["acento_inicio"], colores["acento_fin"]) if activo else
                 colores["relleno_en_elevada"] if nombre in ("Exercise.TButton", "HeaderMenu.TButton", "PopupSelected.TButton")
                 else colores["campo"])
        hover = base if activo else colores["hover_elevada"]
        anillo = colores["foco_sobre_acento"] if activo else colores["foco"]
        contorno = colores["acento_fin"] if activo else borde
        if nombre == "Danger.TButton":
            base, hover, contorno = (colores[rol] for rol in ("relleno_destructivo", "hover_destructivo", "error"))
        estados = [("", base, contorno),
                   ("disabled", colores["relleno_deshabilitado"], borde),
                   ("focus pressed", hover, anillo), ("focus active", hover, anillo),
                   ("pressed", hover, anillo), ("active", hover, anillo if activo else contorno), ("focus", base, anillo)]
        exterior = (colores["noche"] if nav else colores["cabecera"] if nombre == "HeaderMenu.TButton" else
                    colores["suave"] if nombre == "Exercise.TButton" else superficie
                     if nombre in ("Card.TButton", "CardPrimary.TButton", "ReportMenu.TButton", "Popup.TButton", "PopupSelected.TButton") else fondo)
        elem = elemento(nombre, estados, exterior, RADIOS["boton"], 20,
                        sombra=nombre in ("Primary.TButton", "CardPrimary.TButton"))
        # El fondo rectangular de ttk debe ser el exterior, nunca el relleno del botón.
        estilo.configure(nombre, background=exterior, relief="flat", borderwidth=0)
        estilo.map(nombre, background=[("disabled", exterior), ("pressed", exterior), ("active", exterior)])
        estilo.layout(nombre, [(elem, {"sticky": "nsew", "children": [
            ("Button.padding", {"sticky": "nsew", "children": [("Button.label", {"sticky": "nsew"})]})]})])
    estados = [("", colores["campo"], borde), ("disabled", colores["relleno_deshabilitado"], borde),
               ("focus", colores["campo"], colores["foco"]), ("active", colores["campo"], borde)]
    for nombre, exterior in (("Header.TCombobox", colores["cabecera"]), ("TCombobox", None)):
        elem = elemento(nombre, estados, exterior, RADIOS["campo"], 18)
        estilo.configure(nombre, background=exterior or superficie, relief="flat", borderwidth=0)
        estilo.layout(nombre, [(elem, {"sticky": "nsew", "children": [
            ("Combobox.downarrow", {"side": "right", "sticky": ""}),
            ("Combobox.padding", {"sticky": "nsew", "children": [("Combobox.textarea", {"sticky": "nsew"})]}),
        ]})])
    elem = elemento("TEntry", estados, None, RADIOS["campo"], 18)
    estilo.layout("TEntry", [(elem, {"sticky": "nsew", "children": [
        ("Entry.padding", {"sticky": "nsew", "children": [("Entry.textarea", {"sticky": "nsew"})]}),
    ]})])
    for nombre, exterior in (("Header.TMenubutton", colores["cabecera"]), ("Report.TMenubutton", superficie)):
        elem = elemento(nombre, estados, exterior, 10)
        estilo.layout(nombre, [(elem, {"sticky": "nsew", "children": [
            ("Menubutton.padding", {"sticky": "nsew", "children": [
                ("Menubutton.indicator", {"side": "right", "sticky": ""}),
                ("Menubutton.label", {"side": "left", "sticky": ""}),
            ]}),
        ]})])
    for orientacion in ("Vertical", "Horizontal"):
        clave = f"Dirope.{tema}.{orientacion}.thumb"
        if clave not in existentes:
            ancho, alto = (10, 28) if orientacion == "Vertical" else (28, 10)
            fotos = []
            for rol in ("borde_control", "texto_secundario"):
                color = colores[rol]
                if usa_pillow():
                    foto = dibujar_piel(raiz, ancho, alto, 5, color, color)
                else:
                    foto = tk.PhotoImage(master=raiz, width=ancho, height=alto)
                    for y in range(alto):
                        d = max(4.5 - y, y + .5 - (alto - 5), 0)
                        x = round(5 - sqrt(25 - d*d))
                        foto.put(color, to=(x, y, ancho-x, y+1))
                fotos.append(foto)
            imagenes.extend(fotos)
            estilo.element_create(clave, "image", fotos[0], ("active", fotos[1]), border=5, sticky="nsew")
        estilo.layout(f"{orientacion}.TScrollbar", [(f"{orientacion}.Scrollbar.trough", {"sticky": "nsew",
                      "children": [(clave, {"sticky": "ns" if orientacion == "Vertical" else "ew"})]})])
    raiz.imagenes_redondeadas = cache
