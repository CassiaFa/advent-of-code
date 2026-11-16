# Exercices « expert », jours 13 à 24.
import random, itertools, datetime
from jours_01_12 import EX, add

# ------------------------------------------------------------------ J13
import re as _re
def brute13(motif, mots):
    return [m for m in mots if _re.fullmatch(motif, m)]
t13 = [["lut?ins*", ["lutin", "luins", "lutins", "lutinss", "luti"]], ["[a-c]+[0-9]", ["ab1", "c9", "d1", "abc", "a12"]], [".*", ["", "noel", "x9"]], ["gr.l+ots?", ["grelot", "grellots", "grlot", "grelo", "grolllot"]]]
h13 = [["", ["", "a"]], ["a*", ["", "a", "aaaa", "ab", "b"]], ["a+b?", ["a", "ab", "b", "aab", "abb", ""]], ["[xyz]", ["x", "y", "w", "xy", ""]], ["[a-cx-z0-2]*", ["abc", "xyz012", "d", "", "a3"]], [".+", ["", "a", "ab"]], ["a.*b.*c", ["abc", "aXbYc".lower(), "acb", "abcabc", "ac"]], ["[a-z]+[0-9]?[a-z]+", ["ab", "a1b", "a", "a12b", "abc9z", "9ab"]], ["a?a?a?aaa", ["aaa", "aaaa", "aaaaaa", "aaaaaaa", "aa"]], ["[ab]*a[ab][ab]", ["aaa", "babb", "bbb", "abab", "ab"]], ["s.p?in+", ["sapin", "sain", "spin", "sapinnn", "sapi", "sppin"]], ["0*[1-9][0-9]*", ["007", "0", "10", "000120", "", "1a"]]]
add(day=13, title="Le moteur du grimoire", concept="Moteur de motifs avec classes et répétitions",
    fn=("motsReconnus", "mots_reconnus"), params=("motif, mots", "motif, mots"), comment="Renvoie les mots que le motif décrit en entier",
    statement="""Le grimoire du sous-sol est écrit dans un langage de motifs plus riche que le précédent, et Pixel veut savoir **quelles vieilles commandes** il reconnaît. À toi d'écrire le moteur, **sans** utiliser les expressions régulières du langage.

Un **motif** est une suite d'**éléments**. Un élément décrit **un seul caractère** :
- une lettre minuscule ou un chiffre : ce caractère-là, et pas un autre ;
- un point `.` : n'importe quel caractère ;
- une **classe** entre crochets : un des caractères listés. Dans une classe, `a-f` désigne tous les caractères de `a` à `f` inclus. `[a-cx0-9]` accepte donc `a`, `b`, `c`, `x` et tous les chiffres.

Un élément peut être suivi d'un **signe de répétition**, qui ne porte que sur lui :
- `*` : l'élément peut apparaître zéro, une ou plusieurs fois ;
- `+` : une ou plusieurs fois ;
- `?` : zéro ou une fois.

Écris une fonction `{fn}(motif, mots)` qui renvoie la liste des mots que le motif décrit **en entier** (du premier au dernier caractère, sans rien laisser de côté), dans l'ordre où ils apparaissent dans `mots`.

Précisions : le motif est toujours bien formé. Une classe n'est jamais vide, et le tiret n'y sert qu'à former un intervalle. Les mots ne contiennent que des lettres minuscules et des chiffres, et peuvent être vides. Le motif vide ne décrit que le mot vide.

Exemple : le motif `lut?ins*` reconnaît `lutin`, `luins`, `lutins` et `lutinss`, mais pas `luti`. Le motif `[a-c]+[0-9]` reconnaît `ab1` et `c9`, mais ni `d1`, ni `abc`, ni `a12`.

Attention au piège : devant `a?a?a?aaa`, un moteur qui essaie toutes les possibilités une par une peut s'y perdre très longtemps.
""",
    hint="Commence par traduire le motif en une liste d'éléments, chacun avec ses caractères acceptés et sa répétition. Puis pose la question en deux nombres : « les éléments à partir du numéro `j` décrivent-ils le mot à partir de la position `i` ? ». Chaque réponse ne dépend que de réponses voisines : retiens-les au lieu de les recalculer.",
    js="""function motsReconnus(motif, mots) {
  // 1. Traduire le motif en éléments : { tout, lettres, repetition }.
  const elements = [];
  let p = 0;
  while (p < motif.length) {
    const element = { tout: false, lettres: new Set(), repetition: "" };
    if (motif[p] === ".") {
      element.tout = true;
      p++;
    } else if (motif[p] === "[") {
      p++;
      while (motif[p] !== "]") {
        if (motif[p + 1] === "-" && motif[p + 2] !== "]") {
          for (let c = motif.charCodeAt(p); c <= motif.charCodeAt(p + 2); c++) element.lettres.add(String.fromCharCode(c));
          p += 3;
        } else {
          element.lettres.add(motif[p]);
          p++;
        }
      }
      p++;
    } else {
      element.lettres.add(motif[p]);
      p++;
    }
    if (p < motif.length && "*+?".includes(motif[p])) {
      element.repetition = motif[p];
      p++;
    }
    elements.push(element);
  }

  // 2. ok[j][i] : les éléments à partir de j décrivent-ils le mot à partir de la position i ?
  const reconnu = (mot) => {
    const m = elements.length;
    const n = mot.length;
    const ok = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(false));
    ok[m][n] = true;
    for (let j = m - 1; j >= 0; j--) {
      const e = elements[j];
      for (let i = n; i >= 0; i--) {
        const convient = i < n && (e.tout || e.lettres.has(mot[i]));
        if (e.repetition === "") ok[j][i] = convient && ok[j + 1][i + 1];
        else if (e.repetition === "?") ok[j][i] = ok[j + 1][i] || (convient && ok[j + 1][i + 1]);
        else if (e.repetition === "*") ok[j][i] = ok[j + 1][i] || (convient && ok[j][i + 1]);
        else ok[j][i] = convient && (ok[j][i + 1] || ok[j + 1][i + 1]);
      }
    }
    return ok[0][0];
  };
  return mots.filter(reconnu);
}
""",
    py="""def mots_reconnus(motif, mots):
    # 1. Traduire le motif en éléments : (tout, lettres, repetition).
    elements = []
    p = 0
    while p < len(motif):
        tout = False
        lettres = set()
        if motif[p] == ".":
            tout = True
            p += 1
        elif motif[p] == "[":
            p += 1
            while motif[p] != "]":
                if motif[p + 1] == "-" and motif[p + 2] != "]":
                    for c in range(ord(motif[p]), ord(motif[p + 2]) + 1):
                        lettres.add(chr(c))
                    p += 3
                else:
                    lettres.add(motif[p])
                    p += 1
            p += 1
        else:
            lettres.add(motif[p])
            p += 1
        repetition = ""
        if p < len(motif) and motif[p] in "*+?":
            repetition = motif[p]
            p += 1
        elements.append((tout, lettres, repetition))

    # 2. ok[j][i] : les éléments à partir de j décrivent-ils le mot à partir de la position i ?
    def reconnu(mot):
        m = len(elements)
        n = len(mot)
        ok = [[False] * (n + 2) for _ in range(m + 1)]
        ok[m][n] = True
        for j in range(m - 1, -1, -1):
            tout, lettres, repetition = elements[j]
            for i in range(n, -1, -1):
                convient = i < n and (tout or mot[i] in lettres)
                if repetition == "":
                    ok[j][i] = convient and ok[j + 1][i + 1]
                elif repetition == "?":
                    ok[j][i] = ok[j + 1][i] or (convient and ok[j + 1][i + 1])
                elif repetition == "*":
                    ok[j][i] = ok[j + 1][i] or (convient and ok[j][i + 1])
                else:
                    ok[j][i] = convient and (ok[j][i + 1] or ok[j + 1][i + 1])
        return ok[0][0]

    return [mot for mot in mots if reconnu(mot)]
""",
    tests=t13, hidden=h13 + [["a?" * 22 + "a" * 22, ["a" * 22, "a" * 30, "a" * 44, "a" * 45, "a" * 21]]],
    examples=[(["lut?ins*", ["lutin", "luins", "lutins", "lutinss", "luti"]], ["lutin", "luins", "lutins", "lutinss"]), (["[a-c]+[0-9]", ["ab1", "c9", "d1", "abc", "a12"]], ["ab1", "c9"])],
    brute=lambda a: brute13(*a), brute_on=t13 + h13)

# ------------------------------------------------------------------ J14
def brute14(j, m, a, n):
    d = datetime.date(a, m, j) + datetime.timedelta(days=n)
    return [d.day, d.month, d.year]
