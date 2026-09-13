# S-SYNC — Rapport de la passe de synchronisation sérialisée

Passe exécutée le 2026-09-13 dans le checkout principal, sur `main`, sans worktree dédié : les trois
branches de flux (`stream-s2`, `stream-s2bis`, `stream-s3`, `stream-s7-ter`) étaient déjà fusionnées
au démarrage, et il ne restait aucune écriture concurrente à sérialiser.

Plan exécuté : `docs/plans/PROMPT_S-SYNC.md`. Spécification d'origine : `docs/prompts/PROMPT_S-SYNC.md`.
Manuscrit de référence lu depuis `docs/manuscript/CURRENT`, jamais depuis le PDF.

---

## 1. Bornes de la passe et périmètre réellement exécuté

| borne                                      | valeur mesurée                                                       |
| ------------------------------------------ | -------------------------------------------------------------------- |
| SHA annoncé par le prompt                  | `bf28a694`, puis `519c145` par le plan                               |
| SHA de départ **mesuré** (`git rev-parse`) | `0ddaf51` — `519c145` en est le parent direct                        |
| SHA d'arrivée du code                      | `5d1150b`                                                            |
| commits de la passe                        | `cefa94e` (manuscrit), `5d1150b` (alignement U0), puis ce rapport    |
| `main` vs `origin/main` au départ          | `0 0` — aucun push exécuté par cette passe                           |
| arbre de travail au départ                 | `git status --porcelain` vide                                        |

Le prompt décrivait un dépôt éclaté sur trois branches plus treize fichiers non commités. Cet état
n'existait plus : `main..stream-s7-ter`, `main..stream-s3` et `main..stream-s2bis` valent 0 commit.
**Les étapes 1 (sauvegarde) et 2 (rebase/merge) sont donc sans objet** — rien à archiver, rien à
fusionner, aucune collision à arbitrer. La passe se réduit à l'étape 3 (charges), l'étape 4 (sceau
U0, vérifié intact sans modification), l'étape 5 (cinq portes) et le présent livrable.

---

## 2. Table des charges — 15 lignes

Quatorze charges visent le manuscrit de référence, une vise `config/experiment_ssot.py`. Les numéros
de ligne `.tex` sont donnés en paire **avant → après** la passe ; le décalage `+12` au-delà de L81
est l'insertion du bloc de macros de la charge 3.

| #  | charge                                         | source                             | cible (avant → après)                    | statut                            |
| -- | ---------------------------------------------- | ---------------------------------- | ---------------------------------------- | --------------------------------- |
| 1  | S2 patch A — 12 macros de préambule            | `transfer_S2.md` L109-133          | `.tex` L68-81 (inchangé)                 | **DÉJÀ APPLIQUÉE** (`688bcf5`)    |
| 2  | S2 patch B — `rem:flooding`                    | `transfer_S2.md` L141-152          | `.tex` L345-349 → L357-361               | **DÉJÀ APPLIQUÉE** (`688bcf5`)    |
| 3  | S2-bis T-A(0) — 9 macros                       | `transfer_S2bis.md` L368-387       | ancre `.tex` L81 → bloc L83-93           | **APPLIQUÉE** (`cefa94e`)         |
| 4  | S2-bis T-A(i) — `rem:flooding` §3              | `transfer_S2bis.md` L396-403       | `.tex` L349 → L361                       | **APPLIQUÉE, ancre étendue** (§3b) |
| 5  | S2-bis T-A(ii) — `res:tension`                 | `transfer_S2bis.md` L338-345       | `.tex` L419 → L431, `sec:decoupling`     | **DIFFÉRÉE** → v65                |
| 6  | S2-bis T-B — arme de référence R1              | `transfer_S2bis.md` L485-492       | `.tex` L302 → L314, `sec:starvation`     | **DIFFÉRÉE** → v65                |
| 7  | S7-ter §6a — R4 `1063/1080` → `1070/1080`      | `S7ter_state_transfer.md` L168-178 | `.tex` L529 → L541                       | **APPLIQUÉE** (`cefa94e`)         |
| 8  | S7-ter §6b — BAF, contrôle négatif             | idem L180-188                      | `.tex` L519 → L531                       | **APPLIQUÉE** (`cefa94e`)         |
| 9  | S7-ter §6c — légende Fig. 3, `1%→4%`/`100%→80%` | idem L204-212                      | `.tex` L498 → L510                       | **SANS OBJET (VOID)** sous U0     |
| 10 | S7-ter §6c — zone de signal faible              | idem L214-222                      | `.tex` L504 → L516                       | **VOID** sous U0                  |
| 11 | S7-ter §6c — borne basse `0.09 → 0.12`          | idem L228-234                      | `.tex` L506 → L518                       | **VOID** sous U0                  |
| 12 | S7-ter §6c — manqués `100% → 80%`               | idem L236-244                      | `.tex` L508 → L520                       | **VOID** sous U0                  |
| 13 | S7-ter §6c — coût `23.4 → 23.0` pp              | idem L246-254                      | `.tex` L533 → L545                       | **VOID** sous U0                  |
| 14 | S7-ter §6c — même écart, `sec:discussion`       | idem L256-265                      | `.tex` L544 → L556                       | **VOID** sous U0                  |
| 15 | S7-ter §1b — commentaire `R3_C_INT`             | idem L39-47                        | `config/experiment_ssot.py` L108         | **VOID** ; site réécrit sous un autre motif (§4) |

