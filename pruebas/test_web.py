"""Regresiones del puente de la edición de navegador."""

import json
from pathlib import Path
import subprocess
import sys
import unittest
from tempfile import TemporaryDirectory
from zipfile import ZipFile

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "herramientas"))

from dirope.analisis import analizar_datos
from dirope.entradas import NOTA_NO_CONFORMES
from dirope.informe import informe_html, valor_paso
from dirope.modulos import MODULOS
from dirope.modulos.campos import MODOS
from dirope.practica_inicial import casos_complementarios, casos_practica
from dirope.web import catalogo, resolver
from preparar_web import empaquetar_nucleo


def calcular(modulo, datos, titulo="Caso", enunciado="Enunciado"):
    return json.loads(resolver(json.dumps(dict(modulo=modulo, datos=datos, titulo=titulo, enunciado=enunciado))))


class EdicionWeb(unittest.TestCase):
    def test_catalogo_y_ejemplos_coinciden_con_el_motor(self):
        catalogado = json.loads(catalogo())["modulos"]
        self.assertEqual(len(catalogado), len(MODULOS))
        for item, modulo in zip(catalogado, MODULOS):
            self.assertEqual(item["clave"], modulo.clave)
            self.assertEqual([m["nombre"] for m in item["modos"]], list(MODOS[modulo.clave]))
            for modo in item["modos"]:
                campos = {c["clave"] for g in modo["grupos"] for c in g["campos"]}
                self.assertEqual(campos, set(MODOS[modulo.clave][modo["nombre"]]))
                self.assertTrue(modo["ejemplos"])
                for ejemplo in modo["ejemplos"]:
                    with self.subTest(ejemplo=ejemplo["nombre"]):
                        datos = ejemplo["datos"]
                        respuesta = calcular(modulo.clave, datos)
                        resultado = modulo.calcular(datos)
                        analisis = analizar_datos(modulo.clave, datos, resultado=resultado)
                        self.assertEqual(respuesta["html"], informe_html("Caso", "Enunciado", analisis, resultado, 6))
                        if resultado.principal:
                            self.assertEqual(respuesta["principal"]["valor"], valor_paso(resultado.principal, 6))

    def test_no_conformes_ayuda_validacion_y_equivalencia(self):
        modo = json.loads(catalogo())["modulos"][0]["modos"][-1]
        self.assertEqual(modo["nota"], NOTA_NO_CONFORMES)
        datos = modo["ejemplos"][0]["datos"] | dict(antes="125", defecto_antes="5")
        cantidad = calcular("un_factor", datos)
        porcentaje = calcular("un_factor", datos | dict(medida_calidad="%", defecto_antes="4"))
        for respuesta in (cantidad, porcentaje):
            self.assertIn("120.000000 cierres", respuesta["html"])
        for dato in ("", "126", "1e-99999999999999999999"):
            self.assertIn("defecto_antes", calcular("un_factor", datos | dict(defecto_antes=dato))["errores"])
        self.assertIn("defecto_antes", calcular("un_factor", datos | dict(medida_calidad="%", defecto_antes="101"))["errores"])

    def test_errores_de_fila_y_reglas_globales(self):
        caso = dict(modo="Escenario individual", moneda="USD", unidad_salida="cajas", produccion="100")
        self.assertIn("Añade al menos una fila", calcular("multifactor", caso)["errores"]["insumos"])
        datos = caso | dict(insumos=[dict(nombre="Trabajo", cantidad="2", precio="3", directo="4")])
        self.assertIn("insumos.0.precio", calcular("multifactor", datos)["errores"])

    def test_informe_escapa_texto_editable(self):
        datos = dict(modo="Productividad individual", antes="5", insumo_antes="4",
                     recurso="Trabajo", unidad_salida="<script>", unidad_recurso="h")
        html = calcular("un_factor", datos, "<script>", "<iframe>")["html"]
        self.assertNotIn("<script>", html)
        self.assertNotIn("<iframe>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_practica_y_complementarios_se_publican_aparte_y_se_pueden_resolver(self):
        datos = json.loads(catalogo())
        self.assertEqual(datos["practica"], casos_practica())
        self.assertEqual(datos["complementarios"], casos_complementarios())
        for caso in datos["practica"] + datos["complementarios"]:
            with self.subTest(caso=caso["codigo"]):
                self.assertIn("html", calcular(caso["modulo"], caso["datos"], caso["nombre"], caso["enunciado"]))

    def test_zip_carga_sin_interfaz_de_escritorio(self):
        with TemporaryDirectory() as carpeta:
            archivo = Path(carpeta) / "dirope.zip"
            empaquetar_nucleo(archivo)
            with ZipFile(archivo) as zip_web:
                self.assertIsNone(zip_web.testzip())
                self.assertFalse(any("interfaz/" in n or "historial.py" in n for n in zip_web.namelist()))
            subprocess.run([sys.executable, "-I", "-S", "-c", "import sys; sys.path.insert(0, sys.argv[1]); "
                            "from dirope.web import catalogo; assert catalogo(); "
                            "assert 'tkinter' not in sys.modules and 'reportlab' not in sys.modules", str(archivo)],
                           check=True, timeout=20)
