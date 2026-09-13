# Stream S9 — P0 (gate R(KSWIN) committé) puis P1 (recalcul hors ligne T9.1)

## Contexte

Le manuscrit de référence affirme en `articleA_blindspot_v64_camera_ready.tex:500` que KSWIN est
« structurally immune to transient signal erasure » et atteint F1 = 1.00 sur ProteuS. Le reviewer #3
refuse la portée : tout moniteur fenêtré échoue si le transitoire est court devant sa fenêtre, et un
balayage en α seul ne fonde pas une immunité structurelle. Trois faits mesurés rendent la
revendication indéfendable en l'état :

- `s2bis_proteus_gate.json :: family_requirements_at_lambda_eq` — à λ = 15, point d'opération de la
  Table I, KSWIN est déployé à un α **4.52× plus permissif** que le CUSUM qu'il surpasse. Les
  colonnes de la Table I comparent des calibrations, pas des familles.
- `transfer_S2bis.md §2.7` — à seuil égalisé (λ = 5), PHT+ARF(c=1) rend 1080/1080, F1 = 1.0000,
  ADD = 6.05 contre 14 pour KSWIN. L'avantage KSWIN ne survit pas à l'égalisation.
- V7 de S6 — seul CUSUM est instrumenté. PHT, ADWIN et KSWIN n'ont aucune trajectoire synchronisée :
  l'immunité revendiquée n'est adossée à aucune mesure.

L'issue exigée n'est pas une correction mais une **falsification**. `def:blindspot` donne le
prédicat exact — `A < R(D, ε, α)` — et `eq:Rkswin` donne R pour KSWIN. La région d'échec de KSWIN
est donc calculable **avant** toute mesure. Ce plan l'écrit, la commite, et n'exécute ensuite que du
recalcul hors ligne sur des traces déjà produites.

**Arbitrages opérateur déjà rendus** : traces S6 par lien symbolique (pas de régénération) ; T9.3 =
démonstration analytique **plus** HDDDM minimal NumPy sur le générateur rotation η = 0.05 ; arrêt
contractuel en fin de P1.

## Correction préalable au prompt S9

`PROMPT_S9.md:56` énonce que le prix de la fausse alarme entre « SOUS une racine de W » pour KSWIN.
`framework_v2.tex:363-369` réfute explicitement cette formulation : le terme α de `eq:Rkswin` ne
porte **aucun** W, il est fixé par `n_stat` seul. La région d'échec se dérive donc de `n_stat`, pas
de W. Le plan suit le `.tex`, qui est le document de référence.

Second écart, procédural : `PROMPT_S9.md:18` impose `project_knowledge_search` et §« Format » impose
des DIFF SEARCH/REPLACE à 9 tildes. Ce sont des conventions Claude.ai Projects. Ici les mutations
vont sur disque via `Edit`/`Write` (invariant (b) du CLAUDE.md). Aucune autre divergence.

---

## P0 — Le gate, écrit et committé avant toute exécution

**Livrable unique : `docs/prompts/s9-decision-rules.md`** (format maison : en-tête de gel, ligne
`Stream branch \`stream-s9\`, parent \`346fe89\``, puis une section par règle, puis
`## Terminal states`). Modèle : `docs/prompts/s8-decision-rules.md`.

### Partie A — Dérivation analytique de R(KSWIN, ε, α)

**A.1 Désambiguïsation de W.** Quatre grandeurs distinctes portent aujourd'hui le même symbole et la
confusion est active dans le texte publié :

| grandeur | valeur | où |
|---|---|---|
| `W_transient := τ_erase − τ*`, transitoire exploitable | 57.4 | `def:times`, terme ε de `eq:Rkswin` |
| `W_win`, fenêtre glissante KSWIN | 100 | `exp_R4_main_table.py:167` |
| `W_buf`, tampon de lissage de l'erreur | 30 | `exp_R4_main_table.py:147` |
| `n_stat`, fenêtre de statistique | 30 | idem |

Le « structural lag W/2 = 15 » cité en `.tex:500` est `W_buf/2`, pas `W_transient/2`. La dérivation
fixe la nomenclature une fois.

