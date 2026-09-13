# S-SYNC — passe de synchronisation sérialisée (périmètre réel recalculé)

## Contexte

`docs/prompts/PROMPT_S-SYNC.md` décrit un dépôt éclaté sur trois branches plus un arbre de travail
non commité, et commande une passe d'opérateur en cinq étapes. **Cet état de départ n'existe plus** ;
le prompt ordonne lui-même de relever les SHA réels (L15).

| item                         | état prompt                          | état mesuré                                             |
| ---------------------------- | ------------------------------------ | ------------------------------------------------------- |
| `main`                       | `bf28a694`                           | `519c145` — `bf28a69` en est un ancêtre                 |
| `stream-s7-ter`              | `fd47fb1`, NON MERGÉ                 | `fd47fb1`, mergé (`306b1da`), `main..stream-s7-ter` = 0 |
| `stream-s3`                  | `cd443f4` + 13 fichiers non commités | `047a075`, mergé (`ea22584`), écart 0                   |
| `stream-s2` / `stream-s2bis` | S2-bis commité                       | mergés (`06d4d8c`), écart 0                             |
| worktree                     | 13 non suivis + 2 modifiés           | `git status --porcelain` vide                           |
| `main` vs `origin/main`      | —                                    | `0 0`                                                   |

**Étapes 1 (sauvegarde) et 2 (rebase/merge) sont closes** : rien à archiver, rien à merger, aucune
collision à arbitrer. Le périmètre restant est l'Étape 3 (charges), l'Étape 4 (sceau U0), l'Étape 5
(cinq portes) et le livrable `docs/editorial/sync_pass_report.md`, absent du dépôt.

## Déjà mesuré et conforme — aucune action

**Étape 4, sceau R3/U0 : intact sur les quatre points.** `config/experiment_ssot.py` L316-328 porte
les sept constantes attendues (`R3_DEFAULT_ARM = "U0"`, `R3_WARN_DELTA = R3_WARN_DELTA_U0`,
`R3_C_WARN = R3_C_WARN_U0`). `exp_R3_regime_crossover.py` L129-133 expose `--arm` avec
`default=ssot.R3_DEFAULT_ARM`, résolution L81-82 par noms SSOT, aucun littéral nu de delta/clock ;
`run_experiment_R3.sh` n'impose aucun `--arm`. `tests/test_R3_crossover.py` assertions U0 : 100,0 %
à 0.50 (L89), 1,0 % à 0.26 (L102-103), 23.41 pp (L124), monotonie depuis 0.26 (L106-107).
`R3_regime_crossover_metrics.parquet` : `OK` contre l'oracle gelé.

**Étape 5, portes numériques déjà au niveau attendu.** 122 tests collectés, 0 erreur.
`sha256sum -c` → 27 OK / 7 FAILED sur 34 entrées ; `comm -3` entre l'ensemble FAILED et les sept
entrées déclarées de `authorized_deviations.txt` est **vide** (égalité stricte vérifiée).
`tectonic` 0.17.0 disponible ; `CURRENT` → `articleA_blindspot_v64_camera_ready.tex`.

## Recensement des charges — 15 blocs SEARCH/REPLACE, non 13

Les numéros de ligne des trois documents de transfert ont dérivé (`sec:decoupling` est à L398-433,
non L376-411 ; `res:tension` à L419, non L416). **Toutes les ancres résolvent exactement une fois**,
vérifié par `grep -c -F` sur le fichier vivant.

