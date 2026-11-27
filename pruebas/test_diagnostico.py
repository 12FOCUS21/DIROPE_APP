"""Diagnóstico local sin ventanas, sin dependencias opcionales y sin ejercicios."""

from importlib import metadata
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from dirope.diagnostico import huella_codigo, informacion_entorno


class Diagnostico(unittest.TestCase):
    def test_huella_independiente_de_carpeta_y_finales_de_linea(self):
        with TemporaryDirectory() as temporal:
            base = Path(temporal)
            for carpeta, salto in ((base / "primera", b"\n"), (base / "segunda", b"\r\n")):
                (carpeta / "src" / "dirope").mkdir(parents=True)
                (carpeta / "iniciar.py").write_bytes(b"# Inicio" + salto)
                (carpeta / "src" / "dirope" / "ejemplo.py").write_bytes(b"# Modulo" + salto)
            self.assertEqual(huella_codigo(base / "primera"), huella_codigo(base / "segunda"))
            antes = huella_codigo(base / "segunda")
            (base / "segunda" / "iniciar.py").write_text("# Modificado", encoding="utf-8")
            self.assertNotEqual(antes, huella_codigo(base / "segunda"))
            self.assertIn("No disponible", huella_codigo(base / "inexistente"))

    def test_informacion_sin_opcionales_y_sin_leer_biblioteca(self):
        with TemporaryDirectory() as temporal:
            carpeta = Path(temporal)
            (carpeta / "privado.json").write_text('"No divulgar este enunciado"', encoding="utf-8")
            raiz = SimpleNamespace(tk=SimpleNamespace(call=lambda *args: "8.6.13"))
            with patch("dirope.diagnostico.metadata.version", side_effect=metadata.PackageNotFoundError):
                texto = informacion_entorno(raiz, carpeta_datos=carpeta)
            self.assertIn("8.6.13", texto)
            self.assertIn("No instalado (opcional)", texto)
            self.assertIn("registro.log", texto)
            self.assertIn("Código (huella):", texto)
            self.assertNotIn("No divulgar", texto)
            self.assertEqual(len(list(carpeta.iterdir())), 1)

    def test_tk_danado_no_impide_obtener_diagnostico(self):
        raiz = SimpleNamespace(tk=SimpleNamespace(call=lambda *args: (_ for _ in ()).throw(RuntimeError("Tk cerrado"))))
        self.assertIn("No disponible: Tk cerrado", informacion_entorno(raiz))

    def test_pillow_antiguo_activa_alternativa_tk(self):
        from dirope.interfaz.redondeado import usa_pillow
        with patch("dirope.interfaz.redondeado.Image", SimpleNamespace()):
            self.assertFalse(usa_pillow())

    def test_comando_sin_site_packages_y_desde_otra_carpeta(self):
        with TemporaryDirectory() as temporal:
            proceso = subprocess.run([sys.executable, "-S", str(RAIZ / "iniciar.py"), "--diagnostico"],
                                     cwd=temporal, capture_output=True, timeout=30)
            self.assertEqual(proceso.returncode, 0, proceso.stderr.decode(errors="replace"))
            self.assertIn(b"registro.log", proceso.stdout)
            self.assertIn(b"Python:", proceso.stdout)
            self.assertEqual(list(Path(temporal).iterdir()), [])
