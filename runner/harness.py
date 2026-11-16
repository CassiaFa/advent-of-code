"""Juge Python : exécute le code d'une personne contre des tests JSON.

Bibliothèque standard uniquement : ce fichier tourne aussi dans Pyodide (navigateur).
Point d'entrée : run_tests(code, fn_name, tests_json) -> chaîne JSON.
"""
import contextlib
import copy
import io
import json


def _norm(valeur):
    if isinstance(valeur, (list, tuple)):
        return [_norm(v) for v in valeur]
    if isinstance(valeur, dict):
        return {str(k): _norm(v) for k, v in sorted(valeur.items(), key=lambda kv: str(kv[0]))}
    if isinstance(valeur, float) and valeur.is_integer():
        return int(valeur)
    return valeur


def _json(valeur):
    return json.dumps(_norm(valeur), sort_keys=True, ensure_ascii=False, default=repr)


def run_tests(code, fn_name, tests_json):
    tests = json.loads(tests_json)
    sortie = io.StringIO()
    espace = {"__name__": "__exercice__"}

    try:
        with contextlib.redirect_stdout(sortie):
            exec(compile(code, "<ton_code>", "exec"), espace)
    except BaseException as e:  # noqa: BLE001 - on veut tout rattraper, y compris SystemExit
        return json.dumps(
            {"error": "Erreur dans ton code : " + type(e).__name__ + ": " + str(e), "results": [], "logs": sortie.getvalue()},
            ensure_ascii=False,
        )

    fn = espace.get(fn_name)
    if not callable(fn):
        return json.dumps(
            {
                "error": "La fonction `" + fn_name + "` est introuvable. Garde exactement ce nom.",
                "results": [],
                "logs": sortie.getvalue(),
            },
            ensure_ascii=False,
        )

    resultats = []
    for t in tests:
        base = {"hidden": True} if t.get("hidden") else {"args": t["args"], "expected": t["expected"]}
        try:
            with contextlib.redirect_stdout(sortie):
                obtenu = fn(*copy.deepcopy(t["args"]))
            affiche = "None" if obtenu is None else _json(obtenu)
            resultats.append({**base, "ok": _json(obtenu) == _json(t["expected"]), "got": affiche})
        except BaseException as e:  # noqa: BLE001
            resultats.append({**base, "ok": False, "got": "", "error": type(e).__name__ + ": " + str(e)})

    return json.dumps({"results": resultats, "logs": sortie.getvalue()}, ensure_ascii=False)
