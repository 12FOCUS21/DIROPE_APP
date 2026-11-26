"""Ejercita controles reales en orden reproducible, sin escribir en la biblioteca personal."""

from collections import Counter
from pathlib import Path
from random import Random
import sys
from tempfile import TemporaryDirectory
import tkinter as tk
from tkinter import ttk
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dirope.banco import generar_banco
from dirope.interfaz.opciones import MenuRedondeado, SelectorRedondeado
from dirope.interfaz.ventana import Aplicacion


def controles(contenedor):
    for hijo in contenedor.winfo_children():
        if not isinstance(hijo, tk.Toplevel):
            yield hijo
            yield from controles(hijo)


def comprobar(total=180):
    azar = Random(26112026)
    banco = generar_banco(3)
    errores, cuenta = [], Counter()
    with TemporaryDirectory() as temporal:
        carpeta = Path(temporal)
        app = Aplicacion(carpeta / "biblioteca")
        app.report_callback_exception = lambda tipo, error, traza: errores.append(error)
        try:
            app.geometry("960x600+25+25")
            app.update()
            estilo = ttk.Style(app)
            botones = [c for c in controles(app) if isinstance(c, MenuRedondeado)]
            ajustes = next(c for c in botones if c.cget("text").startswith("Ajustes"))
            assert max(ajustes.winfo_height(), app.selector_tema.winfo_height()) <= 48
            assert ajustes.winfo_reqwidth() >= 65
            assert estilo.lookup("TButton", "font") and "bold" in estilo.lookup("TButton", "font")

            def abrir(selector):
                if isinstance(selector, SelectorRedondeado):
                    selector.event_generate("<ButtonPress-1>", x=4, y=4)
                else:
                    selector.invoke()
                app.update()
                lista = app.opciones_abiertas
                assert lista and lista.grab_current() == lista
                assert all(b.cget("style") in ("Popup.TButton", "PopupSelected.TButton") for b in lista.botones)
                assert all(b.winfo_height() <= 46 and b.winfo_width() >= b.winfo_reqwidth() for b in lista.botones)
                return lista

            popup = abrir(app.selector_tema)
            popup.botones[0].focus_force()
            popup.botones[0].event_generate("<Down>")
            app.update()
            assert popup.focus_get() == popup.botones[1]
            popup.botones[1].invoke()
            app.update()
            assert app.nombre_tema == "Oscuro" and app.grab_current() is None
            popup = abrir(ajustes)
            popup.botones[0].invoke()
            app.update()
            assert app.movimiento.get() and app.grab_current() is None
            ajustes.invoke()
            app.opciones_abiertas.botones[0].invoke()
            assert not app.movimiento.get()

            def destino(**kwargs):
                ext = kwargs["defaultextension"]
                cuenta[f"archivo{ext}"] += 1
                return str(carpeta / f"informe{ext}") if azar.random() < .7 else ""

            with patch("tkinter.messagebox.askyesno", side_effect=lambda *a, **kw: azar.random() < .6), \
                 patch("tkinter.filedialog.asksaveasfilename", side_effect=destino):
                caso = banco[0]
                panel = app.paneles[0]
                panel.cargar_datos(caso["nombre"], caso["enunciado"], caso["datos"])
                app.botones_nav[panel.modulo.clave].invoke()
                assert panel.ver_resultado()
                app.update()
                exportar = next(c for c in controles(panel) if isinstance(c, MenuRedondeado) and
                                c.cget("text").startswith("Exportar"))
                for indice, extension in enumerate((".pdf", ".html")):
                    archivo = carpeta / f"verificado{extension}"
                    with patch("tkinter.filedialog.asksaveasfilename", return_value=str(archivo)):
                        abrir(exportar).botones[indice].invoke()
                    assert archivo.is_file()
                for i in range(total):
                    op = azar.randrange(10)
                    panel = next((p for p in app.paneles if p.modulo.clave == app.activo), None)
                    if op == 0 or i == 0:
                        app.botones_nav[azar.choice(list(app.botones_nav))].invoke()
                        cuenta["navegación"] += 1
                    elif op == 1 or panel is None:
                        caso = azar.choice(banco)
                        panel = next(p for p in app.paneles if p.modulo.clave == caso["modulo"])
                        panel.cargar_datos(caso["nombre"], caso["enunciado"], caso["datos"])
                        app.botones_nav[panel.modulo.clave].invoke()
                        cuenta["carga"] += 1
                    elif op == 2:
                        popup = abrir(app.selector_tema)
                        popup.botones[azar.randrange(2)].invoke()
                        cuenta["tema"] += 1
                    elif op == 3:
                        app.geometry(azar.choice(("960x600+25+25", "1280x760+25+25")))
                        cuenta["tamaño"] += 1
                    elif op == 4:
                        panel.directo.invoke()
                        cuenta["resultado"] += 1
                    else:
                        candidatos = [c for c in controles(panel) if isinstance(c, ttk.Button) and c.winfo_viewable()]
                        if op == 5:
                            candidatos = [c for c in candidatos if isinstance(c, MenuRedondeado)] or candidatos
                        if op == 6 and panel.etapa == 0:
                            candidatos.append(panel.selector_modo)
                        if candidatos:
                            control = azar.choice(candidatos)
                            if isinstance(control, (MenuRedondeado, SelectorRedondeado)):
                                popup = abrir(control)
                                if azar.random() < .3:
                                    popup.cancelar()
                                else:
                                    azar.choice(popup.botones).invoke()
                                cuenta["opciones"] += 1
                            else:
                                retorno = control.invoke()
                                if isinstance(retorno, tk.Toplevel):
                                    retorno.destroy()
                                cuenta["botones"] += 1
                    app.update()
                    assert not errores, (i, errores)
                    assert app.grab_current() is None and app.opciones_abiertas is None
                    for p in app.paneles:
                        assert 0 <= p.etapa <= p.habilitada <= 4, (i, p.etapa, p.habilitada)
                        assert p.modo_actual == p.objetivo.get()
                        if p.etapa in (3, 4):
                            assert p.resultado is not None and p.analisis is not None
            assert cuenta["opciones"] and cuenta["botones"] and cuenta["tema"]
        finally:
            app.destroy()
    print(f"{total} acciones mixtas; 0 errores de interfaz. Cobertura: {dict(cuenta)}")


if __name__ == "__main__":
    comprobar()
