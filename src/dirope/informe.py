"""Informe HTML autocontenido y apto para imprimir desde el navegador."""

from html import escape
from contextlib import contextmanager
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from .formato import numero
from .notacion import componer
from .leyendas import (leyenda_formula, leyenda_sustitucion, elementos_formula,
                       elementos_sustitucion, operadores_expresion)


class PDFNoDisponible(RuntimeError):
    """El motor opcional de exportación no está disponible en este Python."""


@contextmanager
def destino_atomico(ruta):
    """Conserva el informe anterior si falla la generación o la escritura."""
    destino = Path(ruta)
    temporal = None
    try:
        with NamedTemporaryFile(dir=destino.parent, prefix=f".{destino.name}.", suffix=".tmp", delete=False) as archivo:
            temporal = Path(archivo.name)
        yield temporal
        # Windows exige un descriptor escribible para sincronizar el archivo.
        with temporal.open("r+b") as archivo:
            os.fsync(archivo.fileno())
        os.replace(temporal, destino)
    finally:
        if temporal is not None:
            temporal.unlink(missing_ok=True)


def guardar_informe_html(ruta, contenido):
    """Guarda HTML UTF-8 sin dejar un archivo parcial en caso de error."""
    with destino_atomico(ruta) as temporal:
        temporal.write_text(contenido, encoding="utf-8")


def valor_paso(paso, decimales):
    cifra = numero(paso.resultado, 0 if paso.unidad == "personas" else decimales)
    return f"${cifra}" if paso.unidad == "$" else f"{cifra} {paso.unidad}".strip()


def indicadores_informe(resultado):
    indicadores = resultado.indicadores or resultado.procedimiento
    if resultado.principal:
        return (resultado.principal, *(p for p in indicadores if p != resultado.principal))
    return indicadores


def secciones_informe(enunciado, analisis, resultado, decimales):
    """Contenido completo reutilizable por el visor y la copia del informe."""
    yield "PLANTEAMIENTO", [enunciado or "Sin enunciado registrado.", f"Objetivo: {analisis.perfil.objetivo}"]
    yield "ANÁLISIS DE DATOS", [linea for grupo, filas in analisis.grupos
                              for linea in (grupo, *(f"{k}: {v}" for k, v in filas), "")]
    identificacion = [analisis.perfil.tipo, analisis.perfil.criterio]
    for formula in analisis.perfil.formulas:
        identificacion.extend([f"Fórmula: {formula}", leyenda_formula(formula), ""])
    yield "IDENTIFICACIÓN", [*identificacion, *("• " + s for s in analisis.perfil.supuestos)]
    desarrollo = []
    for indice, paso in enumerate(resultado.pasos, 1):
        desarrollo.append(f"Paso {indice}. {paso.titulo}")
        if paso.explicacion:
            desarrollo.append(paso.explicacion)
        desarrollo.extend([f"Fórmula: {paso.formula}", leyenda_formula(paso.formula), f"Sustitución: {paso.sustitucion}",
                           leyenda_sustitucion(paso.sustitucion),
                           f"Resultado: {valor_paso(paso, decimales)}", ""])
    yield "DESARROLLO", desarrollo
    yield "RESULTADOS", [*(f"{p.titulo}: {valor_paso(p, decimales)}" for p in indicadores_informe(resultado)),
                         "", resultado.interpretacion]


def formula_html(texto):
    """MathML local: conserva el texto original como etiqueta y no requiere JavaScript."""
    def construir(nodo):
        tipo = nodo[0]
        if tipo == "texto":
            token = nodo[1].strip()
            if token in ("=", "+", "−", "×"):
                return f"<mo>{token}</mo>"
            return f"<mtext>{escape(nodo[1])}</mtext>"
        if tipo == "fraccion":
            return f"<mfrac>{construir(nodo[1])}{construir(nodo[2])}</mfrac>"
        if tipo == "grupo":
            return f'<mrow><mo stretchy="true">{nodo[1]}</mo>{construir(nodo[2])}<mo stretchy="true">{nodo[3]}</mo></mrow>'
        return "<mrow>" + "".join(construir(n) for n in nodo[1:]) + "</mrow>"

    if "/" not in texto and "techo(" not in texto:
        return f"<code>{escape(texto)}</code>"
    return f'<math aria-label="{escape(texto)}">{construir(componer(texto))}</math>'


