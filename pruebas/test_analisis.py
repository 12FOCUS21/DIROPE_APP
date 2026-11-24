"""Análisis de datos y problemas nuevos independientes de los ejemplos."""

import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dirope.analisis import PERFILES, analizar_datos, describir_ejemplo, validar_planteamiento
from dirope.modulos import MODULOS
from dirope.modulos.productividad import CAPACIDAD, MULTIFACTOR, UN_FACTOR


class Analisis(unittest.TestCase):
    def test_planteamiento_requerido(self):
        for enunciado, objetivo in (("", "Comparar"), ("Problema nuevo", " ")):
            with self.assertRaises(ValueError):
                validar_planteamiento(enunciado, objetivo)
        validar_planteamiento("Un taller compara sus procesos.", "Determinar el cambio de productividad.")

    def test_todos_los_ejemplos_se_analizan(self):
        for modulo in MODULOS:
            for datos in modulo.ejemplos.values():
                with self.subTest(modulo=modulo.clave):
                    copia = copy.deepcopy(datos)
                    analisis = analizar_datos(modulo.clave, datos)
                    self.assertTrue(analisis.datos)
                    self.assertTrue(analisis.perfil.formulas)
                    self.assertTrue(analisis.perfil.incognitas)
                    self.assertTrue(analisis.perfil.supuestos)
                    self.assertEqual(datos, copia)
                    self.assertTrue(describir_ejemplo(modulo.clave, datos))

    def test_perfiles_coinciden_con_las_herramientas(self):
        self.assertEqual(set(PERFILES), {m.clave for m in MODULOS})

    def test_problema_nuevo_un_factor(self):
        datos = dict(antes=240, despues=360, insumo_antes=30, insumo_despues=36, unidad="piezas/h")
        analisis = analizar_datos("un_factor", datos)
        self.assertIn(("Unidad de productividad", "piezas/h"), analisis.datos)
        resultado = UN_FACTOR.calcular(datos)
        self.assertEqual([p.resultado for p in resultado.pasos], [8, 10, 2, 25])

    def test_problema_nuevo_multifactor(self):
        datos = dict(produccion=420, insumos=[dict(nombre="Soldadura", cantidad=24, precio=15, es_laboral=True),
                                           dict(nombre="Acero", cantidad=70, precio=6, es_laboral=False)])
        analizar_datos("multifactor", datos)
        resultado = MULTIFACTOR.calcular(datos)
        self.assertAlmostEqual(resultado.pasos[-1].resultado, 420 / 780)
        self.assertEqual(len(resultado.pasos), 6)

    def test_problema_nuevo_personal(self):
        datos = dict(actual=2400, crecimiento=50, productividad=5, horas=120)
        analizar_datos("capacidad", datos)
        resultado = CAPACIDAD.calcular(datos)
        self.assertEqual(resultado.pasos[0].resultado, 3600)
        self.assertEqual(resultado.pasos[6].resultado, 6)
        self.assertEqual(resultado.pasos[-1].resultado, 2)

    def test_campos_incompletos_no_se_identifican_como_validos(self):
        for clave, datos in (("un_factor", {}), ("capacidad", {}), ("multifactor", {"produccion": 10})):
            with self.subTest(clave=clave), self.assertRaises(ValueError):
                analizar_datos(clave, datos)

    def test_unidad_vacia_y_denominadores_nulos(self):
        base = dict(antes=10, despues=20, insumo_antes=2, insumo_despues=2, unidad="u/h")
        for cambio in (dict(unidad=" "), dict(insumo_antes=0), dict(antes=0), dict(insumo_despues=-1)):
            with self.assertRaises(ValueError):
                analizar_datos("un_factor", dict(base, **cambio))

    def test_invalida_filas_laborales_sin_horas(self):
        datos = dict(produccion=100, insumos=[dict(nombre="Horas", cantidad=0, precio=10, es_laboral=True),
                                            dict(nombre="Otros", cantidad=1, precio=100, es_laboral=False)])
        with self.assertRaises(ValueError):
            analizar_datos("multifactor", datos)
        datos["insumos"][0]["es_laboral"] = "no"
        with self.assertRaises(ValueError):
            analizar_datos("multifactor", datos)

    def test_tipo_no_disponible(self):
        with self.assertRaises(ValueError):
            analizar_datos("inventarios", {})
        with self.assertRaises(ValueError):
            describir_ejemplo("inventarios", {})
