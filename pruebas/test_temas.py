"""Persistencia del tema, recuperación ante errores y contraste de lectura."""

import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dirope.historial import Historial
from dirope.preferencias import Preferencias
from dirope.interfaz.temas import PALETAS


class Temas(unittest.TestCase):
    def test_guardar_reabrir_y_no_confundir_con_ejercicios(self):
        with TemporaryDirectory() as temporal:
            preferencias = Preferencias(temporal)
            self.assertEqual(preferencias.leer_tema(), "Claro")
            for tema in ("Oscuro", "Claro"):
                preferencias.guardar_tema(tema)
                self.assertEqual(Preferencias(temporal).leer_tema(), tema)
            self.assertEqual(Historial(temporal).listar(), ([], 0))
            with self.assertRaises(ValueError):
                preferencias.guardar_tema("Desconocido")

    def test_preferencia_danada_no_impide_iniciar(self):
        with TemporaryDirectory() as temporal:
            preferencias = Preferencias(temporal)
            preferencias.ruta.parent.mkdir()
            for contenido in ("{", "[]", "null", json.dumps({"tema": "Desconocido"})):
                preferencias.ruta.write_text(contenido, encoding="utf-8")
                self.assertEqual(preferencias.leer_tema(), "Claro")

    def test_error_de_disco_conserva_preferencia_anterior(self):
        with TemporaryDirectory() as temporal:
            preferencias = Preferencias(temporal)
            preferencias.guardar_tema("Oscuro")
            with patch("dirope.preferencias.os.fsync", side_effect=OSError("Disco lleno")):
                with self.assertRaises(OSError):
                    preferencias.guardar_tema("Claro")
            self.assertEqual(preferencias.leer_tema(), "Oscuro")
            self.assertFalse(list(preferencias.ruta.parent.glob("*.tmp")))

    def test_contraste_minimo_de_textos(self):
        def luminancia(color):
            canales = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
            lineales = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in canales]
            return sum(v * peso for v, peso in zip(lineales, (0.2126, 0.7152, 0.0722)))

        for tema, colores in PALETAS.items():
            for texto in ("texto", "secundario", "error", "acento"):
                for fondo in ("fondo", "superficie"):
                    with self.subTest(tema=tema, texto=texto, fondo=fondo):
                        a, b = sorted((luminancia(colores[texto]), luminancia(colores[fondo])))
                        self.assertGreaterEqual((b + 0.05) / (a + 0.05), 4.5)
            for texto, fondo in (("nota", "fondo_nota"), ("resultado", "fondo_resultado"),
                                 ("nota", "superficie"), ("resultado", "superficie"), ("enlace", "campo"),
                                 ("secundario", "cabecera"), ("secundario", "suave"), ("blanco", "primario")):
                with self.subTest(tema=tema, texto=texto, fondo=fondo):
                    a, b = sorted((luminancia(colores[texto]), luminancia(colores[fondo])))
                    self.assertGreaterEqual((b + 0.05) / (a + 0.05), 4.5)