r = random.Random(14)
t14 = [[25, 12, 2024, 7], [1, 3, 2024, -1], [1, 3, 1900, -1], [31, 12, 1999, 366]]
h14 = [[24, 12, 2025, 0], [1, 1, 2000, -1], [28, 2, 2100, 1], [29, 2, 2000, 365], [29, 2, 2000, 1461], [1, 1, 1, 3652058], [31, 12, 9999, -3652058], [25, 12, 1, 1000000], [15, 6, 2024, -739000]] + [[r.randint(1, 28), r.randint(1, 12), r.randint(1500, 2500), r.randint(-400000, 400000)] for _ in range(5)]
add(day=14, title="Dans mille nuits", concept="Convertir une date en numéro de jour, et retour",
    fn=("ajouterJours", "ajouter_jours"), params=("jour, mois, annee, n", "jour, mois, annee, n"), comment="Renvoie la date [jour, mois, annee] située n jours plus tard",
    statement="""Le cristal du sous-sol compte en **nuits**, pas en dates : « la tournée a été interrompue il y a 36 525 nuits », dit le journal. Pour s'y retrouver, le Registre doit savoir avancer et reculer dans le calendrier d'un nombre quelconque de jours. Pas d'objet date du langage : tout se calcule à la main, avec des entiers.

Écris une fonction `{fn}(jour, mois, annee, n)` qui renvoie la date située `n` jours **après** la date donnée, sous la forme `[jour, mois, annee]`. Si `n` est négatif, on recule ; si `n` vaut `0`, la date ne change pas.

Rappels :
- Une année est **bissextile** si elle est divisible par 4, sauf les années divisibles par 100, qui ne le sont que si elles sont aussi divisibles par 400. `2000` et `2024` sont bissextiles, `1900` et `2100` ne le sont pas.
- Février a 29 jours les années bissextiles, 28 sinon. Avril, juin, septembre et novembre ont 30 jours, les autres mois 31.
- Ces règles s'appliquent à toutes les années, sans exception, même les plus anciennes.

Précisions : la date de départ est toujours valide, et les deux dates (départ et arrivée) sont comprises entre le 1er janvier de l'an `1` et le 31 décembre de l'an `9999`. `n` peut dépasser **trois millions** dans un sens comme dans l'autre : avancer d'un jour à la fois est possible, mais il existe bien plus élégant.

Exemples : 7 jours après le 25 décembre 2024, on est le `[1, 1, 2025]`. Un jour avant le 1er mars 2024, c'est le `[29, 2, 2024]` ; un jour avant le 1er mars 1900, c'est le `[28, 2, 1900]`.
""",
    hint="Donne un numéro à chaque jour, en comptant depuis le 1er janvier de l'an 1. Avec ce numéro, ajouter `n` jours devient une simple addition. Il te faut donc deux traductions : de la date vers le numéro, et du numéro vers la date. Pour la première, compte les années entières écoulées (dont les bissextiles), puis les mois, puis les jours.",
    js="""function ajouterJours(jour, mois, annee, n) {
  const bissextile = (a) => (a % 4 === 0 && a % 100 !== 0) || a % 400 === 0;
  const joursDuMois = (m, a) => (m === 2 ? (bissextile(a) ? 29 : 28) : [4, 6, 9, 11].includes(m) ? 30 : 31);
  // Nombre de jours écoulés entre le 1er janvier de l'an 1 et le 1er janvier de l'année a.
  const avantAnnee = (a) => {
    const y = a - 1;
    return y * 365 + Math.floor(y / 4) - Math.floor(y / 100) + Math.floor(y / 400);
  };

  // 1. De la date vers le numéro de jour.
  let numero = avantAnnee(annee) + jour - 1;
  for (let m = 1; m < mois; m++) numero += joursDuMois(m, annee);
  numero += n;

  // 2. Du numéro vers la date : une estimation de l'année, puis on ajuste.
  let a = Math.floor(numero / 366) + 1;
  while (avantAnnee(a + 1) <= numero) a++;
  let reste = numero - avantAnnee(a);
  let m = 1;
  while (reste >= joursDuMois(m, a)) {
    reste -= joursDuMois(m, a);
    m++;
  }
  return [reste + 1, m, a];
}
""",
    py="""def ajouter_jours(jour, mois, annee, n):
    def bissextile(a):
        return (a % 4 == 0 and a % 100 != 0) or a % 400 == 0

    def jours_du_mois(m, a):
        if m == 2:
            return 29 if bissextile(a) else 28
        return 30 if m in (4, 6, 9, 11) else 31

    # Nombre de jours écoulés entre le 1er janvier de l'an 1 et le 1er janvier de l'année a.
    def avant_annee(a):
        y = a - 1
        return y * 365 + y // 4 - y // 100 + y // 400

    # 1. De la date vers le numéro de jour.
    numero = avant_annee(annee) + jour - 1
    for m in range(1, mois):
        numero += jours_du_mois(m, annee)
    numero += n

    # 2. Du numéro vers la date : une estimation de l'année, puis on ajuste.
    a = numero // 366 + 1
    while avant_annee(a + 1) <= numero:
        a += 1
    reste = numero - avant_annee(a)
    m = 1
    while reste >= jours_du_mois(m, a):
        reste -= jours_du_mois(m, a)
        m += 1
    return [reste + 1, m, a]
""",
    tests=t14, hidden=h14,
    examples=[([25, 12, 2024, 7], [1, 1, 2025]), ([1, 3, 2024, -1], [29, 2, 2024]), ([1, 3, 1900, -1], [28, 2, 1900]), ([31, 12, 1999, 366], [31, 12, 2000])],
    brute=lambda a: brute14(*a), brute_on=t14 + h14)

# ------------------------------------------------------------------ J15
def brute15(v, chaine, tours, mod):
    v %= mod
    for _ in range(tours):
        for nom, k in chaine:
            v = (v + k) % mod if nom == "ajouter" else (v * k) % mod
    return v
r = random.Random(15)
def gen15(n, tours, mod):
    return [r.randint(0, 50), [[r.choice(["ajouter", "multiplier"]), r.randint(0, 30)] for _ in range(n)], tours, mod]
t15 = [[1, [["multiplier", 2], ["ajouter", 1]], 3, 1000], [1, [["multiplier", 2], ["ajouter", 1]], 0, 1000], [5, [["ajouter", 3]], 1000000000000, 7], [2, [["multiplier", 3]], 4, 50]]
h15s = [[7, [], 12, 5], [1234, [["ajouter", 1]], 0, 100], [3, [["multiplier", 0], ["ajouter", 4]], 5, 9], gen15(4, 17, 97), gen15(6, 1000, 1009), gen15(3, 12345, 2), gen15(8, 4096, 999983)]
h15b = [[1, [["multiplier", 2], ["ajouter", 1]], 1000000000000000, 1000003], [9, [["ajouter", 5], ["multiplier", 7], ["ajouter", 11], ["multiplier", 13]], 999999999999999, 999983], [0, [["multiplier", 1000000], ["ajouter", 999999]], 123456789012345, 1000003], [4, [["multiplier", 1]], 1000000000000000, 10]]
add(day=15, title="Un million de milliards de tours", concept="Composer des fonctions, puis composer la composition",
    fn=("apresLesTours", "apres_les_tours"), params=("valeur, chaine, tours, modulo", "valeur, chaine, tours, modulo"), comment="Renvoie la valeur après `tours` passages dans la chaîne, modulo `modulo`",
    statement="""Givrebug a refermé la chaîne d'emballage sur elle-même : à la sortie de la dernière machine, le paquet repart dans la première. Et il a réglé le compteur sur un nombre de tours délirant.

Une **chaîne** est une liste de machines, chacune étant `["ajouter", k]` (ajoute `k` au compteur du paquet) ou `["multiplier", k]` (le multiplie par `k`). Le compteur ne garde que le **reste de la division par `modulo`** : après chaque machine, la valeur est ramenée entre `0` et `modulo - 1`.

Écris une fonction `{fn}(valeur, chaine, tours, modulo)` qui renvoie la valeur du compteur après que le paquet a traversé la chaîne entière `tours` fois de suite.

Précisions :
- `valeur` et les `k` sont des entiers `>= 0`, au plus égaux à `1 000 000`. `modulo` est un entier entre `2` et `1 000 003`.
- `tours` est un entier `>= 0` qui peut atteindre `1 000 000 000 000 000` : simuler les tours un par un prendrait des années.
- Avec `0` tour, ou une chaîne vide, la réponse est simplement le reste de `valeur` dans la division par `modulo`.
- Dans ces limites, aucun calcul ne dépasse ce qu'un nombre entier ordinaire peut représenter exactement, à condition de prendre le reste **après chaque opération**.

Exemple : avec `valeur = 1`, la chaîne `[["multiplier", 2], ["ajouter", 1]]`, `3` tours et `modulo = 1000`, le compteur vaut successivement `3`, `7`, puis `15` : la réponse est `15`.
""",
    hint="Regarde ce que fait un tour complet, vu de l'extérieur : quelle que soit la chaîne, il transforme `x` en `a * x + b`, pour deux nombres `a` et `b` que tu peux calculer. Deux tours à la suite ont encore cette forme. Alors, combien d'étapes faut-il pour obtenir l'effet de 2 tours, de 4 tours, de 8 tours ?",
    js="""function apresLesTours(valeur, chaine, tours, modulo) {
  // Une transformation x -> a * x + b est notée [a, b].
  // suivre(f, g) : faire f, puis g.
  const suivre = ([a1, b1], [a2, b2]) => [(a2 * a1) % modulo, (a2 * b1 + b2) % modulo];

  // 1. Un tour complet de la chaîne, résumé en une seule transformation.
  let tour = [1, 0];
  for (const [nom, k] of chaine) {
    tour = suivre(tour, nom === "ajouter" ? [1, k % modulo] : [k % modulo, 0]);
  }

  // 2. Le tour répété `tours` fois : on double à chaque étape (1, 2, 4, 8 tours...).
  let total = [1, 0];
  let reste = tours;
  while (reste > 0) {
    if (reste % 2 === 1) total = suivre(total, tour);
    tour = suivre(tour, tour);
    reste = Math.floor(reste / 2);
  }
  return (total[0] * (valeur % modulo) + total[1]) % modulo;
}
""",
    py="""def apres_les_tours(valeur, chaine, tours, modulo):
    # Une transformation x -> a * x + b est notée (a, b).
    # suivre(f, g) : faire f, puis g.
    def suivre(f, g):
        return (g[0] * f[0] % modulo, (g[0] * f[1] + g[1]) % modulo)

    # 1. Un tour complet de la chaîne, résumé en une seule transformation.
    tour = (1, 0)
    for nom, k in chaine:
        tour = suivre(tour, (1, k % modulo) if nom == "ajouter" else (k % modulo, 0))

    # 2. Le tour répété `tours` fois : on double à chaque étape (1, 2, 4, 8 tours...).
    total = (1, 0)
    reste = tours
    while reste > 0:
        if reste % 2 == 1:
            total = suivre(total, tour)
        tour = suivre(tour, tour)
        reste //= 2
    return (total[0] * (valeur % modulo) + total[1]) % modulo
""",
    tests=t15, hidden=h15s + h15b,
    examples=[([1, [["multiplier", 2], ["ajouter", 1]], 3, 1000], 15), ([1, [["multiplier", 2], ["ajouter", 1]], 0, 1000], 1), ([5, [["ajouter", 3]], 1000000000000, 7], (5 + 3 * (10**12 % 7)) % 7), ([2, [["multiplier", 3]], 4, 50], 12)],
    brute=lambda a: brute15(*a), brute_on=[t15[0], t15[1], t15[3]] + h15s)

