"""Genera el banco separado de la biblioteca personal; no modifica ejercicios guardados."""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from dirope.banco import generar_banco


if __name__ == "__main__":
    destino = Path(__file__).resolve().parent / "ejemplos" / "banco_generado.json"
    destino.parent.mkdir(exist_ok=True)
    casos = generar_banco()
    destino.write_text(json.dumps({"version": 1, "semilla": 20261125, "casos": casos}, ensure_ascii=False,
                                 allow_nan=False, indent=2), encoding="utf-8")
    print(f"Generados {len(casos)} ejercicios (100 por modo): {destino}")
