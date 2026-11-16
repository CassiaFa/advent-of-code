// Juge JavaScript : exécute le code d'une personne contre des tests JSON.
// Script classique (pas de module) : chargé par importScripts() dans un Worker
// et par runner.mjs côté Node. Il définit une seule fonction globale : runJS.

function adventNormalize(valeur) {
  if (Array.isArray(valeur)) return valeur.map(adventNormalize);
  if (valeur && typeof valeur === "object") {
    const copie = {};
    for (const cle of Object.keys(valeur).sort()) copie[cle] = adventNormalize(valeur[cle]);
    return copie;
  }
  if (valeur === undefined) return null;
  if (typeof valeur === "number" && !Number.isFinite(valeur)) return String(valeur);
  return valeur;
}

function adventSame(a, b) {
  return JSON.stringify(adventNormalize(a)) === JSON.stringify(adventNormalize(b));
}

function adventShow(valeur) {
  if (valeur === undefined) return "undefined";
  try {
    const texte = JSON.stringify(valeur);
    return texte === undefined ? String(valeur) : texte;
  } catch (e) {
    return String(valeur);
  }
}

function adventClone(valeur) {
  return JSON.parse(JSON.stringify(valeur));
}

function runJS(code, fnName, tests) {
  const logs = [];
  const consoleBac = {
    log: (...args) => logs.push(args.map((a) => (typeof a === "string" ? a : adventShow(a))).join(" ")),
  };
  consoleBac.info = consoleBac.log;
  consoleBac.warn = consoleBac.log;
  consoleBac.error = consoleBac.log;

  let fn;
  try {
    fn = new Function(
      "console",
      code + "\n;return typeof " + fnName + ' === "function" ? ' + fnName + " : undefined;"
    )(consoleBac);
  } catch (e) {
    return { error: "Erreur dans ton code : " + (e && e.message ? e.message : String(e)), results: [], logs: logs.join("\n") };
  }
  if (typeof fn !== "function") {
    return {
      error: "La fonction `" + fnName + "` est introuvable. Garde exactement ce nom.",
      results: [],
      logs: logs.join("\n"),
    };
  }

  const results = tests.map((t) => {
    const base = t.hidden ? { hidden: true } : { args: t.args, expected: t.expected };
    try {
      const obtenu = fn(...adventClone(t.args));
      return { ...base, ok: adventSame(obtenu, t.expected), got: adventShow(obtenu) };
    } catch (e) {
      return { ...base, ok: false, got: "", error: e && e.message ? e.message : String(e) };
    }
  });
  return { results, logs: logs.join("\n") };
}