# ------------------------------------------------------------------ J16
def brute16(releves, duree, n):
    best = {}
    for nom in {x[1] for x in releves}:
        best[nom] = 0
        for t in range(0, max(x[0] for x in releves) + 1):
            best[nom] = max(best[nom], sum(x[2] for x in releves if x[1] == nom and t <= x[0] <= t + duree - 1))
    return [list(p) for p in sorted(best.items(), key=lambda p: (-p[1], p[0]))[:n]]
r = random.Random(16)
def gen16(k, noms, tmax, duree, n):
    return [[[r.randint(0, tmax), r.choice(noms), r.randint(0, 9)] for _ in range(k)], duree, n]
t16 = [[[[0, "pixel", 3], [4, "pixel", 2], [5, "pixel", 4], [9, "pixel", 1], [2, "flocon", 5], [30, "flocon", 5]], 5, 2], [[[10, "ana", 2], [10, "ana", 3], [11, "bob", 5]], 1, 5], [[[3, "zoe", 4], [1, "ali", 4]], 10, 1], [[[0, "a", 1], [10, "a", 1], [20, "a", 1]], 11, 3]]
h16 = [[[], 5, 3], [[[5, "a", 7]], 3, 0], [[[0, "a", 0], [1, "b", 0]], 2, 2], gen16(20, ["pixel", "flocon", "givre"], 30, 4, 2), gen16(40, ["a", "b", "c", "d", "e"], 60, 10, 3), gen16(60, ["lutin1", "lutin2", "lutin10"], 100, 1, 3), gen16(80, ["a", "b", "c", "d"], 50, 100, 10), gen16(50, ["x", "y"], 200, 25, 1)]
add(day=16, title="Les meilleures cadences", concept="Regrouper, trier, puis faire glisser une fenêtre",
    fn=("meilleuresCadences", "meilleures_cadences"), params=("releves, duree, n", "releves, duree, n"), comment="Renvoie les n meilleures paires [lutin, cadence]",
    statement="""Mère Noëlle veut récompenser les lutins capables d'un **coup de collier** : pas ceux qui ont fabriqué le plus de jouets sur toute la nuit, mais ceux qui en ont fabriqué le plus sur une courte période.

Tu reçois la liste des `releves` de la nuit, **dans le désordre**. Chaque relevé est un triplet `[minute, lutin, jouets]` : à la minute `minute` (un entier `>= 0`), le lutin `lutin` a terminé `jouets` jouets (un entier `>= 0`). Un même lutin peut avoir plusieurs relevés à la même minute.

La **cadence** d'un lutin est le plus grand nombre de jouets qu'il a terminés pendant `duree` minutes **consécutives** : on additionne tous ses relevés dont la minute est comprise entre `t` et `t + duree - 1` (bornes incluses), et on garde le meilleur total parmi tous les `t` possibles.

Écris une fonction `{fn}(releves, duree, n)` qui renvoie les `n` meilleures cadences, sous la forme d'une liste de paires `[lutin, cadence]`, triée par **cadence décroissante**. En cas d'égalité, les lutins sont rangés par **ordre alphabétique**.

Précisions : `duree` est un entier `>= 1`, `n` un entier `>= 0`. S'il y a moins de `n` lutins, renvoie-les tous. Les noms sont en minuscules, sans accent. Les minutes peuvent être très grandes : n'essaie pas tous les `t` un par un.

Exemple : avec les relevés `[[0, "pixel", 3], [4, "pixel", 2], [5, "pixel", 4], [9, "pixel", 1], [2, "flocon", 5], [30, "flocon", 5]]`, `duree = 5` et `n = 2`, la meilleure période de Pixel va de la minute 4 à la minute 8 (`2 + 4 = 6` jouets), et Flocon ne dépasse jamais `5` : la réponse est `[["pixel", 6], ["flocon", 5]]`.
""",
    hint="Trois étapes qui s'enchaînent : regrouper les relevés par lutin, résumer chaque groupe en un seul nombre, puis classer. Pour le résumé, trie les relevés du lutin par minute : la meilleure période commence forcément à la minute d'un relevé. Fais alors avancer le début et la fin de la période sans jamais revenir en arrière.",
    js="""function meilleuresCadences(releves, duree, n) {
  // 1. Regrouper les relevés par lutin.
  const parLutin = new Map();
  for (const [minute, lutin, jouets] of releves) {
    if (!parLutin.has(lutin)) parLutin.set(lutin, []);
    parLutin.get(lutin).push([minute, jouets]);
  }
  // 2. Résumer chaque groupe : la meilleure somme sur une fenêtre de `duree` minutes.
  const cadences = [...parLutin].map(([lutin, liste]) => {
    liste.sort((a, b) => a[0] - b[0]);
    let debut = 0;
    let somme = 0;
    let meilleure = 0;
    for (const [minute, jouets] of liste) {
      somme += jouets;
      while (liste[debut][0] < minute - duree + 1) {
        somme -= liste[debut][1];
        debut++;
      }
      if (somme > meilleure) meilleure = somme;
    }
    return [lutin, meilleure];
  });
  // 3. Classer : cadence décroissante, puis nom croissant.
  cadences.sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0));
  return cadences.slice(0, n);
}
""",
    py="""def meilleures_cadences(releves, duree, n):
    # 1. Regrouper les relevés par lutin.
    par_lutin = {}
    for minute, lutin, jouets in releves:
        par_lutin.setdefault(lutin, []).append((minute, jouets))
    # 2. Résumer chaque groupe : la meilleure somme sur une fenêtre de `duree` minutes.
    cadences = []
    for lutin, liste in par_lutin.items():
        liste.sort(key=lambda releve: releve[0])
        debut = 0
        somme = 0
        meilleure = 0
        for minute, jouets in liste:
            somme += jouets
            while liste[debut][0] < minute - duree + 1:
                somme -= liste[debut][1]
                debut += 1
            meilleure = max(meilleure, somme)
        cadences.append([lutin, meilleure])
    # 3. Classer : cadence décroissante, puis nom croissant.
    cadences.sort(key=lambda paire: (-paire[1], paire[0]))
    return cadences[:n]
""",
    tests=t16, hidden=h16 + [[[[1000000000, "a", 4], [999999990, "a", 5], [0, "a", 8], [999999991, "b", 9]], 11, 2]],
    examples=[([[[0, "pixel", 3], [4, "pixel", 2], [5, "pixel", 4], [9, "pixel", 1], [2, "flocon", 5], [30, "flocon", 5]], 5, 2], [["pixel", 6], ["flocon", 5]]), ([[[3, "zoe", 4], [1, "ali", 4]], 10, 1], [["ali", 4]])],
    brute=lambda a: brute16(*a) if a[0] else [], brute_on=t16 + h16)

# ------------------------------------------------------------------ J17
t17 = [[{"traineau": {"places": 2, "couleur": "rouge"}, "rennes": 8}, {"traineau": {"places": 4, "couleur": "rouge"}, "rennes": 8}, {"traineau": {"places": 2, "couleur": "or"}, "rennes": 9, "luge": 1}],
       [{"x": 1}, {"x": 2}, {"x": 3}],
       [{"x": 1, "y": 1}, {"y": 1}, {"x": 1, "y": 2}],
       [{"a": {"b": 1}}, {"a": {"b": 2, "c": 5}}, {"a": {"b": 3, "c": 6, "d": 7}}]]
h17 = [[{}, {}, {}], [{"x": 1}, {"x": 1}, {"x": 1}], [{"x": 1}, {}, {}], [{"x": 1}, {}, {"x": 2}], [{"x": 1}, {"x": 2}, {}],
       [{}, {"n": "sapin"}, {"n": "sapin"}], [{}, {"n": {"a": 1}}, {"n": {"b": 2}}], [{"n": 5}, {"n": {"a": 1}}, {"n": {"a": 2, "b": 3}}],
       [{"n": {"a": 1}}, {"n": 7}, {"n": {"a": 1, "b": 2}}], [{"n": {"a": {"b": {"c": 1}}}}, {"n": {"a": {"b": {"c": 2}}}}, {"n": {"a": {"b": {"c": 1, "d": 4}}, "e": "x"}}],
       [{"z": {"k": 1}, "a": {"k": 1}}, {"z": {"k": 2}, "a": {"k": 3}}, {"z": {"k": 9}, "a": {"k": 8}}], [{"p": {"q": 1}}, {"p": {}}, {"p": {"q": 1, "r": 2}}], [{"p": {"q": {"r": 1}}}, {"p": {"q": {"r": 1}}}, {}]]
