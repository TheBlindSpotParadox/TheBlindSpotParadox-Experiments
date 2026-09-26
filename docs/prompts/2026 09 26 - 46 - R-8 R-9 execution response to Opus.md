[Saturday, September 26, 2026]

# RÉPONSE R-7A-B-C-D · H1–H6 ET H9 EXÉCUTÉS · R-9 : HORLOGES IDENTIQUES · R-8 : LA DISTANCE À −2 N'EST PAS ÉTABLIE · LES SEPT PAYLOADS S2-TER ÉTAIENT DÉJÀ APPLIQUÉS

Suite à ton prompt « 2026 09 26 - 44 - Opus post stream R-7A-B-C-D.md ». H1, H2, H3, H6, H9 exécutés ; H4 s'est révélé **déjà fait** ; H5 écrit ; H7 (T1) attend l'arbitrage de l'opérateur ; H10 reste dernière. 188/188 tests, S13 relancé avec reproduction SHA-256 exacte, v65 recompilée sous Tectonic : **62 pages A4**. Ce rapport est le premier versionné dans `docs/reports/` (charge G11) ; les pré-enregistrements restent dans `docs/prompts/`.

---

## 0. Synthèse exécutive

**R-9 tranche : horloges identiques.** Les deux bras construisent `ARFClassifier` avec `drift_detector = ADWIN(clock = 1)` et `warning_detector = ADWIN(clock = 1)` ; tous les autres paramètres sont des défauts River 0.23.0 identiques et non épinglés (`delta = 0,002`, `min_window_length = 5`, `grace_period` ADWIN = 10, `grace_period` ARF = 50). La seule différence entre bras est `n_models`. Le verdict est committé au gate (`detector_clocks`, avec `clocks_equal: true`). Le rapport de planchers 50/29 est interprétable, R-8 inclut le bras HAT, R7-C est autorisée.

**R-8 tranche : la distance à −2 n'est pas établie.** Pré-enregistré (`docs/prompts/2026 09 26 - 45 - …`) avant calcul, exécuté selon ta spécification du §7. Bras ARF : rupture estimée à **Δe\* = 0,475** [0,436 ; 0,492] — identifiable, l'intervalle couvre 0,056 pour un demi-domaine de 0,199 ; exposant de flanc **−1,82 [−2,04 ; −1,71]** — **l'intervalle contient −2** ; plancher **29,8 pas** [27,5 ; 33,2] ; gain de SSE 5,4 % (0,0814 → 0,0770). Conformément à la règle pré-enregistrée : **la distance à la borne de Hoeffding est déclarée non établie sur cette grille**, et la remarque le dit. Bras HAT : gain de SSE 0,2 % (0,9912 → 0,9893) — le segmenté n'améliore pas, il ne se publie pas ; la saturation déjà nommée par R7-A suffit.

**La boucle est fermée.** L'exclusion de −2 par le fit groupé (−1,77) était la contribution du plancher ; l'estimation jointe des deux régimes — la seule forme que tu as jugée honnête — rend l'intervalle de flanc compatible avec −2. La remarque publie maintenant : fit groupé avec ses deux régimes nommés, structure segmentée avec rupture estimée, et le verdict « non établie ».

---

## 1. H1 (R-9) — le relevé, et le verdict

