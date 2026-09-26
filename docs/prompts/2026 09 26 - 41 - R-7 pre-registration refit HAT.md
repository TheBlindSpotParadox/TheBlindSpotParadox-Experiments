[Saturday, September 26, 2026]

# PRÉ-ENREGISTREMENT R-7 · REFIT DE LA LOI D'ONSET DU BRAS HAT SUR Δe ≥ 0,10

Écrit **avant** tout calcul du refit, conformément à la charge G3 du plan d'Opus (« 2026 09 26 - 40 - Opus post stream S13-bis.md », §4 et §8). Ce document fixe l'estimateur, les données, la règle de décision et les deux lectures admissibles **avant** que le résultat soit lu. Aucune médiane, aucune pente, aucun intervalle HAT n'a été calculé au moment de cette écriture.

---

## 1. Données

- Fichier : `results/R6_hydra_factor/data/R6_hat_instrumented.parquet` (expérience R6, données déjà committées).
- Colonnes : `boundary_shift`, `seed`, `tau_hat`, `delta_e`.
- Structure : 20 amplitudes × 100 graines = 2 000 lignes, grille identique à celle des traces S6 (Δe de 0,028186 à 0,497661).
- Censure déclarée (propriété des données vérifiée avant écriture, indépendante du résultat) : 18 valeurs `tau_hat` manquantes sur 2 000, dont 16 dans la bande de bruit (3 à Δe = 0,028, 13 à Δe = 0,085) et **2 sur le domaine valide** (1 à Δe = 0,141, 1 à Δe = 0,436). Une valeur manquante est un arbre non remplacé dans l'horizon — une observation censurée à droite, pas une donnée perdue.

## 2. Estimateur pré-enregistré

Parité stricte avec le refit ARF de S13 (`experiments/S13_evidence_bell/s13_evidence_bell.py`, refit R-4) :

1. **Domaine** : Δe ≥ 0,10 (18 amplitudes), excluant la bande de bruit non monotone (Remark `rem:bgswap`), même seuil `S13_VALID_DE_MIN = 0.10`.
2. **Statistique par amplitude** : médiane de `tau_hat` sur les graines non censurées.
3. **Fit** : régression linéaire de log(médiane) sur log(Δe) (`scipy.stats.linregress`) ; la pente est l'exposant α̂_HAT.
4. **Intervalle** : bootstrap sur graines, 2 000 répliques, rééchantillonnage des 100 graines avec remise par amplitude, médiane recalculée à chaque tirage sur les valeurs non censurées, percentiles 2,5 / 97,5 — même protocole que `_bootstrap_tau_exponent`, graine distincte.
5. **Référence ARF** (gate committé `s13_gate.json`) : exposant −1,7739, erreur type 0,0471, CI bootstrap graines [−1,898 ; −1,669].

## 3. Les deux lectures pré-enregistrées

Reprises de §4 d'Opus, pré-enregistrées avant lecture :

| issue mesurée | lecture |
| --- | --- |
| **HAT ≈ ARF ≈ −1,77** (les CI se recouvrent, aucun ne contient −2) | l'écart à −2 est une propriété **par arbre**. Le minimum de dix explique la constante, pas la pente. La phrase de `rem:exponent` est fausse et l'explication est à chercher du côté de la phase d'avertissement et de l'arbre de fond. |
| **HAT ≈ −2, ARF ≈ −1,77** (le CI HAT contient −2 et exclut le CI ARF) | l'écart est un **effet d'ensemble** — et alors le minimum de dix ne peut pas en être la cause, puisqu'il préserve les exposants. Un mécanisme dépendant de l'amplitude doit être nommé. |

Dans les deux cas, la phrase actuelle de `rem:exponent` (« the min-of-ten onset … is the candidate mechanism ») tombe ; la charge S13-G (G2) la retire indépendamment de ce résultat.

## 4. Règle de décision

- **Branche « par arbre »** si le CI 95 % HAT recouvre le CI ARF **et** exclut −2.
- **Branche « ensemble »** si le CI 95 % HAT contient −2 **et** exclut le CI ARF.
- **Tout autre issue** (les deux intervalles se recouvrent partiellement sans trancher, ou aucun critère n'est satisfait) : le refit est **déclaré non discriminant** à 100 graines ; aucune des deux lectures n'est écrite comme un résultat, et l'écart à −2 reste une question ouverte avec sa puissance déclarée.

Le résultat sera écrit dans le rapport de stream avec la branche tirée, que la lecture soit favorable ou non à l'interprétation courante du manuscrit.