add(day=17, title="Deux lutins, un seul registre", concept="Fusion à trois versions, sans rien modifier",
    fn=("fusionner", "fusionner"), params=("base, a, b", "base, a, b"), comment="Renvoie { fusion, conflits } sans modifier base, a ni b",
    statement="""Cette nuit, deux lutins sont partis chacun avec une **copie** du Grand Registre, et chacun y a fait ses corrections. Au matin, il faut réunir leurs deux versions `a` et `b` en une seule, en s'aidant de la version de départ `base`. Et bien sûr, **sans toucher** à aucune des trois : Pixel te l'a fait promettre.

Un registre est un dictionnaire dont les valeurs sont des nombres, des textes ou d'autres dictionnaires du même genre. Pour chaque clé présente dans au moins une des trois versions, on applique **la première règle qui convient** (une clé absente d'une version y est « absente », et c'est un état comme un autre) :

1. `a` et `b` sont **d'accord** (même valeur, ou absente des deux côtés) : on garde ce sur quoi ils s'accordent.
2. `a` n'a **rien changé** par rapport à `base` : on garde la version de `b`.
3. `b` n'a **rien changé** par rapport à `base` : on garde la version de `a`.
4. `a` et `b` contiennent **tous les deux un dictionnaire** : on fusionne ces deux dictionnaires avec les mêmes règles, clé par clé. La base utilisée est le dictionnaire de `base` pour cette clé ou, si `base` n'en a pas (clé absente, ou valeur qui n'est pas un dictionnaire), le dictionnaire vide.
5. Sinon, c'est un **conflit** : on garde la version de `a`, et on note le chemin de la clé.

« Garder » une version où la clé est absente, c'est ne pas la mettre dans le résultat : une suppression est une modification comme une autre.

Écris une fonction `{fn}(base, a, b)` qui renvoie un dictionnaire à deux clés : `"fusion"`, le registre réuni, et `"conflits"`, la liste des chemins en conflit, **triée par ordre alphabétique**. Un chemin est la suite des clés traversées, séparées par des points : `"traineau.couleur"`.

Précisions : deux dictionnaires sont égaux s'ils ont les mêmes clés avec des valeurs égales, quel que soit l'ordre des clés. Les clés sont des textes en minuscules, sans point. Les trois registres reçus peuvent être vides.

Exemple : avec `base = {"x": 1, "y": 1}`, `a = {"y": 1}` et `b = {"x": 1, "y": 2}`, le lutin A a supprimé `x` (B n'y a pas touché) et le lutin B a changé `y` (A n'y a pas touché) : la réponse est `{"fusion": {"y": 2}, "conflits": []}`. Avec `base = {"x": 1}`, `a = {"x": 2}` et `b = {"x": 3}`, les deux ont changé `x` différemment : `{"fusion": {"x": 2}, "conflits": ["x"]}`.
""",
    hint="Il te faut d'abord un moyen de dire « absente », différent de toutes les valeurs possibles, et une fonction qui compare deux valeurs en profondeur. Ensuite, les cinq règles se suivent dans l'ordre, et la quatrième se rappelle elle-même. Construis toujours un nouveau dictionnaire : ne range jamais dans le résultat un morceau que tu comptes encore modifier.",
    js="""function fusionner(base, a, b) {
  const estDico = (v) => typeof v === "object" && v !== null;
  // Égalité en profondeur ; `undefined` veut dire « clé absente ».
  const egal = (x, y) => {
    if (!estDico(x) || !estDico(y)) return x === y;
    const cles = Object.keys(x);
    return cles.length === Object.keys(y).length && cles.every((c) => c in y && egal(x[c], y[c]));
  };
  const copie = (v) => (estDico(v) ? Object.fromEntries(Object.keys(v).map((c) => [c, copie(v[c])])) : v);
  const conflits = [];

  const fusion = (vBase, vA, vB, chemin) => {
    const resultat = {};
    const cles = new Set([...Object.keys(vBase), ...Object.keys(vA), ...Object.keys(vB)]);
    for (const cle of cles) {
      const x = vBase[cle];
      const y = vA[cle];
      const z = vB[cle];
      const ici = chemin ? chemin + "." + cle : cle;
      let garde;
      if (egal(y, z)) garde = y;
      else if (egal(y, x)) garde = z;
      else if (egal(z, x)) garde = y;
      else if (estDico(y) && estDico(z)) {
        resultat[cle] = fusion(estDico(x) ? x : {}, y, z, ici);
        continue;
      } else {
        conflits.push(ici);
        garde = y;
      }
      if (garde !== undefined) resultat[cle] = copie(garde);
    }
    return resultat;
  };

  const reuni = fusion(base, a, b, "");
  return { fusion: reuni, conflits: conflits.sort() };
}
""",
    py="""def fusionner(base, a, b):
    absente = object()  # un marqueur qui ne ressemble à aucune valeur du registre
    conflits = []

    def copie(v):
        return {c: copie(x) for c, x in v.items()} if isinstance(v, dict) else v

    def fusion(v_base, v_a, v_b, chemin):
        resultat = {}
        for cle in set(v_base) | set(v_a) | set(v_b):
            x = v_base.get(cle, absente)
            y = v_a.get(cle, absente)
            z = v_b.get(cle, absente)
            ici = chemin + "." + cle if chemin else cle
            # En Python, == compare déjà les dictionnaires en profondeur.
            if y == z:
                garde = y
            elif y == x:
                garde = z
            elif z == x:
                garde = y
            elif isinstance(y, dict) and isinstance(z, dict):
                resultat[cle] = fusion(x if isinstance(x, dict) else {}, y, z, ici)
                continue
            else:
                conflits.append(ici)
                garde = y
            if garde is not absente:
                resultat[cle] = copie(garde)
        return resultat

    reuni = fusion(base, a, b, "")
    return {"fusion": reuni, "conflits": sorted(conflits)}
""",
    tests=t17, hidden=h17,
    examples=[(t17[0], {"fusion": {"traineau": {"places": 4, "couleur": "or"}, "rennes": 9, "luge": 1}, "conflits": []}), (t17[1], {"fusion": {"x": 2}, "conflits": ["x"]}), (t17[2], {"fusion": {"y": 2}, "conflits": []}), (t17[3], {"fusion": {"a": {"b": 2, "c": 5, "d": 7}}, "conflits": ["a.b", "a.c"]}),
              ([{"n": 5}, {"n": {"a": 1}}, {"n": {"a": 2, "b": 3}}], {"fusion": {"n": {"a": 1, "b": 3}}, "conflits": ["n.a"]})])

# ------------------------------------------------------------------ J18
def M(nom, joie, *enfants): return {"nom": nom, "joie": joie, "enfants": list(enfants)}
def brute18(arbre):
    noeuds = []; parent = {}
    def voir(n, p):
        noeuds.append(n); parent[len(noeuds) - 1] = p; moi = len(noeuds) - 1
        for e in n["enfants"]: voir(e, moi)
    voir(arbre, -1)
    best = 0
    for mask in range(1 << len(noeuds)):
        if all(not (mask >> i & 1 and parent[i] >= 0 and mask >> parent[i] & 1) for i in range(len(noeuds))):
            best = max(best, sum(noeuds[i]["joie"] for i in range(len(noeuds)) if mask >> i & 1))
    return best
r = random.Random(18)
compteur18 = [0]
def gen18(n):
    compteur18[0] = 0
    noeuds = [M("m0", r.randint(0, 20))]
    for i in range(1, n):
        e = M("m%d" % i, r.randint(0, 20)); r.choice(noeuds)["enfants"].append(e); noeuds.append(e)
    return [noeuds[0]]
chaine18 = M("c0", 5)
_c = chaine18
for i, v in enumerate([1, 1, 9, 2, 8, 8, 1, 7]):
    e = M("c%d" % (i + 1), v); _c["enfants"].append(e); _c = e
t18 = [[M("mere", 10, M("fils", 4, M("petit", 7), M("petite", 6)), M("fille", 8))], [M("seule", 3)], [M("a", 1, M("b", 10))], [M("a", 5, M("b", 1, M("c", 1, M("d", 5))))]]
h18 = [[M("zero", 0)], [M("a", 2, M("b", 2), M("c", 2), M("d", 2))], [chaine18], gen18(8), gen18(12), gen18(15), gen18(16), gen18(40)]
add(day=18, title="Le réveillon sans dispute", concept="Arbre : la meilleure réponse « avec » et « sans » chaque nœud",
    fn=("joieMaximale", "joie_maximale"), params=("arbre", "arbre"), comment="Renvoie la joie totale maximale des invités",
    statement="""Mère Noëlle organise le grand réveillon de la famille. Une seule règle, mais elle y tient : pour éviter les disputes, on n'invite **jamais en même temps un parent et l'un de ses enfants directs**. Grands-parents et petits-enfants s'entendent très bien, eux : ils peuvent venir ensemble.

Chaque membre de la famille est un dictionnaire `{"nom": "...", "joie": ..., "enfants": [ ... ]}` : `joie` est un entier `>= 0`, la bonne humeur qu'il apporte à la fête, et `enfants` la liste de ses enfants, décrits de la même façon.

Écris une fonction `{fn}(arbre)` qui renvoie la **plus grande joie totale** possible : la somme des `joie` des invités, pour la meilleure liste d'invités qui respecte la règle.

Précisions :
- `arbre` est le membre le plus ancien de la famille ; on peut très bien ne pas l'inviter.
- Un membre sans enfant a une liste `enfants` vide.
- La famille peut compter des milliers de membres : essayer toutes les listes d'invités est sans espoir.

Exemple : la mère (joie `10`) a un fils (`4`) et une fille (`8`). Le fils a deux enfants, de joie `7` et `6`. Inviter la mère et ses deux petits-enfants donne `10 + 7 + 6 = 23`, et aucune autre liste ne fait mieux : la réponse est `23`.

Méfie-toi de l'idée « une génération sur deux » : avec une lignée de quatre personnes de joie `5`, `1`, `1`, `5`, la meilleure fête réunit la première et la dernière, pour une joie de `10`.
""",
    hint="Pour chaque membre, calcule **deux** nombres au lieu d'un : la meilleure joie de sa branche s'il vient, et la meilleure s'il ne vient pas. S'il vient, ses enfants restent chez eux. S'il ne vient pas, chaque enfant est libre de faire ce qui l'arrange le mieux.",
    js="""function joieMaximale(arbre) {
  // Renvoie [meilleure joie de la branche si ce membre vient, meilleure joie s'il ne vient pas].
  function visiter(membre) {
    let avec = membre.joie;
    let sans = 0;
    for (const enfant of membre.enfants) {
      const [avecEnfant, sansEnfant] = visiter(enfant);
      avec += sansEnfant; // le parent vient : l'enfant reste chez lui
      sans += Math.max(avecEnfant, sansEnfant); // sinon, l'enfant fait au mieux
    }
    return [avec, sans];
  }
  return Math.max(...visiter(arbre));
}
""",
    py="""def joie_maximale(arbre):
    # Renvoie (meilleure joie de la branche si ce membre vient, meilleure joie s'il ne vient pas).
    def visiter(membre):
        avec = membre["joie"]
        sans = 0
        for enfant in membre["enfants"]:
            avec_enfant, sans_enfant = visiter(enfant)
            avec += sans_enfant  # le parent vient : l'enfant reste chez lui
            sans += max(avec_enfant, sans_enfant)  # sinon, l'enfant fait au mieux
        return avec, sans

    return max(visiter(arbre))
""",
    tests=t18, hidden=h18,
    examples=[(t18[0], 23), (t18[1], 3), (t18[2], 10), (t18[3], 10)],
    brute=lambda a: brute18(*a), brute_on=t18 + h18[:7])

# ------------------------------------------------------------------ J19
def brute19(routes):
    def composantes(rs):
        parent = {}
        def find(x):
            parent.setdefault(x, x)
            while parent[x] != x:
                parent[x] = parent[parent[x]]; x = parent[x]
            return x
        for a, b in routes: find(a); find(b)
        for a, b in rs: parent[find(a)] = find(b)
        return len({find(x) for x in list(parent)})
    base = composantes(routes); out = set()
    for i in range(len(routes)):
        if composantes(routes[:i] + routes[i + 1:]) > base: out.add(tuple(sorted(routes[i])))
    return sorted([list(x) for x in out])
