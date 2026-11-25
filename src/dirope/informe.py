"""Informe HTML autocontenido y apto para imprimir desde el navegador."""

from html import escape

from .formato import numero


def informe_html(titulo, enunciado, analisis, resultado, decimales):
    datos = "".join(f"<tr><th scope='row'>{escape(k)}</th><td>{escape(v)}</td></tr>"
                    for k, v in analisis.datos)
    supuestos = "".join(f"<li>{escape(s)}</li>" for s in analisis.perfil.supuestos)
    pasos = []
    for paso in resultado.pasos:
        valor = numero(paso.resultado, 0 if paso.unidad == "personas" else decimales)
        pasos.append(
            f"<tr><th scope='row'>{escape(paso.titulo)}<br><small>{escape(paso.explicacion)}</small></th>"
            f"<td>{escape(paso.formula)}</td><td>{escape(paso.sustitucion)}</td>"
            f"<td>{escape(valor)} {escape(paso.unidad)}</td></tr>"
        )
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
        grafico = f"<h2>{escape(resultado.titulo_grafico)}</h2>{''.join(barras)}"
    return f"""<!doctype html>
<html lang="es">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titulo)}</title>
<style>
body {{ color:#112039; font:16px system-ui,sans-serif; margin:2rem auto; padding:0 1rem; max-width:68rem; }}
h2 {{ margin-top:2rem; }}
.enunciado {{ white-space:pre-wrap; }}
table {{ border-collapse:collapse; width:100%; }}
th,td {{ border:1px solid #d5deeb; padding:.6rem; text-align:left; overflow-wrap:anywhere; }}
thead th {{ background:#eaf1fb; }}
small {{ color:#526176; }}
.pista,.barra {{ display:block; height:.55rem; border-radius:.25rem; print-color-adjust:exact; }}
.pista {{ background:#eaf1fb; margin-top:.3rem; }}
.barra {{ background:#164cca; }}
</style>
<main>
<h1>{escape(titulo)}</h1>
<p class="enunciado">{escape(enunciado)}</p>
<h2>Datos utilizados</h2>
<table><tbody>{datos}</tbody></table>
<h2>{escape(analisis.perfil.tipo)}</h2>
<ul>{supuestos}</ul>
<h2>Procedimiento</h2>
<table><thead><tr><th scope="col">Cálculo</th><th scope="col">Fórmula</th><th scope="col">Sustitución</th>
<th scope="col">Resultado</th></tr></thead><tbody>{''.join(pasos)}</tbody></table>
<h2>Interpretación</h2><p>{escape(resultado.interpretacion)}</p>
{grafico}
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
        raise RuntimeError("Para exportar PDF instala ReportLab con python -m pip install -r requirements.txt.") from error

    fuentes = (
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "segoeui.ttf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path(reportlab.__file__).parent / "fonts" / "Vera.ttf",
    )
    fuente = next(p for p in fuentes if p.is_file())
    pdfmetrics.registerFont(TTFont("DiropeInforme", str(fuente)))
    normal = ParagraphStyle("Texto", fontName="DiropeInforme", fontSize=10, leading=15, spaceAfter=6)
    encabezado = ParagraphStyle("Sección", parent=normal, fontSize=13, leading=18,
                                spaceBefore=10, keepWithNext=True)
    principal = ParagraphStyle("Título", parent=encabezado, fontSize=18, leading=24)
    elementos = []

    def parrafo(valor, estilo=normal):
        elementos.append(Paragraph(escape(valor).replace("\n", "<br/>"), estilo))

    parrafo(titulo, principal)
    if enunciado:
        parrafo(enunciado)
    parrafo("Datos utilizados", encabezado)
    if analisis.datos:
        celdas = [[Paragraph(escape(texto), normal) for texto in fila]
                  for fila in (("Dato", "Valor"), *analisis.datos)]
        tabla = LongTable(celdas, colWidths=(160, A4[0] - 260), repeatRows=1, splitInRow=1,
                          style=[("VALIGN", (0, 0), (-1, -1), "TOP"),
                                 ("GRID", (0, 0), (-1, -1), 0.35, colors.lightgrey)])
        elementos.append(tabla)
    parrafo(analisis.perfil.tipo, encabezado)
    for supuesto in analisis.perfil.supuestos:
        parrafo(supuesto)
    for seccion, pasos in (("Procedimiento principal", resultado.procedimiento),
                           ("Detalle del cálculo", resultado.detalles)):
        if pasos:
            parrafo(seccion, encabezado)
        for paso in pasos:
            parrafo(paso.titulo, encabezado)
            if paso.explicacion:
                parrafo(paso.explicacion)
            parrafo(paso.formula)
            parrafo(paso.sustitucion)
            precision = 0 if paso.unidad == "personas" else decimales
            parrafo(f"Resultado · {numero(paso.resultado, precision)} {paso.unidad}")
    parrafo("Interpretación", encabezado)
    parrafo(resultado.interpretacion)

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
