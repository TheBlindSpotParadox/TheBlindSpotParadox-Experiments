# S7-ter — Transfert d'état vers l'orchestrateur

Flux exécuté dans `../worktree-S7ter`, branche `stream-s7-ter`, créée depuis le SHA épinglé
`638ce543edd58c14cc17bc2bf4c91aa32c7e9c07` — le même `HEAD = 638ce54` que `docs/plans/PLAN_S2.md:87`
enregistre pour `stream-s2`. Aucune écriture, aucun test dans le checkout principal du dépôt : le
flux entier s'exécute dans son worktree dédié, comme le plan l'impose.

Plan exécuté : `docs/plans/PLAN_S7-ter.md`. Spécification : `docs/prompts/PROMPT_S7-ter.md`.
Manuscrit de référence lu depuis `docs/manuscript/CURRENT`, jamais depuis le PDF.

---

## 1. Ce que l'orchestrateur doit appliquer lui-même

Deux catégories, et elles sont les seules.

### 1a. Les patchs du manuscrit de référence — produits ici, NON appliqués

Le plan interdit à S7-ter d'écrire dans
`docs/manuscript/articleA_blindspot_v64_camera_ready.tex` : S2 patche le même document dans la même
vague, et les deux passes doivent être sérialisées par l'orchestrateur. Les charges utiles sont en
§6, au format SEARCH/REPLACE, ancres re-grepées sur le fichier vivant.

S7-ter n'écrit pas non plus le bloc de macros du préambule : il appartient au jeu de charges de S2.

### 1b. Une correction d'une ligne dans `config/experiment_ssot.py`, escaladée

`config/experiment_ssot.py:108` porte le commentaire
`R3_C_INT = C_INT  # warning_detector left at river default (see README §5)`.
Il est **faux** depuis B-1. Il n'est pas corrigé ici : S7-ter n'écrit dans ce fichier qu'en ajout, en
fin de fichier, sous une bannière `# S7-ter —`, parce que S2 y ajoute aussi dans la même vague et
qu'une édition en milieu de fichier fusionne silencieusement de travers — `tests/test_S7_consistency.py`
compare des valeurs, il ne voit pas un commentaire rebasé.

Charge à appliquer lors de la passe sérialisée :

`config/experiment_ssot.py`

~~~~~~~~~
<<<<<<< SEARCH
R3_C_INT = C_INT                               # warning_detector left at river default (see README §5)
=======
R3_C_INT = C_INT                               # warning_detector unified onto the drift detector by
                                               # S7-ter/LOT B (R3_C_WARN / R3_WARN_DELTA, banner at
                                               # end of file); README §5 rewritten accordingly
>>>>>>> REPLACE
~~~~~~~~~

---

## 2. Décisions de politique de dépôt — escaladées, non tranchées

**`results/audit_S7/_baseline/sha256_pre.txt`.** Vérifié : **aucun consommateur**. Une recherche sur
tout le dépôt en `.py`, `.sh`, `.md`, `.yml`, `.toml`, `.cfg` ne trouve que des références en prose —
sa propre bannière de dépréciation, une ligne narrative de `reconciliation_report.md`, et la
spécification et le plan S7-ter eux-mêmes. Il n'existe ni configuration CI ni Makefile dans le dépôt.
État vivant conforme à sa bannière : 6 OK, 3 FAILED, 2 chemins qui ne résolvent plus.

Supprimer le fichier ou le conserver comme lignage est un arbitrage de politique de dépôt. S7-ter
vérifie et consigne (`docs/ENVIRONMENT.md`, section « Bit-freeze coverage ») ; il ne tranche pas.

---

## 3. Faits établis, opposables

Chacun est mesuré sur le build épinglé, jamais recopié d'un rapport.

1. **Le `warning_detector` par défaut de River déplace deux paramètres, pas un.** River 0.23.0
   résout un `warning_detector` non fixé de `ARFClassifier` en `ADWIN(delta=0.01, clock=32)`, un
   `drift_detector` non fixé en `ADWIN(delta=0.001, clock=32)`, et un `drift.ADWIN()` nu en
   `delta=0.002, clock=32` — trois valeurs distinctes. `config_matrix.md` §3 n'en enregistrait
   qu'une (« river default 0.002 ») et `README.md` §5 omettait le delta du défaut d'avertissement.
   Les deux sont corrigés.

