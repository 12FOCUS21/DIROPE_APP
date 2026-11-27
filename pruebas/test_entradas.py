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
from dirope.entradas import TEXTOS, ayuda_campo, ayuda_insumo, errores_entrada, regla_campo
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

    def test_exponentes_fuera_de_rango_no_escapan_de_la_validacion(self):
        caso = next(c for c in self.casos if c["datos"]["modo"] == "Comparar conformidad")
        for entrada in ("0e9999999999999999999999", "1e-9999999999999999999999", "1e-400", "-1e-400"):
            with self.subTest(entrada=entrada):
                errores = errores_entrada("un_factor", dict(caso["datos"], defecto_antes=entrada))
                self.assertIn("defecto_antes", errores)
        errores = errores_entrada("un_factor", dict(caso["datos"], medida_calidad="Cantidad",
                                                    antes="125", defecto_antes="125.000000000000000001"))
        self.assertIn("defecto_antes", errores)

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

    def test_campos_de_texto_selectores_y_opcion_que_necesita_produccion(self):
        for caso in generar_banco(1):
            for clave in MODOS[caso["modulo"]][caso["datos"]["modo"]]:
                if clave in TEXTOS or clave == "medida_calidad":
                    datos = dict(caso["datos"], **{clave: "   "})
                    self.assertIn(clave, errores_entrada(caso["modulo"], datos))
        caso = next(c for c in generar_banco(1) if c["datos"]["modo"] == "Comparar alternativas")
        datos = deepcopy(caso["datos"])
        nueva = dict(datos["insumos"][0], escenario="Alternativa 2")
        datos["insumos"].append(nueva)
        self.assertIn("produccion_otra", errores_entrada("multifactor", datos))
        datos["produccion_otra"] = "120"
        self.assertEqual(errores_entrada("multifactor", datos), {})
        nueva["escenario"] = "Escenario incorrecto"
        errores = errores_entrada("multifactor", datos)
        self.assertIn(f"insumos.{len(datos['insumos']) - 1}.escenario", errores)
        self.assertIn("Alternativa 2", errores["insumos"])
        for columna in ("nombre", "cantidad", "precio", "directo", "unidad", "es_laboral", "escenario"):
            self.assertTrue(ayuda_insumo(columna))


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

    def test_practica_fijada_abre_original_editable_sin_sembrar_biblioteca(self):
        from dirope.practica_inicial import casos_practica
        casos = casos_practica()
        self.assertEqual(len(self.app.botones_practica), len(casos))
        for boton, caso in zip(self.app.botones_practica, casos):
            panel = next(p for p in self.app.paneles if p.modulo.clave == caso["modulo"])
            with patch.object(panel, "confirmar_reemplazo", return_value=True):
                self.assertTrue(boton.invoke())
            self.assertEqual(panel.titulo.get(), caso["nombre"])
            self.assertEqual(panel.modo_actual, caso["datos"]["modo"])
            self.assertEqual(panel.texto_enunciado(), caso["enunciado"])
            self.assertIsNone(panel.identificador)
        self.assertEqual(self.app.historial.listar()[0], [])
        self.assertEqual(self.errores, [])

    def test_desarrollo_y_detalle_visibles_sin_usar_rueda(self):
        from dirope.practica_inicial import casos_practica
        caso = next(c for c in casos_practica() if c["codigo"] == "T4")
        self.app.deiconify()
        self.app.geometry("960x600")
        self.assertTrue(self.app.abrir_practica(caso))
        panel = self.app.paneles[1]
        for _ in range(3):
            self.assertTrue(panel.avanzar())
            self.app.update()
        lienzo = panel.lienzos[3]
        self.assertEqual(lienzo.yview()[0], 0)
        for control in (panel.titulo_paso, panel.formula_paso.formula, panel.sustitucion_paso.formula):
            self.assertTrue(control.winfo_viewable())
            self.assertLess(control.winfo_rooty(), lienzo.winfo_rooty() + lienzo.winfo_height())
        self.assertTrue(panel.formula_paso.formula.find_all())
        self.assertLess(panel.valor_paso.winfo_rooty(), panel.leyendas_paso.winfo_rooty())
        panel.mostrar_detalle()
        self.app.update()
        self.assertGreater(lienzo.yview()[0], 0)
        self.assertLessEqual(abs(panel.detalle.winfo_rooty() - lienzo.winfo_rooty()), 12)
        self.assertTrue(panel.avanzar())
        self.app.update()
        self.assertEqual(lienzo.yview()[0], 0)
        self.assertEqual(panel.paso_actual, 1)
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

    def test_nota_no_conformes_persistente_y_cero_explicito(self):
        caso = next(c for c in generar_banco(1) if c["datos"]["modo"] == "Comparar conformidad")
        panel = self.app.paneles[0]
        datos = dict(caso["datos"], antes="125", despues="125", medida_calidad="Cantidad",
                     defecto_antes="", defecto_despues="")
        panel.cargar_datos("No conformes", "", datos)
        self.assertTrue(panel.nota_metodo_calidad.winfo_manager())
        self.assertFalse(panel.ver_resultado())
        self.app.update()
        self.assertTrue(panel.nota_calidad.winfo_manager())
        self.assertIn("escribe 0", panel.ayudas_campos["defecto_antes"].cget("text"))
        self.assertIn("125 unidades", panel.texto_nota_calidad.cget("text"))
        self.assertIn("0.04", panel.texto_nota_calidad.cget("text"))
        panel.variables["defecto_antes"].set("0e9999999999999999999999")
        self.app.update()
        self.assertIn("exponente", panel.ayudas_campos["defecto_antes"].cget("text"))
        for clave in ("defecto_antes", "defecto_despues"):
            panel.variables[clave].set("0")
        self.assertTrue(panel.ver_resultado())
        conformes = [p.resultado for p in panel.resultado.pasos if p.titulo.startswith("Producción conforme")]
        self.assertEqual(conformes, [125, 125])
        for medida, entrada in (("Cantidad", "5"), ("%", "4")):
            panel.variables["medida_calidad"].set(medida)
            panel.variables["defecto_despues"].set(entrada)
            self.assertTrue(panel.ver_resultado())
            conformes = [p.resultado for p in panel.resultado.pasos if p.titulo.startswith("Producción conforme")]
            self.assertEqual(conformes, [125, 120])
            self.assertIn("No conformes: unidades que no cumplen", panel.informe_completo())
        self.assertEqual(self.errores, [])

    def test_cambiar_conformidad_desde_desplegable_real_en_todos_los_temas(self):
        self.app.deiconify()
        self.app.mostrar("un_factor")
        panel = self.app.paneles[0]
        for tema in ("Claro", "Oscuro", "Aurora"):
            self.app.tema.set(tema)
            self.app.cambiar_tema()
            for destino in ("Comparar conformidad", "Recurso requerido", "Comparar escenarios", "Comparar conformidad"):
                panel.mostrar_etapa(0)
                self.app.update()
                panel.selector_modo.abrir()
                popup = self.app.opciones_abiertas
                self.assertIsNotNone(popup)
                popup.botones[list(panel.modos).index(destino)].invoke()
                self.app.update()
                self.assertEqual(panel.modo_actual, destino)
                self.assertIsNone(self.app.opciones_abiertas)
                self.assertEqual(bool(panel.nota_metodo_calidad.winfo_manager()), destino == "Comparar conformidad")
        self.assertEqual(self.errores, [])

    def test_dialogo_de_error_identifica_registro_y_detalle(self):
        from dirope.interfaz.ventana import Aplicacion
        with patch("dirope.interfaz.ventana.messagebox.showerror") as aviso, \
             patch("dirope.interfaz.ventana.logging.error"):
            Aplicacion.report_callback_exception(self.app, ValueError, ValueError("Fallo reproducido"), None)
        texto = aviso.call_args.args[1]
        self.assertIn("ValueError: Fallo reproducido", texto)
        self.assertIn("registro.log", texto)
        self.assertIn("Información y diagnóstico", texto)
        ventana = self.app.mostrar_diagnostico()
        self.app.update_idletasks()
        self.assertEqual(ventana.title(), "Información y diagnóstico")
        ventana.destroy()