r = random.Random(19)
def gen19(n, m):
    noms = ["v%02d" % i for i in range(n)]; rs = []
    for _ in range(m):
        a, b = r.sample(noms, 2); rs.append([a, b])
    return [rs]
t19 = [[[["a", "b"], ["b", "c"], ["c", "a"], ["c", "d"]]], [[["a", "b"], ["b", "c"]]], [[["a", "b"], ["a", "b"]]], [[["lac", "gare"], ["gare", "moulin"], ["moulin", "lac"], ["moulin", "pont"], ["pont", "mairie"], ["mairie", "ecole"], ["ecole", "pont"], ["ecole", "ferme"]]]]
h19 = [[[]], [[["b", "a"]]], [[["a", "b"], ["c", "d"], ["d", "e"], ["e", "c"]]], [[["a", "b"], ["b", "a"], ["b", "c"]]], gen19(8, 9), gen19(12, 14), gen19(15, 16), gen19(20, 24), gen19(25, 26), [[["n%02d" % i, "n%02d" % (i + 1)] for i in range(40)]]]
add(day=19, title="Les routes à déneiger d'abord", concept="Graphes : trouver les ponts",
    fn=("routesCritiques", "routes_critiques"), params=("routes", "routes"), comment="Renvoie la liste triée des routes critiques [x, y]",
    statement="""La tempête approche et il n'y a qu'un seul chasse-neige. Mère Noëlle veut savoir quelles routes dégager en priorité : celles dont la fermeture **couperait le village en deux**.

`routes` est une liste de paires `[village1, village2]` : chaque route relie deux villages différents et se parcourt dans les deux sens. Une route est **critique** si, en la fermant, il existe deux villages qui pouvaient se rejoindre avant et qui ne le peuvent plus.

Écris une fonction `{fn}(routes)` qui renvoie la liste des routes critiques. Chaque route est écrite `[x, y]` avec `x` avant `y` dans l'ordre alphabétique, et la liste est triée par `x`, puis par `y`.

Précisions :
- Les noms des villages sont en minuscules, sans accent.
- La carte peut être en plusieurs morceaux dès le départ : cela ne change rien à la définition.
- Si **deux routes** relient les deux mêmes villages, aucune des deux n'est critique : l'autre prend le relais.
- Sans aucune route, renvoie la liste vide.
- Il peut y avoir des milliers de routes : fermer chaque route une par une pour voir ce qui se passe serait trop lent. Il existe une méthode qui trouve tout en **un seul parcours** de la carte.

Exemple : avec `[["a", "b"], ["b", "c"], ["c", "a"], ["c", "d"]]`, les villages `a`, `b` et `c` forment une boucle, où l'on peut toujours faire le tour par l'autre côté. Seule la route vers `d` est critique : `[["c", "d"]]`.
""",
    hint="Explore la carte en profondeur en numérotant les villages dans l'ordre où tu les découvres. Pour chaque village, retiens le plus petit numéro qu'on peut atteindre depuis lui ou depuis ce qu'il y a derrière lui, sans repasser par la route d'arrivée. Si, derrière une route, personne ne sait remonter plus haut que le village d'arrivée, il n'y a pas d'autre chemin.",
    js="""function routesCritiques(routes) {
  // voisins : village -> liste de [autre village, numéro de la route]
  const voisins = new Map();
  routes.forEach(([a, b], numero) => {
    if (!voisins.has(a)) voisins.set(a, []);
    if (!voisins.has(b)) voisins.set(b, []);
    voisins.get(a).push([b, numero]);
    voisins.get(b).push([a, numero]);
  });
  const ordre = new Map(); // ordre de découverte de chaque village
  const critiques = [];
  let compteur = 0;

  // Renvoie le plus petit ordre de découverte atteignable depuis `village` et ce qu'il y a derrière.
  function explorer(village, routeArrivee) {
    ordre.set(village, compteur);
    let plusHaut = compteur;
    compteur++;
    for (const [autre, numero] of voisins.get(village)) {
      if (numero === routeArrivee) continue; // on ne rebrousse pas chemin par la même route
      if (ordre.has(autre)) {
        plusHaut = Math.min(plusHaut, ordre.get(autre));
      } else {
        const remonte = explorer(autre, numero);
        plusHaut = Math.min(plusHaut, remonte);
        // Derrière cette route, personne ne remonte jusqu'ici : c'est le seul passage.
        if (remonte > ordre.get(village)) critiques.push(village < autre ? [village, autre] : [autre, village]);
      }
    }
    return plusHaut;
  }

  for (const village of voisins.keys()) {
    if (!ordre.has(village)) explorer(village, -1);
  }
  return critiques.sort((p, q) => (p[0] < q[0] ? -1 : p[0] > q[0] ? 1 : p[1] < q[1] ? -1 : p[1] > q[1] ? 1 : 0));
}
""",
    py="""def routes_critiques(routes):
    # voisins : village -> liste de (autre village, numéro de la route)
    voisins = {}
    for numero, (a, b) in enumerate(routes):
        voisins.setdefault(a, []).append((b, numero))
        voisins.setdefault(b, []).append((a, numero))
    ordre = {}  # ordre de découverte de chaque village
    critiques = []

    # Renvoie le plus petit ordre de découverte atteignable depuis `village` et ce qu'il y a derrière.
    def explorer(village, route_arrivee):
        ordre[village] = len(ordre)
        plus_haut = ordre[village]
        for autre, numero in voisins[village]:
            if numero == route_arrivee:
                continue  # on ne rebrousse pas chemin par la même route
            if autre in ordre:
                plus_haut = min(plus_haut, ordre[autre])
            else:
                remonte = explorer(autre, numero)
                plus_haut = min(plus_haut, remonte)
                # Derrière cette route, personne ne remonte jusqu'ici : c'est le seul passage.
                if remonte > ordre[village]:
                    critiques.append(sorted([village, autre]))
        return plus_haut

    for village in voisins:
        if village not in ordre:
            explorer(village, -1)
    return sorted(critiques)
""",
    tests=t19, hidden=h19,
    examples=[(t19[0], [["c", "d"]]), (t19[1], [["a", "b"], ["b", "c"]]), (t19[2], []), (t19[3], [["ecole", "ferme"], ["moulin", "pont"]])],
    brute=lambda a: brute19(*a), brute_on=t19 + h19)

# ------------------------------------------------------------------ J20
def brute20(n, pas):
    return sum(1 for x in range(1, n + 1) if any(x % p == 0 for p in pas))
r = random.Random(20)
t20 = [[10, [2, 3]], [100, [2, 3, 5]], [1000000000, [1]], [20, [4, 6]]]
h20s = [[50, []], [1, [2]], [30, [5, 5]], [1000, [7, 11, 13]], [5000, [6, 10, 15, 4]], [2000, [3, 9, 27, 81]], [9999, [r.randint(2, 60) for _ in range(8)]]]
h20b = [[1000000000, [2, 3, 5, 7, 11, 13]], [999999937, [99991, 99989, 4]], [1000000000, [r.randint(2, 100000) for _ in range(15)]], [1000000000, [6, 10, 14, 15, 21, 35, 22, 33, 55, 77, 26, 39]], [987654321, [100000, 99999, 99998, 2]]]
add(day=20, title="Les maisons servies", concept="Compter sans parcourir : inclusion-exclusion",
    fn=("maisonsServies", "maisons_servies"), params=("n, pas", "n, pas"), comment="Renvoie le nombre de maisons qui reçoivent au moins un cadeau",
    statement="""La grande avenue de Givreville compte `n` maisons, numérotées de `1` à `n`. Chaque lutin de la tournée a sa manie : celui dont le **pas** vaut `p` ne livre que les maisons dont le numéro est un **multiple de `p`** (`p`, `2p`, `3p`...). Pixel veut savoir combien de maisons reçoivent **au moins un cadeau**. Le Registre a essayé de les compter une par une : au bout de trois heures, il n'avait pas fini.

Écris une fonction `{fn}(n, pas)` qui renvoie le nombre de maisons, parmi les `n`, dont le numéro est un multiple d'**au moins un** des pas de la liste.

Précisions :
- `n` est un entier entre `1` et `1 000 000 000`.
- `pas` contient au plus `15` entiers, chacun entre `1` et `100 000`. Le même pas peut apparaître plusieurs fois : cela ne change rien au résultat.
- Sans aucun lutin, aucune maison n'est servie : `0`.
- Avec un milliard de maisons, toute méthode qui les passe en revue une à une est hors course.

Exemple : avec `n = 10` et les pas `[2, 3]`, les maisons servies sont `2, 3, 4, 6, 8, 9, 10` : la réponse est `7`. Remarque que la maison `6` est servie par les deux lutins, mais ne compte qu'une fois.
""",
    hint="Combien y a-t-il de multiples de `p` entre 1 et `n` ? Une division suffit. Avec deux lutins, additionner leurs deux comptes compte deux fois les maisons servies par les deux : il faut les retirer une fois. Et ces maisons-là, ce sont les multiples de quel nombre ? Généralise à trois lutins, puis à tous les groupes de lutins... en t'arrêtant dès qu'un groupe ne peut plus servir aucune maison.",
    js="""function maisonsServies(n, pas) {
  const pgcd = (a, b) => (b === 0 ? a : pgcd(b, a % b));
  // On ajoute les groupes d'un lutin, on retire ceux de deux, on ajoute ceux de trois...
  // `commun` : le plus petit numéro servi par tous les lutins du groupe en cours.
  function compter(depart, commun, signe) {
    let total = 0;
    for (let i = depart; i < pas.length; i++) {
      const suivant = (commun / pgcd(commun, pas[i])) * pas[i];
      if (suivant > n) continue; // ce groupe ne sert plus aucune maison, ni aucun groupe plus grand
      total += signe * Math.floor(n / suivant) + compter(i + 1, suivant, -signe);
    }
    return total;
  }
  return compter(0, 1, 1);
}
""",
    py="""def maisons_servies(n, pas):
    def pgcd(a, b):
        while b:
            a, b = b, a % b
        return a

    # On ajoute les groupes d'un lutin, on retire ceux de deux, on ajoute ceux de trois...
    # `commun` : le plus petit numéro servi par tous les lutins du groupe en cours.
    def compter(depart, commun, signe):
        total = 0
        for i in range(depart, len(pas)):
            suivant = commun // pgcd(commun, pas[i]) * pas[i]
            if suivant > n:
                continue  # ce groupe ne sert plus aucune maison, ni aucun groupe plus grand
            total += signe * (n // suivant) + compter(i + 1, suivant, -signe)
        return total

    return compter(0, 1, 1)
""",
    tests=t20, hidden=h20s + h20b,
    examples=[([10, [2, 3]], 7), ([100, [2, 3, 5]], 74), ([1000000000, [1]], 1000000000), ([20, [4, 6]], 7)],
    brute=lambda a: brute20(*a), brute_on=[t20[0], t20[1], t20[3]] + h20s)