2. **La Table I est invariante sous l'unification, à un compte près.** Les trois effondrements
   `F1 = 0.00` (PHT+ARF c=1, EDDM+ARF c=1, SRP+PHT c=1) restent exactement nuls, ADD reste NaN, et la
   résolution KSWIN reste `F1 = 1.00, ADD = 14 [0]` à variance nulle aux deux horloges. Le rendu
   `exp_R4_table_KSWIN_alpha_sweep.tex` est **bit-identique** entre les deux bras. Le seul numéral du
   manuscrit touché est `ADWIN+ARF c=1` : `1063/1080 → 1070/1080`.

3. **L'IC de la Table I rééchantillonnait le run, pas la graine.** `np.random.choice` sur les 360
   lignes d'une cellule, tiré de l'état NumPy **global**, pendant que la légende affirmait la graine
   comme unité d'indépendance statistique. Les deux énoncés sont incompatibles et la version courue
   sous-estimait la largeur. Corrigé en rééchantillonnage apparié de l'indice de graine sur un
   `default_rng` injecté localement, schéma repris verbatim de `exp_R6_hydra_survival.py:105-111`.

4. **Le mécanisme d'avertissement est simultanément déterminant et inerte.** Déterminant : il
   commande le moment où un arbre de fond commence à apprendre, donc ce qu'un remplaçant a appris
   quand il est installé, donc la durée du transitoire. Inerte dès que les deux détecteurs sont
   épinglés à l'identique : `experiments/S6_synchronized_traces/gates/g2_api_map.json` mesure
   `warning_equals_drift_elementwise: true`, `max_simultaneous_background_trees: 0`,
   `replacements_with_a_warmed_background_tree: 0`, et 47/47 remplacements à `c = 1` comme 36/36 à
   `c = 32` installent un arbre créé au même pas. Les deux faits coexistent et le texte les porte
   tous les deux.

5. **La famille de tests multiples compte 10 membres, pas ~14.** Recensement mesuré : 6 contrastes de
   niveau graine dans `exp_R4_seed_level_tests.csv` (le plan en annonçait 7), 1 dans le sweep α, 3 sur
   les variantes INSECTS de `table2_values.csv` ; les 3 lignes BAF ne portent aucun test. Huit des dix
   p-values sont exactement au plancher de résolution `2^-29`. Holm à α = 0.05 les conserve toutes
   les huit — et **ne conserve pas** INSECTS *abrupt_balanced* (p = 0.043 contre α/2 = 0.025). La
   correction retire une affirmation que le manuscrit avait déjà refusé de faire.

6. **`p = 1.86e-9` n'est pas une estimation.** C'est `2 · 2^-30 = 2^-29 = 1.8626451e-9`, le plancher
   du test des signes bilatéral à `n_eff = 30`, atteint dès que la séparation est complète et
   indépendant de son ampleur. Vérifié numériquement contre `binomtest(30, 30, 0.5)`. Rapporté comme
   `p ≤ 2^-29` et systématiquement apparié à une taille d'effet.

7. **Le Digital Omnibus on AI n'est plus une proposition.** Adopté le 08/07/2026, publié au JO du
   24/07/2026 (Règlement (UE) 2026/1744), en vigueur depuis le 27/07/2026. Il **n'amende pas** le
   libellé de l'Art. 15 — la citation la plus forte du registre en sort renforcée — mais amende
   l'Art. 72(3), remplaçant l'acte d'exécution échu au 02/02/2026 par des lignes directrices assorties
   d'un modèle, à échéance du 02/09/2027.

8. **L'extension du gel à R2, R3 et R7 était déjà acquittée.** `docs/ENVIRONMENT.md:66-73` enregistre
   la ré-exécution de chacun de ces étages avec un verdict de hachage « identique ». Les vraies
   lacunes sont ailleurs et sont déclarées : **R5** (15 des 34 hachages gelés, jamais revérifiés
   empiriquement) et **S6** (zéro entrée au manifeste).

