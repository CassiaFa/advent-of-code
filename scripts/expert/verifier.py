"""Vérifie les exercices du niveau expert, au-delà de ce que fait `npm run validate`.

    python3 scripts/expert/verifier.py           # contrôle (ne modifie rien)
    python3 scripts/expert/verifier.py --write   # ajoute dans content/ les exercices expert absents

Pour chaque exercice défini dans jours_01_12.py et jours_13_24.py :
- les exemples cités dans l'énoncé (calculés à la main) sont comparés à la solution Python ;
- la solution est recoupée avec une méthode naïve indépendante, quand il y en a une ;
- les résultats attendus des tests sont recalculés ;
- l'exercice obtenu est comparé à celui de content/exercises/ : un écart signale que l'un des deux
  a été modifié sans l'autre.
La solution JavaScript, elle, est contrôlée par `npm run validate` (mêmes tests, mêmes résultats attendus).
Pour modifier un exercice expert : change-le ici, retire l'ancien de content/, puis relance avec --write.
"""
import json, copy, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jours_13_24  # noqa: F401  (complète la liste EX)
from jours_01_12 import EX
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "content")
ecrire = "--write" in sys.argv
ecarts = 0
recoupes = 0
assert len(EX) == 24 and [e["day"] for e in EX] == list(range(1, 25))
total_tests = 0
for e in EX:
    env = {}
    exec(e["py"], env)
    f = env[e["fn"][1]]
    run = lambda args: f(*copy.deepcopy(args))
    for args, attendu in e["examples"]:
        got = run(args)
        assert got == attendu, (e["day"], "exemple", args, got, attendu)
    brute = e.get("brute")
    for args in e.get("brute_on", []):
        ref = brute(copy.deepcopy(args))
        if ref is None: continue
        recoupes += 1
        got = run(args)
        assert got == ref, (e["day"], "brute", args, got, ref)
    tests = []
    for i, args in enumerate(e["tests"] + e["hidden"]):
        got = run(args)
        if "check" in e: assert e["check"](args, got), (e["day"], "check", args, got)
        json.dumps(got)
        t = {"args": args, "expected": got}
        if i >= len(e["tests"]): t["hidden"] = True
        tests.append(t)
    assert len(e["tests"]) >= 3 and len(e["hidden"]) >= 1
    total_tests += len(tests)
    js_name, py_name = e["fn"]
    assert "{fn}" in e["statement"] and (js_name == py_name or (js_name not in e["statement"] and py_name not in e["statement"])), e["day"]
    ex = {
        "id": "d%02d-expert" % e["day"], "day": e["day"], "level": "expert", "title": e["title"], "concept": e["concept"],
        "statement": e["statement"],
        "fn": {"javascript": js_name, "python": py_name},
        "starter": {"javascript": "function %s(%s) {\n  // %s\n}\n" % (js_name, e["params"][0], e["comment"]),
                    "python": "def %s(%s):\n    # %s\n    pass\n" % (py_name, e["params"][1], e["comment"])},
        "solution": {"javascript": e["js"], "python": e["py"]},
        "tests": tests, "hint": e["hint"],
    }
    chemin = "%s/exercises/day-%02d.json" % (ROOT, e["day"])
    brut = open(chemin, encoding="utf-8").read()
    jour = json.loads(brut)
    present = next((x for x in jour["exercises"] if x["level"] == "expert"), None)
    etat = "absent de content/" if present is None else "identique à content/" if present == ex else "DIFFÉRENT de content/"
    ecarts += present != ex
    print("J%02d %-40s %2d tests, %s méthode naïve, %s" % (e["day"], e["title"], len(tests), "avec" if brute else "sans", etat))
    if ecrire and present is None:
        # Insertion textuelle avant le crochet fermant de "exercises" : le reste du fichier garde sa mise en forme.
        assert list(json.loads(brut).keys())[-1] == "exercises" and not any(x["level"] == "expert" for x in json.loads(brut)["exercises"]), chemin
        corps = brut.rstrip()
        assert corps.endswith("}")
        pos = corps.rstrip("}").rstrip().rfind("]")
        avant = corps[:pos].rstrip()
        bloc = "\n".join("    " + l for l in json.dumps(ex, ensure_ascii=False, indent=2).split("\n"))
        neuf = avant + ",\n" + bloc + "\n  ]\n}\n"
        relu = json.loads(neuf)
        assert relu["exercises"][:-1] == json.loads(brut)["exercises"] and relu["exercises"][-1] == ex
        open(chemin, "w", encoding="utf-8").write(neuf)
print("%d tests, %d recoupements par méthode naïve, %d exercice(s) en écart avec content/." % (total_tests, recoupes, ecarts))
sys.exit(1 if ecarts and not ecrire else 0)
