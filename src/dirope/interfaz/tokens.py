"""Tokens propuestos para el rediseño; aún no conectados con la interfaz."""

ESPACIOS = (4, 8, 12, 16, 24, 32)
RADIOS = dict(campo=6, chip=6, boton=10, pestana=10, tarjeta=14, panel=14, interruptor="pill")
ALTURAS = dict(compacto=36, principal=44, pestana=40, cabecera=56)
GROSORES = dict(control=1, decorativo=1, foco=2)
TIPOGRAFIA = dict(
    texto=("Segoe UI Variable Text", "Segoe UI"),
    titulos=("Segoe UI Variable Display", "Segoe UI"),
    cifras=("Cascadia Mono", "Consolas"),
    escala_px=(12, 13, 14, 16, 20, 26, 32),
    base_px=13, campo_px=13, boton_px=14, metadatos_px=12, peso_accion="semibold",
)
SUPERMUESTREO = 3

ACENTO = dict(acento_inicio="#2B63D9", acento_fin="#1C47B5", texto_acento="#FFFFFF")

PALETAS = {
    "Claro": dict(
        **ACENTO, fondo="#DCE4F2", superficie="#FFFFFF", elevada="#F3F6FC",
        elevada_inicio="#FFFFFF", cabecera_inicio="#F3F6FC", cabecera="#E6EDF9",
        relleno_secundario="#E3ECFC", relleno_en_elevada="#E3ECFC", hover_elevada="#D9E6FA",
        texto="#0B1530", texto_secundario="#364766", texto_deshabilitado="#66748F",
        relleno_deshabilitado="#E3E8F2", borde_control="#5F79AD", foco="#1C47B5",
        foco_sobre_acento="#FFFFFF", borde_decorativo="#A5B6D0",
        exito="#047857", nota="#92400E", error="#B91C1C", texto_destructivo="#8B1717",
        relleno_destructivo="#E3ECFC", hover_destructivo="#D9E6FA",
        sombra_rgba=(11, 21, 48, .22),
    ),
    "Oscuro": dict(
        **ACENTO, fondo="#030509", superficie="#1F2E50", elevada="#2D4170",
        elevada_inicio="#304577", cabecera_inicio="#2D4170", cabecera="#283B65",
        relleno_secundario="#2D4170", relleno_en_elevada="#34497D", hover_elevada="#3A5390",
        texto="#F5F8FF", texto_secundario="#DBE3F6", texto_deshabilitado="#93A3C6",
        relleno_deshabilitado="#1F2E50", borde_control="#8FA8DD", foco="#A9CBFF",
        foco_sobre_acento="#A9CBFF", borde_decorativo="#607BAC",
        exito="#4ADE80", nota="#FBBF24", error="#FF9A9A", texto_destructivo="#FFE2E2",
        relleno_destructivo="#2D4170", hover_destructivo="#34497D",
        sombra_rgba=(0, 0, 0, .60),
    ),
}

# Mismo degradado en los tres estados; hover y pulsación no aclaran el relleno.
ACENTO_POR_ESTADO = {estado: ("acento_inicio", "acento_fin")
                     for estado in ("reposo", "hover", "presionado")}

PALETAS["Claro"].update(fondo_nota="#FFF4DC", fondo_resultado="#E0F5EC", acento_auxiliar="#075E68",
                        graficos=("#164CCA", "#2671BF", "#075E68", "#447B67", "#535EAB"))
PALETAS["Oscuro"].update(fondo_nota="#403420", fondo_resultado="#173B36", acento_auxiliar="#78E2D6",
                         graficos=("#A9CBFF", "#77B5FF", "#78E2D6", "#96DEAE", "#C1BCFF"))