---

## 4. Ce qui a été écrit dans ce dépôt

| fichier | nature |
|---|---|
| `docs/manuscript/sections/protocol_v2.tex` | **neuf** — livrable LOT A, section orpheline jusqu'à l'assemblage v65 |
| `tests/test_R1_race_condition.py`, `test_R2_starvation.py`, `test_R3_crossover.py`, `test_R4_table1.py`, `test_R5_table2.py` | **neufs** — les cinq tests manquants de `regeneration_spec.md` §G3 |
| `tests/test_S7_consistency.py` | garde AST `float_precision='round_trip'` sur toute ingestion CSV |
| `tests/test_R9_mcrit.py` | durcissement d'un `read_csv` nu |
| `config/experiment_ssot.py` | **ajout en fin de fichier uniquement**, bannière `S7-ter` |
| `experiments/R3_regime_crossover/exp_R3_regime_crossover.py` | `warning_detector` unifié |
| `experiments/R4_proteus_evaluation/exp_R4_main_table.py` | `warning_detector` unifié + bootstrap apparié graine |
| `experiments/R4_proteus_evaluation/exp_R4_kswin_sweep.py` | idem |
| `experiments/R5_real_world_evaluation/exp_R5_compute_delta_e.py`, `exp_R5_config.py`, `run_experiment_R5.sh` | oracle Δe à classifieur gelé |
| `README.md` §5 | réécrite : l'hétérogénéité documentée n'existe plus |
| `results/audit_S7/config_matrix.md` | §3 et §7 corrigées, conflation des défauts River nommée |
| `results/audit_S7/regeneration_spec.md` | §G3 marquée implémentée, quatre valeurs de spécification corrigées contre mesure |
| `results/audit_S7/reconciliation_report.md` | claim de gel périmé corrigé en place |
| `results/audit_S7/_baseline/authorized_deviations.txt` | entrées S7-ter |
| `docs/ENVIRONMENT.md` | couverture du gel, lacunes R5 et S6, vérification de `sha256_pre.txt` |
| `docs/editorial/source_verification.md` | session de re-vérification datée, `expires_on` repoussé |
| `results/audit_S7/s7ter_arms/` | **neuf** — archive des bras U0/U1, avec son `README.md` |

---

## 5. Vérification — chaque porte est une commande, pas un jugement

| porte | commande | résultat |
|---|---|---|
| suite | `PYTHONHASHSEED=0 python -m pytest tests/ -q` | 25 avant la phase D → **62** après, zéro échec |
| gel | `sha256sum -c results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt` | **26 OK / 8 FAILED**, exactement les huit déclarées (29/5 avant ce flux) |
| A | `pytest tests/test_manuscript_integrity.py -q` avec `protocol_v2.tex` présent | 6/6 : aucun environnement non déclaré, aucun `\ref` pendant, aucune `\cite` non résolue |
| A (compilation) | `tectonic` sur un harnais reprenant le préambule IEEEtran du manuscrit | compile ; seuls des avertissements `Underfull \hbox` |
| D | les cinq tests neufs contre les artefacts pré-B | 33 tests verts avant la phase B |
| D-4 | garde flottante contre un `read_csv` nu introduit délibérément | échoue en nommant le site, repasse après retrait |
| B | `test_R4_table1.py`, `test_R3_crossover.py` comme instruments | ont mesuré : 1 échec nommé pour R4, 2 pour R3 ; ré-épinglés ensuite |
| B | `test_manuscript_assets_match_the_pipeline` | vert après recopie de la Table I **et** de la Figure 3 depuis le pipeline |
| C | `delta_e.parquet` | **OK**, octet pour octet — zéro déviation autorisée consommée |
| C | `delta_e_oracle.parquet` | 6 lignes, vecteurs de fenêtres identiques à l'adaptatif ligne à ligne |
| E | `test_source_reservations_have_not_expired` | vert avec la nouvelle date de re-vérification |

Coûts mesurés : R4 3 823 s puis 3 803 s, R3 587 s puis 676 s, étage Δe de R5 393 s.

## 6. Charges SEARCH/REPLACE pour le manuscrit de référence

