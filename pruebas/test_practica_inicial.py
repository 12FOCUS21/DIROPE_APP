"""Resultados de los documentos iniciales y carga sin duplicados ni sobrescrituras."""

from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dirope.historial import Historial
from dirope.modulos.campos import MODOS
from dirope.practica_inicial import casos_complementarios, casos_practica, guardar_practica, resolver_caso


class PracticaInicial(unittest.TestCase):
    def test_orden_y_referencias_de_dirope_01_con_complementarios_aparte(self):
        oficiales = casos_practica()
        self.assertEqual([c["codigo"] for c in oficiales], ["T1", "T2", "T3", "T4", "T5", "1.17", "1.14"])
        for orden, (caso, referencia) in enumerate(zip(oficiales, ("1.1", "1.5", "1.8", "1.9", "1.13", "1.17", "1.14")), 1):
            self.assertTrue(caso["etiqueta"].startswith(f"{orden} · "))
            self.assertTrue(caso["etiqueta"].endswith(f"({referencia})"))
            self.assertTrue(caso["nombre"].endswith(f"Problema {referencia}"))
        extras = casos_complementarios()
        self.assertEqual([c["codigo"] for c in extras], ["T6-laboral", "T6-multifactor", "mesa-ayuda"])
        self.assertEqual([c["nombre"].split(" · ")[0] for c in extras], ["8A", "8B", "9"])

    def test_todos_los_resultados_de_practica_y_complementarios(self):
        esperados = {
            "T1": {"Productividad · Inicial": 3, "Productividad · Final": 3.125,
                   "Diferencia de productividad": 0.125, "Cambio de productividad": 100 / 24},
            "T2": {"Productividad · Inicial": 20, "Productividad · Final": 26.6, "Cambio de productividad": 33},
            "T3": {"Costo total · Base": 8260, "Productividad · Base": 65 / 8260,
                   "Productividad laboral por hora · Base": 0.125,
                   "Productividad por costo laboral · Base": 65 / 6760},
            "T4": {"Costo total · Inicial": 40000, "Costo total · Alternativa": 39000,
                   "Productividad laboral por hora · Inicial": 2.5, "Productividad · Inicial": 0.025,
                   "Productividad · Alternativa": 1000 / 39000,
                   "Cambio de productividad · Alternativa": 100 / 39},
            "T5": {"Meta de producción": 1875, "Horas-persona requeridas": 1875 / 2.344,
                   "Personal necesario": 5, "Personal adicional (+) o excedente (−)": 1,
                   "Cambio de horas-persona": 375 / 2.344},
            "1.17": {"Valor total": 20520, "Productividad económica": 57},
            "1.14": {"Costo total · Inicial": 5120, "Costo total · Alternativa": 6400,
                     "Costo total · Alternativa 2": 5220, "Productividad · Inicial": 1500 / 5120,
                     "Productividad · Alternativa": 1875 / 6400, "Productividad · Alternativa 2": 1875 / 5220,
                     "Cambio de productividad · Alternativa": 0,
                     "Cambio de productividad · Alternativa 2": ((1875 / 5220) / (1500 / 5120) - 1) * 100},
            "T6-laboral": {"Producción conforme · Inicial": 752, "Producción conforme · Final": 784,
                           "Productividad conforme · Inicial": 4.7, "Productividad conforme · Final": 4.9,
                           "Cambio de productividad conforme": 100 * 2 / 47},
            "T6-multifactor": {"Costo total · Inicial": 15000, "Costo total · Alternativa": 15300,
                               "Productividad · Inicial": 752 / 15000, "Productividad · Alternativa": 784 / 15300,
                               "Cambio de productividad · Alternativa": ((784 / 15300) / (752 / 15000) - 1) * 100},
            "mesa-ayuda": {"Producción conforme · Inicial": 132, "Producción conforme · Final": 144,
                          "Productividad conforme · Inicial": 132 / 30, "Productividad conforme · Final": 144 / 32},
        }
        casos = casos_practica() + casos_complementarios()
        self.assertEqual({caso["codigo"] for caso in casos}, set(esperados))
        for caso in casos:
            with self.subTest(caso=caso["codigo"]):
                datos = caso["datos"]
                self.assertTrue(all(isinstance(datos[campo], str) for campo in MODOS[caso["modulo"]][datos["modo"]]))
                resolucion = resolver_caso(caso)
                valores = {p["titulo"]: p["resultado"] for p in resolucion["resultado"]["pasos"]}
                for titulo, esperado in esperados[caso["codigo"]].items():
                    self.assertAlmostEqual(valores[titulo], esperado, places=9, msg=titulo)
                self.assertIn("5. RESULTADOS", resolucion["informe"])

    def test_carga_repetida_no_duplica_ni_sobrescribe_trabajo(self):
        with TemporaryDirectory() as temporal:
            historial = Historial(Path(temporal))
            registros = guardar_practica(historial)
            primero = registros[0]
            editado = historial.guardar(primero["modulo"], "Mi versión editada", primero["enunciado"],
                                        primero["datos"], primero["id"], resolucion=primero["resolucion"])
            guardar_practica(Historial(Path(temporal)))
            self.assertEqual(len(historial.listar()[0]), 10)
            self.assertEqual(historial.abrir(primero["id"]), editado)
            self.assertEqual(len({r["id"] for r in registros}), 10)
