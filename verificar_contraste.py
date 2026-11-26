"""Comprueba una matriz de combinaciones WCAG 2.x sin abrir Tkinter."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from dirope.interfaz.tokens import ACENTO_POR_ESTADO, PALETAS


def luminancia(color):
    canales = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lineales = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in canales]
    return sum(canal * peso for canal, peso in zip(lineales, (.2126, .7152, .0722)))


def contraste(a, b):
    oscuro, claro = sorted((luminancia(a), luminancia(b)))
    return (claro + .05) / (oscuro + .05)


def pares(tema):
    fondos_control = ("relleno_secundario", "relleno_en_elevada", "hover_elevada")
    contenedores = ("fondo", "superficie", "elevada", "elevada_inicio", "cabecera", "cabecera_inicio")
    for fondo in (*contenedores, *fondos_control):
        yield "Texto normal / controles", "texto", fondo, 7
    # Los metadatos permanecen en el panel; no se dibujan sobre el hover más claro.
    for fondo in contenedores:
        yield "Etiquetas y metadatos", "texto_secundario", fondo, 7
        yield "Borde de control", "borde_control", fondo, 3
        yield "Anillo de foco", "foco", fondo, 3
    for fondo in fondos_control:
        yield "Borde junto al relleno", "borde_control", fondo, 3
        yield "Foco junto al relleno", "foco", fondo, 3
    for fondo in ("relleno_destructivo", "hover_destructivo"):
        yield "Texto destructivo", "texto_destructivo", fondo, 7
        yield "Contorno destructivo", "error", fondo, 3
    for estado, extremos in ACENTO_POR_ESTADO.items():
        # Ambos extremos: la interpolación sRGB de esta rampa es monótona por canal.
        for fondo in extremos:
            yield f"Primario / {estado}", "texto_acento", fondo, 4.5
            yield f"Foco primario / {estado}", "foco_sobre_acento", fondo, 3
    for fondo in ("superficie", "elevada", "elevada_inicio"):
        yield "Borde decorativo", "borde_decorativo", fondo, 1.8
    yield "Texto deshabilitado", "texto_deshabilitado", "relleno_deshabilitado", 3
    if tema == "Oscuro":
        yield "Capas", "fondo", "superficie", 1.5
        for fondo in ("elevada", "elevada_inicio"):
            yield "Capas", "superficie", fondo, 1.25


def main():
    fallos = []
    total = 0
    for tema, paleta in PALETAS.items():
        print(f"\n{tema}")
        print(f"{'Uso':<29} {'Par de tokens':<43} {'Colores':<18} {'Ratio':>7} {'Min.':>6} Estado")
        for uso, a, b, minimo in pares(tema):
            real = contraste(paleta[a], paleta[b])
            ok = real >= minimo
            total += 1
            print(f"{uso:<29} {a + ' / ' + b:<43} {paleta[a] + ' / ' + paleta[b]:<18} {real:>7.3f} {minimo:>6.2f} "
                  f"{'OK' if ok else 'FALLO'}")
            if not ok:
                fallos.append(f"{tema}: {uso}: {a} / {b} ({real:.3f} < {minimo:.2f})")
    print(f"\n{total} pares comprobados; {len(fallos)} fallos.")
    for fallo in fallos:
        print(fallo, file=sys.stderr)
    return int(bool(fallos))


if __name__ == "__main__":
    raise SystemExit(main())