Ancres re-grepées sur le fichier vivant le 2026-09-12, jamais citées depuis un rapport. À appliquer
par l'orchestrateur dans sa passe sérialisée, jamais par ce flux.

### 6a. R4 — un seul numéral, réglé

`docs/manuscript/articleA_blindspot_v64_camera_ready.tex`

~~~~~~~~~
<<<<<<< SEARCH
the adaptive ARF detects marginally \emph{more} than the static RF ($1063/1080$ vs $959/1080$; all $30$ seeds favouring the ARF, $p \approx 2 \times 10^{-9}$)
=======
the adaptive ARF detects marginally \emph{more} than the static RF ($1070/1080$ vs $959/1080$; all $30$ seeds favouring the ARF, $p \approx 2 \times 10^{-9}$)
>>>>>>> REPLACE
~~~~~~~~~

### 6b. BAF — le contrôle négatif, prononcé sur la mesure

~~~~~~~~~
<<<<<<< SEARCH
The three BAF variants sit at $\Delta e \approx 0$ (Weak Signal zone), where the blind spot is dormant and the HT/ARF F1 ratio is indistinguishable from unity.
=======
The three BAF variants sit at $\Delta e \approx 0$ (Weak Signal zone), where the blind spot is dormant and the HT/ARF F1 ratio is indistinguishable from unity. This reading is not an artefact of the estimator being measured on an adapting model: a reference tree forked at the end of the warm-up and never retrained reports the same $\Delta e \approx 0$ at the same canonical positions ($|\Delta e| < 0.001$, every interval covering zero). A frozen model cannot absorb a change, so a jump it does not see is not one adaptation has erased. Both trees in fact sit at the majority-class error rate, which on these streams is the fraud rate itself: no Hoeffding-tree pipeline acquires discriminative signal on BAF, so no error transient exists for any monitor to miss. BAF is therefore an explicit \emph{negative control} for the phenomenon, and the demonstration rests on the two high-magnitude INSECTS variants.
>>>>>>> REPLACE
~~~~~~~~~

### 6c. R3 — bras U1 retenu, six charges

Arbitrage clos par l'opérateur : **U1 (unifié) est le résultat principal du dépôt**, U0 reste archivé
en bras de contrôle dans `results/audit_S7/s7ter_arms/u0_frozen/`. Les six charges ci-dessous
restatent le manuscrit sur les valeurs U1. Aucune n'entre dans les quatre sous-sections exclues par
`CLAUDE.md` : elles visent `sec:crossover` (L468) et `sec:solution_rf` (L501), vérifié.

**Légende de Figure 3 — la bande de manqués.**

~~~~~~~~~
<<<<<<< SEARCH
from $1\%$ at its first grid point $\Delta e{=}0.26$ to $100\%$ at $\Delta e{=}0.50$
=======
from $4\%$ at its first grid point $\Delta e{=}0.26$ to $80\%$ at $\Delta e{=}0.50$
>>>>>>> REPLACE
~~~~~~~~~

**Zone de signal faible — l'ARF n'y filtre plus le bruit, il n'alarme plus du tout.**

~~~~~~~~~
<<<<<<< SEARCH
The ARF (red curve) suppresses this noise via Bagging variance reduction, avoiding early alarms.
=======
The ARF (red curve) suppresses this noise via Bagging variance reduction; below $\Delta e \approx 0.12$ it suppresses the post-drift signal with it, missing $69\%$ of drifts at $\Delta e{=}0.09$ and all of them below that.
>>>>>>> REPLACE
~~~~~~~~~

**Borne basse de la zone sûre.** Sous U1 l'avantage de l'ARF sur le HT n'apparaît qu'à partir de
$\Delta e \approx 0.12$ (manqués $24\%$ contre $59\%$), et a disparu à $0.09$ (manqués $69\%$ contre
$71\%$).

~~~~~~~~~
<<<<<<< SEARCH
\textbf{2. The Safe Zone ($\Delta e \in[0.09, 0.25]$):}
=======
\textbf{2. The Safe Zone ($\Delta e \in[0.12, 0.25]$):}
>>>>>>> REPLACE
~~~~~~~~~

