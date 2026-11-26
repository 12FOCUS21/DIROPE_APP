"""Persistencia completa, búsqueda y protección de la minibase local."""

from dataclasses import asdict
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dirope.historial import Historial
from dirope.modulos import MODULOS


class Biblioteca(unittest.TestCase):
    def setUp(self):
        self.temporal = TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.historial = Historial(Path(self.temporal.name))

    def guardar(self, **opciones):
        return self.historial.guardar("un_factor", "Práctica de cajas", "Producción del turno mañana",
                                      {"modo": "Comparación", "valor": "10.25"}, **opciones)

    def test_resoluciones_completas_sin_redondear_y_reinicio(self):
        for modulo in MODULOS:
            for nombre, datos in modulo.ejemplos.items():
                resultado = asdict(modulo.calcular(datos))
                resolucion = {"resultado": resultado, "informe": "Fórmulas y procedimiento: Δ%", "decimales": 6}
                registro = self.historial.guardar(modulo.clave, nombre, "", datos, resolucion=resolucion)
                nuevo = Historial(self.historial.carpeta).abrir(registro["id"])
                self.assertEqual(nuevo["resolucion"], json.loads(json.dumps(resolucion)))

    def test_busqueda_por_nombre_enunciado_datos_y_modulo(self):
        registro = self.guardar()
        for consulta in ("PRÁCTICA", "mañana", "10.25", "comparación", "  cajas  "):
            self.assertEqual(self.historial.listar(consulta), ([registro], 0))
        self.assertEqual(self.historial.listar("inexistente"), ([], 0))
        self.assertEqual(self.historial.listar(modulo="capacidad"), ([], 0))
        self.assertEqual(self.historial.listar("cajas", "un_factor"), ([registro], 0))

    def test_repetir_guardado_no_duplica_ni_cambia_fecha(self):
        resolucion = {"resultado": {"serie": (("Inicial", 1.23456789),)}, "informe": "Prueba"}
        registro = self.guardar(resolucion=resolucion)
        repetido = self.guardar(identificador=registro["id"], resolucion=resolucion)
        self.assertEqual(registro, repetido)
        self.assertEqual(self.historial.listar(), ([registro], 0))

    def test_registro_antiguo_admite_resolucion_sin_perder_identidad(self):
        registro = self.guardar()
        self.assertNotIn("resolucion", self.historial.abrir(registro["id"]))
        resolucion = {"resultado": {"pasos": []}, "informe": "Procedimiento completo"}
        nuevo = self.guardar(identificador=registro["id"], resolucion=resolucion)
        self.assertEqual(nuevo["datos"], registro["datos"])
        self.assertEqual(self.historial.listar(), ([nuevo], 0))

    def test_error_escritura_conserva_original_y_limpia_temporal(self):
        registro = self.guardar()
        with patch("dirope.historial.os.fsync", side_effect=OSError("Disco lleno")):
            with self.assertRaises(OSError):
                self.guardar(identificador=registro["id"], resolucion={"resultado": {}, "informe": "Nuevo"})
        self.assertEqual(self.historial.abrir(registro["id"]), registro)
        self.assertFalse(list(self.historial.carpeta.glob("*.tmp")))

    def test_rechaza_resolucion_invalida_y_no_finitos(self):
        for resolucion in ({}, "texto", {"resultado": {}, "informe": 42},
                           {"resultado": {"valor": float("nan")}, "informe": ""},
                           {"resultado": {"valor": float("inf")}, "informe": ""}):
            with self.subTest(resolucion=resolucion), self.assertRaises(ValueError):
                self.guardar(resolucion=resolucion)
        self.assertEqual(self.historial.listar(), ([], 0))

    def test_copia_independiente_y_eliminacion(self):
        primero = self.guardar()
        segundo = self.guardar()
        self.assertNotEqual(primero["id"], segundo["id"])
        self.historial.eliminar(segundo["id"])
        self.assertEqual(self.historial.listar(), ([primero], 0))

    def test_rechaza_rutas_fuera_de_biblioteca(self):
        for identificador in ("../ajeno", "C:/ajeno", "sin-uuid"):
            with self.subTest(identificador=identificador), self.assertRaises(ValueError):
                self.historial.abrir(identificador)
