# Plan — Stream S11-a : refonte de la thèse et de la charpente

## Contexte

L'énoncé central de l'article a migré quatre fois. Le manuscrit de record
(`docs/manuscript/articleA_blindspot_v64_camera_ready.tex`, 576 lignes après la passe S-SYNC)
porte encore la **v2** — « plancher mesuré » — dans son titre, son résumé, ses quatre
contributions, le cadrage de la Table I et `sec:hydra`, alors que les mesures livrées par S2,
S2-bis, S3, S6 et S7-ter établissent la **v4** : *les détecteurs cumulatifs ne sont pas condamnés ;
les échecs publiés viennent de seuils calibrés sur des flux stationnaires ouverts et appliqués à
des flux en boucle fermée.*

Trois mesures suffisent à dater le manuscrit :

| fait mesuré | source | ce qu'il contredit dans le `.tex` |
|---|---|---|
| 99.3 % de l'effacement est de l'apprentissage incrémental, 0.7 % des remplacements | `s6_causal.json` | (C1) L149, `sec:solution_rf` L537, Conclusion L568 |
| plancher informationnel `[13.9, 18.3]` < plafond mesuré `33.5` < `R_CUSUM(λ=50) = 59.3` ; à `λ_op = 21.93` le besoin tombe à `31.2` et le plafond le franchit | `s2_gate_T20.json`, `framework_v2.tex` `rem:split_measured` | « Detectability Limits » du titre, le résumé, `sec:complexity` L334 |
| PHT + ARF(c=1) sur ProteuS à `λ = 5` : `1080/1080`, `F1 = 1.0000`, `ADD = 6.05`, précision `1.000` | `s2bis_proteus_sweep.csv` | la « résolution KSWIN » L500, Conclusion L570 |

Ce stream ne mesure rien et n'édite aucune section du manuscrit. Il produit la charpente que
l'assemblage v65 appliquera.

**Porte d'entrée vérifiée** : `docs/editorial/sync_pass_report.md` existe (22 238 o, passe du
2026-09-13). Manuscrit lu via `docs/manuscript/CURRENT`, jamais le PDF.

---

## Décisions prises (arbitrées, pas escaladées)

1. **Arbitrage opérateur — Option 3, séparation des deux numéraux non sourcés.** Les deux ne sont
   pas de même nature et ne reçoivent pas le même traitement.
   - **BAF `0.0110`** (source unique `PROMPT_S9.md:115`) est une **revendication scientifique** :
     elle entre pleinement à l'inventaire T11a.1, sa valeur exacte et sa clé d'artefact étant
     extraites par **lecture seule** de `delta_e_oracle.parquet` / `baf_results.parquet`. Aucune
     écriture sous `results/`, aucune campagne relancée, aucun hachage touché.
   - **Facteurs de largeur d'IC `5×` / `3×`** (aucune occurrence dans le dépôt) : **aucun
     estimateur n'est recalculé.** Ce n'est pas une revendication publiable mais un défaut
     méthodologique interne, relevant exclusivement de T11a.5. Le cadrage le traite
     **qualitativement** sur ce que S7-ter §3 établit — confusion des composantes de variance,
     rééchantillonnage de runs là où la légende affirme la graine comme unité d'indépendance — et
     les deux facteurs sont consignés au `debt_register.md` comme dette d'audit à formaliser si
     l'assemblage v65 l'exige.
2. **(C4) est reformulée, non conditionnée.** S9 n'existe qu'à l'état de prompt :
   `git log --all` ne montre aucune branche, `results/` aucun répertoire, `docs/theory/` aucun
   transfert. Un bras input-space non livré et probablement structurellement aveugle à la dérive
   `P(Y|X)` à `P(X)` fixe — ce que `related_work_v2.tex` L92-95 énonce déjà — ne peut pas porter une
   contribution. (C4) est réécrite sur ce qui est mesuré : l'**ordonnancement** des familles par
   `R(D, ε, α)` et son point de croisement, qui est dérivé (`cor:split`) et instancié
   (`rem:split_measured`). La promesse input-space descend en travaux futurs, déclarée comme telle.
