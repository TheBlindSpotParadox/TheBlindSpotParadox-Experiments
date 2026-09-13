# Plan — Stream S8 : généralité mécanistique, générateur par rotation, bras V4

## Contexte

Le reviewer #2 tient le phénomène pour un artefact de configuration River/ARF/ADWIN. S5 a produit
la réponse argumentative (topologie de boucle fermée) ; sans réplication inter-mécanisme et
inter-bibliothèque, cette réponse reste une analogie. S8 porte la réponse expérimentale.

Trois faits mesurés, lus dans le dépôt, fixent le périmètre réel — plus étroit que ce que le prompt
suppose sur deux points, plus large sur un troisième :

| fait | ancrage | conséquence |
|---|---|---|
| `rem:cf_scope` déclare textuellement le bras manquant : *« an arm with replacement suppressed from $\tau^*$ onward »* | `.tex:234` | T8.1 n'a pas à inventer sa définition, seulement à l'exécuter. `no_swap_ab_initio` = fork à **τ\***, pas à t = 0 |
| `no_swap` est déjà « deepcopy fork + `_drift_detection_disabled = True` + `_warning_detection_disabled = True` » | `s6_runner.py:237-241`, `ssot:226-231` | le bras V4 est un diff de ~12 lignes, pas un harnais neuf |
| le générateur canonique est `y = 1[x0 + x1 > b]`, `b = √2·Φ⁻¹(0.5+Δe)`, deux `rng.normal()` par pas | `s6_runner.py:61-66`, `_gate_common.py:36-38` | la phase pré-dérive est **déjà** la rotation à θ = π/4 : le correctif ne touche que l'étiquetage post-dérive |

Et un fait qui invalide une prémisse du prompt : **CONTRAINTE 2 est close, pas en cours.**
`docs/ENVIRONMENT.md:117` — « The extension to R2, R3 and R7 is already discharged » ; S7-ter est
mergé (`306b1da`). L'interdiction d'écrire sous `results/R2_*`, `R6_*`, `R7_*` tient toujours, mais
au titre du **gel bit-à-bit acquis** (27 OK / 7 FAILED, les sept déclarés), non d'un stream
concurrent.

## Découverte d'ingestion, à porter avant toute conception de T8.3 / T8.3-bis

**Ce que le dépôt appelle « HAT » n'est pas un HAT.** `exp_R6_generate_data.py:44-47` construit
`ARFClassifier(n_models=1, drift_detector=ADWIN(clock=1), warning_detector=ADWIN(clock=1))`, et
`grep -rn "HoeffdingAdaptiveTree\|HATClassifier" experiments/ tests/ config/` **ne rend rien**. Le
learner de base de l'ARF est `class BaseTreeClassifier(HoeffdingTreeClassifier)`
(`river/forest/adaptive_random_forest.py:251`) — un Hoeffding **Tree** à sous-échantillonnage de
variables, remplacé en bloc par un ADWIN externe. Ce n'est pas le HAT de Bifet–Gavaldà (ADWIN par
nœud, sous-arbres alternatifs, aucun reset global). Le manuscrit écrit pourtant
« a single Hoeffding Adaptive Tree (HAT, $M = 1$)~\cite{bifet_hat_2009} » (`.tex:224`).

Conséquences, toutes opérationnelles :

- `τ_HAT` du facteur Hydra est mesuré sur **ARF(M=1)**. T8.3-bis doit garder cet objet comme bras
  apparié, sans quoi la re-dérivation à budget égal ne se compare plus à `4.12×` / `7.99×`.
- `river.tree.HoeffdingAdaptiveTreeClassifier` **existe** dans la version épinglée et n'a **jamais**
  été exécuté ici. C'est donc une famille neuve pour T8.3, pas un doublon de R6.
- La charge terminologique part dans `transfer_S8.md`. S8 mesure, ne réécrit pas le `.tex`.

## Arbitrages

**Opérateur (validés ce tour).**

1. **T8.4 — MOA déclaré infaisable, repli = ré-implémentation ARF.** Mesuré : `java: command not
   found`, aucun jar MOA sous `/home/m53`, `skmultiflow` absent et incompatible py3.12/numpy 1.26.
   Le repli prévu par le prompt est retenu et il est le contrôle le plus fort : une ré-implémentation
   NumPy ne partage **aucune ligne** avec River, là où MOA partage la lignée algorithmique.
2. **Phasage P1 → gate → P2 → P3.** P1 = T8.1 + T8.2 + T8.5 + T8.6 (~1 h). T8.1 porte le risque
   niveau papier ; une réfutation doit être connue avant que P2 consomme des heures.
3. **Bruit d'étiquette η ∈ {0, 0.05}, deux bras d'une seule campagne.**

**Dérivés de la mesure (non escaladés, motivés ici).**

4. **Le bras V4 s'accompagne de `frozen_ab_initio`.** Le prompt demande un seul bras. Mais `frozen`
   forke à `τ_swap^(1/M)` et contient donc déjà le premier remplacement : sans référence ancrée à
   τ\*, la décomposition n'est pas additive et `\LearnShare = 99.3` ne peut pas être restaté. Le
   second bras est le **même deepcopy** avec `learn=False` — coût marginal quasi nul, et c'est ce qui
   rend la décomposition exacte (§ T8.1).