| #    | charge                              | source                             | cible mesurée                        | statut                         |
| ---- | ----------------------------------- | ---------------------------------- | ------------------------------------ | ------------------------------ |
| 1    | S2 patch A (12 macros)              | `transfer_S2.md` L109-133          | `.tex` L68-81                        | **DÉJÀ APPLIQUÉE** (`688bcf5`) |
| 2    | S2 patch B (`rem:flooding`)         | `transfer_S2.md` L141-152          | `.tex` L345-349                      | **DÉJÀ APPLIQUÉE** (`688bcf5`) |
| 3    | S2-bis T-A(0) (9 macros)            | `transfer_S2bis.md` L368-387       | `.tex` L81                           | **À APPLIQUER**                |
| 4    | S2-bis T-A(i)                       | `transfer_S2bis.md` L396-403       | `.tex` L349                          | **À APPLIQUER, ancre étendue** |
| 5    | S2-bis T-A(ii) `res:tension`        | `transfer_S2bis.md` L338-345       | `.tex` L419, `sec:decoupling`        | **DIFFÉRÉE** → v65             |
| 6    | S2-bis T-B                          | `transfer_S2bis.md` L485-492       | `.tex` L302, `sec:starvation`        | **DIFFÉRÉE** → v65             |
| 7    | S7-ter §6a — R4 `1063→1070`         | `S7ter_state_transfer.md` L168-178 | `.tex` L529                          | **À APPLIQUER**                |
| 8    | S7-ter §6b — BAF contrôle négatif   | idem L180-188                      | `.tex` L519                          | **À APPLIQUER**                |
| 9-14 | S7-ter §6c — R3 ×6                  | idem L204-265                      | `.tex` L498, 504, 506, 508, 533, 544 | **SANS OBJET (VOID)** sous U0  |
| 15   | S7-ter §1b — commentaire `R3_C_INT` | idem L39-47                        | `config/experiment_ssot.py` L108     | **SANS OBJET (VOID)** sous U0  |

Quatorze charges visent le `.tex`, une vise le SSOT. Le prompt en annonce treize : **écart de +2
expliqué et validé** (l'addition sommaire du prompt omettait les 2 charges différées de S2-bis :
2 S2 + 4 S2-bis + 9 S7-ter = 15). Aucune entrée n'est ajoutée à `authorized_deviations.txt`.

## Arbitrages retenus (validés par l'opérateur)

**A. Charge 4 — correction d'ancre autorisée.** Le bloc SEARCH s'arrête à « …stays elevated. »
alors que le bloc REPLACE ré-émet la phrase finale « Flooding remains parametrically
controllable…escapes it (Section~\ref{sec:starvation_boundary}). ». Mesuré : cette phrase suit
immédiatement l'ancre dans le `.tex` (1 occurrence), absente du SEARCH (L399), présente une fois
dans le REPLACE (L401). Application verbatim ⇒ phrase dupliquée. Le SEARCH est **étendu d'une
phrase** pour l'absorber ; le REPLACE reste inchangé. La correction est consignée dans le rapport.

**B. Trois sites de prose U1 périmés, alignés sur U0** — précédent A1/A2 du `CLAUDE.md` :
un fichier laissé périmé est un défaut que les tests ne voient pas.

**C. Commits directs sur `main`**, par chemins explicites, sans push, sans trailer, sans co-auteur.

## Exécution

### Phase 1 — charges manuscrit, ordre contraignant

Cible unique : `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` (lu via `CURRENT`).
Avant chaque `Edit`, re-vérifier que l'ancre résout exactement une fois (`grep -c -F`). Toute ancre
qui dévie ⇒ arrêt et remontée, hors la correction (A) déjà arbitrée.

1. **Charge 3 — T-A(0)** : ancre `\newcommand{\FloodArlGap}{3\times10^{4}}     % shortfall factor of the ARL\_0 model`
   (L81). Ajoute le bloc banneré S2-bis et ses 9 macros : `\SpanOverWarm`, `\LamEqArf`, `\LamEqHt`,
   `\FaSpanArf`, `\FaSpanHt`, `\RhoRefMeas`, `\RhoEqSpan`, `\RhoEqSpanCI`, `\ThresholdShare`.
   **Première, obligatoirement** : la charge 4 consomme les neuf.
2. **Charge 4 — T-A(i)** : ancre = texte de L399 du transfert **+ la phrase finale**. Le REPLACE de
   L401 est repris tel quel. Après application, `grep -c -F 'Flooding remains parametrically
   controllable'` doit valoir **1**, et les 9 macros doivent être consommées (def = 1, use ≥ 1).