3. **`blind spot` reste le nom du phénomène.** `terminology_map.md` le retient sur ses trois
   conditions ; `CLAUDE.md` déclare la disjonction titre/corps délibérée. Aucun des trois titres
   proposés ne la referme d'office ; si le titre recommandé la referme, le gain est noté, non exigé.
4. **La figure d'ontologie est réécrite en place** dans `docs/manuscript/figures/fig_ontology.tex`.
   Ce fichier existe déjà, est déjà déclaré `AUTHORED` dans
   `tests/test_manuscript_integrity.py:53`, est déjà `\input` par `intro_v2.tex:82` sous le label
   `fig:ontology`, et **n'est pas inclus par le `.tex` v64** (vérifié : aucune occurrence). Le
   modifier n'édite donc aucune section du manuscrit et ne change pas le document compilé. Créer un
   second fichier obligerait à étendre `AUTHORED` sans rien gagner.

---

## Ce qui est produit

| livrable | nature |
|---|---|
| `docs/editorial/thesis_v4.md` | **neuf** — inventaire T11a.1, titres T11a.2, résumé T11a.3, contributions T11a.4, cadrage Table I T11a.5, liste terminologique T11a.6 |
| `docs/editorial/debt_register.md` | **neuf** — recensement T11a.7, ancres textuelles |
| `docs/manuscript/figures/fig_ontology.tex` | **réécrit** — ontologie v4 |

Anglais pour les trois. Blocs prêts à insérer : le résumé et les contributions sont livrés en
LaTeX, macros du préambule consommées telles quelles (`\DeCrit`, `\LambdaOpNarrow`, `\FloorBand`,
`\LearnShare`, `\RhoEqSpan`…), parce qu'ils atterriront dans un `.tex`.

---

## T11a.1 — Inventaire des revendications publiables

Table unique dans `thesis_v4.md`, colonnes : `claim | value | interval | artifact key | status`.
Une ligne par revendication publiable, aucune sans numéral ni clé d'artefact.

Onze candidats sont donnés par le prompt. Neuf sont déjà sourcés par la lecture d'ingestion :

- `Δe_c = 0.120 [0.114, 0.127]` ; `λ_op = 21.93 [19.876, 22.398]` — `envelope_stats.json`, macros L56-66
- plancher `[13.9, 18.3]` < plafond `33.51` < `R_CUSUM(50) = 59.27` ; `R_KSWIN(α=0.005) = 22.68`
  — `s2_gate_T20.json::floor_and_family`
- ProteuS `λ = 5` : `1080/1080`, `F1 = 1.0000`, `ADD = 6.05`, précision `1.000` — `s2bis_proteus_sweep.csv`
- plafond d'évidence ProteuS dans `(8, 15]` — `transfer_S2bis.md` §2.7 (v)
- flooding `10.570 [9.354, 12.114] → 1.270 [1.156, 1.426]`, `89.9 %` attribuable au seuil
  — `S2bis_calibration.md` L109-112
- α d'égalisation à `λ = 15` : ADWIN `45×` plus serré, KSWIN `4.5×` plus lâche
  — `s2bis_proteus_gate.json::family_requirements_at_lambda_eq`
- croisements `16.34` (KSWIN) / `18.97` (ADWIN) — `s2bis_proteus_gate.json::cor_split_crossings`
- Hydra : `9.22×` par non-exponentialité seule contre `7.99×` mesuré, `ρ̂ ∈ [-0.021, 0.053]`
  — `transfer_S3.md` §4.3, `rho_meff.csv`
- erasure `99.3 %` / `0.7 %`, IQR `[0.987, 0.998]`, `n = 1979` — `s6_causal.json`

Un seul exige une lecture d'artefact :

