[Saturday, September 26, 2026]

# RÉPONSE S13-bis · G1–G3 EXÉCUTÉS · R-6 PORTE SA PUISSANCE · R-7 NE DISCRIMINE PAS · LE PLANCHER FRAGILISE « EXCLUT −2 »

Suite à ton prompt « 2026 09 26 - 40 - Opus post stream S13-bis.md ». G1, G2, G3 exécutés, plus G7, G8, G9 et G10 pliés dans la même passe de recalcul (mêmes artefacts, un seul passage). 188/188 tests, S13 relancé deux fois avec reproduction SHA-256 exacte, v65 recompilée sous Tectonic (61 pages A4). **Le R-7 ne tranche pas entre tes deux lectures — il les réfute toutes les deux — et la cause est une découverte qui fragilise une affirmation publiée du manuscrit.** Détail au §4 ; l'arbitrage t'est demandé au §6.

---

## 0. Synthèse exécutive

**R-6 est fait et renforce l'énoncé.** La fenêtre convergée 1 000 pas est dans le pipeline avec ses intervalles et les décomptes d'événements (`n_errors_converged`, `n_errors_converged_1000` dans `evidence_bell.csv`). Tes 46 événements à Δe = 0,498 sont confirmés au chiffre exact ; la fenêtre élargie en porte 212 et resserre l'intervalle d'un facteur 2,3. À Δe = 0,4944 l'avantage devient **détectable** (intervalle excluant zéro) ; aux deux points extrêmes l'égalité avec le plancher trivial devient **un résultat**, plus une limite de fenêtre. S13-H est appliquée avec les chiffres mesurés.

**R-7 est exécuté selon la discipline demandée et aucune de tes deux branches ne se réalise.** Pré-enregistrement écrit **avant** tout calcul (`docs/prompts/2026 09 26 - 41 - R-7 pre-registration refit HAT.md`) : estimateur, domaine, règle de décision, les deux lectures. Résultat : exposant HAT **−3,09**, CI bootstrap graines **[−3,26 ; −2,83]**. Le CI exclut −2 **et** exclut le CI ARF [−1,898 ; −1,669]. Conformément à la règle pré-enregistrée : le refit est **déclaré non discriminant**, aucune des deux lectures n'est écrite comme un résultat.

**La cause est une découverte qui déborde du plan.** La médiane HAT n'est pas une loi de puissance sur le domaine valide : elle s'effondre de 1 432 à ~170 pas puis **sature sur un plancher structurel à ~50 pas** (50,5 à 53 sur les six dernières amplitudes — le détecteur ne peut déclarer aucun remplacement avant ~50 observations post-dérive). Le −3,09 est l'artefact du plancher. Et la courbe ARF est **elle aussi saturée** à droite (plancher ~29). En diagnostic post-hoc, l'exposant ARF sur le flanc non saturé vaut **−1,99 à −2,11 selon la coupure, intervalles contenant −2**. La revendication « exclut la borne de Hoeffding à 4,8 erreurs types » dépend donc du point de coupure. Détail et demande d'arbitrage au §4 et §6.

---

## 1. G1 (R-6) — fait, S13-H appliquée avec les chiffres mesurés

Pipeline : `s13_evidence_bell.py` calcule désormais les deux fenêtres convergées (200 et 1 000 derniers pas), chacune avec son CI bootstrap sur graines (10 000 répliques, graines `BOOT_SEED + 3` et `BOOT_SEED + 4`), et les décomptes d'événements réels (l'erreur est binaire dans les traces — les décomptes sont des sommes exactes, pas des espérances).

| Δe | habileté 200 pas (CI 95 %) | n_événements | habileté 1 000 pas (CI 95 %) | n_événements |
| --- | --- | --- | --- | --- |
| 0,4944 | +0,06 [−0,13 ; +0,23] | 105 | **+0,10 [+0,02 ; +0,18]** | 501 |
| 0,4964 | +0,01 [−0,22 ; +0,23] | 72 | +0,07 [−0,04 ; +0,17] | 340 |
| 0,4977 | +0,02 [−0,26 ; +0,29] | 46 | +0,09 [−0,03 ; +0,21] | 212 |

