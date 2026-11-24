# Diseño de la experiencia de DIROPE Calc

## Investigación y criterio profesional

Una buena interfaz combina utilidad, claridad, respuesta inmediata, accesibilidad y coherencia; no se demuestra su calidad con animaciones solamente. Estas fuentes orientaron el rediseño:

- [Nielsen Norman Group: 10 heurísticas de usabilidad](https://www.nngroup.com/articles/ten-usability-heuristics/): visibilidad del estado, lenguaje familiar, control del usuario, prevención de errores y consistencia.
- [NN/g: diseño estético y minimalista](https://www.nngroup.com/articles/aesthetic-minimalist-design/): priorizar información útil y revelar detalles de forma progresiva.
- [W3C: WCAG 2.2](https://www.w3.org/TR/WCAG22/): referencia de contraste, operación con teclado y movimiento reducible.
- [W3C: foco visible](https://www.w3.org/WAI/WCAG22/Understanding/focus-visible): identificar siempre qué control recibe el teclado.
- [W3C: tamaño de objetivos](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum): evitar controles pequeños o amontonados.

WCAG es un estándar para contenido web. Aquí se utiliza como guía de diseño, no como certificación de accesibilidad de una aplicación Tkinter. Los píxeles CSS de sus umbrales no se equiparan automáticamente a las unidades de Tk. La lectura con tecnologías de asistencia requiere pruebas específicas de escritorio.

## Aplicación al producto

| Criterio | Decisión implementada |
|---|---|
| Primera experiencia | Inicio con presentación, tres herramientas y demostración de un clic. |
| Orientación | Menú lateral persistente, sección activa, ruta superior y cinco etapas con indicador de avance. |
| Jerarquía | Planteamiento, datos, identificación, desarrollo y resultados en pantallas separadas. |
| Revelación progresiva | Confirmación del método antes del cálculo; desarrollo con fórmula, sustitución y resultado intermedio de un paso a la vez. Síntesis final después del recorrido. |
| Coherencia | Paleta azul noche y turquesa, superficies claras, estados y tipografía compartidos. |
| Retroalimentación | Hover y pulsación de botones, mensajes de carga, éxito, error y copia. |
| Movimiento útil | Deslizamientos de unos 192 ms entre pantallas y pasos, y barras con entrada breve de unos 160 ms; interruptor «Efectos». Transiciones cancelables, sin esperas falsas ni parpadeos. |
| Confianza | Resultados invalidados al cambiar el enunciado, objetivo, título o datos; no se presentan informes obsoletos como actuales. |
| Prevención de confusiones | Gráficos con magnitudes de la misma unidad; costos separados de productividad. |
| Teclado | Botones con foco visible, Tab/Shift+Tab, Enter y Alt+Inicio. |
| Ventanas pequeñas | Paneles desplazables y tamaño inicial ajustado a la pantalla. |
| Privacidad y rendimiento | Todo funciona localmente; sin recursos visuales descargados de internet. |

## Alcance de esta mejora

Se conserva Tkinter y no se añaden dependencias. Se mejora la presentación de los tres módulos existentes sin alterar sus fórmulas. No se añaden acceso con contraseña, servicios remotos, exportaciones ni módulos que todavía no existen. Las preferencias de efectos y decimales son de sesión.

Se mantienen etiquetas numéricas en los gráficos: el color no es el único medio para comprenderlos. La animación no modifica los resultados reales. Se pueden consultar los nombres completos de insumos en el procedimiento si las etiquetas del gráfico se abrevian.

### Resolución guiada y problemas nuevos

El usuario redacta el planteamiento y el objetivo, registra las cifras y revisa el método de la herramienta seleccionada. La identificación no es un clasificador automático de lenguaje natural: presenta datos validados, incógnitas, fórmulas y supuestos para su confirmación. Los ejemplos son opcionales y editables; se admiten casos nuevos de los tres tipos disponibles.

El desarrollo y la presentación final no comparten pantalla. Primero se recorre cada paso; después se habilitan los indicadores, la interpretación y el gráfico. El informe copiable reúne las cinco secciones. Cambiar datos exige revisar el análisis; cambiar el contexto devuelve al planteamiento.

### Refinamiento de la paleta y la densidad

Menú azul noche `#142235`, acciones azules `#2457D6`, acentos y segunda serie turquesa `#087F8C`, fondo `#F4F7FB` y tarjetas blancas. Los colores se centralizan en `componentes.py` con nombres semánticos. El inicio utiliza una cabecera clara y textos más breves; las tarjetas de indicadores se reorganizan en una, dos o tres columnas según el espacio disponible. Las pruebas verifican contraste mínimo de 4.5:1 en las combinaciones principales de texto, incluidos el turquesa y los textos del menú.

## Verificación y siguientes pasos

1. Mantener las pruebas de los cálculos y comprobar inicio, navegación, bloqueo de etapas, ejemplos y problemas nuevos, informe, gráficos, validación y movimiento reducido. La comprobación automatizada actual recorre los cinco ejemplos y un caso propio.
2. Probar manualmente navegación completa con teclado, escalado de Windows al 125/150/200 %, resoluciones pequeñas y contraste.
3. Probar lectores de pantalla y macOS; no asumir accesibilidad total por usar controles estándar.
4. Hacer una prueba con compañeros: elegir herramienta, resolver un ejemplo, interpretar el cambio y copiar el informe sin asistencia. Medir éxito, errores y dificultades antes de sumar efectos.
5. Si se requiere mayor sofisticación visual o soporte de accesibilidad más amplio, evaluar PySide6/Qt en una decisión separada: aumenta dependencias y exige revisar distribución y licencias. No es necesario migrar para validar este diseño inicial.