5. **Aucune écriture sous `results/S6_synchronized_traces/`.** La campagne S8 ré-émet `full`,
   `no_swap` et `frozen` dans son propre répertoire ; leur **identité bit-à-bit** avec les lignes
   commitées de S6 est la porte d'acceptation du tronc. Régénérer S6 déplacerait `envelope_stats.json`
   et les macros du manuscrit pour un gain nul.
6. **S8 ne patche pas le `.tex`.** Les cibles de T8.1 (`rem:cf_scope`, `sec:hydra`) sont dans la zone
   **exclue** par `CLAUDE.md` ; leurs correctifs vont dans `docs/manuscript/sections/framework_v2.tex`.
   Les autres charges sont livrées en blocs SEARCH/REPLACE dans `docs/theory/transfer_S8.md`, non
   appliquées : `stream-s11a` travaille en parallèle sur la charpente v65 du même document.
7. **Les τ_i par arbre sont enregistrés dans la campagne P1.** `segment()` calcule déjà
   `replaced[k]` (`s6_runner.py:114`) ; persister le premier pas d'incrément de chaque index ferme
   **l'item ouvert 1 de `transfer_S3.md` §6** — « no artifact records a per-tree `tau_i` inside the
   ARF », déclaré binding — pour ~4 lignes et 0 s de calcul supplémentaire.

## Périmètre d'écriture et gardes

Répertoires créés — vérifiés contre la garde anti-contamination `results/R0[0-9]_*` /
`results/R1[0-8]_*` : aucun ne tombe dans la plage.

```
experiments/S8_generality/          s8_arms.py, s8_rotation.py, s8_mechanisms.py, s8_figure_r7.py
results/S8_ab_initio/               data/{runs.parquet,traces.parquet/}, tables/
results/S8_rotation_generator/      data/, tables/, figures/
results/S8_r7_figure/figures/       Fig_R7_clock_mismatch.png
```

Jamais touchés : `results/R2_*`, `results/R6_*`, `results/R7_*`, `results/S6_synchronized_traces/`.

**La garde devient exécutable.** Elle n'existe aujourd'hui que dans les prompts — `grep` sur
`*.py`, `*.sh`, `*.md` ne trouve aucune implémentation, et un écrasement inter-projets s'est déjà
produit (`8debd1c`). Quatre lignes dans `tests/test_S7_consistency.py` :

~~~~~~~~~
def test_no_foreign_experiment_directory_under_results():
    """results/R0[0-9]_* and results/R1[0-8]_* belong to The-Whitening-Advantage-Experiments."""
    foreign = sorted(p.name for p in ssot.RESULTS_DIR.glob("R*")
                     if p.is_dir() and re.fullmatch(r"R(0\d|1[0-8])_.*", p.name))
    assert not foreign, f"cross-project directories under results/: {foreign}"
~~~~~~~~~

`.gitignore` reçoit `results/S8_ab_initio/data/traces.parquet/` et
`results/S8_rotation_generator/data/traces.parquet/` — même motif que l'entrée S6 existante
(traces volumineuses, régénérables).

**Conventions que le nouveau code doit respecter sous peine d'échec de la suite, toutes vérifiées
dans les tests existants :**

| règle | mécanisme | effet sur le code S8 |
|---|---|---|
| registre SSOT | `test_S7_consistency.GUARDED_NAMES:48-53` — toute assignation de module dont le nom est gardé doit contenir textuellement `ssot.` | jamais `N_STEPS = 8000` dans un script S8 ; toujours `N_STEPS = ssot.S8_N_STEPS` ou `ssot.N_STEPS` |
| littéraux de paramètres | `GUARDED_PARAMS = {n_steps, tp, t_drift, n_models, threshold}:77` — un `ast.Constant` nu en défaut d'argument ou en mot-clé d'appel échoue | `drift.PageHinkley(threshold=lam)` avec `lam` un `Name` : conforme. `threshold=50.0` : échec |
| tolérance CUSUM | `test_strict_cusum_runs_at_the_cusum_tolerance:250-268` | tout `StrictCUSUM(...)` de S8 prend `delta=ssot.CUSUM_DELTA_P` |
| préfixe d'artefact | précédent S2-bis : `tests/test_S2bis_calibration.py:260-269` impose que tout fichier sous `results/S2bis_calibration/` commence par `s2bis_` | même garde pour S8, basenames `s8_*`, dans `tests/test_S8_generality.py` |
| backend headless | aucun `run_experiment_*.sh` n'exporte `MPLBACKEND` ; le dépôt épingle `matplotlib.use("Agg")` **en ligne** dans chaque script traçant | `s8_figure_r7.py` fait de même, et reprend la palette de maison `'#04617b', '#E8A000', '#C62828', '#2E7D32', '#546E7A'` (dupliquée à l'identique dans R2 et S6 — aucun module de style partagé n'existe) |
| hachage | **`save_fair_csv` n'existe pas dans ce dépôt.** L'utilitaire réel est `s6_writer.sha256_tree:136-141`, appliqué *après* écriture, plus le manifeste gelé | ne pas en inventer un ; réutiliser `sha256_tree` pour la preuve de reproductibilité de campagne |

