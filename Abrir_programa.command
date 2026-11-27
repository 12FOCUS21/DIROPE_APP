#!/bin/sh
cd "$(dirname "$0")" || exit 1
python3 preparar.py "$@"
estado=$?
if [ "$estado" -ne 0 ]; then
    echo 'No se pudo abrir. Comprueba que Python 3.10+ tenga Tkinter instalado.'
    read -r respuesta
fi
exit "$estado"
