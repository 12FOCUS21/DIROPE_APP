"""Pruebas de reapertura local e informe paginado."""
import importlib.util
import re
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dirope.analisis import analizar_datos
from dirope.historial import Historial
from dirope.informe import informe_pdf, guardar_informe_html
from dirope.modulos.productividad import MULTIFACTOR


class Entrega(unittest.TestCase):
    def test_html_atomico_conserva_destino_si_falla_el_disco(self):
        with TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "informe.html"
            guardar_informe_html(ruta, "Producción válida: 1 500.25")
            for operacion in ("fsync", "replace"):
                with self.subTest(operacion=operacion):
                    with patch(f"dirope.informe.os.{operacion}", side_effect=OSError("Disco no disponible")):
                        with self.assertRaises(OSError):
                            guardar_informe_html(ruta, "No debe reemplazar el anterior")
                    self.assertEqual(ruta.read_text(encoding="utf-8"), "Producción válida: 1 500.25")
                    self.assertEqual(list(Path(temporal).iterdir()), [ruta])
            guardar_informe_html(ruta, "Actualización completa")
            self.assertEqual(ruta.read_text(encoding="utf-8"), "Actualización completa")

    @unittest.skipUnless(importlib.util.find_spec("reportlab"), "ReportLab opcional no instalado")
    def test_pdf_fallido_no_sobrescribe_informe_anterior(self):
        datos = MULTIFACTOR.ejemplos["Lakefront · ahorro de energía (T4)"]
        resultado = MULTIFACTOR.calcular(datos)
        analisis = analizar_datos("multifactor", datos, resultado=resultado)
        with TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "informe.pdf"
            ruta.write_bytes(b"Documento anterior")
            with patch("reportlab.platypus.SimpleDocTemplate.build", side_effect=OSError("Disco lleno")):
                with self.assertRaisesRegex(RuntimeError, "Disco lleno"):
                    informe_pdf(ruta, "Prueba", "", analisis, resultado, 4)
            self.assertEqual(ruta.read_bytes(), b"Documento anterior")
            self.assertEqual(list(Path(temporal).iterdir()), [ruta])

    def test_historial_reabre_actualiza_y_omite_archivo_danado(self):
        with TemporaryDirectory() as temporal:
            carpeta = Path(temporal)
            datos = {"modo": "Meta directa", "meta": "2.1"}
            registro = Historial(carpeta).guardar("capacidad", "Turno", "Datos del día", datos)
            self.assertEqual(registro["version"], 1)
            historial = Historial(carpeta)
            self.assertEqual(historial.abrir(registro["id"])["datos"], datos)
            actualizado = historial.guardar("capacidad", "Otro turno", "", dict(datos, meta="2.4"), registro["id"])
            self.assertEqual(actualizado["id"], registro["id"])
            self.assertEqual(historial.abrir(registro["id"]), actualizado)
            (carpeta / "dañado.json").write_text("{", encoding="utf-8")
            self.assertEqual(historial.listar(), ([actualizado], 1))
            historial.eliminar(registro["id"])
            self.assertEqual(historial.listar(), ([], 1))

    @unittest.skipUnless(importlib.util.find_spec("reportlab"), "ReportLab opcional no instalado")
    def test_pdf_real_a4_con_informe_extenso_y_grafico(self):
        datos = MULTIFACTOR.ejemplos["Lakefront · ahorro de energía (T4)"]
        resultado = MULTIFACTOR.calcular(datos)
        analisis = analizar_datos("multifactor", datos, resultado=resultado)
        with TemporaryDirectory() as temporal:
            ruta = Path(temporal) / "informe.pdf"
            with patch("reportlab.rl_config.pageCompression", 0):
                informe_pdf(ruta, "Lakefront", "Producción diaria. " * 800, analisis, resultado, 4)
            pdf = ruta.read_bytes()
        self.assertTrue(pdf.startswith(b"%PDF-"))
        self.assertTrue(pdf.rstrip().endswith(b"%%EOF"))
        self.assertIn(b"/Title (Lakefront)", pdf)
        self.assertIn(b"Productividad por escenario", pdf)
        self.assertIn(b"Procedimiento principal", pdf)
        self.assertIn(b"0.0256 llantas/$", pdf)
        self.assertIn(b" re f*", pdf)
        tamanos = re.findall(rb"/MediaBox \[\s*0\s+0\s+([.\d]+)\s+([.\d]+)\s*\]", pdf)
        self.assertGreater(len(tamanos), 2)
        for ancho, alto in tamanos:
            self.assertAlmostEqual(float(ancho), 595.28, places=2)
            self.assertAlmostEqual(float(alto), 841.89, places=2)
