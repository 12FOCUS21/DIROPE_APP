"""Regresión de recuadros, adaptación al ancho y actualización de fórmulas en Tk."""

import os
from pathlib import Path
import sys
import tkinter as tk
from tkinter import ttk
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dirope.interfaz.componentes import configurar_estilos
from dirope.interfaz.formula_explicada import FormulaExplicada
from dirope.interfaz.temas import actualizar_controles, PALETAS


class RecuadrosFormula(unittest.TestCase):
    def setUp(self):
        try:
            self.raiz = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Tk no disponible: {error}")
        self.addCleanup(self.raiz.destroy)
        self.errores = []
        self.raiz.report_callback_exception = lambda tipo, error, traza: self.errores.append(error)
        self.raiz.nombre_tema = "Claro"
        configurar_estilos(self.raiz)
        self.panel = ttk.Frame(self.raiz, style="Card.TFrame", padding=12)
        self.panel.pack(fill="both", expand=True)
        self.formula = FormulaExplicada(self.panel, "P = Q / I")
        self.formula.pack(fill="x")

    def ajustar(self, ancho):
        self.raiz.geometry(f"{ancho}x800")
        self.raiz.update()
        self.assertEqual(self.errores, [])

    def test_columnas_proporcionadas_y_apilado_al_redimensionar(self):
        for ancho, lateral in ((1250, True), (600, False), (1250, True)):
            with self.subTest(ancho=ancho):
                self.ajustar(ancho)
                self.assertEqual(self.formula.distribucion, (lateral, True))
                posicion = self.formula.leyenda.grid_info()
                self.assertEqual(int(posicion["row"]), 0 if lateral else 1)
                self.assertEqual(int(posicion["column"]), 1 if lateral else 0)
                if lateral:
                    proporcion = self.formula.izquierda.winfo_width() / self.formula.winfo_width()
                    self.assertGreater(proporcion, .30)
                    self.assertLess(proporcion, .48)
                self.assertLessEqual(self.formula.leyenda.winfo_width(), self.formula.winfo_width())

    def test_actualizar_sin_reconstruir_y_vaciar_leyendas(self):
        anteriores = tuple(self.formula.leyenda.winfo_children())
        self.formula.presentar("P = Q / I")
        self.assertEqual(tuple(self.formula.leyenda.winfo_children()), anteriores)
        self.formula.presentar("N = techo(H / jornada)")
        self.ajustar(1250)
        self.assertIn("techo", [clave.cget("text") for clave, _ in self.formula.etiquetas])
        self.formula.presentar("")
        self.ajustar(1250)
        self.assertFalse(self.formula.etiquetas)
        self.assertFalse(self.formula.leyenda.winfo_manager())
        self.assertEqual(self.formula.formula.cget("takefocus"), "1")

    def test_temas_escala_y_motor_sin_pillow(self):
        escala = float(self.raiz.tk.call("tk", "scaling"))
        with patch.dict(os.environ, {"DIROPE_SIN_PILLOW": "1"}):
            for tema in ("Oscuro", "Claro"):
                self.raiz.nombre_tema = tema
                configurar_estilos(self.raiz)
                actualizar_controles(self.raiz)
                self.raiz.tk.call("tk", "scaling", escala * 1.25)
                self.formula.presentar("Meta = Q × (1 + g / 100)")
                self.ajustar(1250)
                self.assertEqual(self.formula.formula.cget("background"), PALETAS[tema]["superficie"])
                for clave, detalle in self.formula.etiquetas:
                    self.assertGreater(int(clave.cget("wraplength")), 0)
                    self.assertGreater(int(detalle.cget("wraplength")), 0)
                    self.assertLessEqual(detalle.winfo_x() + detalle.winfo_width(), detalle.master.winfo_width())
                self.ajustar(600)
                self.assertFalse(self.formula.distribucion[0])

    def test_sustitucion_no_trata_datos_como_constantes_y_permite_copia(self):
        sustitucion = FormulaExplicada(self.panel, "techo(100 / 3)", sustitucion=True)
        sustitucion.pack(fill="x")
        self.ajustar(1250)
        claves = [clave.cget("text") for clave, _ in sustitucion.etiquetas]
        self.assertIn("techo", claves)
        self.assertNotIn("100", claves)
        sustitucion.formula.copiar()
        self.assertEqual(self.raiz.clipboard_get(), "techo(100 / 3)")


if __name__ == "__main__":
    unittest.main()
