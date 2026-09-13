# S-SYNC — PASSE DE SYNCHRONISATION SÉRIALISÉE

## Rôle
Instance secondaire, opérateur de dépôt. Aucune analyse, aucune mesure nouvelle,
aucune réécriture de contenu. Tu rassembles un état distribué sur trois branches et un
arbre de travail non commité, et tu appliques treize charges SEARCH/REPLACE rédigées par
trois streams distincts. Toute ambiguïté remonte, aucune n'est tranchée par toi.

## ÉTAT DE DÉPART, À VÉRIFIER AVANT TOUTE ACTION
  main                 `bf28a694` — porte les patchs S2 déjà appliqués
  stream-s7-ter        `fd47fb1`, base `638ce54`, 59 fichiers, NON MERGÉ
  stream-s3            `cd443f4` seul commité ; 13 fichiers produits et 2 modifiés
                       NON COMMITÉS dans le worktree
  S2-bis               commité, arbre propre
Relève les SHA réels. Ceux-ci datent de la rédaction du prompt.

## ORDRE D'OPÉRATION, NON NÉGOCIABLE

### Étape 1 — SAUVEGARDE AVANT TOUT
Le worktree S3 porte 13 fichiers non suivis et 2 modifiés qui représentent P0 à P7. Aucun
autre item du dépôt n'a ce profil de perte. Avant toute commande git ailleurs :
  a) archiver l'arbre S3 hors du dépôt (tar horodaté) ;
  b) committer S3 sur `stream-s3`, message factuel, aucun trailer, aucun co-auteur,
     staging explicite par chemin — `git add -A` est proscrit par CLAUDE.md ;
  c) vérifier que `git status --porcelain` ne montre aucun fichier hors la table
     d'écriture du plan S3.
N'exécute rien d'autre avant que cette étape soit close.

### Étape 2 — Rebase et merge, dans cet ordre
  1. `stream-s7-ter` sur `main` — c'est le plus gros (59 fichiers) et le seul à modifier
     des scripts d'expérience. Il apporte 3 déviations autorisées (5 -> 8).
  2. `stream-s3` — ne touche que le `.tex` (zone L338-378) et `notation_map`.
  3. S2-bis si sa branche n'est pas déjà sur `main`.
Collisions attendues, et leur résolution :
  - `config/experiment_ssot.py` : deux blocs bannerés append-only (S7-ter, S2-bis).
    Conserver les DEUX, dans l'ordre chronologique. Aucune ligne existante n'a été
    modifiée par l'un ou l'autre — vérifie-le, cétait la discipline imposée.
  - `docs/ENVIRONMENT.md` : couverture de gel (S7-ter) plus lignes d'étape (S2-bis).
    Conserver les deux.
  - `results/audit_S7/_baseline/authorized_deviations.txt` : 7 entrées après merge (R3
    sous U0 restauré ne dévie pas). `sha256sum -c` doit rendre 27 OK / 7 FAILED, ensemble
    strictement égal.
  - `tests/` : 5 tests S7-ter + tests S2-bis + `test_S3_dependence.py`. Aucun ne doit
    disparaître. Le total attendu après merge est à MESURER, pas à estimer.

### Étape 3 — Application des charges, ORDRE CONTRAIGNANT
Treize charges, trois sources. L'ordre est imposé par les dépendances de macros :
  1. S2 patch A — 12 macros de préambule. PREMIER, les autres le consomment.
  2. S2-bis T-A(0) — macros S2-bis, `main` L81. Étend le patch A, ne le supersède pas.
  3. S2 patch B — `rem:flooding`.
  4. S2-bis T-A(i) — `rem:flooding`, `main` L349, ancré sur le texte POST-patch S2.
     S2-bis supersède les DEUX PHRASES FINALES du patch B seulement.
  5. Les charges S7-ter, §6c du transfert : les SIX charges R3 sont SANS OBJET (VOID)
     sous U0 restauré (les numéraux publiés sont conservés). Seules les charges hors R3
     (R4 1063->1070 et BAF contrôle négatif) sont à appliquer.
