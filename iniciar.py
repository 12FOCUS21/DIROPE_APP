"""Entrada local. No necesita instalar el paquete ni descargar bibliotecas."""

import argparse
import logging
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))


def main():
    parser = argparse.ArgumentParser(description="DIROPE Calc: aplicación local de productividad")
    parser.add_argument("--comprobar-interfaz", action="store_true", help="Carga y calcula todos los ejemplos y cierra la ventana")
    parser.add_argument("--diagnostico", action="store_true", help="Muestra versiones y rutas para soporte, sin abrir ventanas ni modificar datos")
    opciones = parser.parse_args()
    if opciones.diagnostico:
        from dirope.diagnostico import informacion_entorno
        print(informacion_entorno())
        return
    from dirope.historial import carpeta_local
    carpeta = carpeta_local()
    carpeta.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=carpeta / "registro.log", encoding="utf-8", level=logging.ERROR,
                        format="%(asctime)s %(levelname)s %(message)s")
    from dirope.interfaz.ventana import Aplicacion
    temporal_pruebas = TemporaryDirectory() if opciones.comprobar_interfaz else None
    app = Aplicacion(Path(temporal_pruebas.name) if temporal_pruebas else None)
    try:
        if opciones.comprobar_interfaz:
            from unittest.mock import patch

            errores_interfaz = []
            app.report_callback_exception = lambda tipo, error, traza: errores_interfaz.append(error)
            app.withdraw()
            assert not app.lateral.winfo_manager()
            total = 0
            for panel in app.paneles:
                app.mostrar(panel.modulo.clave)
                assert app.lateral.winfo_manager() == "pack"
                for nombre in panel.modulo.ejemplos:
                    panel.ejemplo.set(nombre)
                    panel.cargar_ejemplo(confirmar=False)
                    assert panel.etapa == 0 and panel.resultado is None
                    assert not panel.mostrar_etapa(4)
                    assert panel.avanzar() and panel.etapa == 1
                    assert panel.avanzar() and panel.etapa == 2
                    assert panel.analisis is not None and panel.resultado is None
                    assert not panel.mostrar_etapa(3)
                    assert panel.avanzar() and panel.etapa == 3
                    assert panel.resultado.pasos
                    assert not panel.grafico.serie
                    assert "4. DESARROLLO" in panel.informe_completo()
                    assert panel.identificador and not panel.borrador
                    guardado = app.historial.abrir(panel.identificador)
                    assert guardado["resolucion"]["informe"] == panel.informe_completo()
                    assert not panel.mostrar_etapa(4)
                    for _ in panel.pasos_principales():
                        assert panel.avanzar()
                    assert panel.etapa == 4
                    assert bool(panel.grafico.serie) == bool(panel.resultado.serie)
                    informe = panel.informe_completo()
                    for seccion in ("1. PLANTEAMIENTO", "2. ANÁLISIS DE DATOS", "3. IDENTIFICACIÓN", "4. DESARROLLO", "5. RESULTADOS"):
                        assert seccion in informe
                    for ancho, columnas in ((900, 3), (500, 2), (220, 1)):
                        panel.kpis.organizar(ancho)
                        assert panel.kpis.columnas == min(columnas, len(panel.kpis.tarjetas))
                        for indice, tarjeta in enumerate(panel.kpis.tarjetas):
                            posicion = tarjeta.grid_info()
                            assert int(posicion["row"]) == indice // panel.kpis.columnas
                            assert int(posicion["column"]) == indice % panel.kpis.columnas
                    panel.mostrar_etapa(3)
                    if len(panel.pasos_principales()) > 1:
                        panel.retroceder()
                        assert panel.paso_actual == len(panel.pasos_principales()) - 2
                        panel.avanzar()
                    panel.avanzar()
                    assert panel.etapa == 4
                    resultado_guiado = panel.resultado
                    assert panel.ver_resultado() and panel.resultado is resultado_guiado
                    assert panel.mostrar_etapa(3) and panel.resultado is resultado_guiado
                    assert panel.mostrar_etapa(4)
                    total += 1
                # Un dato incorrecto muestra un mensaje dentro del formulario, sin cerrar la app.
                panel.variables["unidad_salida"].set("")
                assert panel.resultado is None and panel.analisis is None and panel.etapa == 1
                assert not panel.ver_resultado()
                assert not panel.avanzar()
                assert "Revisa los datos" in panel.estado.get()
                assert not panel.mostrar_etapa(4)
                panel.cargar_ejemplo(confirmar=False)
                assert panel.etapa == 0
                panel.transicion.cancelar()
                panel.transicion.animar(12)
                assert int(panel.transicion.actual.place_info()["x"]) == 0
            # Caso propio, sin cargar ningún ejemplo.
            panel = app.paneles[0]
            panel.objetivo.set("Comparar escenarios")
            panel.cambiar_modo()
            panel.limpiar(confirmar=False)
            assert not panel.texto_enunciado()
            panel.titulo.set("Caso nuevo del profesor")
            for clave, valor in dict(antes=240, despues=360, insumo_antes=30, insumo_despues=36, unidad_salida="piezas", unidad_recurso="h").items():
                panel.variables[clave].set(str(valor))
            app.mostrar("un_factor")
            datos = panel.recoger_datos()
            app.mostrar("multifactor")
            app.mostrar("un_factor")
            assert panel.recoger_datos() == datos
            for _ in range(3):
                assert panel.avanzar()
            assert panel.resultado.indicadores[-1].resultado == 25
            for _ in panel.pasos_principales():
                assert panel.avanzar()
            assert panel.etapa == 4 and "Caso nuevo del profesor" in panel.informe_completo()
            panel.enunciado.insert("end", " Corrección del planteamiento.")
            panel.enunciado_modificado()
            assert panel.etapa == 0 and panel.resultado is None and panel.analisis is None
            app.movimiento.set(False)
            app.cambiar_movimiento()
            assert all(p.grafico.tarea is None for p in app.paneles)
            assert all(p.transicion.tarea is None for p in app.paneles)
            app.mostrar(None)
            assert app.activo is None and not app.lateral.winfo_manager()
            panel.limpiar(confirmar=False)
            app.abrir_demo()
            assert app.activo == "un_factor"
            assert app.paneles[0].resultado is None and app.paneles[0].etapa == 0
            app.decimales.set(3)
            app.actualizar_formato()
            app.update_idletasks()
            datos_cargados = panel.recoger_datos()
            with patch("dirope.interfaz.asistente.messagebox.askyesno", return_value=False):
                assert not panel.limpiar()
                assert not panel.cargar_ejemplo()
            assert datos_cargados == panel.recoger_datos()
            panel.limpiar(confirmar=False)
            panel.objetivo.set("Recurso requerido")
            panel.cambiar_modo()
            panel.variables["antes"].set("72")
            panel.variables["ritmo"].set("4.5")
            assert panel.avanzar() and panel.avanzar() and panel.avanzar() and panel.avanzar()
            assert panel.resultado.pasos[0].resultado == 16 and not panel.grafico.serie
            app.update_idletasks()
            assert not panel.vista_grafico.serie
            with TemporaryDirectory() as carpeta_temporal:
                destino = Path(carpeta_temporal) / "informe.html"
                with patch("dirope.interfaz.asistente.filedialog.asksaveasfilename", return_value=str(destino)):
                    panel.exportar()
                panel.copiar()
                assert "Recurso requerido" in app.clipboard_get()
                html = destino.read_text(encoding="utf-8")
                assert "Recurso requerido" in html and "16.000 h-persona" in html
                assert '<ol class="pasos">' in html and "<mfrac>" in html and "<table" not in html
                vista = panel.ver_informe_completo()
                assert vista.title() == "Informe completo"
                vista.destroy()
                from importlib.util import find_spec
                if find_spec("reportlab"):
                    pdf = Path(carpeta_temporal) / "informe.pdf"
                    with patch("dirope.interfaz.asistente.filedialog.asksaveasfilename", return_value=str(pdf)):
                        panel.exportar_pdf()
                    assert pdf.read_bytes().startswith(b"%PDF-")
                from dirope.informe import PDFNoDisponible
                alterno = Path(carpeta_temporal) / "alternativa.html"
                with patch("dirope.interfaz.asistente.informe_pdf", side_effect=PDFNoDisponible("Motor ausente")), \
                     patch("dirope.interfaz.asistente.messagebox.askyesno", return_value=True), \
                     patch("dirope.interfaz.asistente.filedialog.asksaveasfilename", side_effect=(str(destino.with_suffix('.pdf')), str(alterno))):
                    panel.exportar_pdf()
                assert alterno.read_text(encoding="utf-8") == html

            panel = app.paneles[1]
            panel.ejemplo.set("Lakefront inicial (T4)")
            assert panel.cargar_ejemplo(confirmar=False)
            panel.objetivo.set("Comparar alternativas")
            panel.cambiar_modo()
            panel.escenario.set("Alternativa")
            panel.duplicar_escenario()
            assert panel.variables["produccion_final"].get() == "1000"
            assert len(panel.recoger_datos()["insumos"]) == 8
            assert panel.avanzar()
            app.deiconify()
            escala_original = float(app.tk.call("tk", "scaling"))
            for ancho, alto, escala in ((960, 600, escala_original), (1280, 760, escala_original),
                                        (960, 600, escala_original * 1.25)):
                app.tk.call("tk", "scaling", escala)
                app.geometry(f"{ancho}x{alto}")
                for clave in (None, *(p.modulo.clave for p in app.paneles)):
                    app.mostrar(clave)
                    app.update()
                    if clave is not None:
                        activo = next(p for p in app.paneles if p.modulo.clave == clave)
                        assert activo.siguiente.winfo_viewable()
                        assert all(b.winfo_width() > 75 for b in activo.botones_etapas)
                        if clave == "multifactor":
                            assert panel.vista_grafico.serie == (("Inicial", 0.025), ("Alternativa", 0.025))
                            medidas = panel.tabla.winfo_width(), panel.cabecera_tabla.winfo_reqwidth()
                            assert medidas[0] >= medidas[1], (ancho, alto, medidas)
                            assert bool(panel.barra_tabla.winfo_manager()) == (
                                panel.tabla.winfo_width() > panel.lienzo_tabla.winfo_width())
            app.tk.call("tk", "scaling", escala_original)
            activo = panel.variables["produccion_final"]
            activo.set("")
            app.update()
            assert not panel.vista_grafico.serie
            activo.set("1000")
            app.update()
            assert panel.vista_grafico.serie
            assert panel.ver_resultado()
            with TemporaryDirectory() as carpeta_temporal:
                from importlib.util import find_spec
                from dirope.historial import Historial

                carpeta_prueba = Path(carpeta_temporal)
                app.historial = Historial(carpeta_prueba / "calculos")
                panel.identificador = None
                panel.titulo.set("Caso persistente")
                assert panel.ver_resultado() and app.guardar_calculo(panel)
                identificador = panel.identificador
                if find_spec("reportlab"):
                    destino = carpeta_prueba / "informe.pdf"
                    with patch("dirope.interfaz.asistente.filedialog.asksaveasfilename", return_value=str(destino)):
                        panel.exportar_pdf()
                    assert destino.read_bytes().startswith(b"%PDF-")
                assert not errores_interfaz, errores_interfaz
                app.destroy()
                app = Aplicacion(carpeta_prueba / "calculos")
                app.report_callback_exception = lambda tipo, error, traza: errores_interfaz.append(error)
                app.withdraw()
                assert app.abrir_guardado(identificador)
                panel = app.paneles[1]
                assert panel.etapa == 4 and panel.titulo.get() == "Caso persistente"
                panel.variables["produccion_final"].set("1250")
                assert panel.ver_resultado() and app.guardar_calculo(panel)
                assert panel.resultado.serie[-1] == ("Alternativa", 0.03125)
                nuevos_datos = app.historial.abrir(identificador)["datos"]
                assert nuevos_datos["produccion_final"] == "1250"
                assert len(app.historial.listar()[0]) == 1
                anterior = app.historial.abrir(identificador)
                # Fallar al escribir no borra la versión anterior ni marca el borrador como guardado.
                panel.variables["produccion_final"].set("1500")
                with patch.object(app.historial, "guardar", side_effect=OSError("Disco lleno")):
                    assert panel.ver_resultado()
                assert panel.borrador and "No se pudo guardar" in panel.estado.get()
                assert app.historial.abrir(identificador) == anterior
                assert app.guardar_calculo(panel) and not panel.borrador
                # Copiar conserva el ejercicio anterior y el nuevo tiene su propio identificador.
                assert app.guardar_calculo(panel, copia=True)
                copia = panel.identificador
                assert copia != identificador and len(app.historial.listar()[0]) == 2
                biblioteca = app.administrar()
                app.update()
                controles = []
                pendientes = list(biblioteca.winfo_children())
                while pendientes:
                    control = pendientes.pop()
                    controles.append(control)
                    pendientes.extend(control.winfo_children())
                from tkinter import ttk
                lista = next(c for c in controles if isinstance(c, ttk.Treeview))
                assert len(lista.get_children()) == 2
                entrada = next(c for c in controles if isinstance(c, ttk.Entry)
                               and not isinstance(c, ttk.Combobox))
                entrada.insert(0, "sin coincidencias")
                assert not lista.get_children()
                entrada.delete(0, "end")
                assert len(lista.get_children()) == 2
                lista.selection_set(copia)
                next(c for c in controles if isinstance(c, ttk.Button)
                     and c.cget("text") == "Ver resolución guardada").invoke()
                app.update()
                assert any(c.winfo_class() == "Toplevel" for c in biblioteca.winfo_children())
                from dirope.interfaz.temas import PALETAS
                from dirope.modulos.campos import grupos_datos
                from dirope.interfaz.matematicas import Formula
                panel_formula = next(p for p in app.paneles if p.modulo.clave == "un_factor")
                for p in app.paneles:
                    grupos = list(grupos_datos(p.modulo.clave, p.objetivo.get()))
                    assert {nombre for nombre, control in p.encabezados_datos.items() if control.winfo_manager()} == {
                        nombre for nombre, _ in grupos}
                    assert p.entradas == [p.marcos[clave][1] for _, campos in grupos for clave in campos]
                muestra = Formula(panel_formula.metodo, text="P = Q / I")
                muestra.pack(fill="x")
                assert any(muestra.type(trazo) == "line" for trazo in muestra.find_all())
                datos_antes = [p.recoger_datos() for p in app.paneles]
                for tema in ("Oscuro", "Claro", "Oscuro"):
                    app.tema.set(tema)
                    assert app.cambiar_tema()
                    app.update()
                    colores = PALETAS[tema]
                    assert ttk.Style(app).layout("Panel.TFrame")[0][0] == f"Dirope.{tema}.Panel.TFrame"
                    assert ttk.Style(app).layout("Header.TCombobox")[0][0] == f"Dirope.{tema}.Header.TCombobox"
                    assert ttk.Style(app).lookup("Header.TFrame", "background") == colores["cabecera"]
                    assert muestra.cget("background") == colores["superficie"]
                    assert all(muestra.itemcget(trazo, "fill") == colores["texto"] for trazo in muestra.find_all())
                    for boton in app.botones_nav.values():
                        assert boton.cget("image") and boton.cget("text")
                    assert ttk.Style(app).lookup("TEntry", "fieldbackground") == colores["superficie"]
                    assert ttk.Style(app).lookup("Treeview", "foreground") == colores["texto"]
                    for p in app.paneles:
                        assert p.enunciado.cget("background") == colores["suave"]
                        assert p.enunciado.cget("foreground") == colores["texto"]
                        assert p.grafico.cget("background") == colores["superficie"]
                        for elemento in p.grafico.find_all():
                            if p.grafico.type(elemento) == "text":
                                assert p.grafico.itemcget(elemento, "fill") in (colores["texto"], colores["secundario"])
                    pendientes = [biblioteca]
                    while pendientes:
                        control = pendientes.pop()
                        pendientes.extend(control.winfo_children())
                        if control.winfo_class() == "Text":
                            assert control.cget("background") == colores["superficie"]
                            assert control.cget("foreground") == colores["texto"]
                    assert datos_antes == [p.recoger_datos() for p in app.paneles]
                assert app.preferencias.leer_tema() == "Oscuro"
                biblioteca.destroy()
                app.historial.eliminar(copia)
                app.historial.eliminar(identificador)
                assert app.historial.listar() == ([], 0)
                # Los casos de los documentos iniciales también se abren como ejercicios editables.
                from dirope.practica_inicial import guardar_practica
                practica = guardar_practica(app.historial)
                for registro in practica:
                    assert app.abrir_guardado(registro["id"])
                assert len(app.historial.listar()[0]) == 9
                app.destroy()
                app = Aplicacion(carpeta_prueba / "calculos")
                app.report_callback_exception = lambda tipo, error, traza: errores_interfaz.append(error)
                app.withdraw()
                assert app.nombre_tema == "Oscuro" and app.tema.get() == "Oscuro"
                assert len(app.historial.listar()[0]) == 9
            assert not errores_interfaz, errores_interfaz
            print(f"Interfaz verificada: {total} ejemplos, datos propios, despeje, duplicación de escenario, "
                  "navegación, borradores, acceso directo, persistencia, informes, gráficos y tamaños 960×600 y 1280×760.")
        else:
            app.mainloop()
    finally:
        if opciones.comprobar_interfaz:
            app.destroy()
            temporal_pruebas.cleanup()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.exception("No se pudo iniciar o verificar la aplicación")
        print("No se pudo iniciar DIROPE Calc. Revisa Python/Tkinter y el archivo registro.log.", file=sys.stderr)
        raise
