# Plan — Stream S3 : Proposition 9, M_crit, dépendance inter-arbres (F24)

## Contexte

`prop:starvation_boundary` (.tex L344–351) énonce `P_miss = P(tau_ARF < tau_det*) = 1 - [1 - F(tau_det*)]^M`
avec un signe **d'égalité**, sous une indépendance conditionnelle jamais démontrée, et contre un
`tau_det* := lambda/(Delta_e - delta_P)` **déterministe**. Le paragraphe *Correlation disclaimer*
(L338–342) affirme la direction du biais — la formule surestime `P_miss` — sans la prouver. C'est
l'objection retenue du reviewer #3 : « positive pairwise correlation alone does not generally
establish the claimed independence upper bound ».

Trois défauts adjacents sont dans le même périmètre :

- **F24** — `cor:mcrit` est marqué `void` dans `docs/theory/notation_map_v63_to_v2.md` L34 et **vivant**
  dans le manuscrit de référence L363–369, converti à la convention `r` par S7-bis. Un énoncé void
  dans la carte et vivant dans le `.tex` est la classe d'incohérence déjà relevée une fois.
- **F22** — `sec:hydra` L194 fonde l'accélération sur « the $M$-fold acceleration is exact for
  exponential $F$ » ; le paragraphe *Numerical example* L372 rapporte qu'un KS ($N=2000$ bootstrap)
  **rejette** l'ajustement exponentiel de `tau_HAT` à toutes les magnitudes ($p < 0.05$).
- `tau_det` est un temps d'arrêt **aléatoire**, pas le scalaire `tau_det*`. La course doit être
  reformulée en risques concurrents sous censure administrative.

Entrée T2.0 acquise : `theta* = 0.6813`, `ARL_0(15) = 4.02e6` à `p_0 = 0.024`, `delta_P = 0.01`,
verdict `lambda_FA` **NON-EMPTY** — `res:tension` et `rem:envelope` tiennent tels quels et **ne sont
pas touchés**.

---

## Périmètre fermé — déclaration liminaire

### Fichiers en ÉCRITURE (exhaustif, aucun autre)

| chemin                                                   | mode                                                                                                                                                                                                                                                                                | justification                                                          |
| -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| le manuscrit vivant, lu depuis `docs/manuscript/CURRENT` | **\*** patch restreint à la zone **définie par labels**, jamais par numéros de ligne : de l'ouverture du paragraphe *Correlation disclaimer* à la fin du paragraphe *Numerical example*, soit `prop:starvation_boundary`, `eq:pmiss`, sa preuve, `cor:mcrit` et l'exemple numérique | zone S3 exclusive, hors des quatre sous-sections exclues par CLAUDE.md |
| `docs/manuscript/sections/dependence_v2.tex`             | **création**                                                                                                                                                                                                                                                                        | Arbitrage d'ancre retenu. Zéro bloc SEARCH dans `framework_v2.tex`.    |
| `docs/theory/S3_dependence_bounds.md`                    | création                                                                                                                                                                                                                                                                            | livrable 2                                                             |
| `docs/theory/S3_competing_risks.md`                      | création                                                                                                                                                                                                                                                                            | livrable 3                                                             |
| `docs/theory/notation_map_v63_to_v2.md`                  | patch **restreint aux 2 lignes** `prop:starvation_boundary` (L33) et `cor:mcrit` (L34)                                                                                                                                                                                              | livrable 6                                                             |
| `docs/prompts/s3-decision-rules.md`                      | création                                                                                                                                                                                                                                                                            | livrable 5, **commité avant lecture**                                  |
| `docs/prompts/s3-pmiss-sweep-prompt.md`                  | création                                                                                                                                                                                                                                                                            | T3.5, prompt gaté non exécuté                                          |
| `docs/theory/transfer_S3.md`                             | création                                                                                                                                                                                                                                                                            | livrable 7                                                             |
| `results/S3/**`                                          | création                                                                                                                                                                                                                                                                            | livrable 4 — répertoire neuf, aucun artefact existant touché           |
| `experiments/S3_dependence/**`                           | création                                                                                                                                                                                                                                                                            | scripts d'analyse et gate RNG                                          |
| `tests/test_S3_dependence.py`                            | création                                                                                                                                                                                                                                                                            | garde de non-régression                                                |

 **\*Pourquoi le numéro de ligne est proscrit ici.** Les bornes L333–374 datent de la session