Aucune entrée n'est ajoutée à `results/audit_S7/_baseline/authorized_deviations.txt` : aucune charge
ne touche un artefact sous `results/`.

---

## 3. Collisions et arbitrages

### 3a. Étapes 1 et 2 — sans objet, par mesure

`git rev-list --count main..<branche>` vaut 0 sur les quatre branches de flux ; les merges
`306b1da` (S7-ter), `ea22584` (S3) et `06d4d8c` (S2/S2-bis) sont antérieurs à la passe. Il n'y a eu
ni conflit à trancher, ni arbitrage de collision : la sérialisation que le prompt commandait avait
déjà eu lieu, et la passe n'a pas rejoué ce travail.

### 3b. Correction d'ancre autorisée sur T-A(i) — dérogation explicite, bornée, mesurée

Le bloc SEARCH livré par `docs/theory/transfer_S2bis.md` L399 s'arrête à « …stays elevated. »,
tandis que le bloc REPLACE L401 **ré-émet** la phrase finale « Flooding remains parametrically
controllable… ». Les quatre comptes qui motivent la correction :

| mesure                                                   | valeur |
| -------------------------------------------------------- | -----: |
| phrase présente dans le SEARCH livré (`transfer` L399)    |      0 |
| phrase présente dans le REPLACE livré (`transfer` L401)   |      1 |
| phrase présente dans le `.tex` **avant** la passe         |      1 |
| phrase présente dans le `.tex` **après** la passe         |      1 |

Appliquer le payload verbatim aurait donc laissé la phrase **deux** fois. Le SEARCH est étendu d'une
phrase — celle qui suit immédiatement l'ancre dans le fichier vivant — pour l'absorber ; **le REPLACE
est repris tel quel, non modifié**. Ancre effectivement appliquée :

~~~~~~~~~
docs/manuscript/articleA_blindspot_v64_camera_ready.tex
<<<<<<< SEARCH
The asymmetry between the two pipelines is a threshold asymmetry: the one-false-alarm-per-warm-up calibration hands the ARF $\FloodLamArf$ and the HT $\FloodLamHt$, a factor of $6.3$, because bagging halves the ARF's pre-change error volatility (Section~\ref{sec:crossover}). The variance reduction that makes the ARF a good classifier buys it a low threshold, and a low threshold is what floods once the error stream stays elevated. Flooding remains parametrically controllable---alarms scale as $1/\lambda$ in the re-arm model---whereas starvation is structural: no CUSUM threshold escapes it (Section~\ref{sec:starvation_boundary}).
=======
[REPLACE = transfer_S2bis.md L401, verbatim, octet pour octet]
>>>>>>> REPLACE
~~~~~~~~~

