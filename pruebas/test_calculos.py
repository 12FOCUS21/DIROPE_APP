"""Regresión de los seis casos y validaciones, sin dependencias externas."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dirope import nucleo as n
from dirope.formato import numero
from dirope.modelos import Insumo
from dirope.modulos import MODULOS
from dirope.modulos.productividad import CAPACIDAD, MULTIFACTOR, UN_FACTOR


class CasosAceptacion(unittest.TestCase):
    def assertCerca(self, actual, esperado):
        self.assertAlmostEqual(actual, esperado, delta=max(abs(esperado) * 1e-4, 1e-10))

    def test_t1_chuck(self):
        self.assertEqual(n.productividad(120, 40), 3)
        self.assertEqual(n.productividad(125, 40), 3.125)
        self.assertEqual(3.125 - 3, 0.125)
        self.assertCerca(n.cambio_pct(3, 3.125), 4.1667)

    def test_t2_lori(self):
        self.assertEqual(n.productividad(100, 5), 20)
        self.assertEqual(n.productividad(133, 5), 26.6)
        self.assertCerca(n.cambio_pct(20, 26.6), 33)

    def test_t3_kleen(self):
        insumos = [Insumo("Horas", 520, 13, True), Insumo("Galones", 100, 5), Insumo("Equipo", 20, 50)]
        self.assertEqual([i.cantidad * i.precio for i in insumos], [6760, 500, 1000])
        self.assertEqual(n.costo_total(insumos), 8260)
        self.assertEqual(n.productividad(65, 520), 0.125)
        self.assertCerca(n.productividad(65, 6760), 0.0096154)
        self.assertCerca(n.multifactor(65, insumos), 0.0078692)

    def test_t4_lakefront(self):
        inicial = [Insumo("Horas", 400, 12.5, True), Insumo("Materia", 1, 20000),
                   Insumo("Energía", 1, 5000), Insumo("Capital", 1, 10000)]
        nuevo = [inicial[0], inicial[1], Insumo("Energía", 1, 4000), inicial[3]]
        self.assertEqual(n.productividad(1000, 400), 2.5)
        self.assertEqual(n.costo_total(inicial), 40000)
        self.assertEqual(n.costo_total(nuevo), 39000)
        self.assertEqual(n.multifactor(1000, inicial), 0.025)
        self.assertCerca(n.multifactor(1000, nuevo), 0.025641)
        self.assertCerca(n.cambio_pct(n.multifactor(1000, inicial), n.multifactor(1000, nuevo)), 2.5641)

    def test_t5_lackey(self):
        meta = 1500 * 1.25
        self.assertEqual(meta, 1875)
        h0, h1 = n.horas_necesarias(1500, 2.344), n.horas_necesarias(meta, 2.344)
        self.assertCerca(h0, 639.93)
        self.assertCerca(h1, 799.915)
        p0, p1 = n.personas_necesarias(h0, 160), n.personas_necesarias(h1, 160)
        self.assertCerca(p0, 3.9996)
        self.assertCerca(p1, 4.9995)
        self.assertEqual((n.personal_entero(p0), n.personal_entero(p1)), (4, 5))

    def test_t6_placas_solo_nucleo(self):
        # El módulo gráfico de calidad todavía no está implementado.
        b0, b1 = n.unidades_buenas(800, 6), n.unidades_buenas(800, 2)
        self.assertEqual((b0, b1), (752, 784))
        base = [Insumo("Horas", 160, 10), Insumo("Componentes", 1, 12000), Insumo("Energía", 1, 400)]
        i0, i1 = base + [Insumo("Otros", 1, 1000)], base + [Insumo("Otros", 1, 1300)]
        self.assertEqual((n.costo_total(i0), n.costo_total(i1)), (15000, 15300))
        p0, p1 = n.multifactor(b0, i0), n.multifactor(b1, i1)
        self.assertCerca(p0, 0.0501333333)
        self.assertCerca(p1, 0.0512418301)
        self.assertCerca(n.cambio_pct(p0, p1), 2.2111)
        self.assertEqual((n.productividad(b0, 160), n.productividad(b1, 160)), (4.7, 4.9))
        self.assertCerca(n.cambio_pct(4.7, 4.9), 4.2553)


class Validaciones(unittest.TestCase):
    def test_entradas_invalidas(self):
        for valor in ("", " ", "hola", "2,5", "nan", "inf", "-inf", -1, True, None, "1 2", "12 34", "1. 5"):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                n.validar_numero(valor, "Dato")

    def test_entradas_validas(self):
        for valor in ("1500", "1 500", "1\u00a0500", " 1500 ", 1500):
            self.assertEqual(n.validar_numero(valor, "Dato"), 1500)
        self.assertEqual(n.validar_numero("1 500.25", "Dato"), 1500.25)

    def test_denominadores_invalidos(self):
        for divisor in (0, -1):
            for funcion in (n.productividad, n.horas_necesarias, n.personas_necesarias):
                with self.subTest(funcion=funcion.__name__, divisor=divisor), self.assertRaises(ValueError):
                    funcion(100, divisor)
        with self.assertRaises(ValueError):
            n.cambio_pct(0, 10)

    def test_costos_invalidos(self):
        for insumos in ([], [Insumo("", 1, 1)], [Insumo("X", -1, 1)],
                        [Insumo("X", 1, -1)], [Insumo("X", 0, 2)]):
            with self.subTest(insumos=insumos), self.assertRaises(ValueError):
                n.costo_total(insumos)

    def test_porcentajes_defectos(self):
        self.assertEqual(n.unidades_buenas(10, 0), 10)
        self.assertEqual(n.unidades_buenas(10, 100), 0)
        for porcentaje in (-1, 101):
            with self.assertRaises(ValueError):
                n.unidades_buenas(10, porcentaje)

    def test_desbordamientos(self):
        with self.assertRaises(ValueError):
            n.productividad(1e308, 1e-308)
        with self.assertRaises(ValueError):
            n.costo_total([Insumo("X", 1e308, 1e308)])
        with self.assertRaises(ValueError):
            n.cambio_pct(1e-308, 1e308)

    def test_tolerancia_personal(self):
        for valor, esperado in ((3.9996, 4), (4.9995, 5), (5.0001, 5), (5.01, 5),
                                (5.0101, 6), (4.5, 5), (0.001, 1), (0, 0)):
            self.assertEqual(n.personal_entero(valor), esperado)

    def test_formato(self):
        self.assertEqual(numero(6760, 2), "6\u00a0760.00")
        self.assertEqual(numero(3.125, 3), "3.125")
        for decimales in (-1, 9):
            with self.assertRaises(ValueError):
                numero(1, decimales)
        with self.assertRaises(ValueError):
            numero(float("inf"))


class Modulos(unittest.TestCase):
    def test_ejemplos_generan_pasos_completos(self):
        for modulo in MODULOS:
            for nombre, datos in modulo.ejemplos.items():
                with self.subTest(modulo=modulo.clave, ejemplo=nombre):
                    resultado = modulo.calcular(datos)
                    self.assertTrue(resultado.interpretacion)
                    self.assertTrue(resultado.pasos)
                    for paso in resultado.pasos:
                        self.assertTrue(all((paso.titulo, paso.formula, paso.sustitucion, paso.unidad)))

    def test_valores_modulos(self):
        datos = UN_FACTOR.ejemplos["Chuck Sox (T1)"]
        self.assertEqual(UN_FACTOR.calcular(datos).pasos[1].resultado, 3.125)
        datos = MULTIFACTOR.ejemplos["Kleen Karpet (T3)"]
        resultado = MULTIFACTOR.calcular(datos)
        self.assertEqual(resultado.pasos[4].resultado, 0.125)
        self.assertAlmostEqual(resultado.pasos[5].resultado, 65 / 6760)
        self.assertEqual(CAPACIDAD.calcular(CAPACIDAD.ejemplos["Lackey (T5)"]).pasos[-1].resultado, 1)

    def test_errores_modulos(self):
        datos = dict(UN_FACTOR.ejemplos["Chuck Sox (T1)"], unidad="")
        with self.assertRaises(ValueError):
            UN_FACTOR.calcular(datos)
        with self.assertRaises(ValueError):
            MULTIFACTOR.calcular(dict(produccion=1, insumos=[dict(nombre="Horas", cantidad=0, precio=1, es_laboral=True),
                                                            dict(nombre="Material", cantidad=1, precio=1, es_laboral=False)]))


if __name__ == "__main__":
    unittest.main()