de planification, sur `a0009d4`. S2 livre deux patchs non appliqués qui déplacent cette
fenêtre : patch A ajoute **douze macros** au bloc de préambule, patch B réécrit
`rem:flooding` (L329–331 à l'époque), immédiatement au-dessus. S7-ter touche le même bloc
de préambule. L'ordre d'application imposé est A, puis B, puis le bloc S7-ter — sans quoi
l'ancre `\DeCritCI` bouge. Au moment où S3 édite, les quatre patchs peuvent avoir atterri
ou non. Chaque ancre SEARCH est donc re-grepée sur le fichier vivant à l'instant de
l'édition, et la conformité de périmètre se vérifie par label, jamais par plage de lignes.

### Fichiers en LECTURE SEULE — jamais patchés

- `docs/manuscript/sections/framework_v2.tex` — **244 lignes intégralement zone S2**
  (`thm:floor`, `cor:split`, `prop:invariance`, `prop:order`, `def:kappa`, instanciations
  `R_CUSUM/R_ADWIN/R_KSWIN`). Aucune ancre, aucun contexte.
- `.tex` hors L333–374, et en particulier les quatre sous-sections exclues par CLAUDE.md :
  `sec:race` L168, `sec:hydra` L185, `sec:starvation` L210, `sec:decoupling` L376.
  `res:tension` L396 et `rem:envelope` L400 sont dans `sec:decoupling` : verdict T2.0 NON-EMPTY,
  ils tiennent, rien à patcher.
- `config/experiment_ssot.py` — **aucune constante ajoutée**. L'arbitrage « prompt en attente »
  ferme `S3_M_GRID` ; `R9_RELIABILITY_TARGETS` et `CUSUM_DELTA_P` sont consommés, jamais redéclarés.
- `results/**` hors `results/S3/` — **zéro entrée nouvelle dans
  `results/audit_S7/_baseline/authorized_deviations.txt`**. Aucun artefact gelé ne bouge.

### Collisions signalées à l'instance primaire (pour information, aucune action S3)

`sec:hydra` L194 porte la moitié de F22 et est en zone exclue : la résolution S3 est écrite dans
`dependence_v2.tex` et référencée depuis L371–374, jamais ancrée dans `sec:hydra`.

---

## Table spécification → phase (Action B6)

| spec             | objet                                              | phase      | fichiers écrits                                                                                                  | porte de sortie                                                 |
| ---------------- | -------------------------------------------------- | ---------- | ---------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| —                | worktree `stream-s3` sur `a0009d4`                 | **P0**     | —                                                                                                                | worktree monté, `git status` propre                             |
| discipline       | règles de décision D1–D7 fixées avant lecture      | **P0**     | `docs/prompts/s3-decision-rules.md`                                                                              | committé avant tout script                                      |
| T3.1 (préalable) | indépendance conditionnelle vs RNG partagé River   | **P1**     | `experiments/S3_dependence/s3_gate_rng_factorization.py`, `results/S3/rng_factorization.json`                    | D1 tranchée, verdict binaire                                    |
| T3.1             | borne de Jensen, preuve                            | **P2**     | `docs/theory/S3_dependence_bounds.md`                                                                            | borne `<=` démontrée **ou** déclarée non disponible             |
| T3.2             | borne de Boole distribution-free                   | **P2**     | idem                                                                                                             | encadrement à deux bornes                                       |
| T3.3             | risques concurrents, censure, CIF, bandes          | **P3**     | `docs/theory/S3_competing_risks.md`, `results/S3/cif_bands.csv`                                                  | `tau_det*` supprimé, identité RMST reproduite                   |
| T3.4             | `rho_hat`, `M_eff`, confrontation au facteur Hydra | **P4**     | `results/S3/rho_meff.csv`                                                                                        | deux estimateurs rapportés, arbitrage moyennes/médianes tranché |
| T3.5             | statut de `cor:mcrit`, courbe `P_miss(M)`          | **P5**     | `results/S3/pmiss_vs_M.csv`, `results/S3/figures/Fig_S3_pmiss_vs_M.png`, `docs/prompts/s3-pmiss-sweep-prompt.md` | statut levé, courbe + 2 ancres mesurées                         |
| T3.6             | contradiction F22 sur l'exponentialité             | **P6**     | `docs/manuscript/sections/dependence_v2.tex`                                                                     | F22 résolue                                                     |
| T3.7             | partition d'écriture                               | **toutes** | —                                                                                                                | zéro ancre en zone S2                                           |
| livrables 1,6,7  | DIFFs, notation_map, transfert                     | **P7**     | `.tex` L333–374, `notation_map`, `transfer_S3.md`, `tests/test_S3_dependence.py`                                 | suite verte, hashes gelés intacts                               |

---

## P0 — Worktree et règles de décision

```
git worktree add /home/m53/worktree-S3 -b stream-s3 3f59b35
```

**Branchement sur `stream-s2` HEAD, pas sur `a0009d4`.** Le motif du plan initial —
« travail S2 en cours » — est périmé : S2 est clos, phases 0 à 7, quatre commits.
`a0009d4` est le commit de porte T2.0 et ne porte AUCUNE des phases 2 à 7. Brancher
dessus ferait lire à S3, en lecture seule, une version de `framework_v2.tex` que S2 a
depuis modifiée sur trois points qui touchent directement S3 :

- `thm:floor` resserré d'un facteur 6.74 (corde sur `u -> d(p_0+u||p_0)` au lieu de la
  relaxation chi-carré). Au point canonique : plancher `[13.9, 18.3]` contre plafond
  mesuré `33.5` et `R_CUSUM = 59.3`. `R_KSWIN = 22.7` passe.
