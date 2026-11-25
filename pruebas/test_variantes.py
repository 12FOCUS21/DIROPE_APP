"""Regresiones del rediseño y comprobaciones independientes de la práctica."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dirope.modulos.productividad import CAPACIDAD, MULTIFACTOR, UN_FACTOR
from dirope.analisis import analizar_datos
from dirope.informe import informe_html


def valores(resultado):
    return {paso.titulo: paso.resultado for paso in resultado.pasos}


class Variantes(unittest.TestCase):
    def test_factor_individual_y_despejes(self):
        datos = dict(unidad_salida="kg", unidad_recurso="kWh", antes=72, insumo_antes=16, ritmo=4.5)
        for modo, esperado, unidad in (
            ("Productividad individual", 4.5, "kg/kWh"),
            ("Producción requerida", 72, "kg"),
            ("Recurso requerido", 16, "kWh"),
        ):
            with self.subTest(modo=modo):
                resultado = UN_FACTOR.calcular(dict(datos, modo=modo))
                self.assertEqual(resultado.pasos[0].resultado, esperado)
                self.assertEqual(resultado.pasos[0].unidad, unidad)
                self.assertFalse(resultado.serie)

    def test_factor_base_cero_y_disminucion(self):
        datos = dict(modo="Comparar escenarios", unidad_salida="piezas", unidad_recurso="h",
                     antes=0, despues=12, insumo_antes=3, insumo_despues=6)
        resultado = UN_FACTOR.calcular(datos)
        self.assertEqual(valores(resultado)["Diferencia de productividad"], 2)
        self.assertNotIn("Cambio de productividad", valores(resultado))
        self.assertIn("indefinida", resultado.interpretacion)
        resultado = UN_FACTOR.calcular(dict(datos, antes=12))
        self.assertEqual(valores(resultado)["Cambio de productividad"], -50)

    def test_factor_valida_unidades_vacios_y_desbordamiento(self):
        datos = dict(modo="Producción requerida", unidad_salida="cajas", unidad_recurso="h", ritmo=3, insumo_antes=5)
        for cambios in (dict(unidad_recurso=""), dict(insumo_antes=""), dict(ritmo="NaN"),
                        dict(ritmo=1e308, insumo_antes=2), dict(modo="Recurso requerido", ritmo=0, antes=1)):
            with self.subTest(cambios=cambios), self.assertRaises(ValueError):
                UN_FACTOR.calcular(dict(datos, **cambios))

    def test_lakefront_costos_y_cambio(self):
        datos = MULTIFACTOR.ejemplos["Lakefront · ahorro de energía (T4)"]
        resultado = MULTIFACTOR.calcular(datos)
        pasos = valores(resultado)
        self.assertEqual(pasos["Costo total · Inicial"], 40000)
        self.assertEqual(pasos["Costo total · Alternativa"], 39000)
        self.assertEqual(pasos["Productividad laboral por hora · Inicial"], 1000 / 400)
        self.assertEqual(pasos["Cambio de costo · Alternativa"], -2.5)
        self.assertAlmostEqual(pasos["Cambio de productividad · Alternativa"], (40000 / 39000 - 1) * 100)

    def test_114_contratacion_e_inversion(self):
        datos = MULTIFACTOR.ejemplos["Lackey · contratación e inversión (1.14)"]
        resultado = MULTIFACTOR.calcular(datos)
        pasos = valores(resultado)
        self.assertEqual(pasos["Productividad · Inicial"], 1500 / (640 * 8))
        self.assertEqual(pasos["Productividad · Alternativa"], 1875 / (800 * 8))
        self.assertEqual(pasos["Productividad · Alternativa 2"], 1875 / (640 * 8 + 100))
        self.assertAlmostEqual(pasos["Cambio de productividad · Alternativa"], 0)
        self.assertAlmostEqual(pasos["Cambio de productividad · Alternativa 2"], (1875 * 5120 / (5220 * 1500) - 1) * 100)
        self.assertEqual(len(resultado.serie), 3)

    def test_117_valor_y_productividad_economica(self):
        datos = MULTIFACTOR.ejemplos["Susan Williams · valor por calidad (1.17)"]
        resultado = MULTIFACTOR.calcular(datos)
        pasos = valores(resultado)
        self.assertEqual(pasos["Valor total"], 52 * 90 + 80 * 198)
        self.assertEqual(pasos["Productividad económica"], (52 * 90 + 80 * 198) / (8 * 45))
        self.assertEqual(resultado.indicadores[-1].unidad, "$/h-persona")

    def test_nuevo_escenario_moneda_y_costos_directos(self):
        datos = dict(modo="Comparar alternativas", unidad_salida="piezas", moneda="PEN", produccion=120,
                     produccion_final=90, insumos=[dict(nombre="Contrato", directo=20),
                                                  dict(nombre="Material", cantidad=5, unidad="kg", precio=4),
                                                  dict(nombre="Energía", cantidad=5, unidad="kWh", precio=2, escenario="Alternativa")])
        resultado = MULTIFACTOR.calcular(datos)
        pasos = valores(resultado)
        self.assertEqual(pasos["Participación · Inicial · Material"], 50)
        self.assertEqual(pasos["Productividad · Inicial"], 3)
        self.assertEqual(pasos["Productividad · Alternativa"], 9)
        self.assertEqual(resultado.unidad_grafico, "piezas/PEN")
        for fila in (dict(nombre="Otro", directo=0, precio=2), dict(nombre="Otro", directo=-1),
                     dict(nombre="Otro", directo=10, moneda="USD"), dict(nombre="Otro", cantidad=5, precio=2,
                                                                        unidad="kg", es_laboral=True)):
            with self.subTest(fila=fila), self.assertRaises(ValueError):
                MULTIFACTOR.calcular(dict(datos, insumos=[*datos["insumos"], fila]))

    def test_costo_total_nulo_y_alternativa_incompleta(self):
        datos = dict(modo="Escenario individual", unidad_salida="piezas", moneda="PEN", produccion=0,
                     insumos=[dict(nombre="Servicio", directo=0)])
        with self.assertRaises(ValueError):
            MULTIFACTOR.calcular(datos)
        with self.assertRaisesRegex(ValueError, "Alternativa"):
            MULTIFACTOR.calcular(dict(datos, modo="Comparar alternativas", produccion_final=1,
                                      insumos=[dict(nombre="Servicio", directo=5)]))

    def test_conformidad_cuenta_o_porcentaje(self):
        datos = UN_FACTOR.ejemplos["Mesa de ayuda · conformidad (T6)"]
        for entrada in (datos, dict(datos, medida_calidad="%", defecto_antes=12, defecto_despues=4)):
            with self.subTest(entrada=entrada):
                pasos = valores(UN_FACTOR.calcular(entrada))
                self.assertAlmostEqual(pasos["Cambio de conformidad"], 8)
                self.assertAlmostEqual(pasos["Cambio de productividad conforme"], ((144 / 32) / (132 / 30) - 1) * 100)
        for cambios in (dict(defecto_antes=151), dict(medida_calidad="%", defecto_antes=101)):
            with self.assertRaises(ValueError):
                UN_FACTOR.calcular(dict(datos, **cambios))

    def test_lackey_horas_incrementales(self):
        base = CAPACIDAD.ejemplos["Lackey (T5)"]
        resultado = CAPACIDAD.calcular(dict(base, modo="Crecimiento porcentual"))
        pasos = valores(resultado)
        self.assertEqual(pasos["Meta de producción"], 1875)
        self.assertAlmostEqual(pasos["Cambio de horas-persona"], 375 / 2.344)
        self.assertEqual(pasos["Personal adicional (+) o excedente (−)"], 1)

    def test_capacidad_directa_aplica_techo_estricto_y_dispone_de_plantilla(self):
        datos = dict(modo="Meta directa", actual=100, meta=100.001, productividad=2.5, horas=8,
                     plantilla=5, unidad_salida="cajas", periodo="semana")
        pasos = valores(CAPACIDAD.calcular(datos))
        self.assertEqual(pasos["Personal necesario"], 6)
        self.assertEqual(pasos["Capacidad disponible"], 100)
        self.assertEqual(pasos["Personal adicional (+) o excedente (−)"], 1)
        self.assertEqual(valores(CAPACIDAD.calcular(dict(datos, meta=40)))["Personal adicional (+) o excedente (−)"], -3)

    def test_capacidad_crecimiento_negativo_y_limites(self):
        datos = dict(modo="Crecimiento porcentual", actual=100, crecimiento=-100, productividad=2.5,
                     horas=8, unidad_salida="cajas", periodo="semana")
        self.assertEqual(valores(CAPACIDAD.calcular(datos))["Personal necesario"], 0)
        for cambios in (dict(crecimiento=-101), dict(horas=0), dict(plantilla=1.5), dict(periodo="")):
            with self.assertRaises(ValueError):
                CAPACIDAD.calcular(dict(datos, **cambios))

    def test_capacidad_distingue_igualdad_decimal_de_exceso_real(self):
        datos = dict(modo="Meta directa", meta="2.1", actual="0", productividad="0.3",
                     horas="1", unidad_salida="piezas", periodo="día")
        for meta, personas in (("2.1", 7), ("2.10000000000000000001", 8)):
            pasos = valores(CAPACIDAD.calcular(dict(datos, meta=meta)))
            self.assertEqual(pasos["Personal necesario"], personas)
            self.assertEqual(pasos["Personal adicional (+) o excedente (−)"], personas)

    def test_procedimiento_multifactor_respeta_dependencias(self):
        datos = MULTIFACTOR.ejemplos["Lakefront · ahorro de energía (T4)"]
        resultado = MULTIFACTOR.calcular(datos)
        titulos = [paso.titulo for paso in resultado.procedimiento]
        self.assertEqual(len(titulos), len(set(titulos)))
        self.assertLess(titulos.index("Costo total · Inicial"), titulos.index("Productividad · Inicial"))
        self.assertLess(titulos.index("Productividad · Alternativa"),
                        titulos.index("Cambio de productividad · Alternativa"))
        self.assertTrue(any(p.titulo.startswith("Participación") for p in resultado.detalles))
        self.assertEqual(len(titulos) + len(resultado.detalles), len(resultado.pasos))

    def test_meta_directa_sin_produccion_de_referencia(self):
        datos = dict(modo="Meta directa", meta=150, productividad=2.5, horas=8, unidad_salida="cajas", periodo="día")
        resultado = CAPACIDAD.calcular(datos)
        self.assertEqual(valores(resultado)["Personal necesario"], 8)
        self.assertFalse(resultado.serie)
        con_plantilla = CAPACIDAD.calcular(dict(datos, plantilla=7))
        self.assertEqual(valores(con_plantilla)["Capacidad disponible"], 140)

    def test_informe_html_escapa_texto_y_muestra_tablas_y_grafico(self):
        datos = MULTIFACTOR.ejemplos["Lakefront · ahorro de energía (T4)"]
        resultado = MULTIFACTOR.calcular(datos)
        analisis = analizar_datos("multifactor", datos, resultado=resultado)
        html = informe_html("<título>", "<script>alert(2)</script>", analisis, resultado, 3)
        self.assertIn("&lt;título&gt;", html)
        self.assertNotIn("<script>", html)
        self.assertIn("40\u00a0000.000", html)
        self.assertIn("Sustitución", html)
        self.assertIn("Productividad por escenario", html)

    def test_modo_desconocido(self):
        with self.assertRaisesRegex(ValueError, "cálculo disponible"):
            UN_FACTOR.calcular({"modo": "Otro"})


if __name__ == "__main__":
    unittest.main()