**A.2 Dérivation.** river 0.23.0 (`river/drift/kswin.py:137-148`) tire `n_stat` points uniformément
parmi les `W_win − n_stat` premiers de la fenêtre et les compare aux `n_stat` plus récents par
`ks_2samp`. Test à deux échantillons, `n = m = n_stat`, taille effective `n_eff = nm/(n+m) =
n_stat/2`. Distance critique asymptotique `D_α = sqrt(−ln(α/2) / (2 n_eff)) = sqrt(ln(2/α)/n_stat)`.
Conversion en unités d'erreurs excédentaires sur la fenêtre récente : `R_fa = n_stat · D_α =
sqrt(n_stat ln(2/α))`, puis addition de la marge ε partagée → `eq:Rkswin`. Équivalence numérique à
vérifier contre `s2bis_proteus_calibration.py:344` et `s2_arl0.py:387` (identité, pas
réimplémentation).

**A.3 Deux termes que `eq:Rkswin` omet, tous deux présents dans river et mesurables sans simulation.**

1. *Garde α-libre.* `kswin.py:147` exige `p_value <= alpha` **et** `st > 0.1`. Plancher dur de
   `0.1 · n_stat` erreurs excédentaires, indépendant de α (3.0 à `n_stat = 30`).
2. *Réseau discret.* `method="auto"` avec `n·m = 900` déclenche la loi **exacte**, portée par le
   réseau `k/n_stat`. Mesuré (scipy 1.16.2, `n_stat = 30`) :

   | α | k* exact | R_fa exact | R_fa asymptotique | écart |
   |---|---|---|---|---|
   | 0.05 | 11 | 11.00 | 10.52 | +4.6 % |
   | 0.01 | 13 | 13.00 | 12.61 | +3.1 % |
   | 0.005 | 14 | 14.00 | 13.41 | +4.4 % |
   | 0.001 | 15 | 15.00 | 15.10 | −0.7 % |

   `eq:Rkswin` n'est donc **pas** une borne uniforme : anti-conservatrice sur trois points sur
   quatre, conservatrice sur le quatrième. Constat pré-enregistré, pas post-hoc.
3. *Lacune déclarée, non réparée.* L'entrée de KSWIN est une moyenne mobile à 30 pas d'un flux
   binaire : ex æquo massifs et recouvrement 29/30 entre tirages consécutifs. La p-value exacte de
   `ks_2samp` n'est pas valide sous ex æquo. Déclaré comme lacune, au même titre que l'absence de
   statistique scalaire d'ADWIN.

### Partie B — Définition de la région d'échec F(KSWIN)

Prédicat : `def:blindspot`, `A < R(KSWIN, ε, α)`, avec `A = Σ_{τ*+1}^{τ_erase} (ē_t − p₀ − δ_P)⁺`
(`def:budget`), forme rectangulaire `A = (Δe − δ_P) · W_transient`. Trois branches, écrites avec
leur frontière analytique et leur prédiction quantitative sur la grille :

- **B1 — branche budget** (capturée par `eq:Rkswin`) :
  `(Δe − δ_P) · W_transient < sqrt(n_stat ln(2/α)) + sqrt(W_transient/2 · ln(1/ε))`.
  Croissante en `n_stat` et en `ln(1/α)`, libre de `W_win`. Table de vérité pré-écrite sur la grille
  Bernoulli entière (20 magnitudes) × `n_stat` × α.
- **B2 — branche dilution** (NON capturée par `eq:Rkswin`, donc test de falsification de la formule
  elle-même) : si `W_transient < n_stat`, la fenêtre récente ne contient jamais que du post-dérive ;
  la distance atteignable est plafonnée à `D_max ≤ (W_transient/n_stat) · Δe`. Échec prédit **alors
  même que** `A ≥ R_KSWIN`. C'est la mise en nombres de l'objection du reviewer #3.
- **B3 — branche contamination du réservoir** : le réservoir est tiré des `W_win − n_stat = 70`
  premières entrées. Passé 70 pas de transitoire, la référence est elle-même post-dérive et D
  s'effondre. Borne supérieure d'horizon : KSWIN doit tirer dans les ~`W_win` pas suivant τ*. C'est
  la condition que `rem:agnostic` (`.tex:306`) porte déjà en clause subordonnée — « while its
  reference window holds pre-drift data » — sans jamais l'instancier.

**B4 — conséquence pré-enregistrée sur le balayage α du manuscrit.** Sur ProteuS le label est
constant 0 avant `T_DRIFT` et constant 1 après (`exp_R4_main_table.py:101-107` : `regime =
1[f_t > 0.5]` avec `f_t` monotone en `t` et indépendant de X). Donc `Δe = 1.0`, `D = 1.0` en
`W_buf` pas, et les quatre α de `{0.001, 0.005, 0.01, 0.05}` sont franchis avec une marge d'un ordre
de grandeur. Prédiction : le balayage est invariant **parce qu'il n'approche jamais R_KSWIN**, à un
point d'opération environ 2× au-dessus de la plus grande magnitude de la grille Bernoulli
(`Δe_max = 0.498`). La « robustesse hyper-paramétrique » de `.tex:500` est vide, pas fausse.

### Partie C — Règles D0..D10 et états terminaux

Format maison : une section par règle, table `| condition | verdict |`, les deux branches nommées en
capitales, seuils numériques déclarés **avant** lecture.

| règle | objet | branches |
|---|---|---|
| D0 | déclaration de lecture préalable (16.34 / 18.97 / 45× / 4.52× / 6.05 / (8,15] / 22.68 / 33.5115) et règle de vérification qu'elle impose | REPRODUCED / UNREPRODUCED |
| D1 | exactitude de `eq:Rkswin` contre river+scipy (réseau exact, garde 0.1) | CONFIRMED / ANTI-CONSERVATIVE / CONSERVATIVE |
| D2 | branche budget B1, prédiction contre mesure | AGREED / REFUTED |
| D3 | branche dilution B2 — existe-t-il une région de manqués que `eq:Rkswin` ne prédit pas ? | PREDICTED-AND-OBSERVED / **PREDICTED-AND-ABSENT → R(KSWIN) faux, remontée S1/S2** |
| D4 | branche contamination B3 | OBSERVED / ABSENT |
| D5 | à α égalisé, KSWIN garde-t-il son avantage ? | KEPT / LOST |
| D6 | nul dégénéré de ProteuS, établi sur le générateur | DEGENERATE / NOT DEGENERATE |
| D7 | même grille sur flux à nul non dégénéré (rotation η = 0.05) | HOLDS / FAILS |
| D8 | corrélation dégradation input-space / `τ_erase` | ABSENT (attendu) / **PRESENT → recadrage boucle fermée FAUX, remontée immédiate** |
| D9 | EDDM : hors table, ou dans la table avec colonne « armé / non armé » | WITHDRAWN / ARMED-COLUMN |
| D10 | ce qui remplace les revendications d'immunité dans le texte | domaine de validité mesuré |

`## Terminal states` : `NOT PRODUCED`, `UNREPRODUCED`, `REFUTED`, `DEGENERATE`, `BLIND`, `LOST`
sont des états terminaux publiables. Aucun n'est absorbé par un re-run à réglages différents ni par
une tolérance élargie.

