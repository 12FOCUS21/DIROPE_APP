/* Prueba la app y el WebAssembly en navegadores reales, bajo una subruta como GitHub Pages. */
const assert = require("node:assert/strict");
const { readFile } = require("node:fs/promises");
const { createServer } = require("node:http");
const { resolve, extname, relative, isAbsolute } = require("node:path");
const motores = require("../../web/node_modules/playwright");

const raiz = resolve(__dirname, "../../build/web");
const prefijo = "/DIROPE_APP/";
const tipos = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".wasm": "application/wasm" };
let bloquear = false;
const servidor = createServer(async (req, res) => {
  try {
    const ruta = new URL(req.url, "http://127.0.0.1").pathname;
    if (!ruta.startsWith(prefijo) || (bloquear && ruta.endsWith("/pyodide.js"))) throw new Error();
    const archivo = resolve(raiz, ruta.slice(prefijo.length) || "index.html");
    const interior = relative(raiz, archivo);
    if (interior.startsWith("..") || isAbsolute(interior)) throw new Error();
    const bytes = await readFile(archivo);
    res.writeHead(200, { "Content-Type": tipos[extname(archivo)] || "application/octet-stream", "Cache-Control": "no-store" });
    res.end(bytes);
  } catch {
    res.writeHead(404).end();
  }
});

async function listo(page) {
  await page.waitForFunction(() => document.querySelector("#estado").textContent.startsWith("Motor listo"), null, { timeout: 60000 });
}

async function probar(tipo, local) {
  const executablePath = tipo === "chromium" ? process.env.CHROME_BIN : undefined;
  const browser = await motores[tipo].launch({ executablePath });
  try {
    if (!process.env.DIROPE_URL) {
      bloquear = true;
      const fallo = await browser.newPage();
      await fallo.goto(local);
      await fallo.locator("#reintentar").waitFor({ state: "visible" });
      assert.match(await fallo.locator("#estado").textContent(), /No se pudo cargar/);
      assert.equal(await fallo.locator("#calcular").isDisabled(), true);
      bloquear = false;
      await fallo.locator("#reintentar").click();
      await listo(fallo);
      await fallo.close();
    }
    const context = await browser.newContext({ viewport: { width: 360, height: 780 } });
    const page = await context.newPage();
    const errores = [];
    const solicitudes = [];
    context.on("request", solicitud => {
      if (/^https?:/.test(solicitud.url())) solicitudes.push(solicitud.url());
    });
    page.on("pageerror", error => errores.push(error.message));
    page.on("dialog", dialogo => dialogo.accept());
    await page.goto(process.env.DIROPE_URL || local);
    await listo(page);
    assert.equal(await page.locator("#metodo option").count(), 10);
    assert.equal(await page.locator("#casos-practica button").count(), 9);
    assert.equal(await page.evaluate(() => document.querySelector("#practica").compareDocumentPosition(document.querySelector("form")) & 4), 4);
    const origen = new URL(process.env.DIROPE_URL || local).origin;
    assert.ok(solicitudes.every(url => url.startsWith(`${origen}/`)));
    const numeroSolicitudes = solicitudes.length;

    for (let indice = 0; indice < 10; indice++) {
      await page.locator("#metodo").selectOption({ index: indice });
      await page.locator("#cargar").click();
      await page.locator("#calcular").click();
      await page.locator("#resultado").waitFor({ state: "visible", timeout: 10000 });
      await page.frameLocator("#informe").locator(".leyenda-formula").first().waitFor({ state: "visible" });
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    }

    const practica = page.getByRole("button", { name: /T6.*Calidad y productividad laboral/ });
    await practica.click();
    assert.match(await page.locator("#nombre").inputValue(), /Placas/);
    assert.match(await page.locator("#nota-texto").textContent(), /120 conformes/);
    const noConformes = page.locator("#entrada-defecto_antes");
    await noConformes.fill("2,5");
    await page.locator("#entrada-defecto_despues").focus();
    const error = page.locator("#entrada-defecto_antes-error");
    await error.waitFor({ state: "visible" });
    assert.match(await error.textContent(), /punto decimal/);
    await noConformes.fill("101");
    await page.locator("#calcular").click();
    await error.waitFor({ state: "visible" });
    assert.match(await error.textContent(), /entre 0 y 100/);
    assert.equal(await noConformes.evaluate(el => el === document.activeElement), true);
    await noConformes.fill("4");
    await page.locator("#entrada-antes").fill("125");
    await page.locator("#calcular").click();
    await page.frameLocator("#informe").getByText("120.000000 placas", { exact: false }).first().waitFor();
    const [descarga] = await Promise.all([page.waitForEvent("download"), page.locator("#descargar-informe").click()]);
    assert.equal(descarga.suggestedFilename(), "DIROPE-informe.html");
    assert.match(await readFile(await descarga.path(), "utf8"), /120\.000000 placas/);
    await practica.click();
    assert.equal(await noConformes.inputValue(), "6");
    assert.equal(await page.locator("#entrada-antes").inputValue(), "800");

    await page.locator("#metodo").selectOption({ label: "Comparar alternativas" });
    await page.locator("#cargar").click();
    await page.locator("#agregar").click();
    const filas = page.locator("#filas fieldset");
    await filas.last().getByLabel("Escenario", { exact: true }).selectOption("Alternativa 2");
    await page.locator("#calcular").click();
    await page.locator("#entrada-produccion_otra-error").waitFor({ state: "visible" });
    assert.match(await page.locator("#entrada-produccion_otra-error").textContent(), /Alternativa 2/);
    assert.equal(await filas.last().getByText("Costo de una unidad.", { exact: false }).isVisible(), true);
    assert.equal(solicitudes.length, numeroSolicitudes, "Calcular no debe generar solicitudes de red");
    assert.deepEqual(errores, []);
    console.log(`${tipo}: carga${process.env.DIROPE_URL ? " pública" : ", fallo y reintento"}, 10 métodos, práctica, correcciones, descarga y ancho móvil verificados.`);
  } finally {
    await browser.close();
  }
}

servidor.listen(0, "127.0.0.1", async () => {
  try {
    const url = `http://127.0.0.1:${servidor.address().port}${prefijo}`;
    for (const tipo of (process.env.DIROPE_NAVEGADORES || "chromium").split(",")) await probar(tipo, url);
  } catch (error) {
    console.error(error);
    process.exitCode = 1;
  } finally {
    servidor.close();
  }
});