S6 n'a **aucune entrée** au manifeste gelé (`ENVIRONMENT.md:127`) : sa seule garde est
`tests/test_S6_traces.py::test_parquet_replay_is_byte_identical`. Les artefacts S8 héritent de ce
régime — rejeu et comparaison, pas de digest gelé — et n'ajoutent aucune ligne à
`authorized_deviations.txt`.

## Ce qui est produit

| livrable | nature | phase |
|---|---|---|
| `docs/prompts/s8-decision-rules.md` | **neuf** — règles D0–D9, commitées AVANT toute lecture de sortie | P0 |
| `experiments/S8_generality/s8_arms.py` | **neuf** — campagne bras V4, importe `s6_runner` | P1 |
| `experiments/S8_generality/s8_rotation.py` | **neuf** — générateur + campagne + confrontation à l'ancien | P1 |
| `experiments/S8_generality/s8_figure_r7.py` | **neuf** — figure autonome depuis le CSV R7 commité | P1 |
| `experiments/S6_synchronized_traces/s6_runner.py` | **modifié** — deux bras, τ_i, mode `abinitio` | P1 |
| `experiments/S6_synchronized_traces/s6_causal.py` | **modifié** — décomposition à trois termes | P1 |
| `config/experiment_ssot.py` | **modifié** — bloc `S8_` append-only | P1 |
| `tests/test_S8_generality.py` | **neuf** — invariants générateur + bras | P1 |
| `tests/test_S7_consistency.py` | **modifié** — garde anti-contamination exécutable | P1 |
| `docs/theory/S8_generality.md` | **neuf** — rapport de mesure et verdicts, style `S6_causal_evidence.md` | P1→P3 |
| `docs/theory/transfer_S8.md` | **neuf** — charges manuscrit en blocs SEARCH/REPLACE, non appliquées, style `transfer_S3.md` | P1→P3 |
| `experiments/S8_generality/s8_mechanisms.py` | **neuf** — grille mécanismes × ensembles à λ_eq | P2 |
| `experiments/S8_generality/s8_marginal.py` | **neuf** — HAT isolé vs arbre DANS l'ARF, budget égal | P2 |
| `experiments/S8_generality/s8_minimal_arf.py` | **neuf** — ARF NumPy instrumenté, zéro River | P3 |

Anglais pour code, docstrings, commits et rapports. Aucune section du `.tex` éditée.

---

# P0 — Règles de décision, commitées avant exécution

Convention de maison (`s3-decision-rules.md`, `s2bis-decision-rules.md`) : le fichier est commité
**avant** que la moindre sortie soit lue. Contenu minimal :

- **D1 (bras V4, inertie).** Le remplacement est déclaré INERTE si, sur la médiane appariée par
  graine, `share_swap_all = (A_abinit − A_full) / (A_frozen_abinit − A_full)` a son IC bootstrap 95 %
  inclus dans `[0, 0.05]` **et** le test des signes sur `A_abinit − A_full` ne rejette pas à α = 0.01.
- **D2 (contribution propre du premier swap).** Déclarée mesurée si l'IC 95 % de la médiane de
  `share_swap_first = (A_abinit − A_no_swap) / (A_frozen_abinit − A_full)` est strictement positive.
  Le prompt oppose `A_full` à `A_abinit` : ce contraste mesure **tous** les remplacements. La
  contribution du **premier** est `A_abinit − A_no_swap`. Les deux sont rapportés, sans substitution.
- **D3 (lecture décisionnelle).** Taux de détection à λ = 50 par bras au point canonique
  Δe = 0.3268, à comparer aux 0/100 (`full`) et 18/100 (`no_swap`) publiés.
- **D4 (identité du générateur).** `|Δe_mesuré − θ/π·(1−2η)| ≤ 3·SE` sur les 20 points de grille.
- **D5 (nul non dégénéré).** `e_pre` strictement positif, rapporté avec sa dispersion, sur les deux
  bras η. Critère de non-dégénérescence : à η = 0.05, au moins un λ de l'échelle produit un taux de
  fausse alarme pré-dérive dans `(0, 1)`.
- **D6 (bascule haute, T8.5).** Le point de bascule est `inf{Δe : médiane(A/A_rect) < 0}`. Sous le
  générateur par rotation il est déclaré ABSENT si aucun point de grille n'a de médiane négative.
- **D7 (collapse S5).** Les courbes taux-de-manqué contre `A` de tous les mécanismes internes sont
  déclarées collapsées si, à `A` apparié, l'écart inter-mécanisme reste sous l'IC 95 % intra-mécanisme.
  Le recadrage boucle fermée est FAUX si un mécanisme non-ADWIN à `tau_erase` comparable et à λ_eq ne
  produit pas de point aveugle comparable.
- **D8 (facteur Hydra à budget égal).** Décomposition part-seuil / part-taille-d'ensemble publiée,
  ou déclarée `NOT PRODUCED` avec la mesure manquante nommée — jamais absorbée.
- **D9 (réplication).** Si la ré-implémentation infirme le phénomène, c'est un artefact
  d'implémentation : décision de poursuite remontée à l'utilisateur, aucune correction unilatérale.

---

# P1 — T8.1 : bras V4

## Ce que les autres streams ont déjà retiré au budget

