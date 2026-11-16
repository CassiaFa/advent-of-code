# Exercices « expert », jours 1 à 12. Source des exercices dNN-expert de content/exercises/.
# Chaque entrée : énoncé, solutions JS et Python, arguments des tests, exemples calculés à la main
# et, quand c'est possible, une méthode naïve (`brute`) qui sert de contre-vérification.
# Voir verifier.py pour le mode d'emploi.
import random
EX = []

def add(**k):
    EX.append(k)

# ------------------------------------------------------------------ J1
def brute1(grelots):
    if not grelots: return 0
    for t in range(0, 200000):
        if all(t % p == d for p, d in grelots): return t
    return -1
r = random.Random(1)
t1 = [[[[3, 2], [5, 3]]], [[[4, 1], [6, 2]]], [[[4, 3], [6, 5]]], [[[7, 0]]]]
h1 = [[[]], [[[1, 0], [1, 0]]], [[[6, 4], [10, 8], [15, 13]]], [[[2, 1], [4, 0]]], [[[9, 4], [12, 7], [5, 0]]], [[[12, 5], [18, 11], [8, 1]]], [[[17, 3], [19, 18], [23, 22], [4, 3]]], [[[10, 3], [10, 4]]], [[[97, 96], [89, 0], [64, 63]]]]
add(day=1, title="Les grelots synchronisés", concept="Congruences et PPCM",
    fn=("premierAccord", "premier_accord"), params=("grelots", "grelots"), comment="Renvoie la première minute où tous les grelots sonnent ensemble, ou -1",
    statement="""Pour relancer le Grand Registre, il faut appuyer sur le bouton à l'instant précis où **tous les grelots de l'atelier sonnent en même temps**. Chaque grelot est une paire `[periode, decalage]` : il sonne à la minute `decalage`, puis toutes les `periode` minutes (donc aux minutes `decalage`, `decalage + periode`, `decalage + 2 * periode`, et ainsi de suite).

Écris une fonction `{fn}(grelots)` qui renvoie la **première minute** (un entier `>= 0`) où tous les grelots sonnent ensemble, ou `-1` si cela n'arrive jamais.

Précisions :
- `periode` est un entier `>= 1` et `0 <= decalage < periode`.
- Sans aucun grelot, la réponse est `0`.
- Il peut y avoir beaucoup de grelots, et la réponse peut dépasser le milliard : essayer les minutes une par une ne suffira pas. Quand elle existe, la réponse reste inférieure à `1 000 000 000 000`.

Exemple : avec `[[3, 2], [5, 3]]`, le premier grelot sonne aux minutes 2, 5, 8, 11... et le second aux minutes 3, 8, 13... : la réponse est `8`. Avec `[[4, 1], [6, 2]]`, le premier ne sonne qu'aux minutes impaires et le second qu'aux minutes paires : la réponse est `-1`.
""",
    hint="Traite les grelots un par un. Si tu connais une minute qui convient aux premiers grelots, les suivantes reviennent à intervalle régulier : lequel ? Pour savoir si un nouveau grelot est compatible, regarde ce que ton intervalle et sa période ont en commun.",
    js="""function premierAccord(grelots) {
  const pgcd = (a, b) => (b === 0 ? a : pgcd(b, a % b));
  let minute = 0; // première minute qui convient aux grelots déjà vus
  let pas = 1; // ensuite, ça revient toutes les `pas` minutes
  for (const [periode, decalage] of grelots) {
    const commun = pgcd(pas, periode);
    const ecart = (((decalage - minute) % periode) + periode) % periode;
    if (ecart % commun !== 0) return -1;
    while (minute % periode !== decalage) minute += pas;
    pas = (pas / commun) * periode;
  }
  return minute;
}
""",
    py="""def premier_accord(grelots):
    def pgcd(a, b):
        while b:
            a, b = b, a % b
        return a

    minute = 0  # première minute qui convient aux grelots déjà vus
    pas = 1  # ensuite, ça revient toutes les `pas` minutes
    for periode, decalage in grelots:
        commun = pgcd(pas, periode)
        if (decalage - minute) % commun != 0:
            return -1
        while minute % periode != decalage:
            minute += pas
        pas = pas // commun * periode
    return minute
""",
    tests=t1, hidden=h1 + [[[[9973, 9972], [9967, 1], [10, 9]]], [[[1000, 999], [999, 998], [997, 996]]]],
    examples=[([[[3, 2], [5, 3]]], 8), ([[[4, 1], [6, 2]]], -1), ([[[4, 3], [6, 5]]], 11), ([[]], 0)],
    brute=lambda a: brute1(*a), brute_on=t1 + h1)

# ------------------------------------------------------------------ J2
def brute2(n, regles):
    v = ["sage"] * (n + 1)
    for a, b, x in regles:
        for i in range(a, b + 1): v[i] = x
    out = []
    for i in range(1, n + 1):
        if out and out[-1][2] == v[i]: out[-1][1] = i
        else: out.append([i, i, v[i]])
    return out
