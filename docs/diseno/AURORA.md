# Aurora: fondo ambiental y jerarquía de color

Revisión: 27 de noviembre de 2026.

## Investigación

- [Microsoft — principios de diseño de Windows](https://learn.microsoft.com/en-us/windows/apps/design/design-principles): el color debe ayudar a distinguir jerarquía y superficies, manteniendo un entorno tranquilo y coherente.
- [Microsoft Atlas — degradados](https://design.learn.microsoft.com/components/gradients.html): los degradados sirven para fundir colores y límites entre superficies; conviene limitar dónde se utilizan y hacer coincidir los fondos para evitar cortes visuales.
- [W3C — contraste mínimo, WCAG 2.2](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html): al menos 4.5:1 para texto normal y 3:1 para texto grande. El contraste debe evaluarse frente al fondo que aparece detrás del texto, no solo frente a un color de referencia.

Estas guías orientan la adaptación; no constituyen una certificación de accesibilidad de la aplicación ni prescriben porcentajes universales de distribución de color.

## Distribución aplicada

1. **Fondo ambiental amplio**, no solo una línea decorativa: lavanda suave en la parte superior izquierda, cian a la derecha y tonos casi blancos rosados/azulados abajo. Transiciones sin animaciones ni saturación intensa.
2. **Tarjetas blancas y opacas** para formularios, fórmulas y tablas. El usuario lee e introduce datos sobre una superficie estable, no sobre un arcoíris.
3. **Azul tinta `#0A2540`** para texto y **azul oscuro `#173B67`** para acciones principales y selección. Los botones principales ya no añaden otro degradado multicolor que compita con el fondo.
4. **Violeta** reservado a foco y acentos; colores de éxito, error y notas conservan sus significados. El color no sustituye los mensajes de validación.
5. El degradado usa las coordenadas de la ventana para mantener continuidad entre el título y los espacios libres de las superficies. Claro y Oscuro mantienen sus fondos originales.

### Colores del fondo

| Zona | Color |
|---|---|
| Superior izquierda | `#DBD9FB` |
| Superior derecha | `#D3EDF5` |
| Inferior izquierda | `#F2E8F5` |
| Inferior derecha | `#EDF5FC` |

Se comprueba una malla de 21 × 21 puntos: texto principal y secundario ≥ 7:1, foco y contorno de controles ≥ 3:1. Es una comprobación de esta paleta concreta, no de todas las posibles configuraciones del sistema.

## Implementación local

`src/dirope/interfaz/fondos.py` comparte el fondo entre Inicio, módulos y áreas de navegación. El texto de los títulos sigue siendo texto de Tk, no una imagen generada con letras. Las tarjetas y campos conservan sus controles existentes.

Se interpola una malla pequeña, con ampliación bilineal si Pillow está disponible y una alternativa nativa Tk si no lo está. Solo se conserva la última imagen de cada superficie, se evita repintar si no cambian tamaño/posición/tema y se cancelan tareas al destruir los controles. No se añaden dependencias, conexión a internet ni imágenes descargadas durante la ejecución.

La revisión visual debe hacerse con una instancia nueva: una ventana que ya estaba abierta conserva el código anterior en memoria.
