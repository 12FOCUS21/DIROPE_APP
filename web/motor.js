/* Ejecuta Python fuera de la interfaz. Los mensajes nunca se envían a la red. */
let puente;

async function iniciar() {
  const ruta = new URL("runtime/", self.location.href);
  importScripts(new URL("pyodide.js", ruta).href);
  const python = await loadPyodide({ indexURL: ruta.href });
  const respuesta = await fetch(new URL("dirope.zip", self.location.href));
  if (!respuesta.ok) throw new Error(`Motor DIROPE: HTTP ${respuesta.status}`);
  python.FS.writeFile("/dirope.zip", new Uint8Array(await respuesta.arrayBuffer()));
  python.runPython("import sys; sys.path.insert(0, '/dirope.zip')");
  puente = python.pyimport("dirope.web");
  self.postMessage({ tipo: "listo", catalogo: JSON.parse(puente.catalogo()) });
}

self.onmessage = ({ data }) => {
  if (!puente || !["calcular", "revisar"].includes(data.tipo)) return;
  try {
    const solicitud = JSON.stringify(data.solicitud);
    if (data.tipo === "revisar") {
      self.postMessage({ tipo: "revisado", id: data.id, errores: JSON.parse(puente.revisar(solicitud)) });
    } else {
      self.postMessage({ tipo: "respuesta", id: data.id, resultado: JSON.parse(puente.resolver(solicitud)) });
    }
  } catch (error) {
    console.error(error);
    if (data.tipo === "revisar") return;
    self.postMessage({ tipo: "respuesta", id: data.id, resultado: {
      mensaje: "No se pudo completar el cálculo. Revisa los datos y vuelve a intentarlo.",
    } });
  }
};

iniciar().catch(error => {
  console.error(error);
  self.postMessage({ tipo: "fallo" });
});