`docs/theory/S6_causal_evidence.md` §5 : 99.3 % de l'effacement post-fork est l'apprentissage
incrémental des M−1 arbres survivants. `transfer_S3.md` §4.3 : l'écart au 10× de Tartakovsky vient
majoritairement de la non-exponentialité de F (9.22× contre 7.99× mesuré, résidu 0.87), `rho_hat ∈
[−0.021, 0.053]`. S7-ter : sous U1 la famine s'atténue au haut de la bande. Il ne reste au bras V4
qu'une question : **le premier remplacement porte-t-il une contribution propre à l'amorce ?**

## Pourquoi les bras actuels ne peuvent pas y répondre

`no_swap` et `frozen` sont des `deepcopy` pris à `fork_abs`, l'instant du premier remplacement
(`s6_runner.py:215-220`). Ils **partagent** ce remplacement avec `full`. Leur contraste identifie
l'apprentissage post-bifurcation — ce que le harnais reconnaît déjà lui-même :
`s6_causal.py:162-164`, « Isolating the first swap would need a fourth arm forked BEFORE it fires,
which this campaign does not simulate. » Le point de fork est **endogène** : il dépend du bras.
Forker à τ\*, instant **exogène** fixé par le protocole, restaure l'appariement.

Aucune ébauche n'existe : `grep -rn "ab_initio\|ab initio" --include="*.py"` ne rend rien dans tout
le dépôt. Le bras est à écrire, pas à réactiver.

## Diff

Deux bras, un seul `deepcopy` supplémentaire, pris avant le segment `head` :

~~~~~~~~~
    head, fork_abs = segment(arf, x, y, T_DRIFT, N_STEPS, stop_on_new_tree=True)
~~~~~~~~~
devient
~~~~~~~~~
    drift_src = copy.deepcopy(arf) if {"no_swap_ab_initio", "frozen_ab_initio"} & set(arms) else None
    head, fork_abs = segment(arf, x, y, T_DRIFT, N_STEPS, stop_on_new_tree=True)
~~~~~~~~~

puis, après la boucle des branches existantes :

~~~~~~~~~
    for arm in [a for a in ("no_swap_ab_initio", "frozen_ab_initio") if a in arms]:
        branch = copy.deepcopy(drift_src)
        branch._drift_detection_disabled = True
        branch._warning_detection_disabled = True
        seg, _ = segment(branch, x, y, T_DRIFT, N_STEPS, learn=(arm == "no_swap_ab_initio"))
        rec, der = _metrics(seed, delta_e, arm, seg, pre["err"], pre_swaps, 0.0, nodes_at_drift)
        records.append(rec)
        frames.append(_frame(seed, delta_e, arm, pre, seg, der))
~~~~~~~~~

`post` est le segment complet `[T_DRIFT, N_STEPS)`, sans `_concat(head, …)` : il n'y a pas de préfixe
partagé, c'est exactement ce qui fait l'identification. `fork_t_rel = 0.0` marque le fork à τ\*.

Trois points de vigilance, tous vérifiables :

- **Neutralité PRNG.** `ssot:228-231` l'établit pour `no_swap` : River tire le poids de Poisson
  **avant** les blocs détecteurs, et les blocs ne consomment aucune entropie. Le même argument tient
  ici. La gate G1 (`g1_deepcopy_fidelity.py`) certifie déjà le `deepcopy` sur 150 forks.
- **`tau_swap` est NaN** sur ces bras (aucun remplacement) ⇒ `tau_erase`, `a`, `a_rect`, `kappa` le
  sont aussi. La statistique de décision est `a_unrefl_peak` (`max_t A_unrefl`), sans seuil et sans
  `tau_erase` — `S6_causal_evidence.md` §4 la retient déjà comme « the one budget statistic free of
  every definitional dispute ». Le contraste causal passe par `a_pos_common`, la fenêtre commune que
  `s6_causal._partition_stats:77-79` calcule déjà pour la même raison (`frozen` ne se stabilise jamais).
- **`ARM_NAMES` s'allonge** ⇒ `s6_runner.demo()` (`:298-301`) casse sur `set(by_arm) == set(ARM_NAMES)`.
  Le self-check est à étendre, pas à contourner : `swaps_total == 0` et `fork_t_rel == 0` sur les deux
  nouveaux bras sont les invariants qui prouvent l'intervention.

## Décomposition rendue exacte

`s6_causal.erasure_share` (`:144-170`) calcule aujourd'hui `e_total = A_frozen − A_full`,
`e_learn = A_frozen − A_no_swap`. Les deux références sont ancrées à `τ_swap^(1/M)`. Avec le bras
gelé ab initio comme référence unique ancrée à τ\* :

```
E_total       = A_frozen_abinit − A_full          toute l'adaptation post-τ*
E_learn_pure  = A_frozen_abinit − A_abinit        apprentissage seul, aucun arbre jamais remplacé
E_swap_first  = A_abinit        − A_no_swap       le PREMIER remplacement, isolé
E_swap_rest   = A_no_swap       − A_full          les remplacements suivants
E_total = E_learn_pure + E_swap_first + E_swap_rest      exactement
```

`\LearnShare = 99.3` est aujourd'hui `E_learn/E_total` avec un `E_learn` qui **contient** le premier
swap. La mesure P1 le réattribue ou le confirme. C'est le résultat publiable du bras V4, et c'est
aussi son risque : si `E_swap_first` est substantiel, le numéral `99.3` du résumé, de `sec:hydra` et
de la conclusion bouge.

