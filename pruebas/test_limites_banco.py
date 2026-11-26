"""Límites no cubiertos por los valores moderados del banco generado."""

from copy import deepcopy
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dirope.banco import generar_banco
from dirope.modulos import MODULOS
from dirope.nucleo import validar_numero


class LimitesBanco(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.muestras = {(c["modulo"], c["datos"]["modo"]): c["datos"] for c in generar_banco(1)}
        cls.modulos = {m.clave: m for m in MODULOS}

    def test_espacios_decimales_notacion_cientifica_y_no_finitos(self):
        for entrada, valor in (("1 234.50", 1234.5), ("1\u00a0234.50", 1234.5),
                               ("1.2345e3", 1234.5), (" 0.00001 ", 0.00001), ("5e-324", 5e-324)):
            self.assertEqual(validar_numero(entrada, "Dato"), valor)
        for entrada in ("1,25", "1 23", "1.2 3", "", None, True, "NaN", "Inf", "-Inf", "1e9999"):
            with self.subTest(entrada=entrada), self.assertRaises(ValueError):
                validar_numero(entrada, "Dato")

    def test_desbordamientos_se_rechazan_sin_excepciones_aritmeticas(self):
        mutaciones = {
            ("un_factor", "Producción requerida"): dict(ritmo="1e308", insumo_antes="1e308"),
            ("un_factor", "Recurso requerido"): dict(antes="1e308", ritmo="5e-324"),
            ("un_factor", "Comparar escenarios"): dict(antes="1e-308", insumo_antes="1", despues="1e308", insumo_despues="1"),
            ("capacidad", "Crecimiento porcentual"): dict(actual="1e308", crecimiento="1e308"),
            ("capacidad", "Meta directa"): dict(meta="1e308", productividad="5e-324"),
            ("multifactor", "Valor por calidad"): dict(insumos=[dict(nombre="Categoría", cantidad="1e308", precio="1e308")]),
            ("multifactor", "Escenario individual"): dict(insumos=[dict(nombre="Costo", cantidad="1e308", precio="1e308")]),
        }
        for clave, cambios in mutaciones.items():
            with self.subTest(clave=clave), self.assertRaises(ValueError):
                self.modulos[clave[0]].calcular(dict(self.muestras[clave], **cambios))

    def test_calidad_bordes_y_medidas_invalidas(self):
        base = dict(self.muestras[("un_factor", "Comparar conformidad")], medida_calidad="%")
        modulo = self.modulos["un_factor"]
        for porcentaje in (0, 100):
            resultado = modulo.calcular(dict(base, defecto_antes=porcentaje, defecto_despues=porcentaje))
            self.assertTrue(all(math.isfinite(p.resultado) for p in resultado.pasos))
        for cambios in (dict(defecto_antes=100.0001), dict(defecto_despues=-0.01), dict(medida_calidad="otro"),
                         dict(medida_calidad=None), dict(medida_calidad="Cantidad", defecto_antes=1e9)):
            with self.subTest(cambios=cambios), self.assertRaises(ValueError):
                modulo.calcular(dict(base, **cambios))

    def test_filas_contradictorias_y_escenarios_incompletos(self):
        base = self.muestras[("multifactor", "Escenario individual")]
        modulo = self.modulos["multifactor"]
        for fila in (dict(nombre="", directo=1), dict(nombre="Costo", directo=0),
                     dict(nombre="Costo", directo=1, precio=1), dict(nombre="Costo", directo=1, moneda="AJENA"),
                     dict(nombre="Trabajo", cantidad=1, precio=1, unidad="kg", es_laboral=True),
                     dict(nombre="Trabajo", cantidad=0, precio=0, es_laboral=True)):
            with self.subTest(fila=fila), self.assertRaises(ValueError):
                modulo.calcular(dict(base, insumos=[fila]))
        comparar = deepcopy(self.muestras[("multifactor", "Comparar alternativas")])
        comparar["insumos"] = [f for f in comparar["insumos"] if f["escenario"] != "Alternativa"]
        with self.assertRaises(ValueError):
            modulo.calcular(comparar)

    def test_capacidad_limites_y_personal_fraccionario(self):
        modulo = self.modulos["capacidad"]
        base = self.muestras[("capacidad", "Meta directa")]
        for cambios in (dict(plantilla="0.5"), dict(horas=0), dict(productividad=0), dict(meta=-1), dict(periodo="")):
            with self.subTest(cambios=cambios), self.assertRaises(ValueError):
                modulo.calcular(dict(base, **cambios))
        for meta, personas in (("2.1", 7), ("2.10000000000000000001", 8), ("0", 0)):
            resultado = modulo.calcular(dict(base, meta=meta, productividad="0.3", horas="1"))
            paso = next(p for p in resultado.pasos if p.titulo == "Personal necesario")
            self.assertEqual(paso.resultado, personas)
