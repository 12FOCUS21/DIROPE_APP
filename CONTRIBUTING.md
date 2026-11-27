# Trabajo en equipo

## Preparación

Instala Python 3.10+ con Tkinter y Git. Clona el repositorio y entra en su carpeta. Para probar la app sin instalar paquetes ejecuta `python iniciar.py`; para preparar las dependencias opcionales, usa el lanzador.

## Flujo recomendado

1. Actualiza `main`: `git switch main` y luego `git pull --ff-only`.
2. Crea una rama para una tarea: `git switch -c mejora/calidad`.
3. Haz cambios pequeños. No mezcles tareas sin relación.
4. Ejecuta `python -m unittest discover -s pruebas -v` y prueba la interfaz con `python iniciar.py`.
5. Revisa `git diff`, selecciona tus archivos con `git add` y crea un commit descriptivo.
6. Sube tu rama con `git push -u origin mejora/calidad` y abre un pull request en GitHub.
7. Pide revisión a un compañero antes de integrar a `main`.

Los nuevos cálculos no deben importar Tkinter; añade pruebas y ejemplos. Antes de agregar paquetes externos, acuerda la dependencia con el equipo. No incluyas credenciales, `.venv`, resultados privados ni `registro.log` en commits.

El propietario debe invitar a los compañeros desde **Settings → Collaborators**. En un repositorio privado los colaboradores necesitan invitación. La licencia de distribución debe acordarse con el equipo; esta entrega no asigna una licencia automáticamente.

## Preparar el ZIP de una versión

Ejecuta `python herramientas/empaquetar.py --ref <etiqueta-o-commit>` desde un repositorio Git. Adjunta `dist/DIROPE-Calc.zip` y `dist/DIROPE-Calc.zip.sha256` en GitHub Releases. Usa siempre el mismo nombre para el ZIP y marca la versión publicada como **Latest**: así se mantiene el enlace directo del README. El empaquetador usa una lista explícita de archivos; no incluye pruebas, `.git`, materiales del curso ni datos locales.

## Probar la edición web

Con Node.js 22+ y Python 3.10+, ejecuta `npm --prefix web ci --ignore-scripts` y `python herramientas/preparar_web.py`. La preparación descarga el runtime fijado en el lock de npm y comprueba las huellas de sus licencias. Sirve `build/web` con `python -m http.server --bind 127.0.0.1 --directory build/web` y abre `http://127.0.0.1:8000/`; no abras el HTML directamente como archivo.

Para la prueba de navegador, ejecuta `npx --no-install playwright install chromium` desde `web/` y `npm --prefix web run probar` desde la raíz. `DIROPE_NAVEGADORES=chromium,firefox,webkit` selecciona los tres motores (instálalos primero). GitHub Actions prueba el sitio y publica el contenido estático en GitHub Pages al actualizar `main`. No subas `build/` ni `node_modules/` al repositorio.
