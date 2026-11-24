# Trabajo en equipo

## Preparación

Instala Python 3.10+ con Tkinter y Git. Clona el repositorio cuando exista el remoto y entra en su carpeta. No necesitas dependencias para esta versión.

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