- `cor:split` corrigé : sa clause KSWIN contredisait `eq:Rkswin`. L'axe opérant est
  `alpha`, pas `W` — `R_CUSUM` linéaire en `ln(1/alpha)` à pente `1/theta* = 1.468`,
  les deux autres en racine, croisement à `ln(1/alpha) ~ 13`.
- `R_EDDM` retiré des exigences (règle R5, verdict WITHDRAWN).

Le SHA exact est relevé sur `stream-s2` avant création du worktree et INSCRIT ICI.
Ne jamais brancher sur `HEAD` ni sur un nom de branche mobile.

**Ingestion obligatoire avant P1**, en lecture seule, au même titre que `framework_v2.tex` :
`docs/theory/transfer_S2.md`, `docs/theory/S2_arl0_recomputation.md`,
`docs/theory/S2_numerical_validation.md` (§5, les deux corrections d'énoncé de S2),
`docs/manuscript/sections/prop3_v2.tex`.
Deux entrées y sont bloquantes pour S3 et sont traitées en P4-bis ci-dessous :
l'asymétrie de seuil mesurée (`lambda` à budget égal : 20.97 ARF contre 132.50 HT) et
le constat `p_pre != p_true` au site R1 (`exp_R1_generate_data.py:56`, tolérance
effective 0.036 au lieu de 0.01).

Convention de worktree reprise de `/home/m53/worktree-S7ter`.

`docs/prompts/s3-decision-rules.md` est écrit et **committé avant l'exécution de tout script S3**.
Il porte sept règles à deux branches, et une déclaration d'honnêteté obligatoire : la phase de
planification a déjà lu `results/R9_mcrit/data/exp_R9_mcrit_comparison.csv` (lignes `delta_e = 0.33`)
et l'en-tête de `results/audit_S7/hydra_survival.csv`. Les règles portant sur ces numéraux sont donc
écrites comme **règles de vérification à deux branches**, avec la lecture antérieure déclarée — pas
comme des règles d'arbitrage prétendument aveugles.

| règle     | objet                                                              | décision                                                              |
| --------- | ------------------------------------------------------------------ | --------------------------------------------------------------------- |
| D1        | factorisation du RNG River                                         | seuil binaire sur la carte des tirages ; branche « tombe » prévue     |
| D2        | laquelle des deux bornes porte la revendication                    | fixée avant lecture de leur écart                                     |
| D3        | tolérance de reproduction de l'identité RMST                       | `1e-9` (S7 mesure `9.1e-13` sur 40 cellules)                          |
| D4        | accord entre les deux estimateurs de `M_eff`                       | facteur déclaré ; désaccord = incertitude publiée, jamais moyennée    |
| D5        | statut de `cor:mcrit` : reconstruction (a) ou retrait (b)          | critère fixé sur la validité de D1/D2, pas sur l'agrément du résultat |
| D6        | résolution F22                                                     | quelle moitié de la contradiction cède, fixé d'avance                 |
| D7        | tolérance modèle-vs-mesure de `P_miss(M)` aux ancres `M in {1,10}` | déclarée avant calcul                                                 |
| D8 **\*** | `prop:starvation_boundary` : réparer ou retirer                    | critère fixé avant P2                                                 |

**\*D8 — la branche de retrait, arbitrée explicitement.** S2 a rendu R3 = `RETAIN, restreinte
et rétrogradée` sur l'équation (4), et `prop:certificate` — déterministe, sans hypothèse
distributionnelle — porte désormais le résultat publié : `def:decoupling` (i-bis) et
`res:tension` routent tous deux par `A_swap`. La question que S3 doit trancher avant de
réparer est donc : **à quoi sert encore `prop:starvation_boundary` une fois le certificat
load-bearing ?**
Argumenter les deux côtés dans `dependence_v2.tex`, exactement comme S2 l'a fait pour
l'équation (4) :
- la conserver coûte une proposition dont les deux bornes sont numériquement quasi vacantes
  au point d'opération, et dont le seul usage publiable est l'inversion en `M_crit` ;
- la retirer coûte le seul énoncé qui relie la taille d'ensemble à la probabilité de manqué,
  donc le seul support formel de l'effet Hydra — alors même que S6 a établi que les
  remplacements ne produisent que 0.7 % de l'effacement.
Le critère est fixé avant P2, pas après lecture des bornes. `NOT PRODUCED` et `WITHDRAWN`
sont des états terminaux légitimes.                                            |

---

## P1 — Le point décisif : indépendance conditionnelle contre RNG partagé

`experiments/S6_synchronized_traces/gates/g2_river_introspection.py` L183–185 enregistre déjà
`model.data[i].rng is model._rng`, vérifié `True` sur les dix arbres : River enfile **un** générateur
à travers toute la forêt. Le prompt a raison d'exiger que ce point ne soit pas traité par confiance,
mais le partage d'objet ne suffit **ni** à établir **ni** à réfuter l'hypothèse. Ce qui décide est la
**factorisation du flux de tirages** :

- conditionnellement au flux `S`, l'aléa résiduel est le seul PRNG ;
- le poids de Poisson est tiré une fois par arbre et par instance, dans l'ordre d'index : les
  positions consommées par l'arbre `i` forment l'ensemble déterministe `{i, M+i, 2M+i, ...}`. Des
  ensembles d'indices disjoints et déterministes sur un flux i.i.d. idéalisé sont indépendants —
  **ce canal factorise** ;
- `max_features='sqrt'` tire des sous-ensembles de variables **au moment des coupes**, et les bris
  d'égalité en consomment d'autres. Le *nombre* et la *position* de ces tirages dépendent de l'état
  propre de l'arbre `i`, donc décalent les positions de l'arbre `j` — **ce canal ne factorise pas
  a priori**. C'est là, et nulle part ailleurs, que l'hypothèse peut tomber.

**Gate.** `s3_gate_rng_factorization.py`, calqué sur `g2_river_introspection.py` et réutilisant
`gates/_gate_common.py` (`lock_rng`, `seed_pool`) — rung 2 de l'échelle, aucun harnais nouveau.
Il instrumente `_rng` pour enregistrer la carte position-de-tirage → arbre sur une trajectoire
courte, puis perturbe l'état d'un seul arbre et mesure si les positions des autres se décalent.
Coût : quelques secondes, une seule trajectoire, sortie dans `results/S3/rng_factorization.json`.
Il vérifie de surcroît l'absence de rétroaction du vote d'ensemble vers l'apprentissage par arbre.

**Les deux branches sont écrites dans D1 avant de lancer le gate :**

| verdict                                                              | conséquence                                                                                                                                                                  |
| -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| positions par arbre disjointes et indépendantes de l'état des autres | indépendance conditionnelle **tenable** ; la voie Jensen de T3.1 est ouverte                                                                                                 |
| décalage mesuré                                                      | la voie Jensen **tombe** ; la borne de Boole de T3.2 porte seule, et la borne de Jensen n'est énoncée que sous une hypothèse nommée et mesurée fausse, donc **non utilisée** |

---

## P2 — Les deux bornes (T3.1, T3.2)

`docs/theory/S3_dependence_bounds.md` porte les deux énoncés, leurs preuves complètes, et la
validation empirique.

**Jensen (sous D1 favorable).** `G_S(s) := P(tau_i > s | S)` ; échangeabilité et indépendance
conditionnelle donnent `P(min_i tau_i > s | S) = G_S(s)^M` ; `x -> x^M` est convexe sur `[0,1]`,
donc `P(min > s) = E_S[G_S(s)^M] >= (E_S[G_S(s)])^M = (1 - F(s))^M`, d'où

```
P(min_i tau_i <= s)  <=  1 - [1 - F(s)]^M .
```

La direction du *Correlation disclaimer* est donc **démontrée**, pas postulée, et le disclaimer est
promu au rang de corollaire.

**Boole (inconditionnelle).** `P(min_i tau_i <= s) <= min(1, M * F(s))`, valide quelle que soit la
structure de dépendance. C'est elle qui rend l'énoncé inattaquable, et c'est elle qui porte seule si
D1 est défavorable.

**Vacuité numérique des deux bornes au point canonique — à écrire, pas à découvrir.**
À `F_hat(tau_det*) = 0.49` et `M = 10` : Boole rend `min(1, 4.90) = 1`, strictement vacant ;
Jensen rend `1 - 0.51^10 = 0.9988`. Les deux disent « `P_miss` vaut au plus 100 % ». Un
reviewer calcule ces deux nombres en trente secondes.
Ce que les bornes achètent n'est pas la valeur de `P_miss` mais son **inversion** :
`M_crit = floor(ln r / ln(1 - F))`, qui rend `0` à `r = 0.95` — aucune taille d'ensemble,
pas même `M = 1`, n'atteint la cible. Écrire cet usage explicitement dans
`S3_dependence_bounds.md` et dans `dependence_v2.tex`, et ne jamais publier une valeur de
borne sans dire à quoi elle sert.

**Conséquence de D1-négatif, à inscrire dans D5 avant le gate.**
Si la factorisation du RNG tombe, la voie Jensen n'est pas utilisée et Boole porte seule. Or
Boole SATURE dès `M * F(s) >= 1`, c'est-à-dire dès `F >= 0.10` à `M = 10` — donc partout où
l'article opère. L'inversion en `M_crit` devient impossible : `min(1, M F)` est indépendante
de `M` dans la région saturée.
**Tout l'appareil `M_crit` repose donc sur D1.** D5 doit l'énoncer ainsi : D1-négatif
implique la branche (b), retrait de `cor:mcrit`, remplacé par la courbe `P_miss(M)` mesurée
aux deux ancres et par l'enveloppe de Boole déclarée saturée. Ce n'est pas un échec du
stream, c'est le verdict que le gate est là pour rendre — et il est préférable à un
corollaire qui survit sur une hypothèse mesurée fausse.

Les deux bornes sont évaluées sur `F_hat` = CDF empirique de `tau_HAT`
(`results/R6_hydra_factor/data/R6_hat_instrumented.parquet`, 2000 lignes, identique à
`results/R9_mcrit/data/results_instrumented_A_ADWIN_HAT.csv` — garanti par
`tests/test_S7_consistency.py::test_tau_hat_identical_between_R6_and_R9`) et confrontées à la
distribution mesurée de `tau_ARF` (`results/R2_instrumented_blind_spot/data/R2_instrumented_A_PHT_ARF.parquet`,
mêmes graine et `boundary_shift`). Toute ingestion tabulaire d'une clé de jointure flottante passe par
`float_precision='round_trip'` — `delta_e` joint R6 et R9 sur 20 points et le parseur C par défaut en
perd 1 ULP (`tests/test_S7_consistency.py` L288–291).

---

## P3 — Risques concurrents et censure (T3.3)

`tau_det*` est supprimé du raisonnement. L'événement d'intérêt est `{tau_ARF < tau_det}`, la censure
administrative est l'horizon commun `t_c = 4000` pas post-dérive.

**Réutilisation imposée, pas de cadre nouveau.** Sous censure administrative unique à horizon commun,
Kaplan–Meier se réduit à la survie empirique et `RMST(t_c) = mean(min(tau, t_c))` exactement ; S7 a
vérifié l'identité à `9.1e-13` sur 40 cellules — colonne `rmst_identity_dev` de
`results/audit_S7/hydra_survival.csv`, 20 lignes, une par magnitude. S3 reprend ce cadre et le
re-vérifie sous D3, il n'en introduit aucun autre.

`tau_det` empirique est lu dans R1/R2 (`tau_det` de `R2_instrumented_A_PHT_ARF.parquet`, entièrement
`NaN` au scénario A — la censure est totale à ce point d'opération et doit être rapportée comme telle,
jamais supprimée par un `dropna`). L'incidence cumulée est estimée non paramétriquement et ses bandes
de confiance sont calculées par bootstrap apparié à la graine, réplication et graine déclarées.

---

## P4 — Taille d'ensemble effective (T3.4)

**Contrainte de données, à déclarer dans le livrable.** Aucun artefact committé ne porte les `tau_i`
par arbre. `runs.parquet` ne donne que les statistiques d'ordre `tau_swap^(q)` pour
`q in {0.10, 0.25, 0.50, 1.00}` — soit `tau_(1)`, `tau_(3)`, `tau_(5)`, `tau_(10)` sur `M = 10`,
2000 runs au bras `full`, avec `tau_swap_q100` censuré sur 227 runs (le balayage complet des dix
arbres n'aboutit pas dans l'horizon). `traces.parquet` n'agrège que `swaps_cum` et
`trees_swapped_cum`. R2_A ne donne que le minimum. Le `rho_hat` « corrélation intra-run » de T3.4
n'est donc **pas directement estimable** ; l'arbitrage retenu est de l'estimer sans réexécution ni
déviation autorisée, par deux voies bracketantes :

- **(a) méthode des moments sous échangeabilité** — `Var(moyenne) = sigma^2 (1 + (M-1) rho) / M` ;
  les quatre statistiques d'ordre par run séparent la variance intra-run de la variance inter-run et
  rendent `rho_hat` par moments ;
- **(b) `M_eff` par appariement direct** — `M_eff := argmin_m | E[tau_(1:M)] mesuré −
  E[min de m tirages de F_hat] |`, sans passer par `rho`.

L'écart entre (a) et (b) est **publié comme incertitude de modèle**, jamais moyenné. Un troisième
écart est nommé explicitement et non réparé : `F_hat` est la marginale du **HAT**, pas celle d'un
arbre **dans** l'ARF (`max_features='sqrt'`, pondération de Poisson, capacité différente) ; le
manuscrit L345 fait déjà cette assimilation, S3 la déclare comme hypothèse au lieu de la laisser
tacite.

**Confrontation.** `M_eff` contre le facteur Hydra mesuré sous censure : `4.12x [3.45, 4.96]` à
`Delta_e = 0.14` et `7.99x [6.40, 9.72]` à `Delta_e = 0.33`, verdict **borne inférieure** (bras ARF
non censuré partout, `censored_frac_arf = 0.0` sur les 20 magnitudes). Le ratio des **médianes**
diverge : `5.32x` et `3.10x`. La revendication porte sur des espérances ; un run typique montre ~3x.
Les deux sont rapportés, et **D4 tranche d'avance lequel le manuscrit doit citer**.

---

## P4-bis — Le facteur Hydra est-il une comparaison équitable ?

Phase ajoutée après ingestion de `transfer_S2.md`. S2 a mesuré que la calibration à une
fausse alarme par warm-up donne `lambda = 20.97` à l'ARF et `lambda = 132.50` au HT : la
réduction de variance par bagging achète un seuil bas. Le facteur Hydra `4.12x` et `7.99x`
compare pourtant `tau_HAT` (`M = 1`) et `tau_ARF` (`M = 10`) à seuil nominal commun.

Le plan nomme déjà l'écart — `F_hat` est la marginale du HAT, pas celle d'un arbre DANS
l'ARF (`max_features='sqrt'`, pondération de Poisson, capacité moindre) — et le classe en
hypothèse déclarée. S2 lui donne une direction : les deux flux d'erreur n'ont pas la même
variance, donc un seuil commun n'achète pas le même budget de fausses alarmes, donc une
part du facteur mesuré est une différence de calibration et non une accélération
d'ensemble. C'est exactement le défaut que S2 a trouvé dans la comparaison de flooding, sur
la grandeur centrale de S3.

Mesure, sans ré-exécution et sans nouvelle déviation autorisée :
  a) taux d'erreur pré-dérive et variance de fenêtre, pour le HAT (R6) et pour un membre
     de l'ARF (traces S6), sur graines et magnitudes appariées ;
  b) si les deux marginales diffèrent, calculer le seuil qui égalise le budget de fausses
     alarmes entre elles, et RE-DÉRIVER le facteur Hydra à budget égal ;
  c) publier la décomposition — part seuil, part taille d'ensemble — jamais un facteur
     unique.