def grupos_explicacion(formula, sustitucion=""):
    """Agrupa los significados, sin repetir operaciones de fórmula y sustitución."""
    simbolos = elementos_formula(formula)
    claves = {clave for clave, _ in simbolos}
    operaciones = dict((*operadores_expresion(formula), *elementos_sustitucion(sustitucion)))
    return (("Elementos de la fórmula", simbolos),
            ("Operaciones y lectura", tuple((k, v) for k, v in operaciones.items() if k not in claves)))


def panel_formula_html(formula, sustitucion=None):
    """Panel adaptable: operación a la izquierda y tarjetas semánticas a la derecha."""
    grupos = []
    for titulo, elementos in grupos_explicacion(formula, sustitucion or ""):
        if elementos:
            tarjetas = "".join(f'<div><dt>{escape(k)}</dt><dd>{escape(v)}</dd></div>' for k, v in elementos)
            grupos.append(f'<section class="grupo-leyenda"><h4>{escape(titulo)}</h4><dl>{tarjetas}</dl></section>')
    reemplazo = (f'<div class="calculo"><h4>Sustitución</h4>{formula_html(sustitucion)}</div>'
                 if sustitucion is not None else "")
    return (f'<div class="desarrollo-grid"><div class="calculos"><div class="calculo">'
            f'<h4>Fórmula</h4>{formula_html(formula)}</div>{reemplazo}</div>'
            f'<aside class="leyenda-formula" aria-label="Explicación de los elementos">{"".join(grupos)}</aside></div>')


