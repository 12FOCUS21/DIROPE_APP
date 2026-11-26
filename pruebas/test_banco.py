"""Mil ejercicios y mutaciones inválidas con resultados de referencia independientes."""

from collections import Counter
from copy import deepcopy
import json
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dirope.banco import generar_banco
from dirope.modulos import MODULOS


class Banco(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.casos = generar_banco()
        cls.modulos = {m.clave: m for m in MODULOS}

    def test_cien_por_cada_uno_de_los_diez_modos(self):
        conteos = Counter((c["modulo"], c["datos"]["modo"]) for c in self.casos)
        self.assertEqual(len(self.casos), 1000)
        self.assertEqual(len(conteos), 10)
        self.assertEqual(set(conteos.values()), {100})
        self.assertEqual(self.casos, generar_banco())
        for cantidad in (0, -1, True, 1.5, "100"):
            with self.assertRaises(ValueError):
                generar_banco(cantidad)

    def test_mil_resultados_independientes_y_finitos(self):
        for caso in self.casos:
            with self.subTest(caso=caso["nombre"]):
                resultado = self.modulos[caso["modulo"]].calcular(caso["datos"])
                pasos = {p.titulo: p.resultado for p in resultado.pasos}
                for titulo, valor in caso["esperados"].items():
                    self.assertTrue(math.isclose(pasos[titulo], valor, rel_tol=1e-10, abs_tol=1e-8), (titulo, pasos[titulo], valor))
                self.assertTrue(all(math.isfinite(p.resultado) for p in resultado.pasos))
                json.dumps(caso, allow_nan=False)

    def test_mutaciones_invalidas_de_todos_los_campos_numericos(self):
        campos = {"antes", "despues", "insumo_antes", "insumo_despues", "ritmo", "defecto_antes", "defecto_despues",
                  "produccion", "produccion_final", "produccion_otra", "horas_calidad", "actual", "crecimiento",
                  "meta", "productividad", "horas", "plantilla"}
        for caso in self.casos:
            modulo = self.modulos[caso["modulo"]]
            for campo in campos.intersection(caso["datos"]):
                # Las magnitudes opcionales vacías no se usan en el cálculo.
                if not str(caso["datos"][campo]).strip():
                    continue
                invalidos = ["texto", "NaN", "Infinity", "-Infinity", True]
                invalidos += [-101] if campo == "crecimiento" else [-1]
                if campo not in ("actual", "plantilla", "produccion_otra"):
                    invalidos.append("")
                for valor in invalidos:
                    with self.subTest(caso=caso["nombre"], campo=campo, valor=valor), self.assertRaises(ValueError):
                        modulo.calcular(dict(caso["datos"], **{campo: valor}))

    def test_mutaciones_de_filas_y_denominadores(self):
        for caso in self.casos:
            modulo = self.modulos[caso["modulo"]]
            datos = caso["datos"]
            for campo in ("insumo_antes", "insumo_despues", "horas_calidad", "productividad", "horas"):
                if campo not in datos:
                    continue
                with self.subTest(caso=caso["nombre"], cero=campo), self.assertRaises(ValueError):
                    modulo.calcular(dict(datos, **{campo: 0}))
            if datos["modo"] == "Recurso requerido":
                with self.assertRaises(ValueError):
                    modulo.calcular(dict(datos, ritmo=0))
            for fila in datos.get("insumos", [])[:1]:
                for campo in ("cantidad", "precio", "directo"):
                    if campo not in fila:
                        continue
                    for valor in ("", "error", "nan", "inf", -1, True):
                        mutado = deepcopy(datos)
                        mutado["insumos"][0][campo] = valor
                        with self.subTest(caso=caso["nombre"], fila=campo, valor=valor), self.assertRaises(ValueError):
                            modulo.calcular(mutado)