- **BAF — entre pleinement à l'inventaire.** Lire
  `results/R5_real_world_evaluation/data/delta_e_oracle.parquet` (colonne `err_mean_post_fork`) et
  `baf_results.parquet` pour extraire la valeur exacte de l'erreur du modèle gelé et la confronter
  au taux de fraude, `dtype` relu tel quel. La ligne d'inventaire porte les deux valeurs, leur
  égalité, et la clé d'artefact précise (fichier, colonne, filtre de variante). Si `0.0110` ne se
  reproduit pas, la ligne est consignée **UNREPRODUCED** avec les deux valeurs côte à côte, jamais
  absorbée — règle R1(b) de `transfer_S2.md` §2.

Le dernier candidat n'exige aucune lecture nouvelle, seulement un arbitrage de sourçage déjà
tranché en amont :

- **R3 sous U0** : `100 %` de manqués à `Δe = 0.50`, zone sûre `[0.09, 0.25]`. Le bras publié est
  **U0** depuis `44cc572` ; `sync_pass_report.md` §2 déclare les six charges U1 **VOID** et vérifie
  les sites intacts. L'inventaire porte U0 comme valeur publiée et U1 (`80 %`, `0.12`) comme
  ablation archivée dans `results/audit_S7/s7ter_arms/`, jamais l'inverse.

Complément à produire, au-delà des candidats : un balayage du `.tex` pour toute revendication
numérique publiable non couverte — `1070/1080` vs `959/1080`, `913/1080` vs `0/1080`,
`882/1080`, `p ≤ 2^-29` (jamais `p ≈ 1.86e-9`, S7-ter §3 fait 6), `23.4 pp`, `ADD = 31 [0]`,
`κ ≥ 1` sur `1835/1836`, `10.57×` et `1.61×` de la Table II.

---

## T11a.2 — Le titre

Le titre courant présuppose une limite là où la mesure dit qu'il n'y en a pas au point canonique :
le plancher informationnel vaut `1.80` sous la relaxation `χ²` et `15.40` sous la borde corde, le
plafond mesuré vaut `33.5`, et le détecteur échoue à `59.3` **parce qu'il est calibré à un niveau
de fausse alarme de `6.3e-16`**. Trois titres portant la v4 sont proposés, chacun argumenté sur ce
qu'il gagne et ce qu'il coûte, avec une recommandation unique. Contraintes : aucun superlatif,
aucun verbe de la famille de `defeat`, le mécanisme mesuré (calibration) au premier plan et non
l'effacement seul.

L'arbitrage A8 est cité et son point ouvert — titre sans `blind spot`, corps avec — repris
explicitement plutôt que reconduit par silence.

---

## T11a.3 — Le résumé

