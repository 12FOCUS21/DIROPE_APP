# Diseño de interfaz

La [referencia de Inicio](referencias/inicio.png) guía los colores, la cabecera y las tarjetas. La barra lateral azul marino aparece dentro de los módulos. Inicio destaca **Práctica a desarrollar** por encima de las tarjetas de módulos y la biblioteca personal. Cada botón abre una copia editable del ejercicio de referencia.

- **Planteamiento.** Título y enunciado opcionales, selector de cálculo y ejemplos editables.
- **Datos.** Campos según el modo. La vista previa comparte el resultado con el flujo guiado y señala qué entrada necesita revisión. La tabla multifactor permite cambiar de escenario, duplicar el inicial y desplazarse horizontalmente cuando las columnas exceden el ancho.
- **Identificación y desarrollo.** Datos utilizados y supuestos, seguidos por el procedimiento principal. Cada paso abre desde arriba y coloca fórmula, sustitución y resultado antes de sus explicaciones. El detalle desplegable lleva directamente a los costos individuales y otros cálculos auxiliares.
- **Resultados.** Respuesta principal, indicadores pertinentes, gráfica cuando hay datos e interpretación. Desde esta etapa se accede al procedimiento, copia, PDF, HTML y guardado.

Las entradas válidas habilitan **Ver resultado**. Editar los datos invalida el resultado anterior. Cambiar de módulo conserva los borradores. El guardado automático en Desarrollo y Resultados conserva las entradas y una instantánea del procedimiento en JSON. Abrir recalcula; consultar la resolución guardada muestra la instantánea. La biblioteca permite buscar, filtrar y guardar variantes como copias.

## Cambio de cálculo y práctica

La jerarquía visual sigue la [tipografía de Windows](https://learn.microsoft.com/windows/apps/design/signature-experiences/typography), sus [guías de iconografía](https://learn.microsoft.com/en-us/windows/apps/design/iconography) y los [encabezados de GOV.UK](https://design-system.service.gov.uk/styles/headings): títulos prominentes, subtítulos de sección y texto de lectura diferenciados por tamaño, peso y espacio. Inicio y la barra lateral usan iconos de línea junto con etiquetas. Los botones, paneles e indicadores usan esquinas redondeadas sin reemplazar los controles de teclado.

El banco presenta primero un caso en prosa. La etapa **Datos** reúne los campos editables por unidades y criterios, escenarios, objetivo y personal; los insumos y las categorías conservan su propia tabla. Identificación y Desarrollo componen fórmulas y sustituciones con fracciones apiladas y signos de techo, sin instalar LaTeX. El texto original sigue disponible con Ctrl+C sobre la fórmula y en los informes.

Cada opción de **¿Qué calcular?** conserva durante la sesión su propio título, enunciado, datos e identificador. Una opción sin borrador se abre limpia; volver restaura sus entradas, pero no reutiliza resultados de otro cálculo. Los ejemplos se filtran por método. **Nuevo problema** limpia únicamente la opción activa y el cierre avisa también de borradores ocultos sin guardar.

**Inicio → Banco de práctica** permite filtrar y abrir 1 000 casos sintéticos, 100 por cada uno de los 10 métodos. Abrir no llena la biblioteca personal: el guardado ocurre al desarrollar. El banco reproducible incluye respuestas independientes calculadas con fracciones racionales y variaciones de unidades, costos, calidad, escenarios, producción y personal.

La verificación intensiva utiliza una biblioteca temporal: 1 000 ejercicios y 112 secuencias de cambio entre opciones, en ambos temas, incluyendo recuperación de opciones con borradores propios. Las pruebas del banco comprueban además el rechazo de 24 584 entradas inválidas. Esta cobertura no equivale a descartar todos los errores posibles.

## Tema claro y oscuro

El selector **Tema** permanece visible en la cabecera. Las dos paletas distinguen los fondos, campos y cabeceras por capas de azul, con verde para resultados y ámbar para notas. La negrita identifica acciones, títulos y cifras; la cursiva señala interpretación y supuestos. Se actualizan estilos ttk, menús, texto, listas desplegables, tablas y gráficos sin reconstruir formularios ni alterar resultados. Los controles nuevos reciben el tema vigente, incluidas las ventanas de biblioteca e informe. La preferencia se guarda aparte del historial; un error de escritura conserva el tema durante la sesión y avisa al usuario.

La revisión incluyó una captura real de Resultados en oscuro, pruebas de contraste mínimo 4.5:1 para texto principal, secundario, acento y errores, cambio repetido de tema con biblioteca e informe abiertos y comprobación de persistencia al reiniciar. Los marcos y diálogos nativos del sistema no se fuerzan a otro aspecto. La opción «Capacidad y personal» se divide en dos líneas para evitar el corte observado en la barra lateral.

Tab y Shift+Tab recorren los controles. Enter activa la acción correspondiente y Alt+Inicio regresa al inicio. La animación es opcional y empieza desactivada.

La comprobación de Tkinter cubre ventanas de 960 × 600 y 1280 × 760 en Windows y simula un aumento del 25 % en la escala de Tk. macOS, lectores de pantalla y otros ajustes de pantalla requieren validación adicional.