Chaque charge a été vérifiée par son stream comme résolvant EXACTEMENT UNE FOIS contre le
fichier vivant. Re-vérifie avant application : `main` a bougé depuis. Toute ancre qui ne
résout pas exactement une fois s'arrête et remonte — ne la répare pas toi-même.
Les DEUX charges S2-bis marquées DEFERRED (L416 dans `sec:decoupling`, L302 dans
`sec:starvation`) restent NON APPLIQUÉES : elles visent des sous-sections exclues par
CLAUDE.md et leur application relève de l'assemblage v65.

### Étape 4 — VÉRIFICATION ET CONTRÔLE DU BRAS R3 (U0 par défaut)
Le bras publié de R3 a été tranché et restauré sur **U0** (défauts River explicitement épinglés
dans le SSOT), avec U1 conservé en bras de contrôle d'ablation (`--arm U1`) et les deux documentés
dans `protocol_v2.tex`. L'instance S-SYNC doit se contenter de **vérifier (et corriger si nécessaire)**
que cet état nominal est scellé :
  1. `config/experiment_ssot.py` : vérifier la présence de `R3_WARN_DELTA_U0 = 0.01`,
     `R3_C_WARN_U0 = 32`, `R3_WARN_DELTA_U1 = 0.002`, `R3_C_WARN_U1 = C_INT`, et le routage
     actif `R3_DEFAULT_ARM = "U0"`, `R3_WARN_DELTA = R3_WARN_DELTA_U0`, `R3_C_WARN = R3_C_WARN_U0`.
  2. `experiments/R3_regime_crossover/exp_R3_regime_crossover.py` : vérifier que le script prend
     `--arm` en paramètre (défaut `ssot.R3_DEFAULT_ARM`), sans aucun littéral nu dans le code.
  3. `tests/test_R3_crossover.py` : vérifier que les assertions testent le comportement U0
     (100 % de manqués à Delta_e = 0.50, 1 % à 0.26, gap d'exactitude 23.41 pp, monotonie dès 0.26).
  4. Artefacts R3 : vérifier que `R3_regime_crossover_metrics.parquet` et son PNG reproduisent
     bit pour bit l'oracle gelé pré-SSOT (`sha256sum -c` rend OK sur R3).
  5. Charges manuscrit : constater que les six charges R3 de S7-ter sont **SANS OBJET (VOID)**
     car U0 préserve les numéraux déjà publiés (100 %, 0.09, 1 %, 23.4 pp). Aucune écriture
     dans le texte vivant n'est à effectuer pour R3.
Si l'un de ces points a dérivé, appliquer le correctif d'alignement U0 correspondant.

### Étape 5 — Vérification de sortie
  `pytest tests/ -q`                       total mesuré (122 tests), zéro échec
  `sha256sum -c ...pre_ssot.txt`           27 OK / 7 FAILED, ensemble égal à
                                           authorized_deviations.txt (`comm` vide)
  `tectonic docs/manuscript/$(cat docs/manuscript/CURRENT)`   compile, 0 référence indéfinie
  `git status --porcelain`                 vide
  recensement des charges                  13 traitées : appliquées, différées ou sans
                                           objet (les 6 charges R3 étant VOID), chacune
                                           avec son statut

## CE QUE TU NE FAIS PAS
Aucune réécriture de contenu. Aucune correction de prose. Aucune décision éditoriale.
Aucun push vers un remote. Aucune suppression d'artefact. Aucune entrée ajoutée à
`authorized_deviations.txt` — si une charge en exigerait une, tu t'arrêtes.

## LIVRABLE
`docs/editorial/sync_pass_report.md` : SHA de départ et d'arrivée, table des 13 charges
avec statut, collisions rencontrées et résolution, résultats des cinq portes, liste des
items remontés non tranchés.