## Exécution

```bash
PYTHONHASHSEED=0 /home/m53/miniforge3/envs/Trading/bin/python \
  experiments/S6_synchronized_traces/s6_runner.py demo          # invariants des 6 bras
PYTHONHASHSEED=0 .../python experiments/S8_generality/s8_arms.py smoke    # 5 graines x 3 Δe
PYTHONHASHSEED=0 .../python experiments/S8_generality/s8_arms.py full     # ~25 min estimés
PYTHONHASHSEED=0 .../python experiments/S8_generality/s8_arms.py causal   # décomposition + verdicts
```

`s8_arms.py` est un pilote mince sur `s6_runner.campaign` : `arms = ("full", "no_swap", "frozen",
"no_swap_ab_initio", "frozen_ab_initio")`, `out_dir = results/S8_ab_initio/`, grille et graines
canoniques. `static` est écarté — `S6_causal_evidence.md` §8.5 le déclare non apparié en capacité et
non utilisable comme contrôle.

**Les graines ne sont pas `range(1, 101)`.** `s6_runner.py:321` passe
`common.seed_pool(len(ssot.S6_CAMPAIGN_SEEDS))` : `S6_CAMPAIGN_SEEDS` ne fournit que le **cardinal**,
les valeurs sortent de `SeedSequence(42).spawn(100)` (`_gate_common.py:54-56`). Reprendre
`seed_pool` tel quel, jamais la liste ; une reconstruction naïve ferait échouer la porte d'identité
du tronc pour une raison qui n'a rien à voir avec le bras.

**Porte d'acceptation du tronc, avant toute lecture causale** : les lignes `full`, `no_swap`,
`frozen` de `results/S8_ab_initio/data/runs.parquet` doivent être identiques colonne à colonne aux
lignes homonymes de `results/S6_synchronized_traces/data/runs.parquet` (jointure sur `seed`,
`delta_e`, `arm`, lecture `float_precision='round_trip'`). Un écart signifie que le `deepcopy`
supplémentaire a perturbé le tronc : arrêt, pas de correction du bras.

---

# P1 — T8.2 : générateur par rotation

## Le défaut, mesuré

`BOUNDARY_SHIFTS = np.linspace(0.1, 4.0, 20)` avec `y = 1[x0 + x1 > b]` : la prior post-rupture est
`P(y=1) = 0.5 − Δe`. Aux sept derniers points de grille elle tombe sous 2.5 %, et à Δe = 0.498 le
prédicteur de classe majoritaire atteint 0.002 — **sous** `e_pre = 0.024`. C'est mécaniquement le
`A/A_rect = −14.12` de `S6_causal_evidence.md` §3.

## Le correctif, et ce qu'il préserve

Le flux pré-dérive **est déjà** la rotation à φ = π/4 : `x0 + x1 > 0` ⟺ `cos(π/4)x0 + sin(π/4)x1 > 0`.
Le correctif ne change donc que l'étiquetage post-dérive :

```python
phi = np.pi / 4 + np.pi * delta_e / (1 - 2 * eta)      # Δe = (1−2η)·|φ−π/4|/π
y_pre  = x[:T, 0] + x[:T, 1] > 0                        # expression canonique, inchangée, bit-à-bit
y_post = np.cos(phi) * x[T:, 0] + np.sin(phi) * x[T:, 1] > 0
```

- **CONTRAINTE 1 respectée verbatim.** `x = rng.normal(size=(N_STEPS, 2))` est inchangé : deux tirages
  normaux par pas, même consommation, même ordre. `s6_runner.demo:291-294` teste déjà cette
  convention ; le test est réutilisé tel quel.
- **Δe exact.** Deux demi-plans passant par l'origine, normales séparées de `|φ − π/4|` : sous un
  gaussien isotrope le taux de désaccord vaut l'angle sur π. Équilibre 50/50 constant, erreur de
  Bayes nulle à η = 0.
- **La phase pré-dérive est bit-identique** à la famille canonique, donc le préchauffage, `e_pre`,
  les swaps de bruit et l'état de l'ARF à τ\* sont **les mêmes**. La comparaison ancien/nouveau est
  appariée à la graine, pas seulement à la distribution.

## CONTRAINTE 1-bis — le nul non dégénéré

Le générateur spécifié a une erreur de Bayes nulle : le nul est asymptotiquement dégénéré, le défaut
même que la contrainte interdit de reproduire. Correctif retenu : bruit d'étiquette déclaré η,
appliqué aux deux phases, `y ^= bernoulli(η)`. Erreur de Bayes = η, stable ; `Δe = (1−2η)·|φ−π/4|/π`
reste exact. Deux bras : η = 0 (comparabilité à la famille canonique) et η = 0.05 (budget de fausses
alarmes contraignant).

**Le tirage du bruit sort d'un Generator séparé**, issu de la même `SeedSequence` que le flux
(`np.random.SeedSequence(safe_seed).spawn(2)`), jamais du `rng` des features : c'est ce qui garde
l'invariant des deux `rng.normal()` intact au bit près. Le verrou triple par worker est repris verbatim.

`e_pre` et sa dispersion sont mesurés et rapportés sur les 20 points × 2 bras η (D5).