Si les données committées ne permettent pas (b), le déclarer, borner la sensibilité par le
rapport de variances mesuré en (a), et transmettre la mesure manquante à l'orchestrateur.
Ne pas moyenner, ne pas supposer l'équité.

**Second contrôle, même origine.** S2 a établi `p_pre != p_true` au site R1
(`exp_R1_generate_data.py:56`, tolérance effective 0.036 au lieu de 0.01). P3 lit
`tau_det` dans R1/R2. Vérifie le même point sur R2 AVANT d'utiliser un `tau_det` issu de
ces artefacts : un `tau_det` mesuré à une tolérance effective de 0.036 n'est pas le
`tau_det` de `eq:cusum`, et le modèle de risques concurrents de P3 en dépend entièrement.

---

## P5 — Statut de `cor:mcrit` et courbe `P_miss(M)` (T3.5)

**Incohérence de statut, levée d'abord.** `void` dans `notation_map` L34, vivant au `.tex` L363–369.
Le motif inscrit dans la carte — « rests on the independence bound rejected by reviewer #3 » — est
exactement ce que P2 répare : une fois `eq:pmiss` passée de `=` à `<=` avec preuve, `M_crit` devient
un **certificat suffisant** et non une prédiction, ce que le texte L368 dit déjà. La branche (a),
reconstruction en quantité de conception encadrée par l'enveloppe distribution-free de T3.2, est
donc la sortie attendue — mais elle est conditionnée par **D5**, fixée avant lecture, et la branche
(b) retrait pur reste ouverte si D1 et D2 échouent tous deux.