L'identité octet pour octet du REPLACE appliqué est vérifiée, pas affirmée :
`grep -c -F "$(sed -n '401p' docs/theory/transfer_S2bis.md)"` sur le `.tex` vaut **1**. Le même
contrôle sur le bloc de macros de la charge 3 (`transfer_S2bis.md` L373-385) vaut **1**, et sur les
payloads S7-ter §6a et §6b (`S7ter_state_transfer.md` L176 et L186) vaut **1** chacun.

### 3c. Dérive des numéros de ligne des documents de transfert

Les trois documents de transfert citent des lignes qui ont bougé depuis leur rédaction. Aucune ancre
n'a été prise depuis un rapport : toutes ont été re-grepées sur le fichier vivant, `grep -c -F`
valant **1** avant chaque édition.

| ancre                      | ligne citée par le transfert | ligne mesurée avant la passe | ligne après la passe |
| -------------------------- | ---------------------------- | ---------------------------- | -------------------- |
| `res:tension` (T-A(ii))    | L416                         | L419                         | L431                 |
| `sec:decoupling`           | L376-411                     | L398-433                     | L410-445             |
| `sec:solution_rf` (R4)     | —                            | L529                         | L541                 |
| `sec:crossover` (BAF)      | —                            | L519                         | L531                 |

---

## 4. Alignement U0 des cinq sites de prose

