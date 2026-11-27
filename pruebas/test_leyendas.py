"""Leyendas de símbolos y su presencia en los informes."""

from pathlib import Path
from types import SimpleNamespace
from tempfile import TemporaryDirectory
from unittest.mock import patch
import re
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dirope.banco import generar_banco
from dirope.informe import informe_html, secciones_informe, grupos_explicacion, panel_formula_html
from dirope.analisis import PERFILES, analizar_datos
from dirope.informe import informe_pdf
from dirope.leyendas import ELEMENTOS, elementos_formula, leyenda_formula, leyenda_sustitucion, operadores_expresion
from dirope.modulos import MODULOS
from dirope.practica_inicial import casos_practica, resolver_caso


class Leyendas(unittest.TestCase):
    def test_productividad_en_orden_sin_repetir(self):
        self.assertEqual([k for k, _ in elementos_formula("P = Q / I")], ["P", "Q", "I"])
        self.assertEqual([k for k, _ in elementos_formula("Δ% = (final − inicial) / inicial × 100")],
                         ["Δ%", "final", "inicial", "100"])

    def test_no_confunde_simbolos_compuestos(self):
        for formula, claves in (
            ("PM = Q / C", ["PM", "Q", "C"]),
            ("P₀ = Q₀ / I₀", ["P₀", "Q₀", "I₀"]),
            ("P = Q conforme / I", ["P", "Q conforme", "I"]),
            ("C = Σ Cᵢ", ["C", "Σ", "Cᵢ"]),
            ("PL$ = Q / costo laboral", ["PL$", "Q", "costo laboral"]),
            ("N₁ entero = ajuste(N₁)", ["N₁ entero", "ajuste", "N₁"]),
        ):
            with self.subTest(formula=formula):
                self.assertEqual([k for k, _ in elementos_formula(formula)], claves)
        self.assertEqual(elementos_formula("PALABRA"), ())
        self.assertEqual(leyenda_formula(""), "")

    def test_cubre_formulas_del_banco_y_ejemplos_originales(self):
        modulos = {m.clave: m for m in MODULOS}
        resultados = [modulos[c["modulo"]].calcular(c["datos"]) for c in generar_banco()]
        resultados.extend(m.calcular(datos) for m in MODULOS for datos in m.ejemplos.values())
        for resultado in resultados:
            for paso in resultado.pasos:
                with self.subTest(formula=paso.formula):
                    self.assertTrue(elementos_formula(paso.formula))
                    self.assertTrue(all(texto for _, texto in elementos_formula(paso.formula)))

    def test_informe_texto_y_html_incluyen_leyendas(self):
        caso = generar_banco(1)[0]
        modulo = next(m for m in MODULOS if m.clave == caso["modulo"])
        resultado = modulo.calcular(caso["datos"])
        analisis = SimpleNamespace(grupos=(), perfil=SimpleNamespace(
            objetivo="Prueba", tipo="Productividad", criterio="Prueba", supuestos=(), formulas=("P = Q / I",)))
        texto = "\n".join(linea for _, lineas in secciones_informe("", analisis, resultado, 6) for linea in lineas)
        html = informe_html("Prueba", "", analisis, resultado, 6)
        for contenido in (texto, html):
            self.assertIn("Elementos de la fórmula", contenido)
        self.assertIn("Q: Cantidad producida", texto)
        self.assertIn("<dt>Q</dt><dd>Cantidad producida", html)
        self.assertIn('class="desarrollo-grid"', html)
        self.assertIn('class="leyenda-formula"', html)
        self.assertIn("@media print", html)

    def test_panel_agrupa_sin_repetir_y_escapa_contenido(self):
        grupos = grupos_explicacion("N = techo(H / jornada)", "techo(100 / 3)")
        claves = [clave for _, filas in grupos for clave, _ in filas]
        self.assertEqual(len(claves), len(set(claves)))
        self.assertIn("techo", claves)
        self.assertNotIn("100", claves)
        html = panel_formula_html("P = Q / I", '<script>alert("x")</script>')
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_cada_elemento_de_cada_formula_tiene_descripcion(self):
        formulas = {f for perfil in PERFILES.values() for f in perfil.formulas}
        modulos = {m.clave: m for m in MODULOS}
        resultados = [modulos[c["modulo"]].calcular(c["datos"]) for c in generar_banco()]
        resultados.extend(m.calcular(datos) for m in MODULOS for datos in m.ejemplos.values())
        formulas.update(p.formula for r in resultados for p in r.pasos)
        patron = re.compile(r"(?<![\w$])(?:" + "|".join(
            re.escape(c) for c in sorted(ELEMENTOS, key=len, reverse=True)) + r")(?![\w$])")
        for formula in formulas:
            with self.subTest(formula=formula):
                resto = patron.sub("", formula)
                # La conjunción «o» no es una variable ni una operación matemática.
                resto = re.sub(r"\bo\b", "", resto)
                resto = re.sub(r"[\s=+−×/()%]", "", resto)
                self.assertEqual(resto, "", "Hay elementos sin explicar")

    def test_operadores_y_sustituciones_no_confunden_cifras_con_constantes(self):
        self.assertEqual([k for k, _ in operadores_expresion("(12 + 3) / 5 = 3")],
                         ["(…)", "+", "/", "="])
        self.assertIn("techo:", leyenda_sustitucion("techo(100 / 3)"))
        self.assertNotIn("100:", leyenda_sustitucion("techo(100 / 3)"))
        self.assertNotIn("1:", leyenda_sustitucion("1 × 40"))
        self.assertEqual(leyenda_sustitucion("125"), "")
        self.assertIn("1:", leyenda_formula("Meta = Q × (1 + g / 100)"))
        self.assertIn("precio unitario:", leyenda_formula("Cᵢ = cantidad × precio unitario"))
        self.assertIn("horas por persona:", leyenda_formula("N = H / horas por persona"))

    def test_calidad_distingue_cantidad_y_porcentaje(self):
        self.assertEqual(dict(elementos_formula("Q conforme = Q − defectos"))["defectos"],
                         "Cantidad de unidades no conformes.")
        self.assertIn("Porcentaje", dict(elementos_formula("Q conforme = Q × (1 − defectos / 100)"))["defectos"])

    def test_practica_inicial_contiene_leyendas(self):
        for caso in casos_practica():
            with self.subTest(caso=caso["nombre"]):
                informe = resolver_caso(caso)["informe"]
                self.assertIn("Elementos de la fórmula", informe)
                self.assertIn("Elementos de la expresión", informe)

    def test_pdf_incluye_explicaciones(self):
        try:
            from reportlab.platypus import Paragraph
        except ImportError:
            self.skipTest("ReportLab opcional no instalado")
        caso = generar_banco(1)[0]
        modulo = next(m for m in MODULOS if m.clave == caso["modulo"])
        resultado = modulo.calcular(caso["datos"])
        analisis = analizar_datos(caso["modulo"], caso["datos"], resultado=resultado)
        with TemporaryDirectory() as carpeta, patch("reportlab.platypus.Paragraph", wraps=Paragraph) as parrafo:
            ruta = Path(carpeta) / "leyendas.pdf"
            informe_pdf(ruta, "Prueba", caso["enunciado"], analisis, resultado, 6)
            self.assertTrue(ruta.read_bytes().startswith(b"%PDF"))
            textos = [llamada.args[0] for llamada in parrafo.call_args_list]
            self.assertIn("Elementos de la fórmula", textos)
            self.assertIn("Operaciones y lectura", textos)

    def test_exportaciones_de_todos_los_modos_y_ejemplos(self):
        try:
            import reportlab
        except ImportError:
            self.skipTest("ReportLab opcional no instalado")
        modulos = {m.clave: m for m in MODULOS}
        casos = [(c["modulo"], c["datos"]) for c in generar_banco(1)]
        casos.extend((m.clave, datos) for m in MODULOS for datos in m.ejemplos.values())
        self.assertEqual(len({(clave, datos["modo"]) for clave, datos in casos if "modo" in datos}), 10)
        with TemporaryDirectory() as carpeta:
            for indice, (clave, datos) in enumerate(casos):
                with self.subTest(modulo=clave, modo=datos.get("modo", "Original")):
                    resultado = modulos[clave].calcular(datos)
                    analisis = analizar_datos(clave, datos, resultado=resultado)
                    html = informe_html("Prueba <segura>", "Texto & datos", analisis, resultado, 8)
                    self.assertIn("Prueba &lt;segura&gt;", html)
                    self.assertIn("Texto &amp; datos", html)
                    self.assertIn('class="desarrollo-grid"', html)
                    ruta = Path(carpeta) / f"informe_{indice}.pdf"
                    informe_pdf(ruta, "Prueba", "Texto & datos", analisis, resultado, 8)
                    pdf = ruta.read_bytes()
                    self.assertTrue(pdf.startswith(b"%PDF-"))
                    self.assertTrue(pdf.rstrip().endswith(b"%%EOF"))

    def test_pdf_pagina_explicaciones_mas_largas_que_una_hoja(self):
        try:
            import reportlab
        except ImportError:
            self.skipTest("ReportLab opcional no instalado")
        caso = generar_banco(1)[0]
        modulo = next(m for m in MODULOS if m.clave == caso["modulo"])
        resultado = modulo.calcular(caso["datos"])
        analisis = analizar_datos(caso["modulo"], caso["datos"], resultado=resultado)
        with TemporaryDirectory() as carpeta, patch.dict(ELEMENTOS, {"Q": "Cantidad producida. " * 300}):
            ruta = Path(carpeta) / "explicacion_extensa.pdf"
            informe_pdf(ruta, "Prueba extensa", "", analisis, resultado, 6)
            self.assertTrue(ruta.read_bytes().rstrip().endswith(b"%%EOF"))


if __name__ == "__main__":
    unittest.main()