### Partie D — Liste des fichiers à inspecter au tour suivant

Exigée par `PROMPT_S9.md:166`. Section finale du document.

**Commit P0** (seul commit de la phase) : `docs(S9): commit decision rules D0-D10 and the R(KSWIN)
failure region before any measurement`. Aucun trailer, aucun co-auteur.

---

## P1 — T9.1, instrumentation hors ligne, aucune simulation neuve

### P1.0 — Accès aux traces et hygiène git (bloquant)

`results/S6_synchronized_traces/data/traces.parquet/` est absent de ce worktree. Source vérifiée :
`/home/m53/TheBlindSpotParadox-Experiments/…/data/traces.parquet`, 20 partitions, 402 Mo.

1. `ln -s` vers cette source.
2. **Piège vérifié** : `.gitignore:24` porte un slash final, qui ne matche que les répertoires. Un
   lien symbolique n'est pas un répertoire pour git — `git check-ignore` confirme que le lien
   **ne serait pas ignoré** et apparaîtrait comme un chemin absolu `/home/m53/…` stageable, ce que
   le CLAUDE.md proscrit. Correctif : retirer le slash final de la ligne 24 (diff d'un caractère),
   puis re-vérifier par `git check-ignore -v`.
3. Dette déclarée dans le rapport S9 et dans `docs/ENVIRONMENT.md` : les résultats hors ligne de S9
   ne sont pas reproductibles depuis un clone tant que le corpus n'est pas régénéré.

### P1.1 — Constantes SSOT

`window_size`, `stat_size`, `KSWIN_LAG` et le tampon de 30 sont aujourd'hui des littéraux locaux
dans les deux scripts R4. Toute nouvelle grille S9 doit passer par des noms préfixés dans
`config/experiment_ssot.py` — `S9_KSWIN_WINDOW`, `S9_KSWIN_STAT`, `S9_KSWIN_LAG`, `S9_KSWIN_BUFFER`,
`S9_KSWIN_ALPHA_GRID`, `S9_NSTAT_GRID`, `S9_OFFLINE_LAMBDAS` — sinon
`test_S7_consistency.py::test_ssot_registry_and_no_value_drift` échoue. Motif déjà établi par le
bloc `S8_*`.

### P1.2 — Le passage hors ligne

**Nouveau fichier unique : `experiments/S9_detector_coverage/s9_offline_detectors.py`.**
Rejoue PHT, ADWIN et KSWIN sur la colonne `err` des traces committées. Réutilise sans réécrire :

- `experiments/S6_synchronized_traces/s6_detectors.py` — `PHT`, `ADWINDetector`, `KSWINDetector`,
  `StrictCUSUM`. L'interface `.update/.drift_detected/.statistic()/.threshold/.alarm_sense` existe :
  ne pas la toucher. `window_size`/`stat_size` passent déjà par `**kwargs`.
- `s6_recompute_cusum_delta001.py:128-149` — motif de lecture partition par partition, projection de
  colonnes `["arm","seed","t_rel","err"]` et filtre poussé `t_rel >= -WARMUP & t_rel < T_HORIZON`.
  C'est le gabarit exact, il est déjà écrit.
- `gates/_gate_common.py:28-33` — verrou PRNG triple, verbatim.

**Point de déterminisme (invariant (c))** : `drift.KSWIN` est **stochastique** — son réservoir est
tiré par `random.Random(self.seed)`. Chaque cellule `(arm, seed, Δe)` reçoit une graine dérivée par
`SeedSequence`, jamais l'état global. Deux passes doivent rendre des sha256 identiques.

**Deux bras d'entrée, déclarés, jamais fusionnés** : (i) `err` brut ; (ii) moyenne mobile à
`S9_KSWIN_BUFFER` pas, convention R4 (`run_concept_drift_kswin`). Les trois particularités imposées
par `PROMPT_S9.md:36-44` sont reportées telles quelles : `statistic()` non rescalée, sens d'alarme
KSWIN inversé (p-value contre α, **aucun** recodage monotone en échelle d'évidence), ADWIN sans
quantité de test scalaire (`threshold = None`, légende obligatoire sur toute figure comparative).
Familles CUSUM sur `ssot.CUSUM_DELTA_P`, autres sur `ssot.DELTA_P` — arbitrage A1, garde active
dans `test_S7_consistency.py::test_strict_cusum_runs_at_the_cusum_tolerance`.

**Sorties** : `results/S9_detector_coverage/data/s9_offline_traces.parquet` (contrat Parquet
déterministe de `s6_writer`), `tables/s9_offline_summary.json`, `tables/s9_requirement_lattice.json`
(le réseau exact de la partie A.3, calculé sans simulation).

### P1.3 — Garde exécutable

`tests/test_S9_coverage.py`, minimal : identité du réseau exact contre `eq:Rkswin`, invariance du
sens d'alarme KSWIN, rejeu bit-identique d'une cellule. Une seule vérification runnable par logique
non triviale, pas de suite par fonction.

### Arrêt contractuel

Fin de P1. Présentation des règles committées et des trajectoires hors ligne. **Aucune campagne
neuve** (T9.2 grille complète, T9.3 HDDDM, T9.5 flux non dégénéré) avant retour opérateur.

---

## Vérification

```bash
git check-ignore -v results/S6_synchronized_traces/data/traces.parquet   # doit matcher après P1.0
PYTHONHASHSEED=0 ./run_tests.sh                                          # suite entière verte
sha256sum -c results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt    # reste 27 OK / 7 FAILED
```

Déterminisme du passage hors ligne : deux exécutions consécutives, `sha256sum` identiques sur
`s9_offline_traces.parquet` et les deux JSON. Un écart est un défaut, pas une mise à jour.

Non-régression ciblée : `test_S7_consistency.py::test_ssot_registry_and_no_value_drift` après ajout
des `S9_*`, `::test_strict_cusum_runs_at_the_cusum_tolerance`, `::test_no_foreign_experiment_directory_under_results`
(`results/S9_detector_coverage/` est hors de la plage `R0[0-9]_*` / `R1[0-8]_*`, vérifié).

## Fichiers touchés

| fichier | nature |
|---|---|
| `docs/prompts/s9-decision-rules.md` | nouveau — le gate, seul livrable de P0 |
| `.gitignore` | 1 caractère — slash final ligne 24 |
| `config/experiment_ssot.py` | additif — bloc `S9_*` |
| `experiments/S9_detector_coverage/s9_offline_detectors.py` | nouveau — passage hors ligne |
| `tests/test_S9_coverage.py` | nouveau — garde minimale |
| `results/S9_detector_coverage/{data,tables}/` | nouveaux artefacts, hors manifeste gelé |

Aucun fichier de `docs/manuscript/` n'est touché dans ces deux phases. Les quatre sous-sections
exclues par le CLAUDE.md (`sec:race`, `sec:hydra`, `sec:starvation`, `sec:decoupling`) ne sont pas
approchées ; les corrections de `rem:agnostic` (`.tex:306`, à l'intérieur de `sec:starvation`)
iront dans `framework_v2.tex` lors d'une phase ultérieure, pas ici.

## Risques déclarés

1. Lien symbolique vers un artefact non versionné hors worktree — reproductibilité depuis un clone
   suspendue jusqu'à régénération. Déclaré, non masqué.
2. `ks_2samp` sous ex æquo : p-value exacte non valide sur un flux binaire lissé. Lacune documentée,
   non réparée dans S9.
3. `test_manuscript_integrity.py::test_source_reservations_have_not_expired` échoue par date. À la
   date du jour (2026-09-13) une réservation peut arriver à échéance et faire rougir la suite pour
   une raison étrangère à S9 ; à distinguer explicitement d'une régression S9.