**Numéraux A1 — vérification, pas confiance.** `results/audit_S7/_baseline/authorized_deviations.txt`
enregistre pour `results/R9_mcrit/data/exp_R9_mcrit_comparison.csv` : « Action A1 […] At Delta_e =
0.33, lambda = 50 : tau_det* 155 -> 157.83. E[tau_HAT] = 463, F_emp = 0.49 and M_crit = 0 are
unchanged ». L'artefact le confirme ligne à ligne (`delta_e_eff = 0.3268`, `tau_det_star = 157.83`
= `50 / (0.3268 − 0.01)`, `F_emp = 0.49`, `Mcrit_emp = 0` à `r = 0.95`). Le numéral `F_hat(tau_det*)
= 0.49` du manuscrit est donc **vivant et correct** post-A1 ; la suspicion de T3.5 se résout
négativement. P5 le re-vérifie mécaniquement, avec les deux branches écrites d'avance, plutôt que de
le reprendre sur la foi de cette lecture.

Contrainte de convention tenue : `r = 1 - P_miss`, `R9_RELIABILITY_TARGETS = [0.99, 0.95, 0.50]` lu
au registre. `beta` est banni.

**Courbe.** `results/S3/pmiss_vs_M.csv` pour `M in {1, 2, 3, 5, 10, 20, 50}` :

