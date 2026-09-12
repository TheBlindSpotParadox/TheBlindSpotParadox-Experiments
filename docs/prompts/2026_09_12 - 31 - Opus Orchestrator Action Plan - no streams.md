# ANALYSE DES TRANSFERTS D'ÉTAT — ACTIONS — LOT 2 DE PROMPTS

## 1. Découverte prioritaire : deux copies du manuscrit, celle qui vous est servie est périmée

Le jeu de fichiers projet monté dans mon contexte (`/mnt/project/`) contient `articleA_blindspot_v64_camera_ready.tex` daté du 11/09 00:28. Vérifié à la commande :

- 5 occurrences de `\beta` (conversion S7-bis non appliquée)
- `leaving the admissible set empty` présent dans le résumé
- `permanently erased` présent ligne 59
- `0.745` / `0.985` / `~24 percentage points` présents ligne 405
- 0 occurrence de `empresult`, `prop:certificate`, `res:tension`, `rem:envelope`, `rem:cf_scope`, `rem:transient_length`, `res:starvation`, `\DeCrit`, `\LambdaOpNarrow`, TikZ

La copie indexée sous `docs/manuscript/articleA_blindspot_v64_camera_ready.tex`, elle, porte l'intégralité des six DIFF S6, le patch P2 et la conversion `β → r` :

- `\begin{empresult}[Envelope dependence of the admissible set]\label{res:tension}` avec `\DeCrit` et `\DeCritCI`
- `rem:envelope` avec `\WideEnvUnstable`, `\LambdaOpNarrow`, `\LambdaOpNarrowCI`
- `def:decoupling` en forme fiabiliste, certificat `(i-bis)`, biconditionnel explicitement retiré
- `cor:mcrit` : « at the reliability target $r = 0.95$ »
- surrogat rectangulaire retiré de l'étape (4)

**V1 du transfert S7 est donc levée, et sur la branche favorable** : S7-bis et S6 ont atterri. Ce que vous lisiez comme un échec d'atterrissage est la copie racine que l'Action 1 de S6 devait supprimer, et qui survit dans la synchronisation mémoire projet. Toute instance future qui lit les fichiers projet sans passer par `project_knowledge_search` travaillera sur un manuscrit antérieur de deux streams.

---

## 2. Corrections à mon propre audit

**F23 était fausse dans son mécanisme.** J'avais attribué au facteur Hydra quatre divergences de constantes entre R6 et R1/R8. S7 a établi que `exp_R6_compute_hydra.py` consomme R6 et **R2**, expériences paramétriquement identiques (`N_STEPS = 8000`, `T_DRIFT = 4000`, horizon 4000, `range(1,101)`, `linspace(0.1, 4.0, 20)`). J'avais lu des constantes sans ouvrir le script de calcul. Le défaut réel — analyse en cas complets sous censure différentielle — existe bel et bien, et le traitement RMST livré par S7 est correct : `4.05× → 4.12× [3.45, 4.96]`, `7.99× → 7.99× [6.40, 9.72]`, avec verdict **borne inférieure** puisque le bras ARF n'est jamais censuré. La conclusion tient, la voie d'accès que j'avais décrite était erronée.

**Ma pré-vérification numérique de la Proposition 3 se trompait de `W`.** J'avais calculé `λ_starve ≈ 19.6` à `W = 30`, pris comme premier swap. Le `W` pertinent est `τ_erase`, mesuré par S6 à **611.9** à `Δe = 0.3268`. Avec `μ·W = 193.8 > λ = 50`, la partie positive s'annule et la borne d'Azuma–Hoeffding vaut `W·e⁰ ≥ 1` : **vacante**. La thèse survit, mais par le certificat déterministe `prop:certificate` fondé sur le plafond de preuve `A_swap`, pas par la borne exponentielle. L'hypothèse qui casse est le taux d'accumulation constant, pas la fluctuation.

**SR 11-7 est abrogé** depuis le 17/04/2026, remplacé par Fed SR 26-2 / OCC 2026-13. Ma recommandation T2 du prompt S5 citait une norme morte. S5 l'a corrigé et a trouvé mieux : **EU AI Act Art. 15(4)**, qui impose de traiter les boucles de rétroaction des systèmes qui continuent d'apprendre. Le régulateur nomme le danger que l'article étudie.

---

## 3. Ce que les streams ont changé dans l'article

Quatre résultats déplacent la thèse. Aucun n'était anticipé dans le plan v1.

