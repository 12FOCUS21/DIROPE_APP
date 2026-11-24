"""Comprueba que los indicadores y gráficos no mezclen magnitudes."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dirope.interfaz.componentes import (
    ACENTO, FONDO, NOCHE, PRIMARIO, SECUNDARIO, SUPERFICIE, TEXTO, TEXTO_SOBRE_OSCURO,
    resumen_resultado,
)
from dirope.modulos.productividad import CAPACIDAD, MULTIFACTOR, UN_FACTOR


class Presentacion(unittest.TestCase):
    def test_un_factor_compara_la_misma_unidad(self):
        resultado = UN_FACTOR.calcular(UN_FACTOR.ejemplos["Chuck Sox (T1)"])
        indicadores, serie, unidad, titulo = resumen_resultado("un_factor", resultado)
        self.assertEqual(serie, [("Antes", 3), ("Después", 3.125)])
        self.assertEqual(unidad, "cajas/h")
        self.assertEqual(indicadores[-1].unidad, "%")
        self.assertTrue(titulo)

    def test_capacidad_presenta_personas_enteras(self):
        resultado = CAPACIDAD.calcular(CAPACIDAD.ejemplos["Lackey (T5)"])
        indicadores, serie, unidad, _ = resumen_resultado("capacidad", resultado)
        self.assertEqual(serie, [("Actual", 4), ("Necesario", 5)])
        self.assertEqual(unidad, "personas")
        self.assertEqual(indicadores[-1].resultado, 1)

    def test_multifactor_no_mezcla_costos_con_productividad(self):
        resultado = MULTIFACTOR.calcular(MULTIFACTOR.ejemplos["Kleen Karpet (T3)"])
        indicadores, serie, unidad, _ = resumen_resultado("multifactor", resultado)
        self.assertEqual(unidad, "$")
        self.assertEqual(sum(valor for _, valor in serie), 8260)
        self.assertEqual(indicadores[-1].unidad, "unidades/h")

    def test_agrupa_insumos_sin_perder_costo(self):
        datos = dict(produccion=100, insumos=[dict(nombre=f"Insumo {i}", cantidad=1, precio=i) for i in range(1, 8)])
        resultado = MULTIFACTOR.calcular(datos)
        indicadores, serie, _, _ = resumen_resultado("multifactor", resultado)
        self.assertEqual(len(serie), 5)
        self.assertEqual(serie[-1], ("Otros insumos", 6))
        self.assertEqual(sum(v for _, v in serie), 28)
        self.assertEqual(len(indicadores), 2)

    def test_contraste_de_textos_principales(self):
        # Fórmula de luminancia relativa sRGB de WCAG; no sustituye una auditoría completa.
        def luminancia(color):
            canales = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
            lineales = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in canales]
            return sum(c * peso for c, peso in zip(lineales, (0.2126, 0.7152, 0.0722)))

        for texto, fondo in ((TEXTO, FONDO), (SECUNDARIO, FONDO), (SECUNDARIO, SUPERFICIE),
                             (PRIMARIO, SUPERFICIE), (SUPERFICIE, PRIMARIO), (SUPERFICIE, NOCHE),
                             (ACENTO, SUPERFICIE), (TEXTO_SOBRE_OSCURO, NOCHE)):
            claro, oscuro = sorted((luminancia(texto), luminancia(fondo)), reverse=True)
            with self.subTest(texto=texto, fondo=fondo):
                self.assertGreaterEqual((claro + 0.05) / (oscuro + 0.05), 4.5)