# ------------------------------------------------------------------ J21
def brute21(notes):
    from functools import lru_cache
    t = tuple(notes)
    @lru_cache(None)
    def f(s):
        if not s: return 0
        best = None
        for k in (1, 2):
            if k <= len(s):
                for gain, reste in ((sum(s[:k]), s[k:]), (sum(s[-k:]), s[:-k])):
                    v = gain - f(reste)
                    if best is None or v > best: best = v
        return best
    return f(t)
r = random.Random(21)
t21 = [[[5, 3, 7]], [[4]], [[1, 100, 1]], [[2, 9, 1, 8, 3]]]
h21 = [[[]], [[3, 3]], [[-5]], [[-2, -9, -4]], [[1, 2, 3, 4, 5, 6, 7, 8]], [[10, -20, 30, -40, 50]]] + [[[r.randint(-10, 30) for _ in range(n)]] for n in (12, 20, 35, 60)]
add(day=21, title="La comptine à deux voix", concept="Mémoïsation sur un intervalle : jeu à deux joueurs",
    fn=("avanceMaximale", "avance_maximale"), params=("notes", "notes"), comment="Renvoie l'avance du premier chanteur si les deux jouent au mieux",
    statement="""Le cristal chante la comptine du solstice, et deux lutins se la disputent. Les notes sont alignées sur la partition, chacune avec sa **valeur** (un entier, parfois négatif : une fausse note fait perdre des points). Les deux chanteurs jouent **chacun leur tour**. À son tour, un chanteur doit prendre **une ou deux notes**, à **une seule extrémité** de ce qui reste de la partition : soit au début, soit à la fin. Il marque la somme des notes qu'il prend. La partie s'arrête quand il n'y a plus de note.

Les deux chanteurs sont très malins : chacun joue de façon à finir avec la **plus grande avance possible** sur l'autre.

Écris une fonction `{fn}(notes)` qui renvoie l'**avance du premier chanteur** à la fin de la partie : son score moins celui du second. Le résultat peut être négatif.

Précisions :
- Prendre deux notes, c'est prendre les deux premières ou les deux dernières : jamais une de chaque côté.
- On est obligé de prendre au moins une note, même si elle est négative. S'il ne reste qu'une note, on prend celle-là.
- Une partition vide donne `0`.
- La partition peut compter quelques dizaines de notes : explorer toutes les parties possibles une par une prendrait jusqu'au solstice suivant.

Exemple : avec `[5, 3, 7]`, le premier chanteur prend les deux dernières notes (`3 + 7 = 10`) et laisse le `5` au second : son avance est `5`. Avec `[1, 100, 1]`, il prend `1` et `100` d'un même côté et finit avec `100` d'avance.
""",
    hint="Une partie en cours se résume à deux nombres : où commence et où finit ce qui reste de la partition. Pose-toi la question « quelle avance peut obtenir celui qui joue maintenant ? ». Après son coup, c'est l'autre qui se pose exactement la même question, sur un reste plus court. Les mêmes restes reviennent très souvent : note chaque réponse la première fois.",
    js="""function avanceMaximale(notes) {
  const memo = new Map();
  // Meilleure avance pour celui qui joue, quand il reste les notes de `debut` à `fin` (incluses).
  function avance(debut, fin) {
    if (debut > fin) return 0;
    const cle = debut * 1000 + fin;
    if (memo.has(cle)) return memo.get(cle);
    // Ce que je prends, moins la meilleure avance de l'autre sur ce que je lui laisse.
    let meilleure = notes[debut] - avance(debut + 1, fin);
    meilleure = Math.max(meilleure, notes[fin] - avance(debut, fin - 1));
    if (fin > debut) {
      meilleure = Math.max(meilleure, notes[debut] + notes[debut + 1] - avance(debut + 2, fin));
      meilleure = Math.max(meilleure, notes[fin] + notes[fin - 1] - avance(debut, fin - 2));
    }
    memo.set(cle, meilleure);
    return meilleure;
  }
  return avance(0, notes.length - 1);
}
""",
    py="""def avance_maximale(notes):
    memo = {}

    # Meilleure avance pour celui qui joue, quand il reste les notes de `debut` à `fin` (incluses).
    def avance(debut, fin):
        if debut > fin:
            return 0
        if (debut, fin) in memo:
            return memo[(debut, fin)]
        # Ce que je prends, moins la meilleure avance de l'autre sur ce que je lui laisse.
        meilleure = notes[debut] - avance(debut + 1, fin)
        meilleure = max(meilleure, notes[fin] - avance(debut, fin - 1))
        if fin > debut:
            meilleure = max(meilleure, notes[debut] + notes[debut + 1] - avance(debut + 2, fin))
            meilleure = max(meilleure, notes[fin] + notes[fin - 1] - avance(debut, fin - 2))
        memo[(debut, fin)] = meilleure
        return meilleure

    return avance(0, len(notes) - 1)
""",
    tests=t21, hidden=h21,
    examples=[([[5, 3, 7]], 5), ([[4]], 4), ([[1, 100, 1]], 100), ([[]], 0), ([[-5]], -5)],
    brute=lambda a: brute21(*a), brute_on=t21 + h21[:8])

# ------------------------------------------------------------------ J22
def brute22(cadeaux, pm, vm):
    fam = {}
    for f, p, v, j in cadeaux: fam.setdefault(f, []).append((p, v, j))
    best = 0
    for choix in itertools.product(*[[None] + g for g in fam.values()]):
        p = sum(c[0] for c in choix if c); v = sum(c[1] for c in choix if c)
        if p <= pm and v <= vm: best = max(best, sum(c[2] for c in choix if c))
    return best
r = random.Random(22)
def gen22(k, fams, pm, vm):
    return [[[r.choice(fams), r.randint(1, 8), r.randint(1, 8), r.randint(0, 20)] for _ in range(k)], pm, vm]
t22 = [[[["peluche", 2, 2, 5], ["peluche", 3, 1, 8], ["train", 2, 2, 6], ["livre", 1, 1, 3]], 4, 4], [[["luge", 5, 1, 9], ["luge", 1, 5, 9]], 4, 4], [[["a", 1, 1, 4], ["b", 1, 1, 4], ["c", 1, 1, 4]], 2, 3], [[["a", 3, 3, 10], ["a", 3, 3, 12], ["a", 3, 3, 11]], 9, 9]]
h22 = [[[], 5, 5], [[["a", 1, 1, 7]], 0, 9], [[["a", 2, 9, 5], ["b", 9, 2, 5], ["c", 5, 5, 6]], 10, 10], gen22(8, ["a", "b", "c"], 10, 10), gen22(10, ["a", "b", "c", "d"], 12, 9), gen22(12, ["a", "b", "c", "d", "e"], 15, 15), gen22(14, ["p", "q", "r", "s", "t", "u"], 20, 14), gen22(16, ["a", "b", "c", "d", "e", "f", "g"], 25, 25)]
add(day=22, title="Un seul cadeau par famille", concept="Sac à dos à deux contraintes, avec des groupes",
    fn=("joieDuTraineau", "joie_du_traineau"), params=("cadeaux, poidsMax, volumeMax", "cadeaux, poids_max, volume_max"), comment="Renvoie la joie totale maximale",
    statement="""Le traîneau a deux limites, et Mère Noëlle vient d'en ajouter une troisième. Il ne doit dépasser ni un **poids** total de `poidsMax`, ni un **volume** total de `volumeMax`. Et pour que tout le village soit servi, on charge **au plus un cadeau par famille**.

Chaque cadeau est une liste `[famille, poids, volume, joie]` : le nom de la famille à qui il est destiné, son poids et son volume (des entiers `>= 1`) et la joie qu'il apporte (un entier `>= 0`). Une même famille peut avoir plusieurs cadeaux en attente : il faudra en choisir un seul, ou aucun.

Écris une fonction `{fn}(cadeaux, poidsMax, volumeMax)` qui renvoie la **plus grande joie totale** qu'on peut charger en respectant les trois règles.

Précisions :
- `poidsMax` et `volumeMax` sont des entiers `>= 0`. Un total exactement égal à une limite est autorisé.
- Si on ne peut rien charger, la réponse est `0`.
- Il peut y avoir des dizaines de familles : essayer toutes les combinaisons est impossible. Les limites, elles, restent petites (quelques dizaines).

Exemple : avec `[["peluche", 2, 2, 5], ["peluche", 3, 1, 8], ["train", 2, 2, 6], ["livre", 1, 1, 3]]`, `poidsMax = 4` et `volumeMax = 4`, on peut charger la peluche à `8` et le livre (poids `4`, volume `2`) pour une joie de `11`. Les deux peluches ensemble feraient mieux, mais elles vont à la même famille.
""",
    hint="Garde un tableau à deux entrées : pour chaque poids et chaque volume disponibles, la meilleure joie obtenue avec les familles déjà traitées. Traite ensuite les familles une par une. Le point délicat : quand tu essaies les cadeaux d'une famille, chacun doit s'ajouter à un chargement qui ne contient **encore aucun** cadeau de cette famille.",
    js="""function joieDuTraineau(cadeaux, poidsMax, volumeMax) {
  // Regrouper les cadeaux par famille.
  const familles = new Map();
  for (const [famille, poids, volume, joie] of cadeaux) {
    if (!familles.has(famille)) familles.set(famille, []);
    familles.get(famille).push([poids, volume, joie]);
  }
  // meilleur[p][v] : joie maximale avec un poids <= p et un volume <= v, pour les familles déjà vues.
  let meilleur = Array.from({ length: poidsMax + 1 }, () => new Array(volumeMax + 1).fill(0));
  for (const groupe of familles.values()) {
    // On part d'une copie : chaque cadeau s'ajoute à un chargement SANS cette famille.
    const suivant = meilleur.map((ligne) => ligne.slice());
    for (const [poids, volume, joie] of groupe) {
      for (let p = poids; p <= poidsMax; p++) {
        for (let v = volume; v <= volumeMax; v++) {
          const total = meilleur[p - poids][v - volume] + joie;
          if (total > suivant[p][v]) suivant[p][v] = total;
        }
      }
    }
    meilleur = suivant;
  }
  return meilleur[poidsMax][volumeMax];
}
""",
    py="""def joie_du_traineau(cadeaux, poids_max, volume_max):
    # Regrouper les cadeaux par famille.
    familles = {}
    for famille, poids, volume, joie in cadeaux:
        familles.setdefault(famille, []).append((poids, volume, joie))
    # meilleur[p][v] : joie maximale avec un poids <= p et un volume <= v, pour les familles déjà vues.
    meilleur = [[0] * (volume_max + 1) for _ in range(poids_max + 1)]
    for groupe in familles.values():
        # On part d'une copie : chaque cadeau s'ajoute à un chargement SANS cette famille.
        suivant = [ligne[:] for ligne in meilleur]
        for poids, volume, joie in groupe:
            for p in range(poids, poids_max + 1):
                for v in range(volume, volume_max + 1):
                    total = meilleur[p - poids][v - volume] + joie
                    if total > suivant[p][v]:
                        suivant[p][v] = total
        meilleur = suivant
    return meilleur[poids_max][volume_max]
""",
    tests=t22, hidden=h22,
    examples=[(t22[0], 11), (t22[1], 0), (t22[2], 8), (t22[3], 12)],
    brute=lambda a: brute22(*a), brute_on=t22 + h22)