**Régime du blind spot — le taux de manqués au sommet de la bande.**

~~~~~~~~~
<<<<<<< SEARCH
driving Missed Detections to 100\%
=======
driving Missed Detections to $80\%$
>>>>>>> REPLACE
~~~~~~~~~

**Coût prédictif de la fidélité de monitoring.**

~~~~~~~~~
<<<<<<< SEARCH
falls below ARF by up to $23.4$ percentage points at $\Delta e = 0.50$ (RF $\approx 0.750$ vs ARF $\approx 0.984$)
=======
falls below ARF by up to $23.0$ percentage points at $\Delta e = 0.50$ (RF $\approx 0.750$ vs ARF $\approx 0.980$)
>>>>>>> REPLACE
~~~~~~~~~

**Reprise du même écart dans le fix (S2) de `sec:discussion`.** Cette ligne est hors des quatre
sous-sections exclues (elle est en L522, dans `sec:discussion`, pas dans `sec:decoupling` L376).

~~~~~~~~~
<<<<<<< SEARCH
at a $23.4$ percentage-point post-drift accuracy cost
=======
at a $23.0$ percentage-point post-drift accuracy cost
>>>>>>> REPLACE
~~~~~~~~~

**Ce qui ne bouge pas et n'a donc pas de charge** : le manqué artefactuel de $77\%$ du HT
(identique, le HT n'a pas de `warning_detector`), le halving des fausses alarmes pré-drift
(1.98 → 2.00, la formulation qualitative « halving » tient), et `$0\%$ missed detection` pour le RF
statique à $\Delta e = 0.50$ (inchangé).

## 7. Points laissés ouverts

**Le bras publié de R3 — TRANCHÉ, avec sa dette de portée.** Le plan avait réglé U1 « pour la
comparabilité », en anticipant que le phénomène serait plus faible sous U0. La mesure est inverse :
la famine est **plus forte sous les défauts de River**, c'est-à-dire dans la configuration
réellement déployée. Manqués à $\Delta e = 0.50$ : 100 % sous U0, 80 % sous U1.

L'opérateur a retenu **U1 comme résultat principal**, U0 archivé en contrôle. Les six charges de §6c
restatent le manuscrit en conséquence. Ce que cet arbitrage coûte est nommé ici plutôt que dissous
dans les numéraux : la revendication `100 %` est perdue, la borne basse de la zone sûre remonte de
0.09 à 0.12, et le phénomène est désormais publié sous la configuration où il est le **plus faible**
des deux mesurées. Un relecteur qui connaît River 0.23.0 peut demander pourquoi ; la réponse est
`results/audit_S7/s7ter_arms/`, et elle est plus forte que la question — le bras de contrôle est
mesuré, archivé et reproductible octet pour octet.

**L'oracle Δe est inutilisable sur INSECTS au préchauffage prescrit.** Le préchauffage vaut 10 % d'un
flux court — 2 414 à 7 998 pas — ce qui laisse l'arbre gelé au hasard sur un problème à six classes.
Diagnostic mesuré, colonne `err_mean_post_fork` de `delta_e_oracle.parquet` : erreur gelée 0.6625
contre 0.4127 en adaptatif sur `gradual_balanced`, 0.6521 contre 0.4914 sur `reoccurring`. Un modèle
au hasard ne peut pas exhiber de saut d'erreur : `Δe_oracle ≈ 0` y signifie « plus rien à perdre »,
pas « pas de dérive ». L'estimation adaptative INSECTS n'est ni confirmée ni infirmée par l'oracle, et
le manuscrit ne doit pas s'en réclamer. Chemins de relèvement, par coût croissant : préchauffage plus
long pour le seul arbre de référence, ou oracle à base d'ARF (marqué `# ponytail:` dans la source).

**La couverture du gel reste incomplète.** 14 des 15 hachages R5 n'ont toujours jamais été
revérifiés par exécution — l'étage BAF coûte ~4,5 h — et S6 n'a **aucune** entrée au manifeste.

**`sha256_pre.txt`** : vérifié sans consommateur, suppression ou conservation escaladée (§2).
