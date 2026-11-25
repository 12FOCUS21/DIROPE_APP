"""Modos y campos del espacio de trabajo."""

from .base import Campo

CAMPOS_COMUNES = {
    "unidad_salida": Campo("unidad_salida", "Unidad de producción", "unidades"),
    "unidad_recurso": Campo("unidad_recurso", "Unidad del recurso", "h-persona"),
    "recurso": Campo("recurso", "Nombre del recurso", "Trabajo"),
    "antes": Campo("antes", "Producción inicial"),
    "insumo_antes": Campo("insumo_antes", "Cantidad del recurso inicial"),
    "despues": Campo("despues", "Producción final"),
    "insumo_despues": Campo("insumo_despues", "Cantidad del recurso final"),
    "ritmo": Campo("ritmo", "Productividad requerida"),
    "medida_calidad": Campo("medida_calidad", "Medida de no conformes", "Cantidad"),
    "defecto_antes": Campo("defecto_antes", "No conformes · inicial"),
    "defecto_despues": Campo("defecto_despues", "No conformes · final"),
    "moneda": Campo("moneda", "Moneda común", "$"),
    "produccion": Campo("produccion", "Producción inicial"),
    "produccion_final": Campo("produccion_final", "Producción de la alternativa"),
    "produccion_otra": Campo("produccion_otra", "Producción de la alternativa 2 (opcional)"),
    "horas_calidad": Campo("horas_calidad", "Horas-persona"),
    "actual": Campo("actual", "Producción actual del período"),
    "crecimiento": Campo("crecimiento", "Crecimiento (%)"),
    "meta": Campo("meta", "Meta de producción"),
    "productividad": Campo("productividad", "Productividad (producción/h-persona)"),
    "horas": Campo("horas", "Horas por persona en el período"),
    "plantilla": Campo("plantilla", "Plantilla disponible (opcional)"),
    "periodo": Campo("periodo", "Período", "mes"),
}

MODOS = {
    "un_factor": {
        "Comparar escenarios": ("unidad_salida", "unidad_recurso", "recurso", "antes", "insumo_antes", "despues", "insumo_despues"),
        "Productividad individual": ("unidad_salida", "unidad_recurso", "recurso", "antes", "insumo_antes"),
        "Producción requerida": ("unidad_salida", "unidad_recurso", "recurso", "ritmo", "insumo_antes"),
        "Recurso requerido": ("unidad_salida", "unidad_recurso", "recurso", "ritmo", "antes"),
        "Comparar conformidad": ("unidad_salida", "unidad_recurso", "recurso", "medida_calidad",
                                  "antes", "despues", "defecto_antes", "defecto_despues", "insumo_antes", "insumo_despues"),
    },
    "multifactor": {
        "Escenario individual": ("unidad_salida", "moneda", "produccion"),
        "Comparar alternativas": ("unidad_salida", "moneda", "produccion", "produccion_final", "produccion_otra"),
        "Valor por calidad": ("unidad_salida", "moneda", "horas_calidad"),
    },
    "capacidad": {
        "Crecimiento porcentual": ("unidad_salida", "periodo", "actual", "crecimiento", "productividad", "horas", "plantilla"),
        "Meta directa": ("unidad_salida", "periodo", "actual", "meta", "productividad", "horas", "plantilla"),
    },
}