r = random.Random(2)
def gen2(n, k):
    rs = []
    for _ in range(k):
        a = r.randint(1, n); b = r.randint(a, min(n, a + r.randint(0, max(1, n // 3))))
        rs.append([a, b, r.choice(["sage", "charbon", "cadeau", "orange"])])
    return [n, rs]
t2 = [[10, [[3, 7, "charbon"], [5, 5, "sage"], [6, 9, "cadeau"]]], [5, [[1, 5, "charbon"], [2, 4, "charbon"]]], [4, []], [6, [[1, 3, "cadeau"], [4, 6, "cadeau"]]]]
h2 = [[1, [[1, 1, "charbon"]]], [8, [[2, 3, "charbon"], [2, 3, "sage"]]], gen2(30, 6), gen2(40, 10), gen2(60, 14), gen2(12, 12)]
add(day=2, title="Les règles qui se chevauchent", concept="Règles en cascade sur de grands intervalles",
    fn=("resumerRegles", "resumer_regles"), params=("n, regles", "n, regles"), comment="Renvoie les tranches [debut, fin, verdict] qui couvrent les enfants 1 à n",
    statement="""Le Registre connaît `n` enfants, numérotés de `1` à `n`. Au départ, ils sont tous notés `"sage"`. Puis les lutins dictent leurs règles, **dans l'ordre** : chaque règle `[debut, fin, verdict]` donne le verdict `verdict` à tous les enfants numérotés de `debut` à `fin` (bornes incluses). Une règle dictée plus tard **écrase** les précédentes là où elles se chevauchent.

Écris une fonction `{fn}(n, regles)` qui renvoie le résultat final sous forme de **tranches** : une liste de `[debut, fin, verdict]`, triée par `debut` croissant, qui couvre tous les enfants de `1` à `n` sans trou ni chevauchement. Deux tranches voisines n'ont **jamais le même verdict** : si c'est le cas, elles doivent être fusionnées en une seule.

Précisions :
- `n` est un entier `>= 1`, et pour chaque règle `1 <= debut <= fin <= n`. Un verdict est un texte en minuscules.
- `n` peut atteindre **un milliard** : pas question de garder une case par enfant. Le nombre de règles, lui, reste raisonnable (quelques centaines au plus).
- Sans aucune règle, la réponse est `[[1, n, "sage"]]`.

Exemple : avec `n = 10` et les règles `[[3, 7, "charbon"], [5, 5, "sage"], [6, 9, "cadeau"]]`, la réponse est `[[1, 2, "sage"], [3, 4, "charbon"], [5, 5, "sage"], [6, 9, "cadeau"], [10, 10, "sage"]]`.
""",
    hint="Le verdict ne peut changer qu'à quelques endroits précis : lesquels ? Entre deux de ces endroits, tous les enfants ont le même verdict, et il suffit de regarder un seul d'entre eux. N'oublie pas de recoller les tranches voisines qui se ressemblent.",
    js="""function resumerRegles(n, regles) {
  // Le verdict ne peut changer qu'au début d'une règle, ou juste après sa fin.
  const bornes = new Set([1, n + 1]);
  for (const [debut, fin] of regles) {
    bornes.add(debut);
    bornes.add(fin + 1);
  }
  const coupes = [...bornes].sort((a, b) => a - b);
  const tranches = [];
  for (let i = 0; i + 1 < coupes.length; i++) {
    const debut = coupes[i];
    const fin = coupes[i + 1] - 1;
    let verdict = "sage";
    for (let k = regles.length - 1; k >= 0; k--) {
      if (regles[k][0] <= debut && debut <= regles[k][1]) {
        verdict = regles[k][2];
        break;
      }
    }
    const derniere = tranches[tranches.length - 1];
    if (derniere && derniere[2] === verdict) derniere[1] = fin;
    else tranches.push([debut, fin, verdict]);
  }
  return tranches;
}
""",
    py="""def resumer_regles(n, regles):
    # Le verdict ne peut changer qu'au début d'une règle, ou juste après sa fin.
    bornes = {1, n + 1}
    for debut, fin, _ in regles:
        bornes.add(debut)
        bornes.add(fin + 1)
    coupes = sorted(bornes)
    tranches = []
    for i in range(len(coupes) - 1):
        debut = coupes[i]
        fin = coupes[i + 1] - 1
        verdict = "sage"
        for regle in reversed(regles):
            if regle[0] <= debut <= regle[1]:
                verdict = regle[2]
                break
        if tranches and tranches[-1][2] == verdict:
            tranches[-1][1] = fin
        else:
            tranches.append([debut, fin, verdict])
    return tranches
""",
    tests=t2, hidden=h2 + [[1000000000, [[1, 1000000000, "charbon"], [500000000, 500000000, "cadeau"], [999999999, 1000000000, "sage"]]], [1000000000, [[2, 999999999, "orange"], [400000000, 600000000, "sage"], [450000000, 550000000, "orange"]]]],
    examples=[([10, [[3, 7, "charbon"], [5, 5, "sage"], [6, 9, "cadeau"]]], [[1, 2, "sage"], [3, 4, "charbon"], [5, 5, "sage"], [6, 9, "cadeau"], [10, 10, "sage"]]), ([5, [[1, 5, "charbon"], [2, 4, "charbon"]]], [[1, 5, "charbon"]]), ([4, []], [[1, 4, "sage"]])],
    brute=lambda a: brute2(*a), brute_on=t2 + h2)

# ------------------------------------------------------------------ J3
def brute3(p, e):
    best = [0, 0]
    for i in range(len(p)):
        for j in range(i, len(p)):
            if max(p[i:j + 1]) - min(p[i:j + 1]) <= e and j - i + 1 > best[1]: best = [i, j - i + 1]
    return best
r = random.Random(3)
t3 = [[[4, 6, 5, 9, 8, 7, 3], 2], [[1, 1, 1], 0], [[5, 1], 3], [[2, 9, 4, 5, 6, 4, 10], 2]]
h3 = [[[], 5], [[7], 0], [[1, 2, 3, 4, 5, 6], 100], [[5, 4, 3, 2, 1], 1]] + [[[r.randint(0, 20) for _ in range(n)], e] for n, e in [(25, 3), (40, 5), (60, 0), (80, 8), (120, 10)]]
add(day=3, title="Le tapis qui tangue", concept="Fenêtre glissante avec minimum et maximum",
    fn=("serieStable", "serie_stable"), params=("poids, ecart", "poids, ecart"), comment="Renvoie [debut, longueur] de la plus longue série stable",
    statement="""Le convoyeur se dérègle dès que des paquets trop différents se suivent. Pixel cherche la plus longue série de paquets **consécutifs** qu'on peut laisser passer d'une traite : une série est **stable** si l'écart entre son paquet le plus lourd et son paquet le plus léger ne dépasse pas `ecart`.

Écris une fonction `{fn}(poids, ecart)` qui renvoie `[debut, longueur]` : la position du premier paquet de la plus longue série stable (les positions commencent à `0`), et son nombre de paquets.

Précisions :
- `poids` est une liste d'entiers, `ecart` un entier `>= 0`. Un écart exactement égal à `ecart` est accepté.
- Si plusieurs séries ont la longueur maximale, renvoie celle qui **commence le plus tôt**.
- Un paquet seul forme toujours une série stable. Si la liste est vide, renvoie `[0, 0]`.
- Le convoyeur voit passer des centaines de milliers de paquets : vise une solution qui ne reparcourt pas toute la série à chaque nouveau paquet.

Exemple : avec `[4, 6, 5, 9, 8, 7, 3]` et un écart de `2`, les séries `4, 6, 5` et `9, 8, 7` sont stables et de longueur 3 : la première gagne, donc `[0, 3]`.
""",
    hint="Fais avancer deux positions, le début et la fin de la série, sans jamais reculer. La vraie difficulté : connaître à tout moment le plus lourd et le plus léger de la série en cours. Quels paquets n'ont plus aucune chance de devenir le plus lourd une fois qu'un paquet plus lourd est arrivé derrière eux ?",
    js="""function serieStable(poids, ecart) {
  // Positions des candidats au maximum (poids décroissants) et au minimum (poids croissants).
  const hauts = [];
  const bas = [];
  let teteHauts = 0;
  let teteBas = 0;
  let debut = 0;
  let meilleur = [0, 0];
  for (let fin = 0; fin < poids.length; fin++) {
    while (hauts.length > teteHauts && poids[hauts[hauts.length - 1]] <= poids[fin]) hauts.pop();
    hauts.push(fin);
    while (bas.length > teteBas && poids[bas[bas.length - 1]] >= poids[fin]) bas.pop();
    bas.push(fin);
    while (poids[hauts[teteHauts]] - poids[bas[teteBas]] > ecart) {
      debut++;
      if (hauts[teteHauts] < debut) teteHauts++;
      if (bas[teteBas] < debut) teteBas++;
    }
    if (fin - debut + 1 > meilleur[1]) meilleur = [debut, fin - debut + 1];
  }
  return meilleur;
}
""",
    py="""from collections import deque


def serie_stable(poids, ecart):
    # Positions des candidats au maximum (poids décroissants) et au minimum (poids croissants).
    hauts = deque()
    bas = deque()
    debut = 0
    meilleur = [0, 0]
    for fin, p in enumerate(poids):
        while hauts and poids[hauts[-1]] <= p:
            hauts.pop()
        hauts.append(fin)
        while bas and poids[bas[-1]] >= p:
            bas.pop()
        bas.append(fin)
        while poids[hauts[0]] - poids[bas[0]] > ecart:
            debut += 1
            if hauts[0] < debut:
                hauts.popleft()
            if bas[0] < debut:
                bas.popleft()
        if fin - debut + 1 > meilleur[1]:
            meilleur = [debut, fin - debut + 1]
    return meilleur
""",
    tests=t3, hidden=h3,
    examples=[([[4, 6, 5, 9, 8, 7, 3], 2], [0, 3]), ([[1, 1, 1], 0], [0, 3]), ([[5, 1], 3], [0, 1]), ([[], 5], [0, 0])],
    brute=lambda a: brute3(*a), brute_on=t3 + h3)

# ------------------------------------------------------------------ J4
from functools import lru_cache
def brute4(s):
    @lru_cache(None)
    def f(i):
        if i == len(s): return 0
        return min(1 + f(j) for j in range(i + 1, len(s) + 1) if s[i:j] == s[i:j][::-1])
    return f(0)
r = random.Random(4)
t4 = [["kayak"], ["noelle"], ["aab"], ["givre"]]
h4 = [[""], ["a"], ["abba"], ["abcbaelle"], ["aaaaaaab"], ["banana"]] + [["".join(r.choice("ab") for _ in range(n))] for n in (30, 60)] + [["".join(r.choice("abc") for _ in range(90))], ["ressasser" * 8 + "x"]]
add(day=4, title="Le mot de passe en morceaux", concept="Découpage minimal en palindromes",
    fn=("morceauxMinimum", "morceaux_minimum"), params=("texte", "texte"), comment="Renvoie le plus petit nombre de morceaux palindromes",
    statement="""Le coffre-fort des vœux est devenu plus exigeant : il n'accepte le texte gravé dans le givre que s'il est tapé **morceau par morceau**, et chaque morceau doit être un palindrome (il se lit pareil dans les deux sens). Pixel veut appuyer sur « valider » le moins souvent possible.

Écris une fonction `{fn}(texte)` qui renvoie le **plus petit nombre de morceaux** dans lesquels on peut découper `texte`, de sorte que chaque morceau soit un palindrome. Les morceaux se suivent, sans rien sauter ni réordonner, et recouvrent tout le texte.

Précisions :
- Un caractère seul est un palindrome : une réponse existe toujours.
- Le texte ne contient que des lettres minuscules sans accent. Un texte vide demande `0` morceau.
- Le texte peut faire quelques centaines de caractères : essayer tous les découpages possibles prendrait plus que la nuit de Noël.

Exemple : `"noelle"` se découpe en `n`, `o`, `elle` : la réponse est `3`. Pour `"aab"`, c'est `2` (`aa`, `b`), et pour `"kayak"`, `1`.
""",
    hint="Deux questions se cachent ici. D'abord : quels bouts du texte sont des palindromes ? Un bout l'est si ses deux extrémités sont égales et si l'intérieur l'est aussi. Ensuite : si tu connais la meilleure réponse pour tous les débuts du texte plus courts, comment trouver celle du début suivant ?",
    js="""function morceauxMinimum(texte) {
  const n = texte.length;
  // pal[i][j] : le bout qui va de i à j (inclus) est-il un palindrome ?
  const pal = Array.from({ length: n }, () => new Array(n).fill(false));
  for (let i = n - 1; i >= 0; i--) {
    for (let j = i; j < n; j++) {
      pal[i][j] = texte[i] === texte[j] && (j - i < 2 || pal[i + 1][j - 1]);
    }
  }
  // mini[j] : nombre minimal de morceaux pour les j premiers caractères
  const mini = new Array(n + 1).fill(0);
  for (let j = 1; j <= n; j++) {
    mini[j] = j;
    for (let i = 0; i < j; i++) {
      if (pal[i][j - 1] && mini[i] + 1 < mini[j]) mini[j] = mini[i] + 1;
    }
  }
  return mini[n];
}
""",
    py="""def morceaux_minimum(texte):
    n = len(texte)
    # pal[i][j] : le bout qui va de i à j (inclus) est-il un palindrome ?
    pal = [[False] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):
        for j in range(i, n):
            pal[i][j] = texte[i] == texte[j] and (j - i < 2 or pal[i + 1][j - 1])
    # mini[j] : nombre minimal de morceaux pour les j premiers caractères
    mini = [0] * (n + 1)
    for j in range(1, n + 1):
        mini[j] = j
        for i in range(j):
            if pal[i][j - 1] and mini[i] + 1 < mini[j]:
                mini[j] = mini[i] + 1
    return mini[n]
""",
    tests=t4, hidden=h4,
    examples=[(["kayak"], 1), (["noelle"], 3), (["aab"], 2), (["givre"], 5), ([""], 0)],
    brute=lambda a: brute4(*a), brute_on=t4 + h4[:8])

# ------------------------------------------------------------------ J5
r = random.Random(5)
t5 = [[["luge", "train", "luge", "poupee", "train", "luge"], 2], [["a", "b", "c"], 2], [["sapin", "sapin", "sapin"], 1], [["a", "b", "a", "c", "b", "d", "a"], 3]]
h5 = [[[], 3], [["a", "b", "c", "d"], 1], [["a", "b", "c"], 5], [["a", "a", "b", "c", "a", "b", "c", "d", "d", "d", "e"], 2]] + [[[r.choice("abcdefg") for _ in range(n)], k] for n, k in [(30, 3), (50, 4), (70, 2), (90, 5)]]
add(day=5, title="L'étagère qui oublie", concept="Dictionnaires : compteurs et dernier passage",
    fn=("objetsOublies", "objets_oublies"), params=("demandes, places", "demandes, places"), comment="Renvoie la liste des objets retirés de l'étagère, dans l'ordre",
    statement="""Pour retrouver vite les jouets les plus demandés, Pixel installe une **petite étagère** à l'entrée de l'entrepôt. Elle n'a que `places` places, et elle est vide au départ. Les lutins viennent demander des jouets, un par un, dans l'ordre de la liste `demandes`.

À chaque demande :
- si le jouet est **déjà sur l'étagère**, son compteur de demandes augmente de 1 ;
- sinon, on va le chercher au fond de l'entrepôt et on le pose sur l'étagère, avec un compteur à `1`. Si l'étagère est pleine, il faut **d'abord** en retirer un jouet : celui dont le **compteur est le plus petit**. En cas d'égalité, on retire celui qui a été **demandé le moins récemment** parmi les ex æquo.

Un jouet retiré est oublié : s'il revient plus tard sur l'étagère, son compteur repart de `1`.

Écris une fonction `{fn}(demandes, places)` qui renvoie la **liste des jouets retirés** de l'étagère, dans l'ordre où ils l'ont été (le même jouet peut y figurer plusieurs fois).

Précisions : `places` est un entier `>= 1`. Les noms sont des textes en minuscules. Sans demande, ou si l'étagère n'est jamais pleine, renvoie la liste vide.

Exemple : avec `["luge", "train", "luge", "poupee", "train", "luge"]` et `2` places, la poupée chasse le train (demandé une fois, contre deux pour la luge), puis le train revient et chasse la poupée : `["train", "poupee"]`. Avec `["a", "b", "c"]` et `2` places, `a` et `b` sont à égalité : `a`, demandé le moins récemment, s'en va : `["a"]`.
""",
    hint="Pour chaque jouet présent sur l'étagère, tu as besoin de deux informations : combien de fois il a été demandé depuis son arrivée, et à quel moment il l'a été pour la dernière fois. Un numéro de demande qui augmente à chaque passage fait une très bonne horloge.",
    js="""function objetsOublies(demandes, places) {
  const etagere = new Map(); // jouet -> { compteur, dernier }
  const retires = [];
  demandes.forEach((jouet, instant) => {
    const fiche = etagere.get(jouet);
    if (fiche) {
      fiche.compteur++;
      fiche.dernier = instant;
      return;
    }
    if (etagere.size === places) {
      let victime = null;
      for (const [nom, f] of etagere) {
        const v = victime === null ? null : etagere.get(victime);
        if (v === null || f.compteur < v.compteur || (f.compteur === v.compteur && f.dernier < v.dernier)) victime = nom;
      }
      etagere.delete(victime);
      retires.push(victime);
    }
    etagere.set(jouet, { compteur: 1, dernier: instant });
  });
  return retires;
}
""",
    py="""def objets_oublies(demandes, places):
    etagere = {}  # jouet -> [compteur, dernier passage]
    retires = []
    for instant, jouet in enumerate(demandes):
        if jouet in etagere:
            etagere[jouet][0] += 1
            etagere[jouet][1] = instant
            continue
        if len(etagere) == places:
            # Le plus petit compteur, puis le passage le plus ancien.
            victime = min(etagere, key=lambda nom: (etagere[nom][0], etagere[nom][1]))
            del etagere[victime]
            retires.append(victime)
        etagere[jouet] = [1, instant]
    return retires
""",
    tests=t5, hidden=h5,
    examples=[([["luge", "train", "luge", "poupee", "train", "luge"], 2], ["train", "poupee"]), ([["a", "b", "c"], 2], ["a"]), ([["sapin", "sapin", "sapin"], 1], [])])

# ------------------------------------------------------------------ J6
def brute6(h):
    return sum(max(0, min(max(h[:i + 1]), max(h[i:])) - h[i]) for i in range(len(h)))
r = random.Random(6)
t6 = [[[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]], [[3, 0, 2]], [[1, 2, 3]], [[4, 2, 0, 3, 2, 5]]]
h6 = [[[]], [[5]], [[2, 2, 2]], [[5, 4, 3, 2, 1]], [[9, 0, 0, 0, 9]]] + [[[r.randint(0, 12) for _ in range(n)]] for n in (20, 45, 80, 150)]
add(day=6, title="La neige entre les piquets", concept="Bornes à gauche et à droite",
    fn=("neigeRetenue", "neige_retenue"), params=("hauteurs", "hauteurs"), comment="Renvoie la quantité totale de neige retenue",
    statement="""La piste des rennes est bordée de piquets collés les uns aux autres, tous de la même largeur (1) mais de hauteurs différentes. Cette nuit, il a neigé à gros flocons, puis le vent a balayé tout ce qui n'était pas retenu : il ne reste de la neige que **dans les creux**, là où elle est bloquée par un piquet plus haut **à gauche** et un autre **à droite**.

Écris une fonction `{fn}(hauteurs)` qui renvoie la **quantité totale de neige retenue**. Au-dessus de chaque piquet, la neige monte jusqu'à la hauteur du plus bas des deux « murs » qui l'entourent (le plus haut piquet à sa gauche, le plus haut à sa droite), jamais plus haut. Un piquet qui dépasse déjà ce niveau ne retient rien.

Précisions :
- `hauteurs` est une liste d'entiers `>= 0`. La neige s'échappe par les deux bords de la piste.
- Une liste vide, ou sans aucun creux, donne `0`.
- La piste peut compter des centaines de milliers de piquets : évite de rechercher les deux murs en repartant de zéro pour chaque piquet.

Exemple : `[3, 0, 2]` retient `2` (le creux du milieu se remplit jusqu'à la hauteur 2). `[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]` retient `6`, et `[1, 2, 3]` ne retient rien.
""",
    hint="Pour un piquet donné, le niveau de la neige dépend de deux bornes : le plus haut piquet rencontré à gauche, et le plus haut à droite. Chacune se calcule en un seul passage sur la piste. Et si tu avançais par les deux bouts à la fois ?",
    js="""function neigeRetenue(hauteurs) {
  let gauche = 0;
  let droite = hauteurs.length - 1;
  let murGauche = 0;
  let murDroit = 0;
  let total = 0;
  // On avance toujours du côté du mur le plus bas : c'est lui qui limite le niveau.
  while (gauche <= droite) {
    if (murGauche <= murDroit) {
      murGauche = Math.max(murGauche, hauteurs[gauche]);
      total += murGauche - hauteurs[gauche];
      gauche++;
    } else {
      murDroit = Math.max(murDroit, hauteurs[droite]);
      total += murDroit - hauteurs[droite];
      droite--;
    }
  }
  return total;
}
""",
    py="""def neige_retenue(hauteurs):
    gauche = 0
    droite = len(hauteurs) - 1
    mur_gauche = 0
    mur_droit = 0
    total = 0
    # On avance toujours du côté du mur le plus bas : c'est lui qui limite le niveau.
    while gauche <= droite:
        if mur_gauche <= mur_droit:
            mur_gauche = max(mur_gauche, hauteurs[gauche])
            total += mur_gauche - hauteurs[gauche]
            gauche += 1
        else:
            mur_droit = max(mur_droit, hauteurs[droite])
            total += mur_droit - hauteurs[droite]
            droite -= 1
    return total
""",
    tests=t6, hidden=h6,
    examples=[([[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]], 6), ([[3, 0, 2]], 2), ([[1, 2, 3]], 0)],
    brute=lambda a: brute6(*a), brute_on=t6 + h6)

# ------------------------------------------------------------------ J7
def brute7(e):
    return sum(1 for i in range(len(e)) for j in range(i + 1, len(e)) if e[i] > e[j])
r = random.Random(7)
t7 = [[[3, 1, 2]], [[1, 2, 3]], [[2, 2, 1]], [[4, 3, 2, 1]]]
h7 = [[[]], [[7]], [[5, 5, 5, 5]], [[-3, 4, -8, 0, 4, -3]]] + [[[r.randint(0, 50) for _ in range(n)]] for n in (30, 60, 120)] + [[list(range(150, 0, -1))]]
add(day=7, title="Le désordre de la carte", concept="Compter les inversions (tri par fusion)",
    fn=("echangesMinimum", "echanges_minimum"), params=("eclats", "eclats"), comment="Renvoie le nombre minimal d'échanges entre voisines",
    statement="""Mère Noëlle veut ranger les étoiles de la carte par **éclat croissant**. Mais la vieille carte est fragile : le seul geste permis, c'est d'**échanger deux étoiles voisines**. Avant de s'y mettre, elle veut savoir combien de gestes il faudra, au minimum.

Écris une fonction `{fn}(eclats)` qui renvoie le **plus petit nombre d'échanges entre voisines** nécessaire pour trier la liste par ordre croissant.

Précisions :
- `eclats` est une liste d'entiers (positifs, nuls ou négatifs). Deux étoiles de même éclat n'ont jamais besoin d'être échangées entre elles.
- Une liste vide, ou déjà triée, demande `0` échange.
- La carte compte des centaines de milliers d'étoiles : comparer chaque étoile à toutes les autres serait bien trop long. Il existe une méthode qui compte **pendant** qu'elle trie.

Exemple : `[3, 1, 2]` demande `2` échanges (le `3` doit passer derrière le `1`, puis derrière le `2`). `[4, 3, 2, 1]` en demande `6`, et `[2, 2, 1]` en demande `2`.
""",
    hint="Le nombre d'échanges est égal au nombre de paires d'étoiles « à l'envers » : la plus brillante placée avant la moins brillante. Coupe la liste en deux moitiés, compte dans chacune, puis demande-toi ce que tu apprends au moment de fusionner deux moitiés déjà triées.",
    js="""function echangesMinimum(eclats) {
  // Trie la liste et renvoie [liste triée, nombre de paires à l'envers].
  function trier(liste) {
    if (liste.length < 2) return [liste, 0];
    const milieu = liste.length >> 1;
    const [gauche, a] = trier(liste.slice(0, milieu));
    const [droite, b] = trier(liste.slice(milieu));
    const fusion = [];
    let total = a + b;
    let i = 0;
    let j = 0;
    while (i < gauche.length || j < droite.length) {
      if (j >= droite.length || (i < gauche.length && gauche[i] <= droite[j])) {
        fusion.push(gauche[i++]);
      } else {
        // droite[j] passe devant tout ce qui reste à gauche : autant de paires à l'envers.
        total += gauche.length - i;
        fusion.push(droite[j++]);
      }
    }
    return [fusion, total];
  }
  return trier(eclats)[1];
}
""",
    py="""def echanges_minimum(eclats):
    # Trie la liste et renvoie (liste triée, nombre de paires à l'envers).
    def trier(liste):
        if len(liste) < 2:
            return liste, 0
        milieu = len(liste) // 2
        gauche, a = trier(liste[:milieu])
        droite, b = trier(liste[milieu:])
        fusion = []
        total = a + b
        i = j = 0
        while i < len(gauche) or j < len(droite):
            if j >= len(droite) or (i < len(gauche) and gauche[i] <= droite[j]):
                fusion.append(gauche[i])
                i += 1
            else:
                # droite[j] passe devant tout ce qui reste à gauche : autant de paires à l'envers.
                total += len(gauche) - i
                fusion.append(droite[j])
                j += 1
        return fusion, total

    return trier(eclats)[1]
""",
    tests=t7, hidden=h7,
    examples=[([[3, 1, 2]], 2), ([[1, 2, 3]], 0), ([[2, 2, 1]], 2), ([[4, 3, 2, 1]], 6)],
    brute=lambda a: brute7(*a), brute_on=t7 + h7)

# ------------------------------------------------------------------ J8
def brute8(a, b, k):
    return sorted(x + y for x in a for y in b)[k - 1]
r = random.Random(8)
def gen8(n, m):
    a = sorted(r.randint(-30, 60) for _ in range(n)); b = sorted(r.randint(-30, 60) for _ in range(m))
    return [a, b, r.randint(1, n * m)]
t8 = [[[1, 3, 5], [2, 4], 1], [[1, 3, 5], [2, 4], 3], [[1, 3, 5], [2, 4], 4], [[1, 3, 5], [2, 4], 6]]
h8 = [[[7], [5], 1], [[-5, -1], [-4, 0], 2], [[2, 2, 2], [3, 3], 5], gen8(10, 12), gen8(20, 20), gen8(35, 8), gen8(40, 40), gen8(1, 30)]
add(day=8, title="La k-ième adresse", concept="Recherche dichotomique sur la réponse, avec comptage",
    fn=("kiemeSomme", "kieme_somme"), params=("a, b, k", "a, b, k"), comment="Renvoie la k-ième plus petite somme a[i] + b[j]",
    statement="""Pour retrouver le paquet perdu, Pixel a deux listes de numéros, chacune **triée par ordre croissant** : les numéros de rue `a` et les numéros de porte `b`. L'adresse d'un paquet est la **somme** d'un numéro de chaque liste. Le givre a laissé un indice : le paquet se trouve à la `k`-ième plus petite adresse.

Écris une fonction `{fn}(a, b, k)` qui renvoie la **`k`-ième plus petite somme** `a[i] + b[j]`, toutes les paires `(i, j)` comptant, **doublons compris** (deux paires différentes qui donnent la même somme occupent deux rangs).

Précisions :
- `a` et `b` sont des listes non vides d'entiers triées par ordre croissant (les entiers peuvent être négatifs et se répéter).
- `k` commence à `1` (la plus petite somme) et ne dépasse jamais le nombre de paires.
- Les listes peuvent contenir des dizaines de milliers de numéros : fabriquer et trier toutes les sommes prendrait trop de place et de temps. Cherche la **valeur** de la réponse, pas sa position.

Exemple : avec `a = [1, 3, 5]` et `b = [2, 4]`, les sommes rangées sont `3, 5, 5, 7, 7, 9`. Pour `k = 3` la réponse est `5`, pour `k = 4` c'est `7`.
""",
    hint="Retourne la question : pour une valeur `x` donnée, combien de sommes sont inférieures ou égales à `x` ? Comme les deux listes sont triées, ce comptage se fait en un seul passage, avec une position qui avance dans une liste pendant que l'autre recule. Il reste à trouver la plus petite valeur `x` pour laquelle ce compte atteint `k`.",
    js="""function kiemeSomme(a, b, k) {
  // Combien de paires ont une somme inférieure ou égale à x ?
  const compter = (x) => {
    let total = 0;
    let j = b.length - 1;
    for (let i = 0; i < a.length; i++) {
      while (j >= 0 && a[i] + b[j] > x) j--;
      total += j + 1;
    }
    return total;
  };
  let bas = a[0] + b[0];
  let haut = a[a.length - 1] + b[b.length - 1];
  // La plus petite valeur x pour laquelle au moins k sommes sont <= x.
  while (bas < haut) {
    const milieu = Math.floor((bas + haut) / 2);
    if (compter(milieu) >= k) haut = milieu;
    else bas = milieu + 1;
  }
  return bas;
}
""",
    py="""def kieme_somme(a, b, k):
    # Combien de paires ont une somme inférieure ou égale à x ?
    def compter(x):
        total = 0
        j = len(b) - 1
        for valeur in a:
            while j >= 0 and valeur + b[j] > x:
                j -= 1
            total += j + 1
        return total

    bas = a[0] + b[0]
    haut = a[-1] + b[-1]
    # La plus petite valeur x pour laquelle au moins k sommes sont <= x.
    while bas < haut:
        milieu = (bas + haut) // 2
        if compter(milieu) >= k:
            haut = milieu
        else:
            bas = milieu + 1
    return bas
""",
    tests=t8, hidden=h8,
    examples=[([[1, 3, 5], [2, 4], 1], 3), ([[1, 3, 5], [2, 4], 3], 5), ([[1, 3, 5], [2, 4], 4], 7), ([[1, 3, 5], [2, 4], 6], 9)],
    brute=lambda a: brute8(*a), brute_on=t8 + h8)

# ------------------------------------------------------------------ J9
r = random.Random(9)
mots9 = "le givre dessine des fleurs sur la vitre et pixel relit chaque lettre du sac postal avant que la nuit ne tombe sur givreville".split()
t9 = [[["le", "givre", "dessine", "des", "fleurs", "sur", "la", "vitre"], 14], [["un", "train", "bleu"], 16], [["luge"], 7], [["a", "b", "c", "d", "e"], 5]]
h9 = [[[], 10], [["noel"], 4], [["a", "bb", "ccc", "dddd"], 4], [mots9, 20], [mots9, 11], [mots9, 34], [["x"] * 9, 4], [["cher", "pere", "noel", "je", "voudrais", "une", "luge", "et", "un", "livre", "sur", "les", "rennes"], 13]]
add(day=9, title="La lettre bien alignée", concept="Découper et justifier un texte",
    fn=("justifier", "justifier"), params=("mots, largeur", "mots, largeur"), comment="Renvoie la liste des lignes, chacune de `largeur` caractères",
    statement="""Le Registre n'accepte les lettres d'enfants que si elles sont **justifiées** : toutes les lignes doivent faire exactement la même largeur, comme dans un livre. À toi de remettre en page les mots sortis du sac postal.

Écris une fonction `{fn}(mots, largeur)` qui renvoie la **liste des lignes**. Chaque ligne est un texte d'exactement `largeur` caractères.

Règles :
- Les mots restent dans l'ordre. On remplit chaque ligne avec **le plus de mots possible**, en comptant au moins une espace entre deux mots.
- Sur une ligne de plusieurs mots (sauf la dernière), on ajoute des espaces **entre** les mots pour atteindre la largeur, réparties le plus également possible. Si elles ne se partagent pas exactement, les intervalles **de gauche** reçoivent chacun une espace de plus que ceux de droite.
- Une ligne qui ne contient **qu'un seul mot** est calée à gauche, et complétée par des espaces à droite.
- La **dernière ligne** est calée à gauche elle aussi : une seule espace entre les mots, puis des espaces à droite jusqu'à la largeur.

Précisions : chaque mot est un texte non vide, sans espace, d'au plus `largeur` caractères. Sans aucun mot, renvoie la liste vide.

Exemple : avec les mots `le`, `givre`, `dessine`, `des`, `fleurs`, `sur`, `la`, `vitre` et une largeur de `14`, on obtient quatre lignes (la dernière se termine par 9 espaces) :

`le       givre`
`dessine    des`
`fleurs  sur la`
`vitre         `
""",
    hint="Sépare le travail en deux temps : d'abord décider quels mots vont sur la ligne, ensuite fabriquer la ligne. Pour le partage des espaces, une division entière et son reste te donnent tout : combien d'espaces par intervalle, et combien d'intervalles en reçoivent une de plus.",
    js="""function justifier(mots, largeur) {
  const lignes = [];
  let i = 0;
  while (i < mots.length) {
    // Les mots i à j - 1 tiennent sur la ligne, avec une espace entre chacun.
    let j = i;
    let lettres = 0;
    while (j < mots.length && lettres + mots[j].length + (j - i) <= largeur) {
      lettres += mots[j].length;
      j++;
    }
    const groupe = mots.slice(i, j);
    const intervalles = groupe.length - 1;
    let ligne;
    if (j === mots.length || intervalles === 0) {
      ligne = groupe.join(" ").padEnd(largeur, " ");
    } else {
      const espaces = largeur - lettres;
      const base = Math.floor(espaces / intervalles);
      const enPlus = espaces % intervalles;
      ligne = "";
      groupe.forEach((mot, k) => {
        ligne += mot;
        if (k < intervalles) ligne += " ".repeat(base + (k < enPlus ? 1 : 0));
      });
    }
    lignes.push(ligne);
    i = j;
  }
  return lignes;
}
""",
    py="""def justifier(mots, largeur):
    lignes = []
    i = 0
    while i < len(mots):
        # Les mots i à j - 1 tiennent sur la ligne, avec une espace entre chacun.
        j = i
        lettres = 0
        while j < len(mots) and lettres + len(mots[j]) + (j - i) <= largeur:
            lettres += len(mots[j])
            j += 1
        groupe = mots[i:j]
        intervalles = len(groupe) - 1
        if j == len(mots) or intervalles == 0:
            ligne = " ".join(groupe).ljust(largeur)
        else:
            base, en_plus = divmod(largeur - lettres, intervalles)
            ligne = ""
            for k, mot in enumerate(groupe):
                ligne += mot
                if k < intervalles:
                    ligne += " " * (base + (1 if k < en_plus else 0))
        lignes.append(ligne)
        i = j
    return lignes
""",
    tests=t9, hidden=h9,
    examples=[([["le", "givre", "dessine", "des", "fleurs", "sur", "la", "vitre"], 14], ["le       givre", "dessine    des", "fleurs  sur la", "vitre         "]), ([["luge"], 7], ["luge   "]), ([[], 10], [])],
    check=lambda a, out: all(len(l) == a[1] for l in out) and " ".join(out).split() == a[0])

# ------------------------------------------------------------------ J10
r = random.Random(10)
def gen10(depth):
    if depth == 0 or r.random() < 0.25:
        s = str(r.randint(0, 12))
        return ("-" + s) if r.random() < 0.15 else s
    c = r.random()
    if c < 0.2: return "(" + gen10(depth - 1) + ")"
    if c < 0.3: return "-(" + gen10(depth - 1) + ")"
    sp = r.choice(["", " "])
    return gen10(depth - 1) + sp + r.choice("+-*") + sp + gen10(depth - 1)
t10 = [["2 + 3 * 4"], ["(2 + 3) * 4"], ["-(4 - 6) * 3"], ["2 * -3"], ["10 - 2 - 3"]]
h10 = [["42"], ["  7  "], ["--5"], ["2*(3+(4-1))*2"], ["-3 - -3"], ["100 - 5 * (2 + 3) * 2"], ["((((1))))"], ["3 - (2 - (1 - (4 - 6)))"]] + [[gen10(4)] for _ in range(6)]
add(day=10, title="L'addition de Mère Noëlle", concept="Deux piles pour évaluer une expression",
    fn=("calculer", "calculer"), params=("texte", "texte"), comment="Renvoie la valeur de l'expression",
    statement="""Sur un coin de table, Mère Noëlle a griffonné le calcul des quantités de la fournée : des nombres, des `+`, des `-`, des `*` et des parenthèses. Le Registre, lui, ne sait lire que de gauche à droite : il lui faut une méthode pour respecter les priorités.

Écris une fonction `{fn}(texte)` qui renvoie la **valeur** (un entier) de l'expression. Tu n'as **pas le droit** de confier le calcul au langage (pas de `eval` ni d'équivalent) : c'est justement ce qu'on te demande d'écrire.

Règles :
- Les nombres sont des entiers écrits avec des chiffres (`0`, `7`, `120`).
- La multiplication `*` passe **avant** l'addition `+` et la soustraction `-`. À priorité égale, on calcule **de gauche à droite** : `10 - 2 - 3` vaut `5`.
- Les parenthèses passent avant tout, et peuvent s'emboîter.
- Un `-` placé au début de l'expression, juste après une parenthèse ouvrante ou juste après un autre opérateur est un **signe moins** : il change le signe de ce qui le suit directement (un nombre, une parenthèse, ou un autre signe moins). Il est prioritaire sur la multiplication : `2 * -3` vaut `-6`, et `-(4 - 6) * 3` vaut `6`.
- Les espaces sont ignorées, où qu'elles soient.

Précisions : l'expression est toujours bien formée, et aucun résultat intermédiaire ne dépasse un milliard en valeur absolue.

Exemples : `2 + 3 * 4` vaut `14`, et `(2 + 3) * 4` vaut `20`.
""",
    hint="Garde deux piles : une pour les nombres, une pour les opérateurs en attente. Quand un nouvel opérateur arrive, demande-toi lesquels, parmi ceux qui attendent, doivent être calculés avant lui. Le signe moins est un opérateur comme les autres, mais il ne prend qu'un seul nombre : il te faut un moyen de le distinguer de la soustraction.",
    js="""function calculer(texte) {
  const nombres = [];
  const operateurs = []; // "+", "-", "*", "(" ou "~" (le signe moins)
  const priorite = { "+": 1, "-": 1, "*": 2, "~": 3 };
  const appliquer = () => {
    const op = operateurs.pop();
    if (op === "~") {
      nombres.push(-nombres.pop());
      return;
    }
    const b = nombres.pop();
    const a = nombres.pop();
    nombres.push(op === "+" ? a + b : op === "-" ? a - b : a * b);
  };
  let attendUnNombre = true; // vrai au début, après "(" et après un opérateur
  let i = 0;
  while (i < texte.length) {
    const c = texte[i];
    if (c === " ") {
      i++;
    } else if (c >= "0" && c <= "9") {
      let n = 0;
      while (i < texte.length && texte[i] >= "0" && texte[i] <= "9") {
        n = n * 10 + Number(texte[i]);
        i++;
      }
      nombres.push(n);
      attendUnNombre = false;
    } else if (c === "(") {
      operateurs.push(c);
      attendUnNombre = true;
      i++;
    } else if (c === ")") {
      while (operateurs[operateurs.length - 1] !== "(") appliquer();
      operateurs.pop();
      attendUnNombre = false;
      i++;
    } else if (c === "-" && attendUnNombre) {
      operateurs.push("~");
      i++;
    } else {
      while (operateurs.length && operateurs[operateurs.length - 1] !== "(" && priorite[operateurs[operateurs.length - 1]] >= priorite[c]) appliquer();
      operateurs.push(c);
      attendUnNombre = true;
      i++;
    }
  }
  while (operateurs.length) appliquer();
  return nombres[0];
}
""",
    py="""def calculer(texte):
    nombres = []
    operateurs = []  # "+", "-", "*", "(" ou "~" (le signe moins)
    priorite = {"+": 1, "-": 1, "*": 2, "~": 3}

    def appliquer():
        op = operateurs.pop()
        if op == "~":
            nombres.append(-nombres.pop())
            return
        b = nombres.pop()
        a = nombres.pop()
        nombres.append(a + b if op == "+" else a - b if op == "-" else a * b)

    attend_un_nombre = True  # vrai au début, après "(" et après un opérateur
    i = 0
    while i < len(texte):
        c = texte[i]
        if c == " ":
            i += 1
        elif "0" <= c <= "9":
            n = 0
            while i < len(texte) and "0" <= texte[i] <= "9":
                n = n * 10 + int(texte[i])
                i += 1
            nombres.append(n)
            attend_un_nombre = False
        elif c == "(":
            operateurs.append(c)
            attend_un_nombre = True
            i += 1
        elif c == ")":
            while operateurs[-1] != "(":
                appliquer()
            operateurs.pop()
            attend_un_nombre = False
            i += 1
        elif c == "-" and attend_un_nombre:
            operateurs.append("~")
            i += 1
        else:
            while operateurs and operateurs[-1] != "(" and priorite[operateurs[-1]] >= priorite[c]:
                appliquer()
            operateurs.append(c)
            attend_un_nombre = True
            i += 1
    while operateurs:
        appliquer()
    return nombres[0]
""",
    tests=t10, hidden=h10,
    examples=[(["2 + 3 * 4"], 14), (["(2 + 3) * 4"], 20), (["-(4 - 6) * 3"], 6), (["2 * -3"], -6), (["10 - 2 - 3"], 5)],
    brute=lambda a: eval(a[0].replace("--", "- -").replace("--", "- -")), brute_on=t10 + h10, limit=10**9)

# ------------------------------------------------------------------ J11
import re
def expand11(code):
    while "[" in code:
        code = re.sub(r"(\d+)\[([a-z]*)\]", lambda m: m.group(2) * int(m.group(1)), code)
    return code
def brute11(code, k):
    s = expand11(code)
    return s[k] if k < len(s) else ""
t11 = [["2[ab]c", 3], ["2[ab]c", 4], ["2[ab]c", 5], ["3[a2[bc]]", 7]]
h11s = [["", 0], ["noel", 3], ["10[a]b", 10], ["2[3[x]y]z", 7], ["2[3[x]y]z", 8], ["a2[b3[cd2[e]]f]g", 17], ["3[]a", 0], ["12[ab]", 23], ["12[ab]", 24], ["4[a3[b2[c1[d]]]]", 30]]
hbig = [["1000000[ab2[c]]", 3999998], ["1000000[ab2[c]]", 4000000], ["999999[9999[xy]z]9[w]", 19998980005], ["30[30[30[30[30[30[30[30[ab]]]]]]]]c", 1312200000000], ["30[30[30[30[30[30[30[30[ab]]]]]]]]c", 777777777777]]
add(day=11, title="La poupée sans fond", concept="Récursion : trouver sans construire",
    fn=("caractereNumero", "caractere_numero"), params=("code, k", "code, k"), comment="Renvoie le caractère de position k du texte déplié, ou \"\"",
    statement="""Le dernier coffre contient une minuscule étiquette écrite en **code replié** : `3[ab]` veut dire « `ab`, trois fois de suite », donc `ababab`. Et comme les coffres, les replis s'emboîtent : `2[a3[b]]` se déplie en `abbbabbb`. Le cadeau se cache derrière **une seule lettre** du texte déplié. Seulement voilà : déplié, le texte peut compter des millions de milliards de lettres. Il ne tiendrait dans aucune mémoire.

Écris une fonction `{fn}(code, k)` qui renvoie le **caractère de position `k`** du texte déplié (les positions commencent à `0`). Si le texte déplié est trop court, renvoie le texte vide `""`.

Le code suit ces règles :
- une lettre minuscule se déplie en elle-même ;
- un nombre entier suivi de crochets, comme `12[...]`, répète ce nombre de fois le dépliage de ce qui est entre les crochets ;
- tout cela se met bout à bout, et l'intérieur des crochets suit les mêmes règles (il peut aussi être vide).

Précisions : le code est toujours bien formé. Les nombres sont des entiers `>= 1`, parfois à plusieurs chiffres. `k` est un entier `>= 0`. La longueur du texte déplié ne dépasse jamais `9 000 000 000 000 000`.

Exemple : `2[ab]c` se déplie en `ababc`. La position `3` contient `b`, la position `4` contient `c`, et la position `5` n'existe pas : `""`. Pour `3[a2[bc]]` (soit `abcbcabcbcabcbc`), la position `7` contient `c`.
""",
    hint="Tu n'as pas besoin du texte déplié, seulement de sa **longueur**, morceau par morceau. Lis d'abord le code comme un emboîtement de coffres, en notant la longueur de chacun. Ensuite, pour atteindre la position `k`, saute les morceaux entiers qui sont trop courts. Et dans un morceau répété, toutes les copies sont identiques : inutile de savoir dans laquelle tu tombes.",
    js="""function caractereNumero(code, k) {
  let i = 0;
  // Lit une suite de morceaux jusqu'au crochet fermant (ou la fin) : renvoie [morceaux, longueur dépliée].
  function lire() {
    const morceaux = [];
    let total = 0;
    while (i < code.length && code[i] !== "]") {
      if (code[i] >= "0" && code[i] <= "9") {
        let fois = 0;
        while (code[i] !== "[") {
          fois = fois * 10 + Number(code[i]);
          i++;
        }
        i++; // le crochet ouvrant
        const [interieur, longueur] = lire();
        i++; // le crochet fermant
        morceaux.push({ fois, interieur, longueur });
        total += fois * longueur;
      } else {
        morceaux.push({ lettre: code[i] });
        total += 1;
        i++;
      }
    }
    return [morceaux, total];
  }
  function chercher(morceaux, position) {
    for (const m of morceaux) {
      if (m.lettre !== undefined) {
        if (position === 0) return m.lettre;
        position -= 1;
      } else {
        const taille = m.fois * m.longueur;
        // Toutes les copies sont identiques : seule compte la position dans une copie.
        if (position < taille) return chercher(m.interieur, position % m.longueur);
        position -= taille;
      }
    }
    return "";
  }
  const [racine, total] = lire();
  return k < total ? chercher(racine, k) : "";
}
""",
    py="""def caractere_numero(code, k):
    i = 0

    # Lit une suite de morceaux jusqu'au crochet fermant (ou la fin) : renvoie (morceaux, longueur dépliée).
    def lire():
        nonlocal i
        morceaux = []
        total = 0
        while i < len(code) and code[i] != "]":
            if code[i].isdigit():
                fois = 0
                while code[i] != "[":
                    fois = fois * 10 + int(code[i])
                    i += 1
                i += 1  # le crochet ouvrant
                interieur, longueur = lire()
                i += 1  # le crochet fermant
                morceaux.append((fois, interieur, longueur))
                total += fois * longueur
            else:
                morceaux.append(code[i])
                total += 1
                i += 1
        return morceaux, total

    def chercher(morceaux, position):
        for m in morceaux:
            if isinstance(m, str):
                if position == 0:
                    return m
                position -= 1
            else:
                fois, interieur, longueur = m
                taille = fois * longueur
                # Toutes les copies sont identiques : seule compte la position dans une copie.
                if position < taille:
                    return chercher(interieur, position % longueur)
                position -= taille
        return ""

    racine, total = lire()
    return chercher(racine, k) if k < total else ""
""",
    tests=t11, hidden=h11s + hbig,
    examples=[(["2[ab]c", 3], "b"), (["2[ab]c", 4], "c"), (["2[ab]c", 5], ""), (["3[a2[bc]]", 7], "c"), (["1000000[ab2[c]]", 4000000], ""), (["30[30[30[30[30[30[30[30[ab]]]]]]]]c", 1312200000000], "c")],
    brute=lambda a: brute11(*a), brute_on=t11 + h11s)

# ------------------------------------------------------------------ J12
def chiffrer12(clair, cle):
    out = []; n = 0
    for c in clair:
        if "a" <= c <= "z":
            out.append(chr((ord(c) - 97 + cle[n % len(cle)]) % 26 + 97)); n += 1
        else: out.append(c)
    return "".join(out)
def brute12(message, mot, lmax):
    import itertools
    lettres = [c for c in message if "a" <= c <= "z"]
    for L in range(1, lmax + 1):
        if L > 3: return None
        for cle in itertools.product(range(26), repeat=L):
            clair = []; n = 0
            for c in message:
                if "a" <= c <= "z":
                    clair.append(chr((ord(c) - 97 - cle[n % L]) % 26 + 97)); n += 1
                else: clair.append(c)
            clair = "".join(clair)
            if mot in clair:
                # la clé doit aussi être la plus petite : les colonnes libres valent 0, ce que l'ordre de product garantit
                return clair
    return ""
p12a = "le cristal du sous-sol garde un souvenir : la tournee de noel n'a jamais ete finie."
p12b = "pixel, 3 rennes et 1 luge : rendez-vous a minuit pres du grand sapin !"
t12 = [["opfm", "noel", 3], [chiffrer12("joyeux noel a tous", [3, 1]), "noel", 4], [chiffrer12(p12a, [6, 4, 11]), "tournee", 5], ["abc", "zzz", 2]]
h12 = [["", "noel", 3], [chiffrer12(p12b, [2, 25, 7, 13]), "minuit", 6], [chiffrer12(p12a, [0]), "noel", 2], [chiffrer12(p12a, [9, 9]), "souvenir", 4], [chiffrer12("le givre, la luge", [5, 1, 0]), "luge", 3], [chiffrer12(p12b, [1, 2, 3, 4, 5]), "sapin", 4], [chiffrer12("abab abab", [1, 2]), "ab", 2], [chiffrer12(p12a, [17, 3, 20, 8, 1, 12]), "cristal", 8], ["x-y-z", "xyz", 2]]
add(day=12, title="Le mot que Givrebug n'a pas pu cacher", concept="Casser un chiffre à clé répétée avec un mot probable",
    fn=("dechiffrerAvecMot", "dechiffrer_avec_mot"), params=("message, mot, longueurMax", "message, mot, longueur_max"), comment="Renvoie le message d'origine, ou \"\" si aucune clé ne convient",
    statement="""Nouveau message de Givrebug, et cette fois Pixel ne connaît **ni la clé, ni sa longueur**. Mais Mère Noëlle en est sûre : le message d'origine contient un mot précis, `mot`. Un seul mot connu peut suffire à tout faire tomber.

Le chiffre est le même que d'habitude : une clé est une liste de décalages, chacun entre `0` et `25`, répétée en boucle. La 1re **lettre** du message est avancée de `d1` rangs dans l'alphabet, la 2e de `d2`, et ainsi de suite ; après le dernier décalage, on repart du premier. L'alphabet boucle (`z` est suivi de `a`). Seules les lettres minuscules de `a` à `z` sont chiffrées : tout le reste (espaces, chiffres, ponctuation) est recopié tel quel et **ne fait pas avancer la clé**.

Écris une fonction `{fn}(message, mot, longueurMax)` qui renvoie le **message d'origine**, en choisissant la clé ainsi :

1. Une clé **convient** si, une fois le message déchiffré avec elle, `mot` y apparaît **d'un seul tenant** (ses lettres se suivent, sans rien entre elles).
2. On garde la clé qui convient la **plus courte** possible, parmi les longueurs de `1` à `longueurMax`.
3. S'il en reste plusieurs de cette longueur, on garde la **plus petite** : on compare les décalages un par un, de gauche à droite, et le premier qui diffère décide (`[2, 0, 9]` passe avant `[2, 1, 0]`).

Si aucune clé ne convient, renvoie le texte vide `""`.

Précisions : `mot` n'est jamais vide et ne contient que des lettres de `a` à `z`. `longueurMax` est un entier `>= 1`. Il existe `26` puissance `longueurMax` clés : les essayer toutes n'est pas une option.

Exemple : avec le message `"opfm"`, le mot `"noel"` et `longueurMax = 3`, la clé `[1]` convient : la réponse est `"noel"`. Avec `"abc"` et le mot `"zzz"`, il faudrait trois décalages différents : aucune clé de longueur 1 ou 2 ne convient, la réponse est `""`.
""",
    hint="N'essaie pas les clés : essaie les **emplacements**. Si le mot se trouve à un endroit précis du message, chacune de ses lettres t'impose un décalage pour une position de la clé. Deux exigences différentes pour la même position, et l'emplacement est impossible. Et les positions de la clé que le mot ne touche pas ? Pense à la règle 3.",
    js="""function dechiffrerAvecMot(message, mot, longueurMax) {
  const estLettre = (c) => c >= "a" && c <= "z";
  const code = (c) => c.charCodeAt(0) - 97;
  // rang[i] : numéro d'ordre du caractère i parmi les lettres (ou -1 si ce n'est pas une lettre)
  const rang = [];
  let lettres = 0;
  for (let i = 0; i < message.length; i++) rang.push(estLettre(message[i]) ? lettres++ : -1);

  const plusPetite = (a, b) => {
    for (let i = 0; i < a.length; i++) if (a[i] !== b[i]) return a[i] < b[i];
    return false;
  };

  for (let longueur = 1; longueur <= longueurMax; longueur++) {
    let meilleure = null;
    for (let debut = 0; debut + mot.length <= message.length; debut++) {
      // Si le mot est caché ici, chaque lettre impose un décalage à une position de la clé.
      const cle = new Array(longueur).fill(-1);
      let possible = true;
      for (let j = 0; j < mot.length && possible; j++) {
        const c = message[debut + j];
        if (!estLettre(c)) {
          possible = false;
          break;
        }
        const decalage = (code(c) - code(mot[j]) + 26) % 26;
        const position = rang[debut + j] % longueur;
        if (cle[position] === -1) cle[position] = decalage;
        else if (cle[position] !== decalage) possible = false;
      }
      if (!possible) continue;
      // Les positions libres valent 0 : c'est ce qui donne la plus petite clé.
      const complete = cle.map((d) => (d === -1 ? 0 : d));
      if (meilleure === null || plusPetite(complete, meilleure)) meilleure = complete;
    }
    if (meilleure !== null) {
      let clair = "";
      for (let i = 0; i < message.length; i++) {
        const c = message[i];
        clair += estLettre(c) ? String.fromCharCode(((code(c) - meilleure[rang[i] % longueur] + 26) % 26) + 97) : c;
      }
      return clair;
    }
  }
  return "";
}
""",
    py="""def dechiffrer_avec_mot(message, mot, longueur_max):
    def est_lettre(c):
        return "a" <= c <= "z"

    # rang[i] : numéro d'ordre du caractère i parmi les lettres (ou -1 si ce n'est pas une lettre)
    rang = []
    lettres = 0
    for c in message:
        if est_lettre(c):
            rang.append(lettres)
            lettres += 1
        else:
            rang.append(-1)

    for longueur in range(1, longueur_max + 1):
        meilleure = None
        for debut in range(len(message) - len(mot) + 1):
            # Si le mot est caché ici, chaque lettre impose un décalage à une position de la clé.
            cle = [-1] * longueur
            possible = True
            for j, lettre in enumerate(mot):
                c = message[debut + j]
                if not est_lettre(c):
                    possible = False
                    break
                decalage = (ord(c) - ord(lettre)) % 26
                position = rang[debut + j] % longueur
                if cle[position] == -1:
                    cle[position] = decalage
                elif cle[position] != decalage:
                    possible = False
                    break
            if not possible:
                continue
            # Les positions libres valent 0 : c'est ce qui donne la plus petite clé.
            complete = [0 if d == -1 else d for d in cle]
            if meilleure is None or complete < meilleure:
                meilleure = complete
        if meilleure is not None:
            clair = []
            for i, c in enumerate(message):
                if est_lettre(c):
                    clair.append(chr((ord(c) - 97 - meilleure[rang[i] % longueur]) % 26 + 97))
                else:
                    clair.append(c)
            return "".join(clair)
    return ""
""",
    tests=t12, hidden=h12,
    examples=[(["opfm", "noel", 3], "noel"), (["abc", "zzz", 2], ""), ([chiffrer12(p12a, [6, 4, 11]), "tournee", 5], p12a), ([chiffrer12("joyeux noel a tous", [3, 1]), "noel", 4], "joyeux noel a tous")],
    brute=lambda a: brute12(*a), brute_on=[t12[0], t12[1], t12[3], h12[0], h12[2], h12[6], h12[8]])
