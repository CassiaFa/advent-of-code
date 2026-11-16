// Lanceur Node du juge : chaque exécution tourne dans un sous-processus
// avec un délai maximal, ce qui neutralise les boucles infinies.
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ici = dirname(fileURLToPath(import.meta.url));
const HARNESS_JS = join(ici, "harness.js");
const HARNESS_PY = join(ici, "harness.py");

const SCRIPT_JS = `
const fs = require("node:fs");
const src = fs.readFileSync(process.argv[1], "utf8");
const runJS = new Function(src + "\\nreturn runJS;")();
const d = JSON.parse(fs.readFileSync(0, "utf8"));
process.stdout.write(JSON.stringify(runJS(d.code, d.fn, d.tests)));
`;

const SCRIPT_PY = `
import sys, json
exec(open(sys.argv[1], encoding="utf-8").read())
d = json.load(sys.stdin)
sys.stdout.write(run_tests(d["code"], d["fn"], json.dumps(d["tests"])))
`;

function lancer(commande, args, entree, timeoutMs) {
  const r = spawnSync(commande, args, {
    input: JSON.stringify(entree),
    encoding: "utf8",
    timeout: timeoutMs,
    maxBuffer: 5 * 1024 * 1024,
    env: { ...process.env, PYTHONIOENCODING: "utf-8" },
  });
  if (r.error && r.error.code === "ETIMEDOUT") {
    return { error: `Temps dépassé (${timeoutMs / 1000} s) : une boucle infinie, ou un code trop lent pour ce test ?`, results: [], logs: "", timeout: true };
  }
  if (r.error && r.error.code === "ENOENT") {
    return { error: `Programme introuvable : ${commande}. Installe-le pour jouer dans ce langage.`, results: [], logs: "", missing: true };
  }
  if (r.status !== 0) {
    return { error: "Le juge a échoué : " + (r.stderr || "").trim().split("\n").slice(-3).join(" "), results: [], logs: "" };
  }
  try {
    return JSON.parse(r.stdout);
  } catch {
    return { error: "Réponse illisible du juge.", results: [], logs: "" };
  }
}

/** Exécute `code` dans le langage donné contre les tests de l'exercice. */
export function juger(lang, code, exercice, { timeoutMs = 5000 } = {}) {
  const entree = { code, fn: exercice.fn[lang], tests: exercice.tests };
  if (lang === "javascript") {
    return lancer(process.execPath, ["-e", SCRIPT_JS, HARNESS_JS], entree, timeoutMs);
  }
  if (lang === "python") {
    return lancer(process.env.PYTHON || "python3", ["-I", "-c", SCRIPT_PY, HARNESS_PY], entree, timeoutMs);
  }
  return { error: `Langage inconnu : ${lang}`, results: [], logs: "" };
}

export function resume(rapport) {
  const total = rapport.results.length;
  const reussis = rapport.results.filter((r) => r.ok).length;
  return { total, reussis, tout: !rapport.error && total > 0 && reussis === total };
}
