"use strict";

const $ = id => document.getElementById(id);
const form = $("calculadora");
const metodo = $("metodo");
const controles = new Map();
const borradores = new Map();
const modos = [];
const revisados = new Set();
let worker, espera, activo, listo = false, pendiente = null, secuencia = 0, informeURL;
let revision, demorar, mostrarTodo = false, editado = false;

function nodo(etiqueta, clase, texto) {
  const elemento = document.createElement(etiqueta);
  if (clase) elemento.className = clase;
  if (texto !== undefined) elemento.textContent = texto;
  return elemento;
}

function estado(mensaje, fallo = false) {
  $("estado").textContent = mensaje;
  $("estado").parentElement.classList.toggle("fallo", fallo);
  $("reintentar").hidden = !fallo;
}

function arrancar() {
  estado("Cargando el motor de cálculo. La primera apertura necesita internet y puede tardar.");
  const fallo = (mensaje = "No se pudo cargar el motor. Revisa la conexión, reintenta o descarga el ZIP de escritorio.") => {
    clearTimeout(espera);
    worker?.terminate();
    worker = undefined;
    listo = false;
    pendiente = null;
    $("controles").disabled = true;
    $("calcular").disabled = false;
    $("validacion").textContent = "";
    estado(mensaje, true);
  };
  if (location.protocol === "file:") {
    fallo("Abre DIROPE desde GitHub Pages o un servidor web; no desde un archivo HTML local.");
    return;
  }
  if (!window.WebAssembly || !window.Worker) {
    fallo("Este navegador no admite el motor. Prueba con uno actualizado o usa el ZIP de escritorio.");
    return;
  }
  try {
    worker = new Worker(new URL("motor.js", location.href));
    espera = setTimeout(() => fallo("El motor tardó demasiado. Revisa la conexión y reintenta, o usa el ZIP de escritorio."), 90000);
    worker.onerror = () => fallo("Se interrumpió el motor. Reintenta para continuar o usa el ZIP de escritorio.");
    worker.onmessageerror = () => fallo();
    worker.onmessage = ({ data }) => {
      if (data.tipo === "fallo") fallo();
      if (data.tipo === "listo") {
        clearTimeout(espera);
        const anterior = activo;
        if (anterior !== undefined) guardarBorrador();
        const orden = document.createDocumentFragment();
        modos.length = 0;
        for (const modulo of data.catalogo.modulos) {
          const grupo = nodo("optgroup");
          grupo.label = modulo.nombre;
          for (const modo of modulo.modos) {
            grupo.append(new Option(modo.nombre, modos.length));
            modos.push({ ...modo, modulo: modulo.clave });
          }
          orden.append(grupo);
        }
        metodo.replaceChildren(orden);
        metodo.value = anterior ?? 0;
        $("formato").textContent = data.catalogo.formato;
        mostrarModo();
        mostrarPractica(data.catalogo.practica);
        listo = true;
        $("controles").disabled = false;
        estado("Motor listo. El cálculo se ejecuta en este dispositivo.");
      }
      if (data.tipo === "respuesta" && data.id === pendiente) presentar(data.resultado);
      if (data.tipo === "revisado" && data.id === revision) mostrarErrores(data.errores, false);
    };
  } catch (error) {
    console.error(error);
    fallo();
  }
}

function limpiarErrores() {
  $("validacion").textContent = "";
  $("validacion").classList.remove("error");
  $("insumos-error").hidden = true;
  $("insumos-error").textContent = "";
  for (const { entrada, error } of controles.values()) {
    entrada.removeAttribute("aria-invalid");
    error.hidden = true;
    error.textContent = "";
  }
}

function invalidar() {
  clearTimeout(demorar);
  revision = null;
  pendiente = null;
  $("calcular").disabled = false;
  $("resultado").hidden = true;
  if (informeURL) {
    $("informe").removeAttribute("src");
    $("abrir-informe").removeAttribute("href");
    $("descargar-informe").removeAttribute("href");
    URL.revokeObjectURL(informeURL);
    informeURL = undefined;
  }
  limpiarErrores();
}