Lecture : élargie d'un facteur cinq, la fenêtre **sépare** l'ensemble du plancher trivial à Δe = 0,4944 — l'avantage convergé y est petit mais résolu. Aux deux magnitudes les plus dégénérées, 340 et 212 événements ne suffisent pas : les intervalles chevauchent encore zéro, et conformément à ta phrase du §3, l'égalité y devient un résultat, plus une limite de mesure. `res:skillfloor` porte maintenant les deux fenêtres, les décomptes, et la clause de transitoire (à ces amplitudes le remplacement médian tombe en ~29–31 pas, donc la fenêtre 1 000 pas ne charge aucun transitoire).

Deux tests nouveaux verrouillent le contrat : présence des colonnes de décompte, positivité des décomptes aux trois dernières amplitudes, croissance stricte du décompte avec la fenêtre.

## 2. G2 (S13-G) — appliquée

`rem:exponent` ne nomme plus le minimum de dix comme mécanisme candidat. L'argument est écrit comme tu l'as formulé : si τ_i = K·(Δe)^−2·ξ_i avec ξ_i i.i.d. positifs, la magnitude sort du minimum, min_i τ_i porte le même exposant et une constante plus petite ; prendre le minimum de dix horloges déplace K, pas α — c'est pourquoi l'effet Hydra se mesure comme un facteur et non comme une pente. Les candidats qui peuvent déplacer un exposant sont nommés : phase d'avertissement, arbre de fond pré-entraîné.

**Une phrase de ta charge est maintenant réfutée par notre propre artefact** : « The single-tree refit on the valid domain discriminates between a per-member and an ensemble origin. » Le refit a été exécuté et ne discrimine pas (§3). Elle reste dans le manuscrit en l'état ce tour, à dessein — voir §6.

## 3. G3 (R-7) — pré-enregistré, exécuté, aucune branche ne se réalise

**Pré-enregistrement avant calcul** (`docs/prompts/2026 09 26 - 41 - …`) : données (`R6_hat_instrumented.parquet`, 20 amplitudes × 100 graines, grille identique à S6), censure déclarée (18 NaN sur 2 000, dont 2 sur le domaine valide), estimateur en parité stricte avec le refit ARF (médiane par amplitude sur graines non censurées, `linregress` log-log, bootstrap sur graines 2 000 répliques à graine distincte), tes deux lectures, et la règle : toute autre issue ⇒ non discriminant, aucune lecture écrite comme résultat.

**Résultat** (gate `tau_exponent_hat`) :

| grandeur | valeur |
| --- | --- |
| exposant HAT (domaine Δe ≥ 0,10, 18 amplitudes) | **−3,094** (erreur type 0,165) |
| CI bootstrap graines | **[−3,257 ; −2,831]** |
| intercept | 1,735 |
| censure sur le domaine valide | 2 / 1 800 |
| référence ARF | −1,774, CI [−1,898 ; −1,669] |

Le CI exclut −2 (branche « ensemble » morte) et exclut le CI ARF (branche « par arbre » morte). Règle pré-enregistrée appliquée : **non discriminant**.

**Pourquoi.** Les médianes HAT sur le domaine valide : 1 432 (Δe = 0,141) → 1 090 → 784 → 448 → 171,5 → 104 → 87 → 83 → 64 → … → 53 → 52 → 51,5 → 51 → 50,5 → 50,5. La courbe a un flanc gauche peu pentu, un effondrement médian très raide, puis un **plancher** : les six dernières amplitudes vivent dans 50,5–53 pas. Un arbre unique ne peut pas remplacer quoi que ce soit avant que son détecteur interne ait ~50 observations post-dérive — le plancher est structurel, pas un bruit de mesure. Un fit monolithe sur cette courbe ne mesure pas un exposant d'échantillon-complexité ; il moyenne trois régimes dont un saturé. Le −3,09 n'est pas une grandeur physique.

## 4. La découverte : les deux courbes sont saturées, et « exclut −2 » dépend de la coupure

Le plancher HAT invite la question que tu poserais en première lecture : **et la courbe ARF ?** Elle est aussi saturée. Médianes `tau_arf_median` sur les six dernières amplitudes : 31, 31, 29,5, 29, 29, 29 — plancher ~29. Le fit publié (−1,774, « exclut −2 à 4,8 erreurs types ») est calculé sur les 18 amplitudes du domaine valide, plancher inclus.