def informe_html(titulo, enunciado, analisis, resultado, decimales):
    datos = "".join(f"<section><h3>{escape(grupo)}</h3><dl>" +
                    "".join(f"<div><dt>{escape(k)}</dt><dd>{escape(v)}</dd></div>" for k, v in filas) +
                    "</dl></section>" for grupo, filas in analisis.grupos)
    supuestos = "".join(f"<li>{escape(s)}</li>" for s in analisis.perfil.supuestos)
    pasos = []
    for indice, paso in enumerate(resultado.pasos, 1):
        explicacion = f'<p>{escape(paso.explicacion)}</p>' if paso.explicacion else ""
        pasos.append(
            f'<li class="paso" id="paso-{indice}"><p class="rotulo">Paso {indice}</p>'
            f'<h3>{escape(paso.titulo)}</h3>{explicacion}'
            f'{panel_formula_html(paso.formula, paso.sustitucion)}'
            f'<p class="respuesta"><strong>Resultado:</strong> {escape(valor_paso(paso, decimales))}</p></li>'
        )
    indicadores = "".join(f'<div><dt>{escape(p.titulo)}</dt><dd>{escape(valor_paso(p, decimales))}</dd></div>'
                          for p in indicadores_informe(resultado))
    completo = []
    metodo = "".join(panel_formula_html(f) for f in analisis.perfil.formulas)
    for i, (nombre, lineas) in enumerate(secciones_informe(enunciado, analisis, resultado, decimales), 1):
        if nombre == "DESARROLLO":
            pasos_completos = "".join(p.replace(' id="paso-', ' id="completo-paso-', 1) for p in pasos)
            contenido = f'<ol class="pasos">{pasos_completos}</ol>'
        elif nombre == "IDENTIFICACIÓN":
            contenido = (f'<p>{escape(analisis.perfil.tipo)}</p><p>{escape(analisis.perfil.criterio)}</p>'
                         f'<ul class="supuestos">{supuestos}</ul>{metodo}')
        else:
            texto = escape("\n".join(lineas).strip())
            contenido = f'<p class="enunciado">{texto}</p>'
        completo.append(f'<section><h3>{i:02d} · {escape(nombre.title())}</h3>{contenido}</section>')
    grafico = ""
    if resultado.serie:
        limite = (sum(valor for _, valor in resultado.serie) if resultado.tipo_grafico == "composicion"
                  else max(valor for _, valor in resultado.serie))
        barras = []
        for nombre, valor in resultado.serie:
            ancho = valor / limite * 100 if limite else 0
            etiqueta = (numero(ancho, decimales) + " %" if resultado.tipo_grafico == "composicion"
                        else numero(valor, decimales) + " " + resultado.unidad_grafico)
            barras.append(f"<p>{escape(nombre)} · {escape(etiqueta)}<span class='pista'>"
                          f"<span class='barra' style='width:{ancho:.6f}%'></span></span></p>")
        grafico = f"<h3>{escape(resultado.titulo_grafico)}</h3>{''.join(barras)}"
    return f"""<!doctype html>
<html lang="es">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titulo)}</title>
<style>
* {{ box-sizing:border-box; }}
body {{ color:#14243d; background:#edf3fb; font:16px/1.6 system-ui,sans-serif; margin:0; }}
main {{ width:94%; max-width:104rem; margin:2rem auto; }}
header, main > section, main > details {{ background:white; border:1px solid #d1deee; border-radius:1rem;
  padding:clamp(1rem,3vw,2.5rem); margin-bottom:1.25rem; min-width:0; overflow-wrap:anywhere; }}
header {{ background:#182e50; color:white; }}
header a {{ color:#dceaff; }}
h1,h2,h3,p {{ margin:0 0 .7rem; }}
h4 {{ margin:0 0 .65rem; font-size:.9rem; color:#364766; }}
h1 {{ font-size:clamp(1.65rem,4vw,2.65rem); line-height:1.2; }}
nav {{ display:flex; flex-wrap:wrap; gap:.45rem 1.25rem; }}
.rotulo {{ font-size:.82rem; font-weight:700; letter-spacing:.06em; text-transform:uppercase; }}
.enunciado {{ white-space:pre-wrap; }}
.datos,.indicadores {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,19rem),1fr)); gap:.85rem 1.3rem; }}
dl {{ margin:0; }}
dl div {{ background:#eff5fd; border-radius:.5rem; padding:.55rem .85rem; margin-bottom:.3rem; }}
dt {{ color:#455b76; font-size:.9rem; }} dd {{ margin:0; font-weight:650; }}
.pasos {{ list-style:none; padding:0; margin:0; }}
.paso {{ border-top:1px solid #d1deee; padding:1.2rem 0; }}
.paso .rotulo {{ color:#075e68; }}
.desarrollo-grid {{ display:grid; grid-template-columns:minmax(0, 1fr) minmax(0, 1.25fr);
  gap:1.5rem; align-items:start; margin:1rem 0 1.4rem; }}
.calculos,.leyenda-formula {{ min-width:0; }}
.calculo {{ border:1px solid #a5b6d0; border-radius:.8rem; background:#f3f6fc;
  padding:1.15rem; margin-bottom:1rem; overflow-wrap:anywhere; }}
.grupo-leyenda {{ margin-bottom:1rem; }}
.grupo-leyenda dl div {{ display:grid; grid-template-columns:minmax(3rem, .24fr) minmax(0, 1fr);
  gap:.8rem; border:1px solid #a5b6d0; border-radius:.7rem; padding:.65rem .85rem; margin-bottom:.45rem; }}
.grupo-leyenda dt {{ color:#075e68; font-weight:750; font-size:1rem; }}
.grupo-leyenda dd {{ font-weight:400; font-size:.93rem; line-height:1.45; }}
@media (max-width:760px) {{ .desarrollo-grid {{ grid-template-columns:minmax(0,1fr); gap:.3rem; }} }}
code {{ font:1.13rem/1.55 "Cambria Math",Cambria,serif; white-space:pre-wrap; }}
math {{ font-size:1.3rem; max-width:100%; overflow-wrap:anywhere; }}
.respuesta {{ margin:.65rem 0 0; color:#105f45; background:#e0f5ec; padding:.45rem .8rem; border-radius:.45rem; }}
.indicadores div {{ background:#e0f5ec; }} .indicadores dd {{ color:#105f45; }}
.nota, .supuestos {{ background:#fff4dc; color:#79500f; border-radius:.5rem; padding:.7rem 1rem; }}
.nota p, .supuestos li {{ font-style:italic; }} .supuestos {{ padding-left:2rem; }} .nota {{ margin:1.2rem 0; }}
summary {{ cursor:pointer; font-size:1.25rem; font-weight:700; }}
.compilado section {{ margin-top:1.2rem; }}
@media print {{ body {{ background:white; }} main {{ margin:0; width:100%; }}
 nav, #informe-completo {{ display:none; }} header, main > section {{ padding:1rem 0; border:0; }}
  header {{ background:white; color:#14243d; }}
  .desarrollo-grid {{ grid-template-columns:minmax(0,1fr) minmax(0,1.25fr); gap:1rem; }}
  .calculo,.grupo-leyenda dl div,.respuesta {{ break-inside:avoid; }} }}
.pista,.barra {{ display:block; height:.55rem; border-radius:.25rem; print-color-adjust:exact; }}
.pista {{ background:#eaf1fb; margin-top:.3rem; }}
.barra {{ background:#164cca; }}
</style>
<main>
<header><p class="rotulo">DIROPE Calc · Informe del ejercicio</p><h1>{escape(titulo)}</h1>
<nav aria-label="Secciones del informe"><a href="#planteamiento">Planteamiento</a><a href="#datos">Datos</a>
<a href="#resolucion">Método</a><a href="#procedimiento">Paso a paso</a><a href="#resultados">Resultados</a>
<a href="#informe-completo">Informe completo</a></nav></header>
<section id="planteamiento"><h2>01 · Planteamiento</h2><p class="enunciado">{escape(enunciado or 'Sin enunciado registrado.')}</p></section>
<section id="datos"><h2>02 · Datos utilizados</h2><div class="datos">{datos}</div></section>
<section id="resolucion"><h2>03 · Método de resolución</h2><h3>{escape(analisis.perfil.tipo)}</h3>
<p>{escape(analisis.perfil.criterio)}</p><ul class="supuestos">{supuestos}</ul>{metodo}</section>
<section id="procedimiento"><h2>04 · Procedimiento paso a paso</h2><ol class="pasos">{''.join(pasos)}</ol></section>
<section id="resultados"><h2>05 · Resultados</h2><dl class="indicadores">{indicadores}</dl>
<aside class="nota"><h3>Interpretación</h3><p>{escape(resultado.interpretacion)}</p></aside>{grafico}</section>
<details id="informe-completo"><summary>Informe completo · lectura continua</summary><div class="compilado">{''.join(completo)}</div></details>
</main>
</html>
"""


