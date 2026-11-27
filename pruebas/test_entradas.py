"""Tipos aceptados, límites de campos, errores localizados y recuperación en Tk."""

from copy import deepcopy
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import tkinter as tk
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dirope.banco import generar_banco
from dirope.entradas import TEXTOS, ayuda_campo, errores_entrada, regla_campo
from dirope.modulos.campos import MODOS
from dirope.nucleo import validar_numero


class Entradas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.casos = generar_banco()

    def test_banco_completo_valido_y_ayudas_para_cada_campo(self):
        for caso in self.casos:
            with self.subTest(caso=caso["nombre"]):
                self.assertEqual(errores_entrada(caso["modulo"], caso["datos"]), {})
                for clave in MODOS[caso["modulo"]][caso["datos"]["modo"]]:
                    self.assertTrue(ayuda_campo(clave, caso["datos"]))

    def test_tipos_incorrectos_en_todos_los_campos_numericos(self):
        for caso in generar_banco(1):
            for clave in MODOS[caso["modulo"]][caso["datos"]["modo"]]:
                if clave in TEXTOS or clave == "medida_calidad":
                    continue
                for valor in ("hola", "2,5", "NaN", "Infinity", "1e999", "1_000", "1 2", True):
                    with self.subTest(modo=caso["datos"]["modo"], campo=clave, valor=valor):
                        datos = deepcopy(caso["datos"])
                        datos[clave] = valor
                        self.assertIn(clave, errores_entrada(caso["modulo"], datos))
                datos = deepcopy(caso["datos"])
                datos[clave] = ""
                self.assertEqual(clave in errores_entrada(caso["modulo"], datos),
                                 not regla_campo(clave, datos)[0])

    def test_formato_numerico_aceptado_y_rechazado(self):
        for entrada, esperado in (("1 500.25", 1500.25), ("1\u00a0500.25", 1500.25),
                                  (".5", .5), ("+2.5", 2.5), ("1e3", 1000)):
            self.assertEqual(validar_numero(entrada, "Prueba"), esperado)
        for entrada in ("1_000", "١٢", "2,5", "1 00", "1.2.3", "—2"):
            with self.assertRaises(ValueError):
                validar_numero(entrada, "Prueba")

    def test_dominios_relaciones_y_campos_opcionales(self):
        datos = dict(modo="Meta directa", unidad_salida="cajas", periodo="mes", actual="", meta="100",
                     productividad="10", horas="8", plantilla="")
        self.assertEqual(errores_entrada("capacidad", datos), {})
        for valor in ("1.5", "1.00000000000000000001", "-1"):
            self.assertIn("plantilla", errores_entrada("capacidad", dict(datos, plantilla=valor)))
        for clave in ("productividad", "horas"):
            self.assertIn(clave, errores_entrada("capacidad", dict(datos, **{clave: "0"})))
        datos.update(modo="Crecimiento porcentual", actual="100", crecimiento="-100")
        self.assertNotIn("crecimiento", errores_entrada("capacidad", datos))
        self.assertIn("crecimiento", errores_entrada("capacidad", dict(datos, crecimiento="-100.0001")))
        caso = next(c for c in self.casos if c["datos"]["modo"] == "Comparar conformidad")
        datos = dict(caso["datos"], medida_calidad="Cantidad", antes="10", defecto_antes="11")
        self.assertIn("defecto_antes", errores_entrada("un_factor", datos))
        datos.update(medida_calidad="%", defecto_antes="101")
        self.assertIn("defecto_antes", errores_entrada("un_factor", datos))
        self.assertIn("modo", errores_entrada("un_factor", {"modo": "Inexistente"}))

    def test_filas_invalidas_y_costos_excluyentes(self):
        datos = dict(modo="Escenario individual", unidad_salida="cajas", moneda="$", produccion="100",
                     insumos=[dict(nombre="Trabajo", cantidad="8", precio="2", directo="", unidad="h-persona", es_laboral=True)])
        self.assertEqual(errores_entrada("multifactor", datos), {})
        for clave, valor in (("nombre", ""), ("cantidad", "NaN"), ("precio", "-1"),
                             ("directo", "4"), ("unidad", "kg")):
            copia = deepcopy(datos)
            copia["insumos"][0][clave] = valor
            esperado = "precio" if clave == "directo" else clave
            self.assertIn(f"insumos.0.{esperado}", errores_entrada("multifactor", copia))