function campo(def, clave, valor) {
  const caja = nodo("div", "campo");
  const casilla = def.tipo === "casilla";
  const etiqueta = nodo("label", casilla ? "casilla" : "", def.etiqueta);
  const entrada = nodo(def.tipo === "opciones" ? "select" : "input");
  entrada.id = `entrada-${clave.replaceAll(".", "-")}`;
  etiqueta.htmlFor = entrada.id;
  if (def.tipo === "opciones") {
    for (const opcion of def.opciones) entrada.add(new Option(opcion));
  } else {
    entrada.type = casilla ? "checkbox" : "text";
    if (def.tipo === "numero") {
      entrada.spellcheck = false;
      entrada.autocomplete = "off";
    }
  }
  if (casilla) {
    entrada.checked = Boolean(valor);
    etiqueta.prepend(entrada);
    caja.append(etiqueta);
  } else {
    entrada.value = valor ?? def.valor ?? def.opciones?.[0] ?? "";
    caja.append(etiqueta, entrada);
  }
  const ayuda = nodo("small", "", def.ayuda || "");
  const error = nodo("small", "error");
  ayuda.id = `${entrada.id}-ayuda`;
  error.id = `${entrada.id}-error`;
  error.hidden = true;
  entrada.setAttribute("aria-describedby", def.ayuda ? `${ayuda.id} ${error.id}` : error.id);
  if (def.ayuda) caja.append(ayuda);
  caja.append(error);
  controles.set(clave, { entrada, error, ayuda, def });
  return caja;
}

function valorDe(entrada) {
  return entrada.type === "checkbox" ? entrada.checked : entrada.value;
}

function leerFilas() {
  return Array.from($("filas").children, (_, indice) => Object.fromEntries(
    modos[activo].tabla.campos.map(({ clave }) => [clave, valorDe(controles.get(`insumos.${indice}.${clave}`).entrada)])
  ));
}

function renderizarFilas(filas) {
  for (const clave of controles.keys()) if (clave.startsWith("insumos.")) controles.delete(clave);
  const tabla = modos[activo].tabla;
  $("filas").replaceChildren();
  if (!tabla) return;
  filas.forEach((valores, indice) => {
    const fila = nodo("fieldset", "fila");
    const grilla = nodo("div", "grilla");
    for (const def of tabla.campos) grilla.append(campo(def, `insumos.${indice}.${def.clave}`, valores[def.clave]));
    const quitar = nodo("button", "secundario quitar", "Quitar fila");
    quitar.type = "button";
    quitar.setAttribute("aria-label", `Quitar fila ${indice + 1}`);
    quitar.onclick = () => {
      const actuales = leerFilas();
      actuales.splice(indice, 1);
      renderizarFilas(actuales);
      invalidar();
      editado = true;
      revisarFilasDeNuevo();
      revisar();
      $("agregar").focus();
    };
    fila.append(nodo("legend", "", `Fila ${indice + 1}`), grilla, quitar);
    $("filas").append(fila);
  });
}

function leerEjercicio() {
  const modo = modos[activo];
  const datos = { modo: modo.nombre };
  for (const [clave, { entrada }] of controles) {
    if (!clave.startsWith("insumos.")) datos[clave] = valorDe(entrada);
  }
  if (modo.tabla) datos.insumos = leerFilas();
  return { modulo: modo.modulo, datos, titulo: $("nombre").value, enunciado: $("enunciado").value };
}

function guardarBorrador() {
  borradores.set(activo, { ...leerEjercicio(), ejemplo: $("ejemplo").value, abrir: $("planteamiento").open, cambiado: editado });
}

function actualizarCalidad() {
  const porcentaje = controles.get("medida_calidad")?.entrada.value === "%";
  for (const { def, ayuda } of controles.values()) {
    if (def.ayuda_porcentaje) ayuda.textContent = porcentaje ? def.ayuda_porcentaje : def.ayuda;
  }
}

function mostrarModo() {
  activo = metodo.selectedIndex;
  const modo = modos[activo];
  const borrador = borradores.get(activo) || {};
  $("objetivo").textContent = modo.ayuda;
  $("ejemplo").replaceChildren(...modo.ejemplos.map((e, i) => new Option(e.nombre, i)));
  if (borrador.ejemplo !== undefined) $("ejemplo").value = borrador.ejemplo;
  mostrarCampos(borrador);
}

function mostrarPractica(casos) {
  $("casos-practica").replaceChildren(...casos.map(caso => {
    const item = nodo("li");
    const boton = nodo("button", "secundario", caso.nombre);
    boton.type = "button";
    boton.onclick = () => {
      if (!listo) return;
      const destino = modos.findIndex(m => m.modulo === caso.modulo && m.nombre === caso.datos.modo);
      guardarBorrador();
      if (borradores.get(destino)?.cambiado && !confirm("¿Reemplazar los datos de este método por los de la práctica?")) return;
      metodo.value = destino;
      mostrarModo();
      mostrarCampos({ ...caso, titulo: caso.nombre, abrir: true });
      $("nombre").focus();
    };
    item.append(boton);
    return item;
  }));
}