3. **Charge 7 — R4** : `$1063/1080$` → `$1070/1080$` dans la phrase ADWIN de `sec:solution_rf`
   (L529). Numéral tiré de la déviation R4 déjà déclarée dans `authorized_deviations.txt`.
4. **Charge 8 — BAF** : la phrase BAF de `sec:crossover` (L519) est ré-émise puis suivie des cinq
   phrases du contrôle négatif. Pas de risque de duplication : le REPLACE ne ré-émet pas le texte
   qui suit l'ancre.

Charges 5, 6 : **non appliquées**, sous-sections exclues par `CLAUDE.md`. Charges 9-15 : VOID.

### Phase 2 — alignement U0 des trois sites de prose

| fichier                      | ligne    | affirmation fausse sous U0                                                                                            | action                                                                                                                                                                                                                                                                          |
| ---------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `config/experiment_ssot.py`  | L108     | `# warning_detector left at river default (see README §5)`                                                            | réécrire : défauts River **explicitement épinglés** comme bras U0 (`R3_WARN_DELTA_U0` / `R3_C_WARN_U0`), U1 = ablation                                                                                                                                                          |
| `config/experiment_ssot.py`  | L337-340 | bannière `ESCALATED, NOT REWRITTEN` annonçant une correction due à l'unification                                      | remplacer par le constat de clôture : escalade close par la passe S-SYNC, charge §1b VOID sous U0                                                                                                                                                                               |
| `tests/test_R3_crossover.py` | L7-26    | « The committed artifact is the UNIFIED arm » ; « Which arm the manuscript publishes is escalated, not decided here » | réécrire le paragraphe WHICH ARM : artefact commité = **U0**, U1 archivé en `results/audit_S7/s7ter_arms/r3_u1/`, 23.41 pp = valeur U0, arbitrage du 2026-09-13. Conserver la substance de mesure (starvation plus forte sous les défauts River). **Aucune assertion touchée.** |
| `README.md`                  | L322     | « every ARF…pins both its `drift_detector` and its `warning_detector` to `ADWIN(delta=0.002, clock=c_int)` »          | rendre la phrase consciente des bras : R4/R6-R9 unifiés ; R3 publie U0 (`delta=0.01`, `clock=32`), U1 accessible par `--arm U1`                                                                                                                                                 |
| `README.md`                  | L329     | « the control arm under River's own defaults is archived beside them in `s7ter_arms/` » — inversé depuis U0           | rectifier : les défauts River **sont** le bras publié ; le bras unifié U1 est l'archive (`r3_u1/`)                                                                                                                                                                              |

Les points 1 et 2 du README §5 (défauts River, énumération) restent exacts : non touchés.

### Phase 3 — commits (chemins explicites, jamais `git add -A`)

1. `fix(manuscript): apply S2-bis T-A(0)/T-A(i) and S7-ter R4/BAF charges`
   → `docs/manuscript/articleA_blindspot_v64_camera_ready.tex`
2. `fix(R3): align ssot comment, R3 test docstring and README section 5 onto restored U0 arm`
   → `config/experiment_ssot.py`, `tests/test_R3_crossover.py`, `README.md`
3. `docs(sync): add S-SYNC serialised pass report`
   → `docs/editorial/sync_pass_report.md`

`git diff --staged` audité avant chaque commit. Aucun push.

## Livrable

`docs/editorial/sync_pass_report.md`, dans le style de maison de `docs/editorial/S7ter_state_transfer.md` :
français, H2 numérotées, tableaux porteurs de l'inventaire, numéraux en paires mesurées
avant/après, sections `## Faits établis, opposables` et `## Points laissés ouverts`, blocs
SEARCH/REPLACE en fences de 9 tildes. Contenu imposé par le prompt :

1. SHA de départ (`519c145`) et d'arrivée (mesuré).
2. Table des charges — **15 lignes**, chacune avec son statut : appliquée, déjà appliquée, différée,
   sans objet.
