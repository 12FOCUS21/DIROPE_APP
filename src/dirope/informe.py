"""Informe HTML autocontenido y apto para imprimir desde el navegador."""

from html import escape

from .formato import numero
from .notacion import componer


class PDFNoDisponible(RuntimeError):
    """El motor opcional de exportación no está disponible en este Python."""


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
    yield "IDENTIFICACIÓN", [analisis.perfil.tipo, analisis.perfil.criterio,
                            *("• " + s for s in analisis.perfil.supuestos)]
    desarrollo = []
    for indice, paso in enumerate(resultado.pasos, 1):
        desarrollo.append(f"Paso {indice}. {paso.titulo}")
        if paso.explicacion:
            desarrollo.append(paso.explicacion)
        desarrollo.extend([f"Fórmula: {paso.formula}", f"Sustitución: {paso.sustitucion}",
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
            f'<div class="operacion"><p><span>Fórmula</span>{formula_html(paso.formula)}</p>'
            f'<p><span>Sustitución</span>{formula_html(paso.sustitucion)}</p></div>'
            f'<p class="respuesta"><strong>Resultado:</strong> {escape(valor_paso(paso, decimales))}</p></li>'
        )
    indicadores = "".join(f'<div><dt>{escape(p.titulo)}</dt><dd>{escape(valor_paso(p, decimales))}</dd></div>'
                          for p in indicadores_informe(resultado))
    completo = []
    for i, (nombre, lineas) in enumerate(secciones_informe(enunciado, analisis, resultado, decimales), 1):
        if nombre == "DESARROLLO":
            pasos_completos = "".join(p.replace(' id="paso-', ' id="completo-paso-', 1) for p in pasos)
            contenido = f'<ol class="pasos">{pasos_completos}</ol>'
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
.operacion {{ padding:.7rem 1rem; border-left:3px solid #789dd9; background:#f2f6fc; }}
.operacion p:last-child {{ margin:0; }}
.operacion span {{ display:block; font-size:.86rem; font-weight:700; color:#455b76; }}
code {{ font:1.13rem/1.55 "Cambria Math",Cambria,serif; white-space:pre-wrap; }}
math {{ font-size:1.15rem; max-width:100%; }} .operacion p {{ overflow-x:auto; }}
.respuesta {{ margin:.65rem 0 0; color:#105f45; background:#e0f5ec; padding:.45rem .8rem; border-radius:.45rem; }}
.indicadores div {{ background:#e0f5ec; }} .indicadores dd {{ color:#105f45; }}
.nota, .supuestos {{ background:#fff4dc; color:#79500f; border-radius:.5rem; padding:.7rem 1rem; }}
.nota p, .supuestos li {{ font-style:italic; }} .supuestos {{ padding-left:2rem; }} .nota {{ margin:1.2rem 0; }}
summary {{ cursor:pointer; font-size:1.25rem; font-weight:700; }}
.compilado section {{ margin-top:1.2rem; }}
@media print {{ body {{ background:white; }} main {{ margin:0; width:100%; }}
 nav, #informe-completo {{ display:none; }} header, main > section {{ padding:1rem 0; border:0; }}
 header {{ background:white; color:#14243d; }} .paso {{ break-inside:avoid; }} }}
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
<p>{escape(analisis.perfil.criterio)}</p><ul class="supuestos">{supuestos}</ul></section>
<section id="procedimiento"><h2>04 · Procedimiento paso a paso</h2><ol class="pasos">{''.join(pasos)}</ol></section>
<section id="resultados"><h2>05 · Resultados</h2><dl class="indicadores">{indicadores}</dl>
<aside class="nota"><h3>Interpretación</h3><p>{escape(resultado.interpretacion)}</p></aside>{grafico}</section>
<details id="informe-completo"><summary>Informe completo · lectura continua</summary><div class="compilado">{''.join(completo)}</div></details>
</main>
</html>
"""


def informe_pdf(ruta, titulo, enunciado, analisis, resultado, decimales):
    """Genera un PDF A4 a partir del mismo resultado que el informe HTML."""
    from pathlib import Path
    import os

    try:
        import reportlab
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import Flowable, LongTable, Paragraph, SimpleDocTemplate
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
    for supuesto in analisis.perfil.supuestos:
        parrafo(supuesto, nota)
    parrafo("04 · Procedimiento principal", encabezado)
    for indice, paso in enumerate(resultado.pasos, 1):
        parrafo(f"Paso {indice}. {paso.titulo}", encabezado)
        if paso.explicacion:
            parrafo(paso.explicacion)
        parrafo(f"Fórmula: {paso.formula}")
        parrafo(f"Sustitución: {paso.sustitucion}")
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
        SimpleDocTemplate(str(ruta), pagesize=A4, title=titulo,
                          leftMargin=44, rightMargin=44, topMargin=44, bottomMargin=44).build(elementos)
    except Exception as error:
        raise RuntimeError(f"No se pudo generar el documento. {error}") from error
