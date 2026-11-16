// Worker : le code des joueurs ne s'exécute jamais dans la page principale.
// JavaScript : harness.js. Python : Pyodide (chargé une seule fois) + harness.py.
// Le thread principal tue ce Worker si l'exécution dépasse le délai.

importScripts("runner/harness.js"); // définit runJS

const PYODIDE_VERSION = "0.26.4";
const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v" + PYODIDE_VERSION + "/full/";
let pyRun = null;

async function initPython() {
  if (pyRun) return;
  self.postMessage({ type: "loading" });
  importScripts(PYODIDE_URL + "pyodide.js"); // définit loadPyodide
  const py = await loadPyodide({ indexURL: PYODIDE_URL });
  const harness = await (await fetch("runner/harness.py")).text();
  py.runPython(harness);
  pyRun = py.globals.get("run_tests");
}

function echec(message) {
  return { type: "result", payload: { error: message, results: [], logs: "" } };
}

self.onmessage = async (e) => {
  const { lang, code, fn, tests } = e.data;
  try {
    if (lang === "javascript") {
      self.postMessage({ type: "running" });
      self.postMessage({ type: "result", payload: runJS(code, fn, tests) });
    } else if (lang === "python") {
      try {
        await initPython();
      } catch (err) {
        self.postMessage(echec("Impossible de charger Python dans le navigateur (connexion ?). Réessaie, ou joue en JavaScript. Détail : " + (err && err.message ? err.message : err)));
        return;
      }
      self.postMessage({ type: "running" });
      self.postMessage({ type: "result", payload: JSON.parse(pyRun(code, fn, JSON.stringify(tests))) });
    } else {
      self.postMessage(echec("Langage inconnu : " + lang));
    }
  } catch (err) {
    self.postMessage(echec("Le moteur a rencontré un problème : " + (err && err.message ? err.message : err)));
  }
};