class EntradasInterfaz(unittest.TestCase):
    def setUp(self):
        from dirope.interfaz.ventana import Aplicacion
        self.temporal = TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        try:
            self.app = Aplicacion(Path(self.temporal.name))
        except tk.TclError as error:
            self.skipTest(f"Tk no disponible: {error}")
        self.addCleanup(self.app.destroy)
        self.app.withdraw()
        self.errores = []
        self.app.report_callback_exception = lambda tipo, error, traza: self.errores.append(error)

    def test_invalidar_corregir_y_recalcular_en_los_diez_modos(self):
        for caso in generar_banco(1):
            with self.subTest(modo=caso["datos"]["modo"]):
                panel = next(p for p in self.app.paneles if p.modulo.clave == caso["modulo"])
                panel.cargar_datos(caso["nombre"], caso["enunciado"], caso["datos"])
                clave = next(k for k in MODOS[caso["modulo"]][caso["datos"]["modo"]]
                             if k not in TEXTOS and k != "medida_calidad")
                original = panel.variables[clave].get()
                panel.variables[clave].set("2,5")
                self.assertFalse(panel.ver_resultado())
                self.app.update()
                self.assertIsNone(panel.resultado)
                self.assertIn("invalid", panel.marcos[clave][1].state())
                self.assertIn("punto decimal", panel.ayudas_campos[clave].cget("text"))
                self.assertIsNone(panel.identificador)
                panel.variables[clave].set(original)
                self.app.update()
                self.assertTrue(panel.ver_resultado())
                self.assertNotIn("invalid", panel.marcos[clave][1].state())
                self.assertTrue(panel.identificador)
        self.assertEqual(self.errores, [])

    def test_tema_aurora_persistencia_y_campos_sin_perder_datos(self):
        caso = generar_banco(1)[0]
        panel = self.app.paneles[0]
        panel.cargar_datos("Prueba", "", caso["datos"])
        antes = panel.recoger_datos()
        for tema in ("Aurora", "Oscuro", "Claro", "Aurora"):
            self.app.tema.set(tema)
            self.assertTrue(self.app.cambiar_tema())
            self.app.update()
            self.assertEqual(panel.recoger_datos(), antes)
        self.assertEqual(self.app.preferencias.leer_tema(), "Aurora")
        self.assertIn("Aurora", self.app.selector_tema.cget("values"))
        self.assertEqual(self.errores, [])

    def test_error_de_fila_y_recuperacion_sin_guardar_datos_invalidos(self):
        caso = next(c for c in generar_banco(1) if c["datos"]["modo"] == "Escenario individual")
        panel = self.app.paneles[1]
        panel.cargar_datos("Fila inválida", "", caso["datos"])
        fila = panel.filas[0]
        original = fila[1]["cantidad"].get()
        fila[1]["cantidad"].set("NaN")
        self.assertFalse(panel.ver_resultado())
        self.app.update()
        self.assertIn("invalid", fila[2]["cantidad"].state())
        self.assertIn("finito", fila[2]["aviso"].cget("text"))
        self.assertEqual(self.app.historial.listar()[0], [])
        fila[1]["cantidad"].set(original)
        self.app.update()
        self.assertTrue(panel.ver_resultado())
        self.assertNotIn("invalid", fila[2]["cantidad"].state())
        self.assertEqual(fila[2]["aviso"].cget("text"), "")
        self.assertEqual(self.errores, [])

    def test_error_vacio_persiste_hasta_ser_corregido(self):
        caso = generar_banco(1)[0]
        panel = self.app.paneles[0]
        panel.cargar_datos("Campo vacío", "", caso["datos"])
        panel.variables["antes"].set("")
        self.assertFalse(panel.ver_resultado())
        self.app.update()
        self.assertIn("invalid", panel.marcos["antes"][1].state())
        self.assertIn("vacío", panel.ayudas_campos["antes"].cget("text"))
        panel.variables["antes"].set("0")
        self.app.update()
        self.assertNotIn("invalid", panel.marcos["antes"][1].state())
        self.assertEqual(self.errores, [])

    def test_aurora_sin_pillow_con_escala_y_dos_tamanos(self):
        with patch.dict(os.environ, {"DIROPE_SIN_PILLOW": "1"}):
            self.app.tema.set("Aurora")
            self.assertTrue(self.app.cambiar_tema())
            self.app.deiconify()
            self.app.mostrar("capacidad")
            escala = float(self.app.tk.call("tk", "scaling"))
            self.app.tk.call("tk", "scaling", escala * 1.25)
            for tamano in ("960x600", "1280x760"):
                self.app.geometry(tamano)
                self.app.update()
                self.assertTrue(self.app.cabecera.find_withtag("espectro"))
                self.assertTrue(self.app.paneles[2].siguiente.winfo_viewable())
            self.assertEqual(self.errores, [])