## Confrontation à l'ancien, par lecture seule

Aucun artefact R2/R6/R7 n'est régénéré. La confrontation lit
`results/R2_instrumented_blind_spot/`, `results/R6_hydra_factor/`,
`results/R7_clock_mismatch/tables/exp_R7_regime1_miss_curve.csv` et les joint à la nouvelle grille
sur `delta_e` (`float_precision='round_trip'` — la règle du dépôt, 4 des 20 valeurs perdent 1 ULP
sous le parser C par défaut, cf. `exp_R9_compute_mcrit.py:118`). Sortie : une table
ancien/nouveau/écart par point de grille, et le statut de chaque numéral publié qui en dépend.

## Exécution

```bash
PYTHONHASHSEED=0 .../python experiments/S8_generality/s8_rotation.py demo    # identités Δe et PRNG
PYTHONHASHSEED=0 .../python experiments/S8_generality/s8_rotation.py full    # 2 bras η, ~40 min estimés
PYTHONHASHSEED=0 .../python experiments/S8_generality/s8_rotation.py compare # lecture seule R2/R6/R7
```

---

# P1 — T8.5 : domaine de validité haut

**Aucune campagne propre.** T8.5 est une lecture de la campagne T8.2 : le point de bascule est
`inf{Δe : médiane(A/A_rect) < 0}` (D6), calculé sur les trois jeux — canonique (déjà mesuré :
signe négatif à partir de Δe = 0.452), rotation η = 0, rotation η = 0.05.

Prédiction écrite **avant** lecture, comme S9 l'impose pour sa propre région d'échec : sous rotation
les deux règles sont des demi-plans par l'origine, de difficulté identique, donc la bascule doit
DISPARAÎTRE. Si elle survit, elle n'est pas l'artefact de prior et le domaine de validité haut est
un fait de l'adaptation, pas du générateur — résultat plus fort, et qui remonte.

---

# P1 — T8.6 : figure R7 autonome

Chantier réservé par `space_constraints_audit.md` §2.1. L'ancre dans le manuscrit est textuelle,
non numérique : `% Figure 4 merged with Figure 2 above to respect ICDM page limits.` (aujourd'hui
`.tex:327`, `sec:hardware`, **hors** zone exclue).

L'artefact suffit : `results/R7_clock_mismatch/tables/exp_R7_regime1_miss_curve.csv` porte
`config, delta_e, miss_rate` pour les trois configurations d'horloge × 20 magnitudes. R7 n'est pas
ré-exécuté. `s8_figure_r7.py` lit ce CSV et écrit
`results/S8_r7_figure/figures/Fig_R7_clock_mismatch.png`.

Le test `test_manuscript_assets_match_the_pipeline` glob `results/*/figures/<nom>`
(`tests/test_manuscript_integrity.py:69`) : la copie manuscrit trouve donc son jumeau. **Mais la
copie n'est pas déposée en P1** — insérer une figure change la pagination, et
`space_constraints_audit.md` §4 déclare que le desserrage attend l'arbitrage M8 sur la revue cible.
Le bloc `\begin{figure}` prêt à insérer est livré dans `transfer_S8.md`.

---

# Gate P1 — remontée avant P2

Sont remontés : le verdict D1/D2 (inertie ou contribution propre chiffrée), la décomposition à trois
termes contre `\LearnShare = 99.3`, la table ancien/nouveau du générateur, le statut de la bascule
haute, et la liste des numéraux publiés qui bougent. **Si D1 déclare le remplacement inerte**, la
clause Hydra du résumé, la contribution (C1) de `intro_v2.tex` et la revendication de cause racine
unique tombent : remontée immédiate, P2 reconçu avant exécution.

---

# P2 — T8.3 : mécanismes internes, à budget d'évidence égal

## Le défaut à ne pas reproduire

Trois streams viennent de l'exposer : flooding INSECTS 10.57× → 1.270 au budget de portée (89.9 % du
log-ratio est le seuil) ; à λ = 15, ADWIN déployé 45× plus serré et KSWIN 4.5× plus lâche que le
CUSUM ; plancher `[13.9, 18.3]` < plafond 33.5 < `R_CUSUM = 59.3`. Comparer des familles à seuil
nominal commun compare des calibrations.

## Protocole

Deux axes, une seule règle de calibration.

- **Axe mécanisme interne** : `ARFClassifier(drift_detector=D, warning_detector=D)` pour
  `D ∈ {ADWIN, DDM, EDDM, PageHinkley, KSWIN}`. Faisabilité **vérifiée dans le paquet épinglé** :
  `ARFClassifier._drift_detector_input` retourne `int(not y_true == y_pred)`
  (`river/forest/adaptive_random_forest.py:710-713`), soit exactement l'entrée binaire qu'attendent
  `river.drift.binary.DDM` / `EDDM`, et une valeur 0/1 acceptable par ADWIN, PageHinkley et KSWIN.
  `DDM` et `EDDM` vivent sous `river.drift.binary`, **pas** sous `river.drift` : reprendre l'import
  gardé déjà écrit dans le dépôt (`exp_R4_main_table.py:168-171`). `DDM` n'est instancié nulle part
  aujourd'hui. EDDM s'arme ici, contrairement à ProteuS : `e_pre ≈ 0.024 × 4000 ≈ 96` erreurs
  pré-dérive contre un `warm_start` de 30 — c'est ce qui sort EDDM du statut de « famille vaincue ».
