"""Paletas semánticas y actualización de controles sin reconstruir formularios."""

from .tokens import PALETAS as TOKENS

ROLES = dict(secundario="texto_secundario", primario="acento_fin", hover="acento_fin", noche="superficie",
             acento="acento_auxiliar", lateral="texto", suave="relleno_secundario", borde="borde_control",
             blanco="texto_acento", campo="relleno_secundario", enlace="texto", resultado="exito")
PALETAS = {tema: {**tokens, **{rol: tokens[clave] for rol, clave in ROLES.items()}} for tema, tokens in TOKENS.items()}


class ThemeManager:
    """Coordina la caché y el repintado de los controles registrados."""

    def __init__(self, raiz):
        self.raiz = raiz
        self.imagenes = {}
        self.tema = getattr(raiz, "nombre_tema", "Claro")

    def preparar(self):
        tema = getattr(self.raiz, "nombre_tema", "Claro")
        if tema != self.tema:
            self.imagenes.clear()
            self.tema = tema

    def notificar(self):
        actualizar_controles(self.raiz)


def gestor(widget):
    raiz = widget._root()
    if not hasattr(raiz, "gestor_tema"):
        raiz.gestor_tema = ThemeManager(raiz)
    return raiz.gestor_tema


def paleta(widget):
    return PALETAS[getattr(widget._root(), "nombre_tema", "Claro")]


def vincular_colores(widget, **roles):
    widget.colores_tema = roles
    colores = paleta(widget)
    widget.configure(**{opcion: colores[rol] for opcion, rol in roles.items()})
    return widget


def actualizar_controles(raiz):
    from .iconos import icono
    gestor(raiz).preparar()
    colores = paleta(raiz)
    pendientes = [raiz]
    while pendientes:
        widget = pendientes.pop()
        pendientes.extend(widget.winfo_children())
        if widget.winfo_class() == "Toplevel":
            widget.configure(background=colores["fondo"])
        roles = getattr(widget, "colores_tema", {})
        if roles:
            widget.configure(**{opcion: colores[rol] for opcion, rol in roles.items()})
        for etiqueta, rol in getattr(widget, "etiquetas_tema", {}).items():
            widget.tag_configure(etiqueta, foreground=colores[rol])
        if hasattr(widget, "icono_tema"):
            clave, rol, tamano = widget.icono_tema
            widget.configure(image=icono(widget, clave, colores[rol], tamano))
        if getattr(widget, "es_grafico_tematizado", False):
            widget.dibujar()