| M       | modèle depuis `F_hat` | mesuré                   |
| ------- | --------------------- | ------------------------ |
| 1       | oui                   | R6 `tau_hat` (gratuit)   |
| 2, 3, 5 | oui                   | — (gaté)                 |
| 10      | oui                   | R2_A `tau_arf` (gratuit) |
| 20, 50  | oui                   | — (gaté)                 |

Les deux ancres mesurées viennent d'artefacts committés, sans exécution. Le balayage ARF des cinq
points restants est une expérience nouvelle : le registre ne connaît que `N_MODELS = 10` et
`R6_N_MODELS = 1`. Conformément au prompt, il n'est **pas exécuté** ; `docs/prompts/s3-pmiss-sweep-prompt.md`
l'écrit comme prompt Claude Code gaté, en attente de validation. La porte de sortie T3.5 est déclarée
fermée aux ancres `M in {1, 10}` sous D7, et gatée au-delà.

Figure sous `MPLBACKEND=Agg`, PRNG local (`SeedSequence`), graine déclarée.

---

## P6 — F22 (T3.6)

La contradiction n'oppose pas deux mesures mais une **référence de calibration** et un **test
d'ajustement**. `sec:hydra` L194 énonce une propriété de la famille exponentielle — l'accélération
est exactement `M`-fois *si* `F` est exponentielle — et non une affirmation que `F` l'est ; L372
mesure que `F` ne l'est pas. Les deux tiennent simultanément, mais la section est écrite de façon à
laisser lire la première comme un résultat sur l'ARF, ce qu'elle n'est pas.