Réécriture complète, livrée en LaTeX. Le résumé courant (L115) porte `fundamental race condition`,
que `terminology_map.md` traduit, et `A Starvation Effect renders the transient signal too brief`
avec `an ensemble-level Hydra Effect accelerates this adaptation by at least 4.1 to 8.0 times`, que
S6 §5 rétrograde en accélérateur d'onset. Il porte aussi `The result is a measured bound, not an
impossibility`, qui est déjà v3 et survit.

Contraintes appliquées, vérifiables une à une : **trois numéraux au plus**, chacun avec son
intervalle ; zéro superlatif non démontré ; zéro revendication d'immunité ; la règle de calibration
en position de contribution principale. Les trois numéraux retenus seront le triplet
plancher / plafond / besoin à deux seuils, parce que c'est le seul triplet qui énonce la règle
au lieu de la résumer.

---

## T11a.4 — Les contributions

`intro_v2.tex` L84-105 porte (C1)–(C4) sous la v2. Réécriture des quatre sous la v4.

- **(C1)** attribue le phénomène à l'effet Hydra. S6 lui laisse `0.7 %` du volume ; S3 lui retire
  l'attribution de l'écart au `10×` (`9.22×` par non-exponentialité seule, `ρ̂` indiscernable de
  zéro). Ce qui reste, et qui est tenable : la **topologie** — moniteur sur un résidu endogène —
  plus la prédiction que la sévérité est gouvernée par le rapport `A / R`, ni par River, ni par
  ARF, ni par ADWIN. La version L86-91 d'`intro_v2.tex` est déjà proche ; elle est resserrée sur
  `A < R` et purgée du mot Hydra.
- **(C2)** et **(C3)** sont réécrites sur `def:blindspot` (`A < R`) et sur la décomposition
  synchronisée à trois bras, avec `κ` mesuré et non supposé.
- **(C4)** est reformulée (décision 2 ci-dessus). Le bras input-space part en travaux futurs.

Chaque contribution est accompagnée d'une ligne « tenable avec : » citant l'artefact qui la porte.

---

## T11a.5 — Le cadrage de la Table I

Cinq griefs, dont **un est faux tel qu'énoncé** et sera corrigé plutôt que repris.

1. **Phase pré-dérive à erreur identiquement nulle.** Mesuré : `0.0 / max 0` erreurs pré-changement
   sur les deux bras, `s2bis_proteus_eddm_arming.csv`. Conséquence : aucun budget de fausses
   alarmes n'est consommé, tout `λ > 0` satisfait toute contrainte de fausse alarme, et `λ = 15`
   n'est sélectionné par aucune mesure.
2. **Les familles sont comparées à des niveaux `α` incommensurables.** À `λ = 15`, ADWIN est déployé
   `45×` plus serré et KSWIN `4.5×` plus lâche que ce qu'un `R` commun exigerait ; à `λ = 50` KSWIN
   est lu treize ordres de grandeur plus lâche que le CUSUM auquel on le compare.
   **Correction d'énoncé** : le prompt dit « ses trois colonnes » ; les trois colonnes de la table
   sont les régimes GARCH (IID / Cal. A / Cal. B), qui ne sont pas en cause. Ce qui compare des
   calibrations, ce sont les **lignes** de familles. Le cadrage le dit ainsi.
3. **EDDM est un détecteur jamais armé.** `0` erreur pré-dérive, `9 [6, 12]` erreurs sur les 8 000
   pas contre un `warm_start` de 30, `100 %` des runs sans armement. La ligne `F1 = 0.00` n'est pas
   une défaillance d'accumulation ; `prop:starvation` ne s'y applique jamais.
4. **Le bras HT à un seul réplicat — à vérifier avant d'être repris.** Lecture de
   `exp_R4_main_table.py` : `make_ht()` L174 n'est effectivement pas semé, **mais**
   `simulate_stream(..., seed=seed)` L75/L202 l'est, donc les 30 graines produisent 30 flux
   distincts et le bras HT porte 30 réplicats, pas un. Ce que la dissymétrie produit réellement est
   plus faible et différent : le bras ARF porte deux sources de variation (flux + initialisation de
   forêt) contre une seule pour le HT, et l'IC apparié en hérite. Le cadrage énoncera cette version
   mesurée, avec la citation de ligne, et **non** « un test à un échantillon contre une constante ».
   Découverte collatérale consignée au registre : `simulate_stream` L76 appelle `np.random.seed()`,
   mutation d'état global que la règle PRNG du dépôt proscrit.
5. **Le bootstrap mesurait la mauvaise composante de variance — énoncé qualitatif, aucun
   recalcul.** Établi par S7-ter §3 : `np.random.choice` sur les 360 lignes d'une cellule, tiré de
   l'état NumPy **global**, alors que la légende affirmait la graine comme unité d'indépendance
   statistique. Les deux énoncés sont incompatibles, et les 36 flux qu'une graine produit partagent
   l'initialisation de forêt de cette graine. Corrigé en rééchantillonnage apparié de l'indice de
   graine sur un `default_rng` injecté localement (`exp_R4_main_table.py:235-250`), schéma repris de
   `exp_R6_hydra_survival.py:105-111`. Le cadrage énonce le défaut et sa correction, **sans
   chiffrer l'écart** : les facteurs `5×` / `3×` du prompt n'ont aucune source committée et ne sont
   pas produits ici. Ils partent au `debt_register.md` comme dette d'audit, avec la commande qui les
   fermerait, à formaliser si l'assemblage v65 l'exige.

Le cadrage se clôt sur trois paragraphes : **ce que la table établit** (une séparation complète,
reproductible, à `p ≤ 2^-29`, sur des flux identiques), **ce qu'elle n'établit pas** (aucune
comparaison de familles, aucun arbitrage détection/fausses alarmes, aucun mécanisme
d'accumulation pour EDDM), et **où le lecteur doit aller** — `s2bis_proteus_sweep.csv` pour le
balayage en `λ` qui tranche la question qu'elle ne tranche pas.

---

## T11a.6 — L'ontologie des effets

Deux termes conservés, conformément à `terminology_map.md` : `blind spot` et `starvation`. La liste
finale reprend chaque terme supprimé avec sa traduction et, pour les deux qui ont perdu plus qu'un
nom, la raison mesurée :

- **Hydra** a perdu son mécanisme : `9.22×` s'explique par la non-exponentialité seule, `ρ̂` est
  indiscernable de zéro, et le volume d'effacement lui revient à `0.7 %`. Il devient
  `γ_M := τ_erase^(1) / τ_erase^(M)`, quantité mesurée portant un symbole.
- **Decoupling Principle** a perdu son biconditionnel, retiré dans le corps même du manuscrit
  (`def:decoupling` (i-bis), L423 : *« which we withdraw »*). Il devient une condition de
  réactivité suffisante.

`fig_ontology.tex` est réécrite pour porter la v4. Ce que la version S5 ne dit pas encore et que la
v4 exige : la comparaison `A` contre `R(D, ε, α)` comme nœud terminal, la **séparation** du
plancher informationnel `thm:floor` (aucun moniteur ne détecte) et du besoin propre au moniteur
`R(D, ε, α)` (celui-ci ne détecte pas, un autre le peut) — c'est exactement la bifurcation des deux
régimes de `thm:floor`, et c'est elle qui rend la règle de calibration lisible en une image. La
boucle de rétroaction négative, l'axe `λ` unique portant famine et flooding, et le moniteur sur
`P(X)` hors boucle sont conservés tels quels.

Contraintes de compilation : le préambule du `.tex` charge déjà `tikz` avec
`arrows.meta,positioning,fit,backgrounds` (L11-12), donc aucune dépendance nouvelle. Le label
`fig:ontology` et le nom de fichier sont invariants, sans quoi `intro_v2.tex:82` casse.

---

## T11a.7 — Le registre de dette

`docs/editorial/debt_register.md`. Une ligne par site, colonnes :
`file | textual anchor (verbatim) | refuted claim | refuting source | zone`.

**Ancres textuelles, jamais des numéros de ligne.** Motif mesuré : les trois documents de transfert
citent des lignes qui ont toutes bougé ; `sync_pass_report.md` §3c tabule les dérives, et
`CLAUDE.md` le rappelle pour v63 → v64. Chaque ancre est re-grepée sur le fichier vivant avec
`grep -c -F` valant exactement 1 avant d'être inscrite ; une ancre qui ne résout pas uniquement est
étendue jusqu'à l'unicité, jamais approximée.

La colonne `zone` porte trois valeurs : `editable`, `EXCLUDED (sec:race | sec:hydra |
sec:starvation | sec:decoupling)`, et `GENERATED` — cette dernière pour les sites dont le texte
n'est pas éditable dans le `.tex` : la légende de la Table I est produite par
`exp_R4_main_table.build_caption`, donc sa correction est une édition Python **plus** une
régénération d'artefact, donc une déviation autorisée à déclarer et un hachage à bouger. Le
registre le dit au lieu de laisser l'assembleur le découvrir.

Sites connus repris et re-ancrés (six du prompt, dix KSWIN de
`S2bis_narrative_payload.md` §(b)). Complément déjà identifié à l'ingestion, non exhaustif :

| site | énoncé réfuté | source réfutante |
|---|---|---|
| Abstract, `harbors a fundamental race condition` | terme retiré | `terminology_map.md` |
| Intro, `the stronger the drift, the less likely` | plafond non monotone, pic à `Δe ≈ 0.19` | S6 §4 |
| Intro, `entirely inoperative` | superlatif retiré | `terminology_map.md` |
| (C1) L149, `We derive the critical ensemble size M_crit inducing structural failure` | `cor:mcrit` retiré | S3 D5(b) |
| `rem:bgswap`, `provide additional evidence that…` | corrélation de rang `0.06` en bande faible ; contredit par `rem:envelope` L438 dans le même document | S6 §2 |
| `sec:proteus`, `EDDM confirms family-agnostic starvation` | défaut d'armement, pas d'accumulation | S2-bis T-D |
| `sec:solution_rf`, `the root cause … is not the ensemble itself (Bagging), but its auto-adaptive mechanics (tree-swapping)` | `99.3 %` = apprentissage incrémental | S6 §5 |
| `sec:limitations`, `explaining why empirical acceleration (4--8×) falls short of the M-fold reference rate` | non-exponentialité, pas corrélation | S3 §4.3 |
| Conclusion, `Windowed and distributional monitors are spared by construction` | immunité non établie | S2-bis §(b) |
| `related_work_v2.tex` L110-112, KSWIN sans son `α` | règle B9 | S2-bis §(b) |

Trois dettes d'audit y entrent également, aucune fermée par ce stream :

- **facteurs de largeur d'IC `5×` / `3×`** — dette d'audit ouverte, à formaliser si l'assemblage
  v65 l'exige. Le registre porte la commande qui la fermerait : recalcul des deux estimateurs
  (rééchantillonnage de runs contre rééchantillonnage de graines) sur
  `exp_R4_results_aligned_fusion.csv`, 16 200 lignes, `float_precision='round_trip'`, `default_rng`
  injecté, cellule par cellule. Non exécutée ici, par arbitrage opérateur.
- **BAF `0.0110`** — fermée ou marquée UNREPRODUCED par la lecture de T11a.1, l'issue étant
  inscrite au registre dans les deux cas.
- **mutation PRNG globale** de `simulate_stream` (`exp_R4_main_table.py:76`, `np.random.seed()`),
  proscrite par la règle de déterminisme du dépôt.

---

## Vérification

Aucun test n'assertait ces livrables avant ce stream ; les portes sont donc celles du dépôt, plus
deux contrôles propres aux ancres.

| porte | commande | attendu |
|---|---|---|
| suite complète, non-régression | `PYTHONHASHSEED=0 /home/m53/miniforge3/envs/Trading/bin/python -m pytest tests/ -q` | `122 passed`, inchangé |
| intégrité manuscrit après réécriture de la figure | `… -m pytest tests/test_manuscript_integrity.py -v` | 6/6 ; `fig_ontology.tex` reste couvert par `AUTHORED` |
| gel des artefacts | `sha256sum -c results/audit_S7/_baseline/artifacts_sha256_pre_ssot.txt` | `27 OK / 7 FAILED`, exactement les sept déclarées — aucune écriture sous `results/` |
| arbre propre | `git status --porcelain` | trois fichiers seulement |
| unicité des ancres | `grep -c -F "<ancre>" <fichier>` pour chaque ligne du registre | `1` pour chacune, sans exception |
| compilation de la figure | `tectonic` sur un harnais reprenant le préambule IEEEtran plus `\input{figures/fig_ontology.tex}` | exit 0, aucune `undefined reference` |

Si une ancre ne résout pas à 1, elle est étendue et re-mesurée ; trois échecs consécutifs sur le
même site gèlent l'état et remontent à l'opérateur plutôt que de produire une ancre approximative.

## Hors périmètre, explicitement

Aucune section du `.tex` n'est éditée, les quatre sous-sections exclues comprises. Aucun
`results/` n'est écrit, aucune campagne relancée, aucune constante ajoutée à
`config/experiment_ssot.py`, aucune entrée à `authorized_deviations.txt`. `graphify update .` reste
à exécuter après clôture — l'index n'a pas été rafraîchi depuis S-SYNC.
