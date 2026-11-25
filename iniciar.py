"""Entrada local. No necesita instalar el paquete ni descargar bibliotecas."""

import argparse
import logging
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))


def main():
    parser = argparse.ArgumentParser(description="DIROPE Calc: aplicación local de productividad")
    parser.add_argument("--comprobar-interfaz", action="store_true", help="Carga y calcula todos los ejemplos y cierra la ventana")
    opciones = parser.parse_args()
    from dirope.historial import carpeta_local
    carpeta = carpeta_local()
    carpeta.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=carpeta / "registro.log", encoding="utf-8", level=logging.ERROR,
                        format="%(asctime)s %(levelname)s %(message)s")
    from dirope.interfaz.ventana import Aplicacion
    app = Aplicacion()
    try:
        if opciones.comprobar_interfaz:
            from tempfile import TemporaryDirectory
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
                    assert panel.informe_completo() == ""
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
                app.historial.eliminar(identificador)
                assert app.historial.listar() == ([], 0)
            assert not errores_interfaz, errores_interfaz
            print(f"Interfaz verificada: {total} ejemplos, datos propios, despeje, duplicación de escenario, "
                  "navegación, borradores, acceso directo, persistencia, informes, gráficos y tamaños 960×600 y 1280×760.")
        else:
            app.mainloop()
    finally:
        if opciones.comprobar_interfaz:
            app.destroy()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.exception("No se pudo iniciar o verificar la aplicación")
        print("No se pudo iniciar DIROPE Calc. Revisa Python/Tkinter y el archivo registro.log.", file=sys.stderr)
        raise