La résolution nomme la référence comme telle et la remplace par ce qui est réellement mesuré : le
facteur `4.1–8.0x` mesuré à `M = 10` est **strictement inférieur** au `10x` du nul multichart
Tartakovsky, et l'écart se décompose en deux causes désormais séparables — non-exponentialité de `F`
(P2, via `E[tau_(1:M)] = int (1-F)^M`) et dépendance résiduelle (P4, via `M_eff`).

`sec:hydra` L185–208 étant en zone exclue par CLAUDE.md, **rien n'y est ancré** : la résolution est
écrite dans `dependence_v2.tex`, et le paragraphe *Numerical example* L371–374 — en zone S3 — la
référence.

---

## P7 — Livrables, DIFFs et gardes

**`.tex`, L333–374 uniquement.** Quatre patchs SEARCH/REPLACE, 3–4 lignes de contexte, ancres
re-grepées au moment de l'édition (les numéros de ligne cités ici datent de cette session) :

1. *Correlation disclaimer* L338–342 → corollaire démontré, ou renvoi à la borne de Boole si D1 tombe.
2. `eq:pmiss` L348–350 → `=` remplacé par `<=`, hypothèse nommée dans l'énoncé.
3. `proof` L353–361 → preuve Jensen, plus complémentation sous indépendance postulée.
4. `cor:mcrit` L363–369 et *Numerical example* L371–374 → statut D5, encadrement distribution-free,
   renvoi F22.