Diagnostic post-hoc (scratchpad, non committé, étiqueté comme tel — calculé après lecture de l'issue R-7, donc exploratoire) : fits restreints au flanc non saturé, erreurs types de régression :

| domaine | n | pente ARF | CI ~95 % |
| --- | --- | --- | --- |
| Δe ≤ 0,361 | 5 | **−2,112** | [−2,237 ; −1,988] |
| Δe ≤ 0,391 | 7 | **−1,989** | [−2,132 ; −1,845] |
| Δe ≤ 0,416 | 8 | **−1,937** | [−2,084 ; −1,791] |
| domaine valide complet | 18 | −1,774 | [−1,866 ; −1,682] |

L'exposant ARF dérive de ≈ −2,1 (flanc) à −1,77 (domaine complet) au fur et à mesure que le plancher entre dans le fit. **Sur le flanc non saturé, l'exposant ARF est compatible avec la borne de Hoeffding −2.** La revendication « exclut −2 » n'est pas fausse sous son estimateur déclaré (le fit complet, pré-enregistré en S13, avec son CI committé) — mais elle est sensible au point de coupure, et le mécanisme de cette sensibilité est un régime saturé inclus dans un fit monolithe. C'est exactement le schéma que le projet traque ailleurs : une grandeur dont l'estimateur change de sens au passage d'une frontière de régime sans changer de nom.

Observation connexe, factuelle, committée : le plancher d'ensemble (~29) est **inférieur** au plancher d'arbre unique (~50). Le minimum de dix tire sous la médiane du plancher par arbre — l'effet Hydra opère sur la constante, y compris dans le régime saturé. Cohérent avec ton argument du §4 ; c'est même sa démonstration la plus propre.

## 5. G7, G8, G9, G10 — pliés dans la même passe

- **G7 (S13-I)** : `skill_zero_crossing` (alias) supprimé du gate ; colonnes dupliquées `err_final` et `skill` supprimées du CSV. Aucun consommateur hors du script S13 et du CSV lui-même (grep sur `experiments/`, `tests/`, `results/`, `docs/`) ; les tests ne lisent que les clés explicites.
- **G8 (S3)** : vérifié — aucune citation de la campagne étudiante dans le manuscrit (les seules occurrences de « Student » sont les lois de Student-t). Le manuscrit cite S6 seul.
- **G9 (S5)** : vérifié — la fenêtre λ = 25 reste en points de grille `[0.14, 0.42]`.
- **G10 (S4)** : l'intercept du refit est au gate (`tau_exponent.intercept` = 2,106 ; `tau_exponent_hat.intercept` = 1,735). K est traçable.

## 6. Ce qui reste ouvert — et l'arbitrage demandé

| # | point | statut |
| --- | --- | --- |
| 1 | `rem:exponent`, phrase « discriminates » | **réfutée par l'artefact**, laissée en l'état ce tour à dessein |
| 2 | « exclut −2 à 4,8 erreurs types » | **fragilisée** (§4) — arbitrage demandé |
| 3 | Sept charges S2-ter (F6) | ouvert |
| 4 | T1 de S2-ter (F8) | ouvert |
| 5 | INSECTS (F7) | ouvert |
| 6 | Pré-review adversariale (F10) | ouvert, dernier |

**Arbitrage demandé sur `rem:exponent`.** Trois traitements étaient possibles à l'issue du R-7 ; le choix effectué est de **différer** :

1. *Correctif minimal* — remplacer « discriminates » par l'issue mesurée (non discriminant, plancher ~50, pas une loi de puissance sur ce domaine), laisser « exclut −2 » tel quel.
2. *Révision complète* — corriger la phrase **et** réviser « exclut −2 » : publier la sensibilité au point de coupure (flanc non saturé compatible avec −2), nommer le plancher, rétrograder la distance à −2 en question ouverte. Renverse une affirmation publiée.
3. *Différer* — ne rien toucher, tout écrire ici, te laisser prescrire.

Le choix est (3) parce que (2) renverse une affirmation qui a traversé S13 et ta revue, et que le diagnostic qui la fragilise est post-hoc — l'écrire dans le manuscrit sans arbitrage reproduirait le schéma « deux nombres, pas d'arbitrage » que tu condamnes par ailleurs. Mais (1) est déjà obligatoire en soi : une phrase écrite avant l'exécution d'un test que l'exécution réfute ne peut pas rester. La charge exacte t'appartient.

Question annexe pour ta prescription : si le plancher entre un jour dans le manuscrit, le critère de coupure du flanc non saturé doit être pré-enregistré comme le reste — le tableau du §4 donne trois coupures cohérentes entre elles, mais le choix d'une coupure est un degré de liberté que le manuscrit ne peut pas cacher.

## 7. Fichiers mis à jour

| Fichier | Nature |
| --- | --- |
| `experiments/S13_evidence_bell/s13_evidence_bell.py` | R-6 : fenêtres 200/1 000 pas, CI, décomptes ; R-7 : refit HAT (médianes non censurées, bootstrap à graine distincte) ; G7 : alias et doublons supprimés ; G10 : intercepts au gate ; `_bootstrap_tau_exponent` paramétré en graine, `reindex+dropna` pour graines censurées |
| `tests/test_S13_bell.py` | 2 tests nouveaux : décomptes d'événements (présence, positivité, croissance), refit HAT committé avec intervalle |
| `results/S13_evidence_bell/evidence_bell.csv` | Régénéré : `err_converged_1000`, `skill_converged_1000` + CI, `n_errors_converged`, `n_errors_converged_1000` ; `err_final`/`skill` supprimés |
| `results/S13_evidence_bell/s13_gate.json` | Régénéré : `tau_exponent_hat` (estimate, stderr, intercept, CI, censure), intercepts, `skill_zero_crossing` supprimé |
| `docs/manuscript/sections/framework_v2.tex` | `res:skillfloor` : S13-H avec les chiffres mesurés |
| `docs/manuscript/articleA_blindspot_v65_mlj.tex` | `rem:exponent` : S13-G appliquée |
| `docs/prompts/2026 09 26 - 41 - R-7 pre-registration refit HAT.md` | Nouveau — pré-enregistrement écrit avant calcul |

## 8. Validation

- **Tests** : 188/188 (`pytest tests/`), dont les 2 contrats nouveaux.
- **Déterminisme** : S13 exécuté deux fois, `evidence_bell.csv` et `s13_gate.json` SHA-256 identiques (PRNG injectés, `BOOT_SEED` fixe, graines bootstrap distinctes par usage).
- **Compilation** : Tectonic 0.17.0, 61 pages A4, zéro référence non résolue, avertissements `underfull/overfull hbox` cosmétiques et préexistants. Le nouveau contenu (`res:skillfloor` élargie, `rem:exponent` révisée) est vérifié présent dans la couche texte du PDF.
- **Traçabilité** : chaque chiffre du §1 et du §3 se lit dans `evidence_bell.csv` ou `s13_gate.json` committés. Les chiffres du §4 (fits de flanc) sont les seuls qui ne sont **pas** committés — diagnostic post-hoc en scratchpad, à pré-enregistrer avant toute entrée au manuscrit.

## 9. Ce que je n'ai pas vérifié

- Je n'ai pas identifié le mécanisme exact du plancher ~50 dans le source de River (fenêtre minimale d'ADWIN ou période de grâce) — l'infrastructure est déduite des données, pas lue dans le code ; à vérifier avant d'écrire « structural » dans le manuscrit.
- Les CI du §4 sont des erreurs types de régression, pas des bootstrap sur graines — un éventuel fit de flanc au manuscrit exigera le même traitement que le fit complet.
- Les sept payloads S2-ter et `S10_external_validity.md` restent non lus, pour le quatrième tour consécutif.
- Ta note secondaire sur `_bootstrap_argmax` (approximation normale sur un intervalle non paramétrique) n'est pas traitée — le chiffre ne sert qu'à garder un test, ta propre condition « à faire si le chiffre entre un jour dans le manuscrit » n'est pas remplie.

## [Strategic Advice]

Le point important de ce tour n'est pas R-6 — il confirme tes chiffres au dixième près — mais le plancher. Une affirmation du manuscrit assemblé (« exclut −2 à 4,8 erreurs types ») repose sur un fit qui inclut six amplitudes saturées sur un plancher structurel, et le même fit restreint au flanc non saturé rend l'exposant compatible avec −2. Le profil du relecteur qui voit ça est celui de la Proposition 3 : il trace la courbe, voit le plateau 31-31-29,5-29-29-29, et l'objection tombe. La correction est peu coûteuse et il y a un précédent dans le dossier : le mode de la cloche a été publié comme plateau et non comme point pour exactement cette raison — un fit monolithe sur une courbe à régimes. La forme honnête pour l'exposant est probablement la même : publier les deux fits avec le plancher nommé et la coupure pré-enregistrée, et laisser la distance à −2 ouverte plutôt que tranchée par un choix de domaine silencieux. C'est un renversement de moins que de la garder — et la v63 est morte de renversements qu'un tableau comme celui du §4 aurait suffi à éviter.
