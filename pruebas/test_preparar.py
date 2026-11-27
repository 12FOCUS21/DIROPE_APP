"""Permiso, aislamiento y comprobación del conjunto de dependencias distribuido."""

import hashlib
import importlib.util
from pathlib import Path
import re
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import preparar


class Preparar(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec("ensurepip"), "Este Python no incluye ensurepip")
    def test_no_instala_ni_descarga_sin_permiso(self):
        confirmar = Mock(return_value=False)
        base = Path(sys.executable)
        requisitos = RAIZ / "requirements.txt"
        with patch.object(preparar, "paquetes_disponibles", return_value=False), \
             patch.object(preparar, "origen_paquetes", return_value=(requisitos, None, False)), \
             patch.object(preparar, "preparar_entorno") as instalar:
            self.assertEqual(preparar.elegir_python(RAIZ, base, confirmar, Mock()), (base, True))
        instalar.assert_not_called()
        mensaje = confirmar.call_args.args[0]
        for texto in ("Pillow", "ReportLab", "charset-normalizer", "PDF", "PyPI", "HTML", "pip"):
            self.assertIn(texto, mensaje)

    def test_reutiliza_entorno_verificado_sin_pedir_permiso(self):
        _, python = preparar.entorno_local(RAIZ)
        confirmar = Mock()
        with patch.object(preparar, "paquetes_disponibles", return_value=True), \
             patch.object(preparar, "preparar_entorno") as instalar:
            self.assertEqual(preparar.elegir_python(RAIZ, Path(sys.executable), confirmar, Mock()), (python, False))
        confirmar.assert_not_called()
        instalar.assert_not_called()

    @unittest.skipUnless(importlib.util.find_spec("ensurepip"), "Este Python no incluye ensurepip")
    def test_consentimiento_habilita_instalacion_y_error_abre_modo_basico(self):
        base = Path(sys.executable)
        carpeta, python = preparar.entorno_local(RAIZ)
        origen = (RAIZ / "dependencias" / "requirements-windows-x64.txt", RAIZ / "dependencias" / "wheels", True)
        confirmar, avisar = Mock(return_value=True), Mock()
        with patch.object(preparar, "paquetes_disponibles", return_value=False), \
             patch.object(preparar, "origen_paquetes", return_value=origen), \
             patch.object(preparar, "preparar_entorno") as instalar:
            self.assertEqual(preparar.elegir_python(RAIZ, base, confirmar, avisar), (python, False))
            instalar.assert_called_once_with(RAIZ, carpeta, python, origen)
            self.assertIn("sin internet", confirmar.call_args.args[0])
            instalar.side_effect = subprocess.CalledProcessError(1, "pip")
            self.assertEqual(preparar.elegir_python(RAIZ, base, confirmar, avisar), (base, True))
        aviso, = avisar.call_args.args
        self.assertIn("modo básico", aviso)

    def test_instalacion_offline_bloquea_indices_y_verifica_hashes(self):
        carpeta, python = preparar.entorno_local(RAIZ)
        origen = (RAIZ / "dependencias" / "requirements-windows-x64.txt", RAIZ / "dependencias" / "wheels", True)
        with patch.object(preparar.subprocess, "run", return_value=Mock(returncode=0)) as ejecutar, \
             patch.object(preparar, "paquetes_disponibles", return_value=True):
            preparar.preparar_entorno(RAIZ, carpeta, python, origen)
        comando = next(llamada.args[0] for llamada in ejecutar.call_args_list if "install" in llamada.args[0])
        for opcion in ("--no-index", "--find-links", "--require-hashes", "--isolated", "--only-binary=:all:"):
            self.assertIn(opcion, comando)
        self.assertNotIn("--index-url", comando)

    def test_archivos_oficiales_coinciden_con_el_bloqueo(self):
        requisitos = (RAIZ / "dependencias" / "requirements-windows-x64.txt").read_text(encoding="utf-8")
        esperados = set(re.findall(r"--hash=sha256:([0-9a-f]{64})", requisitos))
        archivos = list((RAIZ / "dependencias" / "wheels").glob("*.whl"))
        self.assertEqual(len(archivos), 7)
        self.assertEqual({hashlib.sha256(p.read_bytes()).hexdigest() for p in archivos}, esperados)

    def test_diagnostico_no_pide_instalar_ni_abre_ventana(self):
        with patch.object(preparar, "paquetes_disponibles", return_value=False), \
             patch.object(preparar, "elegir_python") as elegir, \
             patch.object(preparar.subprocess, "call", return_value=0) as llamar:
            self.assertEqual(preparar.main(["--diagnostico"]), 0)
        elegir.assert_not_called()
        self.assertIn("--diagnostico", llamar.call_args.args[0])