**`dependence_v2.tex`**, création : statistiques d'ordre, les deux bornes, `M_eff`, résolution F22,
risques concurrents. Environnements limités à ceux que `\newtheorem` déclare dans le document
principal — `tests/test_manuscript_integrity.py::test_sections_assemble_into_the_main_document`
vérifie ce point par `rglob("*.tex")` sous `docs/manuscript/` et couvre donc le fichier neuf d'office,
`\ref` compris.

**`notation_map`**, deux lignes : `prop:starvation_boundary` passe de `modified` à son statut de
sortie ; `cor:mcrit` quitte `void` selon D5. Aucune autre ligne du tableau.

**`tests/test_S3_dependence.py`** : une garde par énoncé numérique publié — les deux bornes
encadrent la mesure sur la grille, `M_eff` reproduit, `pmiss_vs_M.csv` reproduit aux ancres
`M in {1, 10}` sous la tolérance D7. Pas de framework, pas de fixture.

**`transfer_S3.md`** sur le modèle de `transfer_S1.md` : défauts traités, porte de sortie, résultats
numériques vérifiés, items ouverts, livrables, état.

---

## Vérification

```
cd /home/m53/worktree-S3

# 1. les artefacts gelés n'ont pas bougé — S3 n'écrit que sous results/S3/
sha256sum -c results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt

# 2. suite complète, y compris la nouvelle garde et l'intégrité du manuscrit
PYTHONHASHSEED=0 /home/m53/miniforge3/envs/Trading/bin/python -m pytest tests/ -q

# 3. déterminisme : deuxième passe des scripts S3, hashes identiques
PYTHONHASHSEED=0 /home/m53/miniforge3/envs/Trading/bin/python experiments/S3_dependence/s3_bounds.py
sha256sum results/S3/*.csv        # comparé à la première passe

# 4. le gate RNG rend le même verdict
PYTHONHASHSEED=0 /home/m53/miniforge3/envs/Trading/bin/python experiments/S3_dependence/s3_gate_rng_factorization.py

# 5. compilation du manuscrit après patch
tectonic docs/manuscript/$(cat docs/manuscript/CURRENT)

# 6. périmètre : aucun fichier hors la table d'écriture
git status --porcelain
git diff --stat a0009d4
```

Critères d'acceptation :

- `sha256sum -c` passe sans une seule ligne `FAILED`, et `authorized_deviations.txt` ne gagne aucune
  entrée ;
- `git diff --stat` ne montre **aucune ligne** de `docs/manuscript/sections/framework_v2.tex` ;
- `git diff` sur le manuscrit vivant ne touche que des hunks dont le contexte contient un des
  cinq labels de la zone S3 (`prop:starvation_boundary`, `eq:pmiss`, sa preuve, `cor:mcrit`,
  *Numerical example*). Le critère est lexical, pas positionnel : une plage de lignes fixée à
  la planification n'est pas vérifiable après l'atterrissage des patchs S2 et S7-ter ;
- aucun hunk ne touche le bloc de préambule — il appartient au patch A de S2 ;
- `pytest tests/` vert, `test_manuscript_integrity.py` inclus ;
- les deux passes des scripts S3 rendent des hashes identiques ;
- chaque porte de sortie du prompt S3 est marquée fermée ou explicitement déclarée partielle avec son
  motif — `NOT PRODUCED` reste un état terminal légitime, jamais remplacé par une esquisse de preuve.

**Circuit breakers.** Trois tentatives de remédiation par faute d'infrastructure ou de syntaxe, puis
gel déclaré et alerte. Sur échec de reproduction d'un numéral publié : arrêt immédiat, aucun
paramètre ajusté pour forcer la convergence.
