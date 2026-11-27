"""Interpolación, contraste y comportamiento del fondo ambiental en Tk."""

import os
from pathlib import Path
import sys
import tkinter as tk
from tkinter import ttk
import unittest
from unittest.mock import patch

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ))

from dirope.interfaz.componentes import configurar_estilos
from dirope.interfaz.fondos import color_ambiental, FondoAmbiental, LienzoAmbiental
from dirope.interfaz.temas import actualizar_controles
from dirope.interfaz.tokens import PALETAS
from verificar_contraste import contraste


class ColorAmbiental(unittest.TestCase):
    def test_esquinas_centro_y_limites(self):
        esquinas = ("#000000", "#FF0000", "#00FF00", "#0000FF")
        for x, y, esperado in ((0, 0, esquinas[0]), (1, 0, esquinas[1]), (0, 1, esquinas[2]),
                               (1, 1, esquinas[3]), (.5, .5, "#404040"), (-2, 4, esquinas[2])):
            self.assertEqual(color_ambiental(x, y, esquinas).upper(), esperado)

    def test_contraste_en_toda_la_malla_no_solo_los_extremos(self):
        aurora = PALETAS["Aurora"]
        for x in range(21):
            for y in range(21):
                fondo = color_ambiental(x / 20, y / 20, aurora["fondo_ambiental"])
                for texto in ("texto", "texto_secundario"):
                    self.assertGreaterEqual(contraste(aurora[texto], fondo), 7)
                for control in ("foco", "borde_control"):
                    self.assertGreaterEqual(contraste(aurora[control], fondo), 3)


class FondoTk(unittest.TestCase):
    def setUp(self):
        try:
            self.raiz = tk.Tk()
        except tk.TclError as error:
            self.skipTest(f"Tk no disponible: {error}")
        self.addCleanup(self.raiz.destroy)
        self.raiz.nombre_tema = "Aurora"
        configurar_estilos(self.raiz)
        self.errores = []
        self.raiz.report_callback_exception = lambda tipo, error, traza: self.errores.append(error)
        self.contenedor = FondoAmbiental(self.raiz, padding=24)
        self.contenedor.pack(fill="both", expand=True)
        self.titulo = LienzoAmbiental(self.contenedor, titulo="Capacidad y personal", height=50)
        self.titulo.pack(fill="x")
        self.dato = tk.StringVar(value="1500.25")
        ttk.Entry(self.contenedor, textvariable=self.dato).pack(fill="x")

    def test_redimensionar_cache_y_cambiar_tema_sin_perder_datos(self):
        for tamano in ("960x600", "1280x760"):
            self.raiz.geometry(tamano)
            self.raiz.update()
            self.assertIsNotNone(self.contenedor.fondo.imagen)
            self.assertEqual(self.contenedor.fondo.winfo_width(), self.contenedor.winfo_width())
            imagen = self.contenedor.fondo.imagen
            self.contenedor.fondo.dibujar()
            self.assertIs(self.contenedor.fondo.imagen, imagen)
        for tema in ("Claro", "Oscuro", "Aurora"):
            self.raiz.nombre_tema = tema
            configurar_estilos(self.raiz)
            actualizar_controles(self.raiz)
            self.raiz.update()
            self.assertEqual(self.dato.get(), "1500.25")
            self.assertEqual(bool(self.contenedor.fondo.winfo_manager()), tema == "Aurora")
        self.assertEqual(self.errores, [])

    def test_fondo_sin_pillow_y_limpieza_de_tareas(self):
        with patch.dict(os.environ, {"DIROPE_SIN_PILLOW": "1"}):
            self.raiz.geometry("960x600")
            self.raiz.update()
            self.assertIsNotNone(self.contenedor.fondo.imagen)
            self.assertGreater(self.contenedor.fondo.imagen.width(), 900)
            self.contenedor.fondo.programar()
            self.contenedor.fondo.cancelar()
            self.assertIsNone(self.contenedor.fondo.tarea)
        self.assertEqual(self.errores, [])