- **Axe ensemble** : `SRPClassifier` (déjà utilisé, R4 seul), `LeveragingBaggingClassifier` et
  `ADWINBaggingClassifier` — **jamais instanciés dans ce dépôt**, tous deux présents à
  `river/ensemble/__init__.py` de la version épinglée — et `HoeffdingAdaptiveTreeClassifier`, le
  vrai HAT, jamais exécuté ici (§ Découverte d'ingestion). Le prompt écrit « OzaBagADWIN » : sous
  river 0.23.0 cet objet s'appelle `ADWINBaggingClassifier`, le nom du prompt n'existe pas.
- **Moniteur externe à λ_eq, par pipeline.** Le seuil externe est calibré sur **le flux pré-dérive
  du pipeline considéré**, jamais partagé : chaque pipeline a sa propre volatilité pré-dérive.
  Réemploi de `exp_R5_common.calibrate_lambda` (`:59-85`, bisection `[1, 500]`, repli `target_fa=3`).
  **La taxonomie terminale est en cinq états répartis sur deux fonctions homonymes**, ce que le
  prompt ne dit pas : `s2bis_lambda_eq.calibration_verdict:189-203` retourne un dict et porte
  `OK` / `SATURATED` / `NOT ATTAINABLE` / `NOT ARMED` ; `s2bis_proteus_calibration.calibration_verdict:171-194`
  retourne un tuple et ajoute le cinquième, `NOT BINDING`, au **plancher** de la bisection — le
  budget est atteint à tout seuil admissible et ne contraint rien. S8 rapporte l'union des cinq :
  sur un flux à `e_pre` faible, `NOT BINDING` est le résultat attendu et il est informatif.
  Rien n'est réécrit ; l'identité `lambda_calibrated == lambda_eq(T_warm)` reste celle que S2-bis a
  vérifiée (`tests/test_S2bis_calibration.py:172-183`, et l'identité bit-à-bit propre est
  `test_injected_lambda_driver_reproduces_run_evaluation_bit_for_bit:128-142`).
- **Bras de contrôle à seuil commun** (λ = 50 et λ = 25, les points R2), rapporté à côté, pour rendre
  l'écart visible — comme S2-bis l'a fait pour le flooding. L'α d'égalisation fermé de
  `s2bis_proteus_calibration.family_requirements:311-365` (`α_ADWIN = 4W·exp(−2λ²/W)`,
  `α_KSWIN = 2·exp(−λ²/n_stat)`) est réutilisé tel quel, non re-dérivé.

Les mécanismes internes ne sont **pas** égalisés entre eux : leur identité est précisément la
variable. Le flux est celui de T8.2 (rotation, η = 0.05), qui est le seul à porter un budget de
fausses alarmes contraignant.

## Test de la prédiction S5

Taux de manqué contre `A` (`a_unrefl_peak`) sur un axe commun, un point par (mécanisme, Δe). D7
tranche le collapse. La frontière avec S9 est nette et doit le rester : **S8 fait varier le mécanisme
INTERNE du classifieur adaptatif ; S9 fait varier la famille du moniteur EXTERNE**
(`PROMPT_S9.md` T9.1/T9.4). Aucun des deux ne réimplémente l'instrumentation de l'autre.

# P2 — T8.3-bis : la marginale d'un arbre DANS l'ARF

Ferme les items ouverts 1 et 2 de `transfer_S3.md` §6, déclarés `NOT PRODUCED` faute d'artefact.

- **τ_i par arbre** : déjà produits par P1 (arbitrage 7). Rien à relancer. `s3_competing_risks.py:23-27`
  déclare le manque en toutes lettres — « no committed artifact carries the per-tree `tau_i` of the
  ARF », seules les quatre statistiques d'ordre `tau_swap_q{010,025,050,100}` existent.
- **Le bras apparié est ARF(M=1), pas un HAT.** C'est l'objet sur lequel `τ_HAT` et les ancres
  `4.12×` / `7.99×` sont mesurés (§ Découverte d'ingestion). Substituer le vrai
  `HoeffdingAdaptiveTreeClassifier` ici casserait la comparabilité avec R6 ; il entre en T8.3 comme
  famille distincte, jamais comme remplaçant.
- **Flux d'erreur pré-dérive par arbre** : c'est la mesure manquante. `segment()` n'enregistre que
  l'erreur d'ensemble ; il faut un drapeau `per_tree=True` ajoutant
  `int(tree.predict_one(x) != y)` pour chacun des M membres. Coût : M `predict_one` par pas.
  **Restreint au fenêtrage pré-dérive** (`S6_WARMUP_WINDOW = 1000` pas) et aux deux ancres de S3
  (Δe = 0.3268 et 0.141) — pas à la grille complète, pas au post-dérive.
- Les deux sont calibrés à une fausse alarme par warm-up, le facteur Hydra est re-dérivé à budget
  égal, et la décomposition part-seuil / part-taille-d'ensemble est publiée — ou déclarée
  `NOT PRODUCED` avec la mesure manquante nommée (D8).

---

# P3 — T8.4 : réplication hors River

MOA est déclaré infaisable, avec la mesure qui le prouve (§ Arbitrages 1), et le repli est
`s8_minimal_arf.py` : ARF minimal, NumPy pur, **zéro import River**.

Portée minimale suffisante pour que la réplication soit opposable : M arbres, `max_features='sqrt'`,
poids `Poisson(λ=6)` par membre, un détecteur ADWIN ré-implémenté depuis
Bifet–Gavaldà 2007, remplacement de l'arbre sur alarme, vote pondéré. Instrumentation identique à
celle de S6 : `τ_swap` par arbre, erreur d'ensemble pas à pas, `A_unrefl`.

Le résultat attendu est **qualitatif** : même flux (générateur par rotation), même protocole, le
point aveugle apparaît ou non. La réplication bit-à-bit n'est ni visée ni possible.

**D9 : si le phénomène ne se reproduit pas, c'est un artefact d'implémentation.** Décision de
poursuite remontée à l'utilisateur ; aucune bascule d'article décidée unilatéralement.

---

## Vérification

```bash
cd /home/m53/wt-s8
PY=/home/m53/miniforge3/envs/Trading/bin/python

# porte 1 — suite complète, aucune régression
PYTHONHASHSEED=0 $PY -m pytest tests/ -q                 # attendu : 122 + nouveaux, 0 failed

# porte 2 — oracle gelé INCHANGÉ : S8 n'écrit dans aucun artefact manifesté
sha256sum -c results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt | tail -1
#   attendu : 27 OK / 7 FAILED, strictement les sept déclarés dans authorized_deviations.txt
#   aucune entrée ajoutée à authorized_deviations.txt par ce stream

# porte 3 — identité du tronc (bras V4)
$PY - <<'EOF'
import pandas as pd
a = pd.read_parquet("results/S6_synchronized_traces/data/runs.parquet")
b = pd.read_parquet("results/S8_ab_initio/data/runs.parquet")
k = ["seed", "delta_e", "arm"]
m = a.merge(b, on=k, suffixes=("_s6", "_s8"))
m = m[m.arm.isin(["full", "no_swap", "frozen"])]
cols = [c[:-3] for c in m.columns if c.endswith("_s6")]
bad = [c for c in cols if not m[f"{c}_s6"].equals(m[f"{c}_s8"])]
print("rows", len(m), "| divergent columns:", bad or "none")
EOF
#   attendu : 6000 lignes, aucune colonne divergente

# porte 4 — garde anti-contamination, désormais exécutable
PYTHONHASHSEED=0 $PY -m pytest tests/test_S7_consistency.py -q
ls -d results/R0* results/R1* 2>/dev/null                 # doit être vide

# porte 5 — invariants du générateur et des bras
PYTHONHASHSEED=0 $PY experiments/S6_synchronized_traces/s6_runner.py demo
PYTHONHASHSEED=0 $PY experiments/S8_generality/s8_rotation.py demo
PYTHONHASHSEED=0 $PY -m pytest tests/test_S8_generality.py -q

# porte 6 — arbre propre, aucun artefact étranger stagé
git status --porcelain
```

`tests/test_S8_generality.py` porte quatre invariants, un par logique non triviale :
identité `Δe = (1−2η)·θ/π` sur la grille ; deux `rng.normal()` par pas sous les deux bras η ;
étiquettes pré-dérive du générateur par rotation **identiques** à celles du générateur canonique sur
la même graine ; `swaps_total == 0` et `fork_t_rel == 0` sur les deux bras ab initio.

Commits par chemins explicites, jamais `git add -A`, Conventional Commits, aucun trailer ni
co-auteur. `graphify update .` après la clôture de la phase, jamais pendant.

## Risques et dette résiduelle

- **`\LearnShare = 99.3` est exposé.** Si `E_swap_first` est substantiel, ce numéral — présent au
  résumé, dans `sec:hydra` et en conclusion — est réattribué. C'est le résultat attendu du bras V4,
  pas un effet de bord, mais il touche la zone **exclue** par `CLAUDE.md` : la charge va dans
  `framework_v2.tex`, jamais dans le `.tex` inline.
- **Le générateur par rotation crée une seconde famille de flux.** Tant que R2/R6/R7 restent publiés
  sur la famille canonique, l'article porte deux générateurs. Statuer à l'assemblage v65 lequel est
  celui de record ; S8 livre la mesure, pas l'arbitrage éditorial.
- **La chaîne de dépendances du `.tex` n'est pas touchée par S8**, mais `stream-s11a` travaille en
  parallèle sur la charpente v65. Toute charge S8 reste en `transfer_S8.md` jusqu'à l'assemblage.
- **`ARCHIVED_MAIN_TEX` est vide** (`tests/test_manuscript_integrity.py:52`) : toute v65 déposée dans
  `docs/manuscript/` fera échouer la suite tant qu'elle n'y est pas déclarée. Hors périmètre S8, signalé.
- **`run_tests.sh` et les neuf `run_experiment_R*.sh` appellent `python` nu**, non l'interpréteur
  épinglé. Déjà signalé par S-SYNC, toujours ouvert, hors périmètre S8.
- **Estimations de temps non mesurées.** ~25 min (P1 bras), ~40 min (P1 rotation), P2 non borné avant
  le smoke. Chaque campagne tourne d'abord en `smoke` et le coût réel est mesuré avant la grille pleine.