# ------------------------------------------------------------------ J23
def brute23(journal):
    attend = {}
    for ligne in journal:
        champs = ligne.split(" ")
        if champs[2] == "REPREND": attend.pop(champs[1], None); continue
        attend[champs[1]] = champs[3]
        vus = [champs[1]]; x = champs[3]
        while x in attend and x not in vus:
            vus.append(x); x = attend[x]
        if x == champs[1]: return [champs[0], sorted(vus)]
    return []
r = random.Random(23)
def gen23(k, noms):
    out = []; t = 6 * 60
    for _ in range(k):
        t += r.randint(0, 7); a = r.choice(noms)
        h = "%02d:%02d" % (t // 60, t % 60)
        out.append("%s %s REPREND" % (h, a) if r.random() < 0.3 else "%s %s ATTEND %s" % (h, a, r.choice([n for n in noms if n != a])))
    return [out]
t23 = [[["08:00 four ATTEND tapis", "08:05 tapis ATTEND grue", "08:07 four REPREND", "08:10 grue ATTEND four", "08:12 four ATTEND tapis"]], [["09:00 a ATTEND b", "09:01 b ATTEND c", "09:02 c REPREND"]], [["10:30 cristal ATTEND cristal"]], [["11:00 a ATTEND b", "11:00 b ATTEND a", "11:05 c ATTEND a"]]]
h23 = [[[]], [["07:00 a REPREND"]], [["07:00 a ATTEND b", "07:01 a ATTEND c", "07:02 c ATTEND a", "07:03 b ATTEND a"]], [["07:00 a ATTEND b", "07:01 b ATTEND c", "07:02 a ATTEND c", "07:03 c ATTEND b"]], [["07:00 d ATTEND a", "07:01 a ATTEND b", "07:02 b ATTEND c", "07:03 c ATTEND a"]], [["23:58 x-1 ATTEND x-2", "23:59 x-2 ATTEND x-3", "23:59 x-3 ATTEND x-1"]],
       gen23(12, ["four", "tapis", "grue", "cloche"]), gen23(20, ["a", "b", "c", "d", "e", "f"]), gen23(30, ["m1", "m2", "m3", "m4", "m5", "m6", "m7", "m8"]), gen23(25, ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]), gen23(40, ["p%d" % i for i in range(14)])]
add(day=23, title="Le cercle de ceux qui attendent", concept="Rejouer un journal et détecter un blocage",
    fn=("premierBlocage", "premier_blocage"), params=("journal", "journal"), comment="Renvoie [heure, noms triés] du premier blocage, ou []",
    statement="""Pixel a enfin trouvé la page du journal qui raconte la panne d'il y a cent ans. Rien n'a cassé : les machines se sont simplement mises à **s'attendre les unes les autres**, en rond, et plus rien n'a bougé. Reste à trouver l'instant exact où le cercle s'est refermé.

Chaque ligne du journal a l'une de ces deux formes, les champs étant séparés par **une seule espace** :
- `HH:MM machine ATTEND autre` : à partir de cette ligne, `machine` est à l'arrêt et attend `autre` ;
- `HH:MM machine REPREND` : `machine` n'attend plus personne.

Une machine n'attend qu'**une seule** autre machine à la fois : un nouveau `ATTEND` de sa part **remplace** le précédent. Un `REPREND` d'une machine qui n'attendait personne ne change rien.

Il y a **blocage** dès qu'un cercle se forme : une machine attend une deuxième, qui en attend une troisième... et la dernière attend la première. Une machine qui s'attend elle-même forme un cercle à elle toute seule.

Écris une fonction `{fn}(journal)` qui rejoue les lignes **dans l'ordre** et s'arrête au **premier** blocage. Elle renvoie alors `[heure, machines]` : l'heure de la ligne qui a refermé le cercle (le texte `HH:MM` tel qu'il est écrit), et la liste des machines du cercle, **triée par ordre alphabétique**. S'il n'y a jamais de blocage, elle renvoie la liste vide `[]`.

Précisions : les lignes sont déjà dans l'ordre chronologique, et plusieurs peuvent porter la même heure. Les noms de machines sont en minuscules, avec éventuellement des chiffres et des tirets, sans espace. Une machine qui attend un cercle sans en faire partie n'est pas dans la réponse.

Exemple : avec `["08:00 four ATTEND tapis", "08:05 tapis ATTEND grue", "08:07 four REPREND", "08:10 grue ATTEND four", "08:12 four ATTEND tapis"]`, à 08:10 la grue attend le four, mais le four est reparti : pas de cercle. À 08:12, le four attend le tapis, qui attend la grue, qui attend le four : la réponse est `["08:12", ["four", "grue", "tapis"]]`.
""",
    hint="À chaque instant, l'état du Pôle tient dans un seul dictionnaire : qui attend qui. Une ligne `REPREND` ne peut jamais créer de cercle. Une ligne `ATTEND`, si : et dans ce cas, le cercle passe forcément par la machine qui vient de se mettre à attendre. Pars d'elle, et suis la file.",
    js="""function premierBlocage(journal) {
  const attend = new Map(); // machine -> la machine qu'elle attend
  for (const ligne of journal) {
    const [heure, machine, action, autre] = ligne.split(" ");
    if (action === "REPREND") {
      attend.delete(machine);
      continue;
    }
    attend.set(machine, autre);
    // Un nouveau cercle passe forcément par `machine` : on suit la file en partant d'elle.
    const file = [machine];
    let suivante = autre;
    while (suivante !== machine && attend.has(suivante) && !file.includes(suivante)) {
      file.push(suivante);
      suivante = attend.get(suivante);
    }
    if (suivante === machine) return [heure, file.sort()];
  }
  return [];
}
""",
    py="""def premier_blocage(journal):
    attend = {}  # machine -> la machine qu'elle attend
    for ligne in journal:
        champs = ligne.split(" ")
        heure, machine, action = champs[0], champs[1], champs[2]
        if action == "REPREND":
            attend.pop(machine, None)
            continue
        attend[machine] = champs[3]
        # Un nouveau cercle passe forcément par `machine` : on suit la file en partant d'elle.
        file = [machine]
        suivante = champs[3]
        while suivante != machine and suivante in attend and suivante not in file:
            file.append(suivante)
            suivante = attend[suivante]
        if suivante == machine:
            return [heure, sorted(file)]
    return []
""",
    tests=t23, hidden=h23,
    examples=[(t23[0], ["08:12", ["four", "grue", "tapis"]]), (t23[1], []), (t23[2], ["10:30", ["cristal"]]), (t23[3], ["11:00", ["a", "b"]])],
    brute=lambda a: brute23(*a), brute_on=t23 + h23)

# ------------------------------------------------------------------ J24
def brute24(routes, a_livrer, places):
    INF = float("inf")
    noms = {"atelier"} | set(a_livrer)
    for x, y, _ in routes: noms |= {x, y}
    d = {x: {y: (0 if x == y else INF) for y in noms} for x in noms}
    for x, y, w in routes:
        d[x][y] = min(d[x][y], w); d[y][x] = min(d[y][x], w)
    for k in noms:
        for i in noms:
            for j in noms:
                if d[i][k] + d[k][j] < d[i][j]: d[i][j] = d[i][k] + d[k][j]
    if any(d["atelier"][v] == INF for v in a_livrer): return -1
    best = INF
    for perm in itertools.permutations(a_livrer):
        # meilleure découpe de cette permutation en voyages d'au plus `places` villages
        n = len(perm); cout = [INF] * (n + 1); cout[0] = 0
        for i in range(n):
            for j in range(i + 1, min(n, i + places) + 1):
                c = d["atelier"][perm[i]] + sum(d[perm[k]][perm[k + 1]] for k in range(i, j - 1)) + d[perm[j - 1]]["atelier"]
                cout[j] = min(cout[j], cout[i] + c)
        best = min(best, cout[n])
    return best
r = random.Random(24)
def gen24(nv, extra, nl, places):
    noms = ["atelier"] + ["v%d" % i for i in range(nv)]; rs = []
    for i in range(1, len(noms)): rs.append([noms[i], noms[r.randrange(0, i)], r.randint(1, 15)])
    for _ in range(extra):
        a, b = r.sample(noms, 2); rs.append([a, b, r.randint(1, 20)])
    r.shuffle(rs)
    return [rs, r.sample(noms[1:], nl), places]