3. Collisions et arbitrages : Étapes 1-2 sans objet (merges antérieurs) ; **correction d'ancre
   autorisée sur T-A(i)**, avec la mesure qui la motive ; dérive des numéros de ligne des transferts.
4. Résultats des cinq portes, chacune comme commande littérale et sortie mesurée.
5. Items documentés : décompte des 15 charges validé (écart 13 → 15 résolu) ; `docs/theory/transfer_S2bis.md`
   conserve le payload T-A(i) défectueux (archive de flux, non réécrite) ; charges 5 et 6 différées pour v65.

## Vérification

```bash
cd /home/m53/TheBlindSpotParadox-Experiments

# porte 1 — suite complète
PYTHONHASHSEED=0 /home/m53/miniforge3/envs/Trading/bin/python -m pytest tests/ -q
#   attendu : 122 passed, 0 failed

# porte 2 — oracle gelé, et égalité stricte des ensembles
sha256sum -c results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt | tail -1
sha256sum -c results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt 2>/dev/null \
  | grep FAILED | sed 's/: FAILED$//' | sort -u > /tmp/failed.txt
grep -E '^results/' results/audit_S7/_baseline/authorized_deviations.txt | sort -u > /tmp/declared.txt
comm -3 /tmp/declared.txt /tmp/failed.txt        # doit être vide
#   attendu : 27 OK / 7 FAILED, comm vide

# porte 3 — compilation
tectonic docs/manuscript/$(cat docs/manuscript/CURRENT) 2>&1 | grep -iE 'undefined|warning' 
#   attendu : 0 référence indéfinie

# porte 4 — arbre propre
git status --porcelain                            # doit être vide

# contrôle ciblé des charges appliquées
M=docs/manuscript/articleA_blindspot_v64_camera_ready.tex
grep -c -F 'Flooding remains parametrically controllable' $M   # 1, pas 2
grep -c -F '1070/1080' $M                                      # 1
grep -c -F 'negative control' $M                               # 1
for m in SpanOverWarm LamEqArf LamEqHt FaSpanArf FaSpanHt RhoRefMeas RhoEqSpan RhoEqSpanCI ThresholdShare; do
  printf '%s def=%s use=%s\n' $m "$(grep -c "newcommand{\\\\$m}" $M)" "$(grep -c "\\\\$m" $M)"
done   # def=1 chacune ; use=2 lignes (préambule + paragraphe), sauf RhoEqSpan que le préfixe
       # partagé avec RhoEqSpanCI fait compter 3 — attendu, pas une anomalie
```

`tectonic` régénère le PDF (non suivi, couvert par `.gitignore`). S'il dépose des intermédiaires,
recompiler avec `--outdir` vers le scratchpad pour que la porte 4 reste tenable.
Vérifier immédiatement après l'appel Tectonic que `git status --porcelain` reste strictement vide.
Interdiction formelle d'exécuter `graphify update .` pendant S-SYNC pour préserver l'arbre propre
(mise à jour d'index hors protocole, à exécuter manuellement après la clôture de la passe).

## Risques et dette résiduelle

- **La correction d'ancre (A) est une dérogation explicite** à « ne la répare pas toi-même ». Elle
  est prouvée par mesure, bornée à une phrase, et consignée. Le payload défectueux reste en place
  dans `docs/theory/transfer_S2bis.md` : archive de flux, à ne pas réécrire — mais c'est
  exactement le motif A1/A2, à traiter à l'assemblage v65.
- **Charges 5 et 6** restent une dette datée : elles visent `sec:decoupling` et `sec:starvation`,
  que `framework_v2.tex` doit remplacer. Leur perte silencieuse à l'assemblage est le risque réel.
- `run_tests.sh` et les neuf `run_experiment_R*.sh` appellent `python` nu, non
  `/home/m53/miniforge3/envs/Trading/bin/python`. Hors périmètre S-SYNC, signalé.
- `ARCHIVED_MAIN_TEX` est vide dans `tests/test_manuscript_integrity.py` L52 : toute v65 déposée
  dans `docs/manuscript/` fera échouer la suite tant qu'elle n'y est pas déclarée.