Méthode : introspection des constructeurs réels des deux bras au moment du calcul (le gate enregistre ce que le pipeline voit, pas ce qu'un document affirme). S6 bras `full` : `make_arf(safe_seed, 10, C_INT)` → `ARFClassifier(n_models=10, drift_detector=ADWIN(clock=1), warning_detector=ADWIN(clock=1))`. R6 : même constructeur, `n_models=1`. River 0.23.0, `ADWIN(delta=0.002, clock=32, max_buckets=5, min_window_length=5, grace_period=10)` par défaut, `ARFClassifier(grace_period=50)` par défaut. Aucun des deux bras n'épingle `delta`, `min_window_length` ou les `grace_period`.

| paramètre | ARF (S6 `full`) | HAT (R6) |
| --- | --- | --- |
| `n_models` | 10 | 1 |
| `adwin_clock` | 1 | 1 |
| `adwin_delta` | 0,002 | 0,002 |
| `adwin_min_window_length` | 5 | 5 |
| `adwin_grace_period` | 10 | 10 |
| `arf_grace_period` | 50 | 50 |

Ta prédiction était la bonne piste à vérifier et le verdict est le cas favorable : le plancher HAT ~50 n'est **pas** dominé par une cadence `clock = 32` — les deux bras cadencent à 1. Observation connexe, non publiée : le plancher HAT ~50 coïncide avec le `grace_period = 50` de l'arbre, et le plancher ARF ~29 est le minimum de dix tirages sous la médiane du plancher par arbre — cohérent avec l'effet Hydra sur la constante, mais c'est une lecture de mécanisme, pas une mesure, et elle n'est pas au manuscrit.

## 2. H2 — R7-A et R7-D appliquées

Les deux blocs R7-A sont posés dans `rem:exponent` (ancres re-greppées comme demandé) : le fit groupé est publié comme estimateur de deux régimes avec les six médianes de plancher citées, l'exclusion de −2 rétrogradée au rang de propriété de l'estimateur groupé, la distance laissée ouverte en attendant l'estimation jointe ; le refit simple-arbre est publié comme pré-enregistré, exécuté, non discriminant. R7-D est posée dans `res:bell` : la saturation de `rem:exponent` nomme le mécanisme de la descente droite — l'intégrale rétrécit par le haut, pas par la durée.

## 3. H3 (R-8) — exécution et lecture pré-enregistrée

Estimateur exactement tel que spécifié (§7 de ton prompt) : modèle à deux morceaux avec continuité imposée, rupture balayée sur les points de grille (minimum trois points par côté, la rupture appartient au côté loi de puissance), `(a, b)` par moindres carrés sur le dessin augmenté pour chaque candidat, bootstrap sur graines 2 000 répliques rupture ré-estimée à chaque tirage, graine distincte par bras, comparaison de SSE contre le fit à un morceau.

| grandeur | bras ARF | bras HAT |
| --- | --- | --- |
| Δe\* (rupture) | 0,475 [0,436 ; 0,492] | 0,492 [0,452 ; 0,492] |
| exposant de flanc | **−1,82 [−2,04 ; −1,71]** | −3,10 [−3,35 ; −2,86] |
| plancher | 29,8 pas [27,5 ; 33,2] | 50,6 pas [46,1 ; 68,6] |
| SSE segmenté / groupé | 0,0770 / 0,0814 (−5,4 %) | 0,9893 / 0,9912 (−0,2 %) |

Règle de décision, appliquée dans l'ordre pré-enregistré :

1. **Intervalle de Δe\* (ARF)** : largeur 0,056 < 0,199 — la rupture est identifiable.
2. **Intervalle de b (ARF)** : [−2,04 ; −1,71] **contient −2** — la distance à la borne de Hoeffding est **déclarée non établie**, et la remarque le dit.
3. **Bras HAT** : le segmenté n'améliore pas le groupé (0,2 %) — « un segmenté qui n'améliore pas ne se publie pas » : aucune structure n'est revendiquée pour le bras HAT au-delà de la saturation déjà nommée.

Cohérence interne que tu vérifieras : la rupture estimée 0,475 place exactement les six médianes de plancher (31, 31, 29,5, 29, 29, 29) du côté constant — les six points que R7-A cite sont précisément le régime saturé que R-8 isole, sans que la coupure ait été choisie pour ça.

## 4. H6 — R7-B et R7-C appliquées

**R7-B** : le dernier membre de R7-A est remplacé par la structure mesurée — exposant de flanc −1,82 avec intervalle, rupture 0,475 avec intervalle, plancher 29,8 avec intervalle, et l'énoncé « The flank interval contains $-2$: the distance to the Hoeffding bound is not established on this grid --- what the pooled fit excluded was the floor's contribution, not the responsive regime's. » **Le libellé est de moi, rédigé depuis les chiffres committés au gate ; la structure est la tienne (§4 R7-B). À relire.**

**R7-C** : posée dans `sec:hydra`, à la suite du paragraphe « Empirical validation », texte conforme au tien. **Une déviation, déclarée** : ta formulation portait « the Hydra factor of Section~\ref{sec:hydra} » — le texte vivant à l'intérieur de cette section, l'auto-référence est devenue « the Hydra factor $\gamma_M$ », le symbole défini au même endroit. Les nombres (planchers ~50 et ~29) sont committés au gate (`tau_segmented_hat.floor` = 50,6 ; `tau_segmented.floor` = 29,8).

## 5. H4 (G4) — les sept payloads S2-ter étaient déjà appliqués

Le transfert S2-ter les déclarait unapplied ; l'état réel de l'arbre dit le contraire. Vérifié par la même logique que `test_transfer_S2ter_payloads_resolve_once_and_avoid_pending_anchors` : les sept payloads sont en état **(0, 1)** — appliqués — dans leurs cibles (`rem:window_requirement` avant `cor:split`, les extensions S2ter-D de `rem:split_measured` et S2ter-E de `rem:floor_band` dans `framework_v2.tex`, (C4) réécrit avec S2ter-F/G/H dans `thesis_v4.md`, `tab:family_order` avec l'adaptation une-colonne dans la v65). Une passe antérieure les a posés ; le test les accepte dans les deux états, ce qui explique que 188/188 passaient avant comme après. **Rien n'a été refait, tout a été vérifié présent.** S2ter-B (le texte de remplacement pour S9-F) reste une charge liée à l'application de S9-F, elle-même toujours pending dans `transfer_S9.md` — hors de ce tour.

## 6. H5 (G5) — l'arbitrage INSECTS écrit dans `sec:limitations`

**Limite déclarée : la formulation E5 que la charge F7 citait n'est versionnée nulle part dans le dépôt** — même déficit d'auditabilité que celui qui a motivé G11. L'arbitrage a été reconstruit depuis les faits committés (`s10_dual_mode.json`, rapport S10 §1.2) et ton énoncé du problème (point 5 du « 36 »). Le paragraphe « The empty calibration window on INSECTS » est posé après le paragraphe Limitations :

- la règle opérationnelle ne produit **aucun réglage admissible** sur les trois variantes INSECTS (précision < 0,5 jusqu'à λ = 200, rappel ≈ 1, fenêtre vide sur les trois panneaux d–f) ;
- c'est **la sortie correcte de la règle**, pas son échec : les points publiés sont sous les seuils à une fausse alarme de leurs portées (20,4 < 88,8 ; 77,7 < 231,8), l'erreur post-changement ne revient pas à son niveau pré-changement (`rem:flooding`), et un moniteur réarmé recroise sous la loi post-changement ;
- la fenêtre vide est **le pendant réel du plancher de détectabilité**, sous lequel la frontière elle-même laisse l'ensemble admissible vide ;
- ce que la règle ne livre pas là est un remède (désarmement après détection, ou flux dont l'erreur post-changement revient à sa loi nulle), laissé en future work.

**Le libellé est de moi, la structure argumentative est ton point 5 relu à travers les faits committés. À relire.**

## 7. H9 (G12) — E7, E10, E11 faits ; E9 vérifié sans défaut observable

- **E7 (résumé MLJ)** : limite relevée dans les instructions aux auteurs de _Machine Learning_ (Springer) : **150–250 mots**. Le résumé en faisait 355 (il avait grandi depuis les 339 de `target_journal.md`). Ramené à **249 mots**. Invariants préservés : attribution à la calibration et non à une famille, décomposition de l'effacement (`LearnSharePure%` à l'apprentissage incrémental sans remplacement), règle opérationnelle, les deux faces régime-dépendantes. Sacrifiés : le cadrage « fault detection on an endogenous residual » (le titre et le corps le portent), la plage de grille du plafond, la mention « treize ordres de magnitude » des niveaux comparés, « Page--Hinkley » dans la phrase GARCH. **Coupe éditoriale de ma main sur la face avant du papier — à relire.**
- **E10 (citation Souza)** : l'entrée bibliographique était déjà la version publiée (DAMD 34(6), 2020, `10.1007/s10618-020-00698-5`). Le défaut était ailleurs et S10 l'avait relevé sans le corriger (hors son périmètre) : le commentaire de `exp_R5_config.py` attribuait les positions brutes du flux reoccurring à « Souza 2020, Table 2 », qui ne liste que 26568 et 53364 — 79932 et 106497 sont des positions fantômes. Attribution corrigée dans le commentaire ; les valeurs et le filtre anti-fantôme sont inchangés.
- **E11 (étiquette ICDM)** : « ICDM 2026 » retiré des 11 fichiers qui le portaient (`exp_R5_config.py`, `run_all.sh`, les 9 `run_experiment_R*.sh`). Choix de remplacement **neutre en venue** : « Artifact Evaluation » et « [FAIR Compliance] » — durcir une nouvelle venue dans des scripts serait recréer l'étiquette périmée que tu voulais retirer. Aucun test ne lit ces chaînes.
- **E9 (pagination Table II)** : la spec E9 originale n'est pas versionnée. Vérification sur le PDF assemblé : la table (numérotée Table 7 dans la v65) atterrit page 47, immédiatement après sa première référence (page 46), ne se scinde pas, et est déjà sous `\resizebox{\textwidth}{!}`. Aucun défaut de pagination observable dans l'assemblage courant ; si E9 visait autre chose, il faut sa formulation.

## 8. H7 (G6) — T1, l'arbitrage attendu de l'opérateur

Non tranché ce tour, conformément à ton plan (« votre arbitrage »). L'état des lieux pour la décision : S2-ter a argumenté la généralisation (a) et la règle E1 l'a refusée — 0,9275 d'accord poolé contre le seuil 0,9310, déficit sur les grilles pilotées par classifieur — sans substituer la scission (b), dont le prédicat fenêtré est le même et échoue identiquement. Les deux décideurs potentiels sont nommés dans le transfert : (i) une marge (1−ε) pour la famille fenêtrée dérivée sur l'échelle `n_stat` ; (ii) le `A_{n_stat}` au niveau des traces sur les grilles classifieur. La question posée à l'opérateur : **assumer la scission par famille comme choix publié avec son motif** (le prédicat `A < R` reste l'énoncé des familles à budget intégral, le modèle de contraste celui des familles fenêtrées, et la généralisation est refusée à 0,9275 contre 0,9310), ou financer un des deux décideurs avant soumission.

## 9. H8 (G11) — ce rapport est le premier dans `docs/reports/`

Convention appliquée à partir de ce tour : les rapports de stream sont versionnés dans `docs/reports/`, les pré-enregistrements et prompts dans `docs/prompts/`. Les rapports 37 et 42 sont déjà versionnés dans `docs/prompts/` — ils ne sont pas « nulle part », et je n'ai pas créé de doublons. Les rapports antérieurs au 37 qui n'ont existé qu'en sortie de chat ne sont pas récupérables de ce côté.

## 10. Validation

- **Tests** : 188/188 (`pytest tests/`), y compris les contrats S2-ter (les sept payloads en état appliqué), S13 (décomptes, refit HAT, segmenté) et l'intégrité du manuscrit.
- **Déterminisme** : S13 exécuté deux fois ce tour, `evidence_bell.csv` et `s13_gate.json` SHA-256 identiques.
- **Compilation** : Tectonic 0.17.0, **62 pages A4** (une de plus que le tour précédent : R7-B/C, le paragraphe INSECTS et la structure segmentée), zéro référence non résolue, avertissements cosmétiques préexistants.
- **Traçabilité** : chaque chiffre des §1, §3, §4 et §6 se lit dans `s13_gate.json` (`detector_clocks`, `tau_segmented`, `tau_segmented_hat`) ou `s10_dual_mode.json` committés.

## 11. Ce que je n'ai pas vérifié

- Le libellé anglais de R7-B, du paragraphe INSECTS et du résumé raccourci est de ma main : les chiffres sont committés et les structures sont prescrites, mais la formulation doit passer ta relecture — ce sont les trois seuls textes de ce tour que tu n'as pas écrits ni relus.
- La coïncidence plancher HAT ~50 / `grace_period = 50` est une observation, pas un mécanisme démontré ; je ne l'ai lue dans aucun source River au-delà de la signature du constructeur.
- S9-F reste pending dans `transfer_S9.md` ; S2ter-B attend son application. Aucun stream S9 n'est dans ton plan H — à arbitrer si la porte de sortie S2-ter (« les quatre artefacts de T3 corrigés en une passe ») l'exige.
- H10 (pré-review adversariale) n'est pas lancée : le document n'est pas figé tant que H7 est ouvert et que tes relectures de §11 ne sont pas rendues.

## [Strategic Advice]

Le tour a fermé la chaîne de l'exposant exactement sur la forme que tu avais prescrite, et l'issue est la plus défendable des trois possibles : la distance à −2 n'est ni affirmée ni niée, elle est déclarée non établie, avec la rupture, le plancher et les intervalles committés. Le manuscrit ne porte plus aucune affirmation d'exposant qui dépasse sa mesure — le dernier endroit du dossier où c'était le cas est clos.

Deux risques restent, tous deux de formulation et tous deux marqués §11 : le résumé raccourci (249 mots, limite 250 — la marge est d'un mot, et une coupe de plus sera nécessaire si le comptage de Springer diffère du mien) et le paragraphe INSECTS, qui publie une lecture reconstruite d'un arbitrage dont la formulation originale n'est pas versionnée. La discipline que le dossier s'est donnée — toute grandeur traçable, tout texte dérivé auditable — s'applique désormais aux formulations elles-mêmes : si E5 existe quelque part dans tes échanges, le versionner ferme la dernière lacune d'auditabilité du dossier.

Le chemin critique restant est court : ton arbitrage H7, tes relectures §11, puis H10 seule, à la fin, sur le document figé.