Le sceau R3/U0 posé par `44cc572` est intact sur ses quatre points (constantes SSOT, `--arm` résolu
par noms SSOT, assertions U0 du test, parquet `OK` contre l'oracle gelé) et **n'a pas été touché**.
Cinq sites de prose contredisaient encore ce sceau ; aucune assertion, aucune constante, aucun
artefact n'est modifié.

| fichier                      | ligne | affirmation avant                                                     | après                                                                                                      |
| ---------------------------- | ----- | --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `config/experiment_ssot.py`  | 108   | « warning\_detector left at river default »                           | défauts River **explicitement épinglés** comme bras U0 (`R3_WARN_DELTA_U0` / `R3_C_WARN_U0`), U1 = ablation |
| `config/experiment_ssot.py`  | 339   | bannière `ESCALATED, NOT REWRITTEN`                                   | `ESCALATION CLOSED` — escalade close par S-SYNC, charge §1b VOID sous U0                                    |
| `tests/test_R3_crossover.py` | 8-31  | « The committed artifact is the UNIFIED arm » ; arbitrage « escalated » | artefact commité = **U0** ; U1 archivé en `s7ter_arms/r3_u1/` ; 23.41 pp = U0, 22.99 pp = U1                |
| `README.md`                  | 322   | « every ARF … pins both … to `ADWIN(delta=0.002, clock=c_int)` »      | R4 et R6–R9 unifiés ; R3 publie U0 (`delta=0.01`, `clock=32`), U1 par `--arm U1`                            |
| `README.md`                  | 329   | « the control arm under River's own defaults is archived … »          | les défauts River **sont** le bras publié ; c'est le bras unifié U1 qui est l'archive (`r3_u1/`)            |

Deux rectifications collatérales, toutes deux mesurées avant écriture :

1. `README.md` L329 attribuait à R3 une déviation autorisée.
   `grep -c 'R3_regime_crossover' authorized_deviations.txt` vaut **0**, et le parquet R3 vérifie
   `OK` contre l'oracle gelé : R3 n'en consomme aucune. La phrase ne cite plus que R4.
2. `run_experiment_R3.sh` ne relaie pas `"$@"` (vérifié dans le script) : le bras U1 ne s'atteint
   donc pas par le wrapper. `README.md` L322 donne l'appel direct du script d'expérience.

Les points 1 et 2 du README §5 (défauts River en trois valeurs, énumération des pipelines) restent
exacts sous U0 : non touchés.

---

## 5. Vérification — cinq portes, chacune une commande et sa sortie

**Porte 1 — suite complète.**

```
PYTHONHASHSEED=0 /home/m53/miniforge3/envs/Trading/bin/python -m pytest tests/ -q
→ 122 passed in 32.84s
```

122 tests collectés, 0 erreur de collecte, 0 échec. Aucune assertion n'a été modifiée par la passe.

**Porte 2 — oracle gelé et égalité stricte des ensembles.**

```
sha256sum -c results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt
→ 27 OK, 7 FAILED   (WARNING: 7 computed checksums did NOT match)

comm -3 <(grep -E '^results/' authorized_deviations.txt | sort -u) <(FAILED | sort -u)
→ (vide)
```

7 entrées FAILED, 7 entrées déclarées, `comm -3` vide : **égalité stricte**, pas une inclusion.
Le compte attendu depuis la restauration U0 (27 / 7) est reproduit à l'identique.

**Porte 3 — compilation.**

```
tectonic docs/manuscript/$(cat docs/manuscript/CURRENT)
→ Tectonic 0.17.0, exit 0, PDF 1.56 MiB, 13 pages
→ dernière passe TeX : 0 « undefined reference », 0 « undefined citation »
→ résidus : Underfull \hbox / \vbox uniquement, plus 1 avertissement BibTeX
  (« empty booktitle in hopcroft_karp_1973 »), antérieur à cette passe
```

Les avertissements « undefined » des deux premières passes sont résolus par la troisième (BibTeX
puis stabilisation de `.out`) ; le contrôle porte sur la passe finale, lignes 1252-1379 du log.

**Porte 4 — arbre propre.**

```
git status --porcelain
→ (vide) après chaque commit
```

`tectonic` n'a déposé aucun intermédiaire (« Skipped writing 3 intermediate files ») ; le PDF
régénéré est couvert par `.gitignore:23`. Vérifié immédiatement après l'appel. Conformément au plan,
`graphify update .` **n'a pas été exécuté** pendant la passe.

**Porte 5 — contrôle ciblé des charges appliquées.**

```
grep -c -F 'Flooding remains parametrically controllable' $M   → 1   (pas 2)
grep -c -F '1070/1080' $M                                      → 1
grep -c -F '1063/1080' $M                                      → 0
grep -c -F 'negative control' $M                               → 1
9 macros S2-bis : def=1 chacune ; use=2 lignes, sauf RhoEqSpan (3, préfixe partagé avec RhoEqSpanCI)
sites VOID sous U0 : 100% (L510, L520), 0.09 (L518), 1% à 0.26 (L510), 23.4 pp (L545, L556) intacts
```

---

## 6. Faits établis, opposables

Chacun est mesuré sur le dépôt vivant, jamais recopié d'un rapport.

1. **Le décompte de charges est de 15, pas 13.** L'addition du prompt omettait les deux charges
   différées de S2-bis : 2 (S2) + 4 (S2-bis) + 9 (S7-ter, dont 8 au manuscrit et 1 au SSOT) = 15.
   L'écart `13 → 15` est expliqué par énumération, pas absorbé. Bilan : 4 appliquées, 2 déjà
   appliquées, 2 différées, 7 sans objet.

2. **Les sept charges VOID le sont par arbitrage, pas par omission.** La restauration de U0
   (`44cc572`) rend les six numéraux U1 de `S7ter_state_transfer.md` §6c non applicables : les
   valeurs publiées (100 % à $\Delta e = 0.50$, borne basse 0.09, 1 % à 0.26, 23.41 pp) sont celles
   du bras publié et restent strictement exactes. Vérifié site par site après la passe.

3. **Le payload T-A(i) livré était défectueux et la correction est d'une phrase.** Mesure en §3b :
   SEARCH 0 occurrence, REPLACE 1, `.tex` 1 avant comme après. La dérogation à « ne répare pas le
   payload toi-même » est bornée à l'extension du SEARCH ; le REPLACE est appliqué octet pour octet.

4. **`docs/theory/transfer_S2bis.md` n'est pas réécrit.** C'est une archive de flux : elle conserve
   le payload T-A(i) défectueux tel que S2-bis l'a livré. La correction vit ici, dans le rapport de
   la passe qui l'a appliquée, et non par réécriture rétroactive de la source.

5. **Le manuscrit gagne 12 lignes et 9 macros.** 564 → 576 lignes, 46 → 55 `\newcommand` en tête de
   ligne. Les neuf macros S2-bis sont définies une fois et consommées par le paragraphe de la charge
   4 : aucune macro orpheline, aucune référence pendante (porte 3).

6. **Le sceau U0 n'a pas été retouché.** Les sept constantes de `config/experiment_ssot.py`
   L316-328, la résolution `--arm` par noms SSOT (L81-82, L130 de
   `exp_R3_regime_crossover.py`) et les quatre assertions U0 de `tests/test_R3_crossover.py` sont
   dans l'état où `44cc572` les a laissées. Seuls des commentaires et des docstrings ont bougé.

7. **Aucune déviation autorisée n'est consommée par la passe.** Le numéral `1070/1080` de la charge 7
   est tiré de `authorized_deviations.txt` L56, déclaré par S7-ter lors de la régénération de R4 ;
   la passe le transcrit dans le manuscrit, elle ne régénère aucun artefact.

---

## 7. Points laissés ouverts

**Charges 5 et 6 — dette datée, et c'est le risque réel.** T-A(ii) (`res:tension`, L431) et T-B
(`sec:starvation`, L314) visent deux des quatre sous-sections que `CLAUDE.md` exclut jusqu'à
l'assemblage v65. Leurs ancres sont consignées en §2 avec leur position mesurée après la passe. Le
risque n'est pas qu'elles soient mal appliquées, c'est qu'elles soient **perdues silencieusement**
quand `framework_v2.tex` remplacera ces sous-sections : personne ne relira ce tableau à ce
moment-là si l'assemblage ne l'impose pas.

**`docs/theory/transfer_S2bis.md` conserve un payload dont on sait qu'il duplique.** Laisser
l'archive intacte est la bonne politique de lignage, mais c'est exactement le motif A1/A2 : un
fichier laissé périmé parce qu'il est « une archive ». Quiconque ré-appliquera T-A(i) depuis cette
source sans lire le présent rapport dupliquera la phrase. À traiter à l'assemblage v65.

**Le préambule L55 cité par S2-bis §2.7.** `transfer_S2bis.md` L347-349 signale que le commentaire
de macro `R4\_PHT\_LAMBDA, ProteuS pre-drift calibration` devrait lire « declared ». Cette ligne
n'est pas une charge livrée en SEARCH/REPLACE et n'est donc pas dans la table de §2 : elle n'a pas
été modifiée par cette passe.

**`run_tests.sh` et les neuf `run_experiment_R*.sh` appellent `python` nu**, non
`/home/m53/miniforge3/envs/Trading/bin/python`. Hors périmètre S-SYNC ; signalé, non corrigé.

**`ARCHIVED_MAIN_TEX` est vide** dans `tests/test_manuscript_integrity.py` L52 : toute v65 déposée
dans `docs/manuscript/` fera échouer
`test_current_manuscript_is_unique_and_live` tant qu'elle n'y est pas déclarée.

**L'index Graphify n'a pas été rafraîchi.** Le plan interdit `graphify update .` pendant la passe
pour préserver l'arbre propre. Trois fichiers de code et le manuscrit ont bougé : la mise à jour
d'index est à exécuter manuellement après la clôture.