function mostrarCampos({ datos = {}, titulo = "", enunciado = "", abrir = false, cambiado = false } = {}) {
  const modo = modos[activo];
  invalidar();
  editado = cambiado;
  revisados.clear();
  mostrarTodo = false;
  controles.clear();
  $("nombre").value = titulo;
  $("enunciado").value = enunciado;
  $("planteamiento").open = abrir;
  $("nota").hidden = !modo.nota;
  $("nota-texto").textContent = modo.nota;
  $("campos").replaceChildren(...modo.grupos.map(grupo => {
    const seccion = nodo("fieldset", "grupo");
    const grilla = nodo("div", "grilla");
    for (const def of grupo.campos) grilla.append(campo(def, def.clave, datos[def.clave]));
    seccion.append(nodo("legend", "", grupo.titulo), grilla);
    return seccion;
  }));
  $("insumos").hidden = !modo.tabla;
  if (modo.tabla) {
    $("insumos-titulo").textContent = modo.tabla.titulo;
    $("insumos-ayuda").textContent = modo.tabla.ayuda;
  }
  renderizarFilas(datos.insumos ?? modo.tabla?.filas ?? []);
  actualizarCalidad();
}

function revisarFilasDeNuevo() {
  for (const clave of revisados) if (clave.startsWith("insumos.")) revisados.delete(clave);
}

function revisar() {
  if (!listo || pendiente !== null || (revisados.size === 0 && !mostrarTodo)) return;
  clearTimeout(demorar);
  revision = ++secuencia;
  demorar = setTimeout(() => worker?.postMessage({ tipo: "revisar", id: revision, solicitud: leerEjercicio() }), 160);
}

function mostrarErrores(errores, enfocar, mensaje) {
  limpiarErrores();
  let primero;
  for (const [clave, control] of controles) {
    if (!errores[clave] || !(mostrarTodo || revisados.has(clave))) continue;
    control.entrada.setAttribute("aria-invalid", "true");
    control.error.textContent = errores[clave];
    control.error.hidden = false;
    primero ??= control.entrada;
  }
  if (mostrarTodo && errores.insumos) {
    $("insumos-error").hidden = false;
    $("insumos-error").textContent = errores.insumos;
    primero ??= $("agregar");
  }
  if (enfocar) {
    $("validacion").classList.add("error");
    $("validacion").textContent = mensaje || errores.modo || "Revisa los avisos junto a los datos.";
    (primero || $("calcular")).focus();
  }
}

function presentar(resultado) {
  pendiente = null;
  $("calcular").disabled = false;
  if (resultado.errores || resultado.mensaje) {
    mostrarTodo = true;
    mostrarErrores(resultado.errores || {}, true, resultado.mensaje);
    return;
  }
  $("validacion").textContent = "Cálculo completado.";
  $("principal").hidden = !resultado.principal;
  $("respuesta-titulo").textContent = resultado.principal?.titulo || "";
  $("respuesta-valor").textContent = resultado.principal?.valor || "";
  $("interpretacion").textContent = resultado.interpretacion;
  informeURL = URL.createObjectURL(new Blob([resultado.html], { type: "text/html;charset=utf-8" }));
  $("informe").src = `${informeURL}#procedimiento`;
  $("abrir-informe").href = informeURL;
  $("descargar-informe").href = informeURL;
  $("resultado").hidden = false;
  $("h-resultado").focus();
}

$("reintentar").addEventListener("click", arrancar);
metodo.addEventListener("change", () => {
  guardarBorrador();
  mostrarModo();
});
$("cargar").addEventListener("click", () => {
  const ejemplo = modos[activo].ejemplos[$("ejemplo").selectedIndex];
  if (editado && !confirm("¿Cargar el ejemplo y reemplazar los datos de este método?")) return;
  mostrarCampos({ ...ejemplo, titulo: ejemplo.nombre, abrir: true });
});
$("agregar").addEventListener("click", () => {
  const filas = leerFilas();
  renderizarFilas([...filas, {}]);
  invalidar();
  editado = true;
  revisar();
  controles.get(`insumos.${filas.length}.nombre`).entrada.focus();
});
form.addEventListener("input", ({ target }) => {
  if (target === metodo || target === $("ejemplo")) return;
  invalidar();
  editado = true;
  if (target.id === "entrada-medida_calidad") actualizarCalidad();
  revisar();
});
form.addEventListener("focusout", ({ target }) => {
  for (const [clave, { entrada }] of controles) {
    if (target === entrada) {
      revisados.add(clave);
      revisar();
      break;
    }
  }
});
form.addEventListener("submit", evento => {
  evento.preventDefault();
  if (!listo || pendiente !== null) return;
  invalidar();
  $("validacion").textContent = "Calculando…";
  $("calcular").disabled = true;
  pendiente = ++secuencia;
  worker.postMessage({ tipo: "calcular", id: pendiente, solicitud: leerEjercicio() });
});

arrancar();