def informe_pdf(ruta, titulo, enunciado, analisis, resultado, decimales):
    """Genera un PDF A4 a partir del mismo resultado que el informe HTML."""
    try:
        import reportlab
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import Flowable, LongTable, Paragraph, SimpleDocTemplate, Spacer
    except ImportError as error:
        raise PDFNoDisponible("La exportación directa a PDF no está disponible en este equipo.") from error

    fuentes = (
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "segoeui.ttf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path(reportlab.__file__).parent / "fonts" / "Vera.ttf",
    )
    fuente = next((p for p in fuentes if p.is_file()), None)
    if fuente is None:
        raise PDFNoDisponible("No hay una fuente compatible para generar el PDF.")
    pdfmetrics.registerFont(TTFont("DiropeInforme", str(fuente)))
    variantes = {"segoeui.ttf": ("segoeuib.ttf", "segoeuii.ttf"),
                 "DejaVuSans.ttf": ("DejaVuSans-Bold.ttf", "DejaVuSans-Oblique.ttf"),
                 "Arial.ttf": ("Arial Bold.ttf", "Arial Italic.ttf"), "Vera.ttf": ("VeraBd.ttf", "VeraIt.ttf")}
    negrita, cursiva = variantes[fuente.name]
    def registrar_variante(nombre, archivo):
        variante = fuente.with_name(archivo)
        if not variante.is_file():
            return "DiropeInforme"
        pdfmetrics.registerFont(TTFont(nombre, str(variante)))
        return nombre

    fuerte = registrar_variante("DiropeInformeNegrita", negrita)
    enfasis = registrar_variante("DiropeInformeCursiva", cursiva)
    normal = ParagraphStyle("Texto", fontName="DiropeInforme", fontSize=10, leading=15, spaceAfter=6,
                            textColor=colors.HexColor("#14243d"))
    encabezado = ParagraphStyle("Sección", parent=normal, fontName=fuerte, fontSize=13, leading=18,
                                textColor=colors.HexColor("#1648a8"), spaceBefore=10, keepWithNext=True)
    nota = ParagraphStyle("Nota", parent=normal, fontName=enfasis, textColor=colors.HexColor("#79500f"))
    respuesta = ParagraphStyle("Resultado", parent=normal, fontName=fuerte, textColor=colors.HexColor("#105f45"))
    principal = ParagraphStyle("Título", parent=encabezado, fontSize=18, leading=24)
    elementos = []

    def parrafo(valor, estilo=normal):
        elementos.append(Paragraph(escape(valor).replace("\n", "<br/>"), estilo))

    compacto = ParagraphStyle("Leyenda", parent=normal, fontSize=8.5, leading=12, spaceAfter=0)
    simbolo_estilo = ParagraphStyle("Símbolo", parent=compacto, fontName=fuerte,
                                    textColor=colors.HexColor("#075e68"))
    rotulo = ParagraphStyle("Rótulo", parent=compacto, fontName=fuerte, spaceAfter=7, keepWithNext=True)
    ancho_util = A4[0] - 88

    def panel_pdf(formula, sustitucion=None):
        ancho_izquierdo = ancho_util * .43
        ancho_derecho = ancho_util - ancho_izquierdo - 12
        izquierda, derecha = [], []
        for titulo_caja, expresion in (("Fórmula", formula), ("Sustitución", sustitucion)):
            if expresion is None:
                continue
            caja = LongTable([[[Paragraph(titulo_caja, rotulo), Paragraph(escape(expresion), normal)]]],
                             colWidths=[ancho_izquierdo - 12], splitInRow=1, cornerRadii=[6] * 4,
                             style=[("BOX", (0, 0), (-1, -1), .6, colors.HexColor("#a5b6d0")),
                                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f3f6fc")),
                                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10)])
            izquierda.extend([caja, Spacer(1, 10)])
        for titulo_grupo, filas in grupos_explicacion(formula, sustitucion or ""):
            if not filas:
                continue
            derecha.append(Paragraph(titulo_grupo, rotulo))
            for clave, descripcion in filas:
                caja = LongTable([[Paragraph(escape(clave), simbolo_estilo), Paragraph(escape(descripcion), compacto)]],
                                 colWidths=[58, ancho_derecho - 70], splitInRow=1, cornerRadii=[5] * 4,
                                 style=[("BOX", (0, 0), (-1, -1), .5, colors.HexColor("#a5b6d0")),
                                        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#eff5fd")),
                                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                        ("TOPPADDING", (0, 0), (-1, -1), 7),
                                        ("BOTTOMPADDING", (0, 0), (-1, -1), 7)])
                derecha.extend([caja, Spacer(1, 5)])
            derecha.append(Spacer(1, 7))
        elementos.append(LongTable([[izquierda, derecha]], colWidths=[ancho_izquierdo, ancho_derecho + 12],
                                   splitInRow=1, style=[("VALIGN", (0, 0), (-1, -1), "TOP"),
                                                       ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                                       ("RIGHTPADDING", (0, 0), (-1, -1), 12)]))
        elementos.append(Spacer(1, 10))

    parrafo(titulo, principal)
    parrafo("01 · Planteamiento", encabezado)
    if enunciado:
        parrafo(enunciado)
    parrafo("02 · Datos utilizados", encabezado)
    for grupo, filas in analisis.grupos:
        if not filas:
            continue
        parrafo(grupo, encabezado)
        celdas = [[Paragraph(escape(texto), normal) for texto in fila]
                  for fila in (("Dato", "Valor"), *filas)]
        tabla = LongTable(celdas, colWidths=(160, A4[0] - 260), repeatRows=1, splitInRow=1,
                          style=[("VALIGN", (0, 0), (-1, -1), "TOP"),
                                 ("GRID", (0, 0), (-1, -1), 0.35, colors.lightgrey)])
        elementos.append(tabla)
    parrafo("03 · Método de resolución", encabezado)
    parrafo(analisis.perfil.tipo)
    parrafo(analisis.perfil.criterio)
    for formula in analisis.perfil.formulas:
        panel_pdf(formula)
    for supuesto in analisis.perfil.supuestos:
        parrafo(supuesto, nota)
    parrafo("04 · Procedimiento principal", encabezado)
    for indice, paso in enumerate(resultado.pasos, 1):
        parrafo(f"Paso {indice}. {paso.titulo}", encabezado)
        if paso.explicacion:
            parrafo(paso.explicacion)
        panel_pdf(paso.formula, paso.sustitucion)
        parrafo(f"Resultado: {valor_paso(paso, decimales)}", respuesta)
    parrafo("05 · Resultados", encabezado)
    for paso in indicadores_informe(resultado):
        parrafo(f"{paso.titulo}: {valor_paso(paso, decimales)}", respuesta)
    parrafo("Interpretación", encabezado)
    parrafo(resultado.interpretacion, nota)

    class Barra(Flowable):
        def __init__(self, proporcion):
            super().__init__()
            self.proporcion = proporcion

        def wrap(self, ancho, alto):
            self.width, self.height = ancho, 14
            return ancho, self.height

        def draw(self):
            self.canv.setFillColor(colors.HexColor("#eaf1fb"))
            self.canv.rect(0, 4, self.width, 7, stroke=0, fill=1)
            self.canv.setFillColor(colors.HexColor("#164cca"))
            self.canv.rect(0, 4, self.width * self.proporcion, 7, stroke=0, fill=1)

    if resultado.serie:
        parrafo(resultado.titulo_grafico, encabezado)
        composicion = resultado.tipo_grafico == "composicion"
        valores = [valor for _, valor in resultado.serie]
        limite = sum(valores) if composicion else max(valores)
        etiqueta_grafico = ParagraphStyle("Serie", parent=normal, keepWithNext=True)
        for etiqueta, valor in resultado.serie:
            proporcion = valor / limite if limite else 0
            cifra = numero(proporcion * 100, decimales) + " %" if composicion else (
                numero(valor, decimales) + " " + resultado.unidad_grafico)
            parrafo(f"{etiqueta} · {cifra}", etiqueta_grafico)
            elementos.append(Barra(proporcion))
    try:
        with destino_atomico(ruta) as temporal:
            SimpleDocTemplate(str(temporal), pagesize=A4, title=titulo,
                              leftMargin=44, rightMargin=44, topMargin=44, bottomMargin=44).build(elementos)
    except Exception as error:
        raise RuntimeError(f"No se pudo generar el documento. {error}") from error
