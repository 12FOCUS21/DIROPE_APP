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
                for nombre in panel.modulo.ejemplos:
                    panel.ejemplo.set(nombre)
                    panel.cargar_ejemplo()
                    if not panel.calcular():
                        raise RuntimeError(f"Falló el ejemplo {nombre}")
                    assert panel.resultado.pasos
                    total += 1
            app.update_idletasks()
            print(f"Interfaz verificada: {total} ejemplos cargados y calculados.")
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