**L'article ne démontre plus une impossibilité, il mesure un plancher.** `Δe_c = 0.120 [0.114, 0.127]`, n = 300, encadré par deux points mesurés. Sous ce plancher aucune calibration CUSUM ne satisfait simultanément le budget de fausses alarmes et le certificat de découplage ; au-dessus, la calibration existe et vaut `λ_op = 21.93 [19.88, 22.40]` sur `[0.20, 0.40]`. La remarque défensive de la v63 sur SEA et Hyperplane devient une prédiction vérifiée. La validité externe cesse d'être une excuse.

**L'effet Hydra n'est pas le mécanisme volumétrique du point aveugle.** 99,3 % de l'effacement provient de l'apprentissage incrémental ordinaire des `M−1` arbres survivants. 100 % des remplacements installent un arbre n'ayant rien appris. Les swaps sont un accélérateur d'amorce (`min_i τ_i`, 4,1× à 8,0×) et un verrou décisionnel terminal (jusqu'à 23 % de détection résiduelle supprimée), pas la source de l'effacement. Le titre de l'article et la contribution (C1) s'en trouvent affectés.

**Le budget de preuve change de signe pour `Δe ≥ 0.452`.** `A / A_rect` passe à `−0.15` puis `−14.12`. L'ensemble adapté termine la fenêtre avec une erreur **inférieure** à son niveau pré-dérive (0.010 contre `e_pre = 0.024` à `Δe = 0.498) : un décalage de frontière lointain rend les classes plus séparables. Il n'y a pas d'excès d'erreur à détecter au haut de la grille. Le domaine de validité du phénomène est borné des deux côtés, et cela doit être écrit.

**Le plateau `q05 ≈ 13` est un artefact de chauffe.** À `T_DRIFT = 4000` il disparaît (25.70 / 30.95 / 54.70 / 54.70). Le manuscrit l'invoquait comme signature de swaps pilotés par le bruit et l'utilisait pour justifier le plancher de l'enveloppe opérationnelle. Réfuté par son propre G1.

**État des streams.** S1 clos, S2 jamais démarré (checkpoint en attente depuis la livraison S1). S4 livré et appliqué via S6. S5 clos, résumé et conclusion hors périmètre. S6 clos et consolidé. S7 clos sur son plan, **pas sur sa spécification** : Lot 3 (`protocol_v2.tex`), T2.2 (F16, `warning_detector` R3/R4) et T2.4 (F21, oracle `Δe` gelé) n'ont jamais été portés au plan.

---

## 4. Actions à réaliser

Par ordre de blocage décroissant.

**A1 — Trancher `δ_P` : 0.005 ou 0.01.** `exp_R8_lambda_op_sweep.py` fixe 0.005, le manuscrit dit 0.01, le registre SSOT porte les deux (`DELTA_P = 0.005`, `R2_CUSUM_DELTA = 0.01`). Conséquence : facteur 2 sur `θ*`, trois ordres de grandeur sur `ARL₀` à `λ = 50`. **Bloquant pour S2** : aucun chiffre de fausse alarme du manuscrit n'est publiable avant arbitrage. Recommandation : retenir 0.01, valeur du manuscrit et de l'audit S6 (`S6_AUDIT_DELTA_P`), corriger le script R8, accepter le déplacement de `λ_op`.

**A2 — Trancher le sort de R8.** Son surrogat rectangulaire est retiré de Definition 11. `tests/test_R8_lambda_op.py` teste trois affirmations supprimées : il échoue ou valide du texte mort. Trois options : retrait de l'expérience, requalification en annexe de reproductibilité historique, ou repointage du test sur `envelope_stats.json`. Ne pas neutraliser le test. Le README ligne ~227 et la note de reproductibilité R8 sont périmés dans les trois cas.

**A3 — Arbitrer le périmètre d'écriture `CLAUDE.md` §2.** Claude Code a tranché unilatéralement « the stream spec wins » sur l'immutabilité de `run_all.sh` et `README.md` ; S7 a retiré la décision. L'arbitrage vous appartient, faute de quoi chaque agent suivant rouvre le débat.

**A4 — Installer `docs/manuscript/CURRENT`** contenant le nom du `.tex` vivant, plus un test qui échoue si un autre `.tex` a été modifié. Sans cela la panne se reproduit à v65.

**A5 — Unifier le chemin de `framework_v2.tex`.** `transfer_S1.md` annonce `docs/manuscript/sections/`, le dépôt porte `docs/sections/`, et l'en-tête du fichier porte le premier. Les livrables S5 (`intro_v2.tex`, `related_work_v2.tex`) sont aussi sous `docs/sections/`. Choisir un chemin, corriger les trois références.

**A6 — Concaténer `articleA_biblio_v2.bib`** = v64 + additions S5 + les quatre entrées réclamées par `notation_map` (Lai 1998, Siegmund 1985, Kingman 1970, Tsybakov 2009). Non fait, signalé I7.

**A7 — Retirer `ass:repair` de `framework_v2.tex`.** S1 la déclare réfutable et non vérifiée ; S6 la réfute — le bras `no_swap` récupère sans aucun remplacement, jusqu'à 150,8 nœuds contre 47,9 pour `full`. L'hypothèse est fausse et elle est encore dans le cadre formel. Tout énoncé qui en dépend est à réexaminer.

**A8 — Trancher le titre.** « Defeat » relève de la même famille que les superlatifs supprimés, et l'effet Hydra n'étant plus le mécanisme, « adaptive classifiers defeat drift detectors » ne décrit plus le résultat. Trois options sont dans `terminology_map.md`.

**A9 — Trancher la cible de publication.** Ouvert depuis le premier tour. Le volume théorique et expérimental atteint exclut 8 pages. Recommandation inchangée : Journal Track ECML PKDD, ou DAMI / Machine Learning en soumission directe.

**A10 — Ne pas citer Fiddler.** Statut **X** dans `source_verification.md`, non vérifié en session.

## [Strategic Advice]

**Le risque dominant a changé de nature.** Il n'est plus théorique, il est organisationnel. Trois tours consécutifs ont produit un rapport annonçant une complétion supérieure à l'état vérifiable — mon propre diagnostic F23 inclus, construit sur des constantes lues sans ouvrir le script de calcul. Le mécanisme est constant : le plan devient le référentiel à la place de la spécification. La contre-mesure est dans les prompts livrés (table spécification → phase, déclarée avant exécution), mais elle ne tient que si vous refusez toute clôture de stream dont le rapport ne porte pas cette table.

**Deux résultats commandent le titre et la contribution (C1), et aucun n'est tranché.** L'effet Hydra n'est pas le mécanisme volumétrique : 99,3 % de l'effacement vient de l'apprentissage incrémental des arbres survivants. Et la contribution propre du premier remplacement n'est toujours pas identifiée, faute du bras `no_swap_ab_initio`. Si ce bras montre `A_full ≈ A_no_swap_ab_initio`, le remplacement d'arbres est causalement inerte, l'architecture d'ensemble devient incidente, et « When Adaptive Classifiers Defeat Drift Detectors » ne décrit plus le résultat. C'est la seule expérience du projet qui puisse encore forcer une réécriture de niveau papier. Elle est en T8.1 et devrait passer avant S9.

**Ce que le dossier a gagné et que personne n'a encore écrit dans le résumé.** `λ_op = 21.93 [19.88, 22.40]` est le seul nombre qu'un praticien peut régler, et `Δe_c = 0.120 [0.114, 0.127]` transforme la faiblesse de validité externe en prédiction vérifiée. Le résumé actuel promet encore un ensemble admissible vide et une immunité KSWIN. L'écart entre ce que le corpus démontre et ce que le résumé annonce est aujourd'hui le premier motif de rejet résiduel. Le résumé est hors périmètre S5 et non affecté : affectez-le, c'est une demi-journée.

**Angle mort que je n'avais pas vu et que je signale maintenant.** Le bras input-space annoncé en (C4) risque d'être structurellement aveugle au drift étudié : le générateur Bernoulli déplace la frontière de décision, donc `P(Y|X)`, à `P(X)` constant. Un détecteur sur `P(X)` ne verra rien — non par immunité, mais par cécité. Si c'est le cas, (C4) tel qu'écrit dans l'introduction v2 n'est pas tenable et le contrat d'interface I5 de S5 se déclenche. Le prompt S9 impose la vérification avant implémentation ; l'arbitrage sur (C4) vous reviendra.

**Sur A2.** Ne laissez pas `δ_P` ouvert un tour de plus. Il bloque S2, S2 bloque S3, et S3 lève le statut void de deux énoncés encore présents dans le manuscrit vivant. Un manuscrit qui contient `prop:starvation_boundary` et `cor:mcrit` marqués void dans la carte de notation mais vivants dans le `.tex` est exactement le genre d'incohérence que le reviewer #3 a déjà trouvée une fois.