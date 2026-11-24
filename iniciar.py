"""Entrada local. No necesita instalar el paquete ni descargar bibliotecas."""

import argparse
import logging
import os
from pathlib import Path
import sys

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))


def main():
    parser = argparse.ArgumentParser(description="DIROPE Calc: aplicación local de productividad")
    parser.add_argument("--comprobar-interfaz", action="store_true", help="Carga y calcula todos los ejemplos y cierra la ventana")
    opciones = parser.parse_args()
    carpeta = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "DIROPE Calc"
    carpeta.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=carpeta / "registro.log", encoding="utf-8", level=logging.ERROR,
                        format="%(asctime)s %(levelname)s %(message)s")
    from dirope.interfaz.ventana import Aplicacion
    app = Aplicacion()
    try:
        if opciones.comprobar_interfaz:
            app.withdraw()
            total = 0
            for panel in app.paneles:
                app.mostrar(panel.modulo.clave)
                for nombre in panel.modulo.ejemplos:
                    panel.ejemplo.set(nombre)
                    panel.cargar_ejemplo()
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
                    for _ in panel.resultado.pasos:
                        assert panel.avanzar()
                    assert panel.etapa == 4
                    assert panel.grafico.serie
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
                    panel.retroceder()
                    assert panel.paso_actual == len(panel.resultado.pasos) - 2
                    panel.avanzar()
                    panel.avanzar()
                    assert panel.etapa == 4
                    total += 1
                # Un dato incorrecto muestra un mensaje dentro del formulario, sin cerrar la app.
                panel.variables[panel.modulo.campos[0].clave].set("")
                assert panel.resultado is None and panel.analisis is None and panel.etapa == 1
                assert not panel.avanzar()
                assert "Revisa los datos" in panel.estado.get()
                assert not panel.mostrar_etapa(4)
                panel.cargar_ejemplo()
                assert panel.etapa == 0
                panel.transicion.cancelar()
                panel.transicion.animar(12)
                assert int(panel.transicion.actual.place_info()["x"]) == 0
            # Caso propio, sin cargar ningún ejemplo.
            panel = app.paneles[0]
            panel.limpiar()
            assert not panel.avanzar()
            panel.enunciado.insert("1.0", "Un taller produce 240 piezas con 30 h y luego 360 piezas con 36 h.")
            panel.enunciado_modificado()
            panel.titulo.set("Caso nuevo del profesor")
            for clave, valor in dict(antes=240, despues=360, insumo_antes=30, insumo_despues=36, unidad="piezas/h").items():
                panel.variables[clave].set(str(valor))
            for _ in range(3):
                assert panel.avanzar()
            assert panel.resultado.pasos[-1].resultado == 25
            for _ in panel.resultado.pasos:
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
            assert app.activo is None
            app.abrir_demo()
            assert app.activo == "un_factor"
            assert app.paneles[0].resultado is None and app.paneles[0].etapa == 0
            app.decimales.set(3)
            app.actualizar_formato()
            app.update_idletasks()
            print(f"Interfaz verificada: {total} ejemplos y un problema nuevo; cinco etapas separadas, "
                  "confirmación del método, desarrollo paso a paso, informe, gráficos, validación, "
                  "invalidación de resultados y transiciones con movimiento reducido correctos.")
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
