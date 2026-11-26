"""Prueba intensiva de Tkinter, aislada de la biblioteca y preferencias personales."""

from itertools import permutations
import json
import math
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dirope.banco import generar_banco
from dirope.interfaz.ventana import Aplicacion


def comprobar():
    casos = generar_banco()
    errores = []
    transiciones = 0
    with TemporaryDirectory() as temporal:
        app = Aplicacion(Path(temporal))
        app.report_callback_exception = lambda tipo, error, traza: errores.append(error)
        app.withdraw()
        paneles = {p.modulo.clave: p for p in app.paneles}
        try:
            for indice, caso in enumerate(casos):
                panel = paneles[caso["modulo"]]
                panel.cargar_datos(caso["nombre"], caso["enunciado"], caso["datos"])
                if indice % 2:
                    assert panel.ver_resultado(), caso["nombre"]
                else:
                    for _ in range(3):
                        assert panel.avanzar(), caso["nombre"]
                    assert panel.etapa == 3 and panel.identificador
                    for _ in panel.pasos_principales():
                        assert panel.avanzar(), caso["nombre"]
                app.update()
                assert not errores, (caso["nombre"], errores)
                assert not panel.borrador and panel.etapa == 4, caso["nombre"]
                valores = {p.titulo: p.resultado for p in panel.resultado.pasos}
                for titulo, esperado in caso["esperados"].items():
                    assert math.isclose(valores[titulo], esperado, rel_tol=1e-10, abs_tol=1e-8), (caso["nombre"], titulo)
                guardado = app.historial.abrir(panel.identificador)
                assert guardado["resolucion"]["informe"] == panel.informe_completo()
                if indice % 25 == 0:
                    app.tema.set("Oscuro" if indice % 50 else "Claro")
                    assert app.cambiar_tema()
            assert len(app.historial.listar()[0]) == 1000
            # Todos los pares dirigidos, con y sin ejercicio guardado, en ambos temas.
            muestras = {(c["modulo"], c["datos"]["modo"]): c for c in casos}
            for tema in ("Claro", "Oscuro"):
                app.tema.set(tema)
                app.cambiar_tema()
                for panel in app.paneles:
                    for origen, destino in permutations(panel.modos, 2):
                        for guardar in (False, True):
                            panel.borradores_modo.clear()
                            caso = muestras[(panel.modulo.clave, origen)]
                            panel.cargar_datos(caso["nombre"], caso["enunciado"], caso["datos"])
                            if guardar:
                                assert panel.ver_resultado()
                            datos = panel.recoger_datos()
                            identificador = panel.identificador
                            anterior = app.historial.abrir(identificador) if identificador else None
                            panel.objetivo.set(destino)
                            panel.selector_modo.event_generate("<<ComboboxSelected>>")
                            app.update()
                            assert panel.modo_actual == destino
                            assert panel.identificador is None
                            assert panel.titulo.get() == "" and panel.texto_enunciado() == ""
                            assert panel.resultado is None and panel.etapa == 0
                            assert not panel.ver_resultado(), (origen, destino, "No debe calcular con datos heredados")
                            ejemplos = tuple(panel.ejemplo.cget("values"))
                            assert all(panel.modulo.ejemplos[n].get("modo", next(iter(panel.modos))) == destino for n in ejemplos)
                            panel.objetivo.set(origen)
                            panel.selector_modo.event_generate("<<ComboboxSelected>>")
                            app.update()
                            assert datos == panel.recoger_datos(), (origen, destino, "Borrador alterado")
                            assert panel.identificador == identificador
                            if anterior:
                                assert app.historial.abrir(identificador) == anterior
                            # También volver a una opción que ya tiene otro borrador propio.
                            panel.objetivo.set(destino)
                            panel.selector_modo.event_generate("<<ComboboxSelected>>")
                            otro = muestras[(panel.modulo.clave, destino)]
                            panel.cargar_datos(otro["nombre"], otro["enunciado"], otro["datos"])
                            if guardar:
                                assert panel.ver_resultado()
                            otros_datos = panel.recoger_datos()
                            otro_id = panel.identificador
                            if guardar:
                                assert otro_id != identificador
                            panel.objetivo.set(origen)
                            panel.selector_modo.event_generate("<<ComboboxSelected>>")
                            assert panel.recoger_datos() == datos and panel.identificador == identificador
                            panel.objetivo.set(destino)
                            panel.selector_modo.event_generate("<<ComboboxSelected>>")
                            assert panel.recoger_datos() == otros_datos and panel.identificador == otro_id
                            transiciones += 1
            # Banco visible: todos los casos, filtro por método y apertura sin modificar la biblioteca.
            from tkinter import ttk
            banco = app.abrir_banco()
            app.update()
            controles = []
            pendientes = [banco]
            while pendientes:
                control = pendientes.pop()
                controles.append(control)
                pendientes.extend(control.winfo_children())
            lista = next(c for c in controles if isinstance(c, ttk.Treeview))
            selector = next(c for c in controles if isinstance(c, ttk.Combobox))
            assert len(lista.get_children()) == 1000
            selector.set("Valor por calidad")
            # La variable del filtro cambia al establecer el selector.
            app.update()
            assert len(lista.get_children()) == 100
            lista.selection_set(lista.get_children()[0])
            cantidad_antes = len(app.historial.listar()[0])
            with patch("dirope.interfaz.asistente.messagebox.askyesno", return_value=True):
                next(c for c in controles if isinstance(c, ttk.Button)
                     and c.cget("text") == "Abrir ejercicio para resolver").invoke()
            assert not banco.winfo_exists()
            assert len(app.historial.listar()[0]) == cantidad_antes
            assert app.paneles[1].objetivo.get() == "Valor por calidad"
            # Un borrador en una opción oculta también debe provocar aviso de cierre.
            panel = app.paneles[0]
            panel.objetivo.set("Comparar escenarios")
            panel.selector_modo.event_generate("<<ComboboxSelected>>")
            panel.titulo.set("Borrador que no se debe perder")
            panel.objetivo.set("Recurso requerido")
            panel.selector_modo.event_generate("<<ComboboxSelected>>")
            assert panel.tiene_borradores
            with patch("dirope.interfaz.ventana.messagebox.askyesno", return_value=False) as aviso:
                app.cerrar()
                assert aviso.called and app.winfo_exists()
            assert not errores, errores
        finally:
            app.destroy()
    resumen = dict(ejercicios=1000, casos_por_modo=100, modos=10, secuencias_cambio=transiciones,
                   temas=["Claro", "Oscuro"], errores_interfaz=len(errores))
    print(json.dumps(resumen, ensure_ascii=False))


if __name__ == "__main__":
    comprobar()