R24 = [["atelier", "mairie", 3], ["atelier", "moulin", 5], ["mairie", "moulin", 1], ["mairie", "gare", 4], ["moulin", "gare", 6], ["gare", "lac", 2], ["lac", "atelier", 9]]
t24 = [[[["atelier", "a", 2], ["atelier", "b", 3], ["a", "b", 1]], ["a", "b"], 2], [[["atelier", "a", 2], ["atelier", "b", 3], ["a", "b", 1]], ["a", "b"], 1], [R24, ["gare", "lac", "moulin"], 2], [R24, ["gare", "lac", "moulin"], 3]]
h24 = [[R24, [], 2], [[["atelier", "a", 4]], ["a", "ile"], 3], [[["atelier", "a", 4], ["ile", "phare", 1]], ["phare"], 1], [[["atelier", "a", 7], ["atelier", "a", 2], ["a", "atelier", 5]], ["a"], 4], [R24, ["mairie", "moulin", "gare", "lac"], 1],
       gen24(5, 3, 4, 2), gen24(7, 5, 6, 3), gen24(8, 6, 7, 2), gen24(9, 8, 7, 4), gen24(8, 4, 8, 3)]
big24 = gen24(12, 10, 10, 3)
add(day=24, title="La tournée en plusieurs voyages", concept="Plus courts chemins et sous-ensembles",
    fn=("tourneeParVoyages", "tournee_par_voyages"), params=("routes, aLivrer, places", "routes, a_livrer, places"), comment="Renvoie la distance totale minimale, ou -1",
    statement="""Dernière porte, dernier défi, et le traîneau d'il y a cent ans a un défaut : sa hotte est minuscule. Il ne peut emporter que `places` cadeaux à la fois, et chaque village à livrer en attend **un**. Il faudra donc faire **plusieurs voyages** : partir de l'`"atelier"`, livrer quelques villages, revenir recharger à l'atelier, repartir... jusqu'à ce que tout le monde soit servi.

Écris une fonction `{fn}(routes, aLivrer, places)` qui renvoie la **distance totale minimale** parcourue, tous voyages confondus, retour final à l'atelier compris.

- `routes` est une liste de `[village1, village2, distance]` (distances entières `>= 1`, noms en minuscules). Chaque route se parcourt dans les deux sens. Si plusieurs routes relient les deux mêmes villages, on prend la plus courte.
- `aLivrer` est la liste des villages à livrer (sans doublon, sans l'atelier).
- `places` est un entier `>= 1` : le nombre maximal de villages livrés pendant un même voyage.
- Chaque voyage commence et finit à l'atelier. Le traîneau peut traverser un village sans le livrer, repasser plusieurs fois au même endroit, et même repasser par l'atelier sans recharger.
- C'est à toi de choisir comment répartir les villages entre les voyages, et dans quel ordre les livrer.
- Si `aLivrer` est vide, la réponse est `0`. Si un village à livrer est inaccessible depuis l'atelier, renvoie `-1`.

Il y a au plus `10` villages à livrer. C'est la dernière porte : graphes, sous-ensembles, mémoïsation, tout ce que tu as appris peut servir. Découpe le problème en étages, et fais confiance à la méthode.

Exemple : avec les routes `[["atelier", "a", 2], ["atelier", "b", 3], ["a", "b", 1]]` et les villages `a` et `b` à livrer, une hotte de `2` places permet un seul voyage, atelier, `a`, `b`, atelier : `2 + 1 + 3 = 6`. Avec une seule place, il faut deux allers-retours : `4 + 6 = 10`.
""",
    hint="Trois étages. D'abord, la plus courte distance entre toutes les paires de lieux qui comptent. Ensuite, pour chaque **groupe** de villages assez petit pour tenir dans la hotte, le coût du meilleur voyage qui les livre tous. Enfin, la meilleure façon de découper l'ensemble des villages en groupes. Un groupe de villages se note très bien avec un seul entier, un bit par village.",
    js="""function tourneeParVoyages(routes, aLivrer, places) {
  const n = aLivrer.length;
  if (n === 0) return 0;

  // 1. Plus courtes distances entre tous les lieux (Floyd-Warshall).
  const numero = new Map();
  const noter = (nom) => {
    if (!numero.has(nom)) numero.set(nom, numero.size);
    return numero.get(nom);
  };
  noter("atelier");
  aLivrer.forEach(noter);
  routes.forEach(([a, b]) => {
    noter(a);
    noter(b);
  });
  const taille = numero.size;
  const d = Array.from({ length: taille }, (_, i) => Array.from({ length: taille }, (_, j) => (i === j ? 0 : Infinity)));
  for (const [a, b, distance] of routes) {
    const i = numero.get(a);
    const j = numero.get(b);
    if (distance < d[i][j]) {
      d[i][j] = distance;
      d[j][i] = distance;
    }
  }
  for (let k = 0; k < taille; k++) {
    for (let i = 0; i < taille; i++) {
      for (let j = 0; j < taille; j++) {
        if (d[i][k] + d[k][j] < d[i][j]) d[i][j] = d[i][k] + d[k][j];
      }
    }
  }
  // Les villages à livrer portent les numéros 1 à n, l'atelier le numéro 0.
  for (let v = 1; v <= n; v++) if (d[0][v] === Infinity) return -1;

  // 2. voyage[groupe] : coût du meilleur voyage qui livre exactement ce groupe (un bit par village).
  const total = 1 << n;
  const combien = (groupe) => {
    let bits = 0;
    for (let g = groupe; g > 0; g >>= 1) bits += g & 1;
    return bits;
  };
  // chemin[groupe][dernier] : plus courte route atelier -> villages du groupe, en finissant par `dernier`.
  const chemin = Array.from({ length: total }, () => new Array(n).fill(Infinity));
  const voyage = new Array(total).fill(Infinity);
  for (let v = 0; v < n; v++) chemin[1 << v][v] = d[0][v + 1];
  for (let groupe = 1; groupe < total; groupe++) {
    if (combien(groupe) > places) continue;
    for (let dernier = 0; dernier < n; dernier++) {
      const ici = chemin[groupe][dernier];
      if (ici === Infinity) continue;
      voyage[groupe] = Math.min(voyage[groupe], ici + d[dernier + 1][0]);
      for (let suivant = 0; suivant < n; suivant++) {
        if (groupe & (1 << suivant)) continue;
        const plusGrand = groupe | (1 << suivant);
        const cout = ici + d[dernier + 1][suivant + 1];
        if (cout < chemin[plusGrand][suivant]) chemin[plusGrand][suivant] = cout;
      }
    }
  }

  // 3. meilleur[groupe] : coût minimal pour livrer tout le groupe, en un ou plusieurs voyages.
  const meilleur = new Array(total).fill(Infinity);
  meilleur[0] = 0;
  for (let groupe = 1; groupe < total; groupe++) {
    // Le premier voyage contient le village de plus petit numéro : on évite de compter deux fois le même découpage.
    const premier = groupe & -groupe;
    for (let part = groupe; part > 0; part = (part - 1) & groupe) {
      if (!(part & premier) || voyage[part] === Infinity) continue;
      const cout = voyage[part] + meilleur[groupe ^ part];
      if (cout < meilleur[groupe]) meilleur[groupe] = cout;
    }
  }
  return meilleur[total - 1];
}
""",
    py="""def tournee_par_voyages(routes, a_livrer, places):
    n = len(a_livrer)
    if n == 0:
        return 0
    infini = float("inf")

    # 1. Plus courtes distances entre tous les lieux (Floyd-Warshall).
    numero = {}

    def noter(nom):
        if nom not in numero:
            numero[nom] = len(numero)
        return numero[nom]

    noter("atelier")
    for village in a_livrer:
        noter(village)
    for a, b, _ in routes:
        noter(a)
        noter(b)
    taille = len(numero)
    d = [[0 if i == j else infini for j in range(taille)] for i in range(taille)]
    for a, b, distance in routes:
        i, j = numero[a], numero[b]
        if distance < d[i][j]:
            d[i][j] = distance
            d[j][i] = distance
    for k in range(taille):
        for i in range(taille):
            for j in range(taille):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]
    # Les villages à livrer portent les numéros 1 à n, l'atelier le numéro 0.
    if any(d[0][v] == infini for v in range(1, n + 1)):
        return -1

    # 2. voyage[groupe] : coût du meilleur voyage qui livre exactement ce groupe (un bit par village).
    total = 1 << n
    # chemin[groupe][dernier] : plus courte route atelier -> villages du groupe, en finissant par `dernier`.
    chemin = [[infini] * n for _ in range(total)]
    voyage = [infini] * total
    for v in range(n):
        chemin[1 << v][v] = d[0][v + 1]
    for groupe in range(1, total):
        if bin(groupe).count("1") > places:
            continue
        for dernier in range(n):
            ici = chemin[groupe][dernier]
            if ici == infini:
                continue
            voyage[groupe] = min(voyage[groupe], ici + d[dernier + 1][0])
            for suivant in range(n):
                if groupe & (1 << suivant):
                    continue
                plus_grand = groupe | (1 << suivant)
                cout = ici + d[dernier + 1][suivant + 1]
                if cout < chemin[plus_grand][suivant]:
                    chemin[plus_grand][suivant] = cout

    # 3. meilleur[groupe] : coût minimal pour livrer tout le groupe, en un ou plusieurs voyages.
    meilleur = [infini] * total
    meilleur[0] = 0
    for groupe in range(1, total):
        # Le premier voyage contient le village de plus petit numéro : on évite de compter deux fois le même découpage.
        premier = groupe & -groupe
        part = groupe
        while part > 0:
            if part & premier and voyage[part] != infini:
                cout = voyage[part] + meilleur[groupe ^ part]
                if cout < meilleur[groupe]:
                    meilleur[groupe] = cout
            part = (part - 1) & groupe
    return meilleur[total - 1]
""",
    tests=t24, hidden=h24 + [big24],
    examples=[(t24[0], 6), (t24[1], 10), ([R24, [], 2], 0), ([[["atelier", "a", 4]], ["a", "ile"], 3], -1)],
    brute=lambda a: brute24(*a), brute_on=t24 + h24)
