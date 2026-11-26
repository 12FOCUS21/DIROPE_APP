"""Comprueba indicadores, composición matemática y organización del banco."""

import json
from pathlib import Path
import sys
import unittest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from dirope.banco import generar_banco
from dirope.interfaz.componentes import (
    ACENTO, FONDO, NOCHE, PRIMARIO, SECUNDARIO, SUPERFICIE, TEXTO, TEXTO_SOBRE_OSCURO,
    resumen_resultado,
)
from dirope.interfaz.matematicas import componer
from dirope.modulos.campos import MODOS, grupos_datos
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

    def test_precedencia_de_porcentaje_y_fraccion(self):
        formula = componer("Δ% = (final − inicial) / inicial × 100")
        self.assertEqual(formula[:3], ("fila", ("texto", "Δ%"), ("texto", " = ")))
        operacion = formula[3]
        self.assertEqual(operacion[1][0], "fraccion")
        self.assertEqual(operacion[1][2], ("texto", "inicial"))
        self.assertEqual(operacion[2:], (("texto", " × "), ("texto", "100")))

    def test_techo_y_divisiones_encadenadas(self):
        formula = componer("techo((Meta − Q) / P / jornada)")
        self.assertEqual(formula[:2], ("grupo", "⌈"))
        self.assertEqual(formula[-1], "⌉")
        self.assertEqual(formula[2][0], "fraccion")
        self.assertEqual(formula[2][1][0], "fraccion")
        self.assertEqual(componer("1e+20 / 3")[1], ("texto", "1e+20"))

    def test_todos_los_campos_se_agrupan_sin_repeticiones(self):
        for modulo, modos in MODOS.items():
            for modo, esperados in modos.items():
                with self.subTest(modo=modo):
                    grupos = list(grupos_datos(modulo, modo))
                    visibles = [campo for _, campos in grupos for campo in campos]
                    self.assertCountEqual(visibles, esperados)
                    self.assertTrue(all(campos for _, campos in grupos))

    def test_banco_reproducible_con_texto_y_datos_separados(self):
        archivo = RAIZ / "ejemplos" / "banco_generado.json"
        casos = generar_banco()
        self.assertEqual(json.loads(archivo.read_text(encoding="utf-8"))["casos"], casos)
        self.assertEqual(len({c["enunciado"] for c in casos}), 40)
        for caso in casos:
            self.assertNotIn("Datos:", caso["enunciado"])
            self.assertIn("modo", caso["datos"])
