[Saturday, September 26, 2026]

# RÉPONSE R8-A…E · REVUE CRITIQUE DES TOURS S13 → R-9 · LE « PLANCHER » N'EXISTE PAS · LE MODÈLE SEGMENTÉ EST INVALIDÉ · I1–I9 EXÉCUTÉS, H10 DIFFÉRÉE

Suite à ton prompt « 2026 09 26 - 48 - Opus post stream R-8A-B-C-D.md ». Arbitrages de l'opérateur pour ce tour : corrections hors liste appliquées, gardes durcies, Table 7 re-composée, commit local sur `main` sans push, arrêt avant H10. 190/190 tests, `sha256sum -c` à 27 OK / 7 FAILED (ensemble identique à la liste autorisée), v65 compilée sous Tectonic : 63 pages A4, zéro référence non résolue.

Règle appliquée à tout ce qui suit : chaque grandeur citée porte le fichier commité d'où elle sort. Les seuls calculs de session non commités sont signalés comme tels.

---

## 0. Synthèse exécutive

**Aucune des cinq charges R8 n'était applicable telle quelle.** Toutes ont été appliquées sous une forme corrigée, chaque écart motivé au §2 avec sa preuve.

**Le « plancher » du bras ARF n'existe pas.** Les six médianes 31, 31, 29,5, 29, 29, 29 (`evidence_bell.csv`, `tau_arf_median`, Δe ≥ 0,482) couvrent un facteur 1,032 en Δe. Une loi en −2 y prédit une baisse de 6,1 % ; les médianes baissent de 6,5 % (`s13_gate.json :: tau_segmented.minus2_decline_past_break`, `median_decline_past_break`). La pente MCO de ces six points vaut −2,58 (`tau_segmented.post_hoc.tail_ols_slope`). Le plateau est un effet visuel de la compression de la grille près de Δe = 0,5, lu à l'œil au rapport 42 et jamais contrôlé en échelle logarithmique. Tout le récit R7-A → R8-A en dépend.

**Le modèle segmenté est invalidé empiriquement.** Il n'est préféré par aucun critère qui pénalise son paramètre supplémentaire : F(1,15) = 0,85, p = 0,37 (anti-conservateur, la rupture étant cherchée sur la grille) ; AIC −93,19 contre −92,18 et BIC −91,41 contre −89,51 en faveur de la loi à un morceau (`tau_segmented.post_hoc`). L'inclusion de −2 dans l'intervalle de flanc ne vient pas du départ des six points : rupture fixée à son estimation, l'intervalle vaut [−1,948 ; −1,714] et exclut −2 (`post_hoc.exponent_ci_break_fixed`). Elle vient entièrement de la ré-estimation de la rupture à chaque tirage, dans un modèle que les données ne sélectionnent pas.

**Le verdict « non établi » survit, son motif change.** La distance à −2 dépend d'un choix de modèle que la grille ne tranche pas : exclue sous la loi à un morceau, incluse sous la loi à deux morceaux, sans préférence entre les deux. `rem:exponent` porte désormais ce motif, et plus aucune affirmation de plancher.

**Trois textes déjà publiés dans la v65 étaient faux au regard des artefacts.** Il s'agit de R7-A/R7-B (plancher, « zero local slope »), R7-C (« cleanest demonstration that the min-of-M onset acts on the constant ») et R7-D (la saturation expliquerait le flanc droit de la cloche). S13-G appliquait hors de son domaine un résultat juste. Tous sont corrigés ou retirés (§3).

**Deux payloads appliqués passaient pour « pending »** (S8-2, S10-C), masqués par des gardes qui acceptaient (1, 0). C'est ton conseil stratégique, instancié deux fois. Les cinq gardes n'acceptent plus que l'état appliqué ; une contre-épreuve par mutation le confirme (§5).

---

## 1. Statut des actions I1–I10

| # | action | statut |
|---|---|---|
| **I1** | gate + R8-A | **fait, corrigé** — `delta_estimate` et `ci_width_ratio` non ajoutés (le texte qui les citait est faux, §2.1) ; ajoutés à la place : `sse_gain`, `minus2_decline_past_break`, `median_decline_past_break` (cités au manuscrit), bloc `post_hoc` (rapport seulement) ; `rem:exponent` réécrite (§3.1) |
| **I2** | vérifier 0,262, puis R8-B | **fait, corrigé** — 0,262 est bien le panneau *abrupt* (`s10_dual_mode.json`, panneau d, `p0` = 0,2617) ; paragraphe INSECTS réécrit (§2.2) |
| **I3** | R8-C, le résumé | **fait** — 223 mots (compteur A) / 225 (compteur B), contre 246 / 251 pour le résumé commité ; cadrage restitué ; retraits listés (§4) |
| **I4** | T1 : 0,9275 / 0,9310, puis R8-D et R8-E | **fait, corrigé** — les deux numéraux ne vivent que dans un test (`tests/test_S2ter_predicate.py::test_published_verdicts`, fractions 3673/3960 et 715/768), pas sous `results/` : non cités ; le texte s'appuie sur les numéraux déjà publiés (93,1 %, 62/80, 36/40) (§2.3, §2.4) |
| **I5** | S9-F / S2ter-B | **résolu, hors de tes deux branches** — S9-F est **appliqué** avec le texte de S2ter-B (`framework_v2.tex`, après `eq:Rkswin_contrast`) ; l'affirmation non restreinte n'est dans aucune version ; seuls les documents de transfert disaient « pending » → errata |
| **I6** | clause de R7-C | **sans objet** — R7-C retirée (§3.2) |
| **I7** | E9 | **fait** — Table 7 (ex-« Table II ») rendue à 4,48 pt → **7,21 pt** ; débordements 15 → 1 (37,3 pt → 2,2 pt) (§6) |
| **I8** | verser E5 | **fait** — `docs/prompts/2026 09 26 - 49 - E5 INSECTS arbitration original formulation.md` |
| **I9** | commit, cinq portes | **fait** — portes au §7 ; commit local sur `main`, sans push ; document non figé, en attente de ta validation |
| **I10** | H10 | **différée** par l'opérateur — protocole proposé au §8, deux décisions t'appartiennent |

---

## 2. Les défauts des charges R8, un par un

### 2.1 R8-A — l'attribution causale est fausse, et le modèle qu'elle défend est invalidé

Ta charge écrivait : « its interval is 44% wider, the six floor points having left the fit. The pooled exclusion of −2 was therefore produced by the floor […] the segmented model is preferred only weakly ». Trois affirmations, et les trois sont contredites par le gate.

| affirmation de R8-A | mesure (`s13_gate.json :: tau_segmented`) |
|---|---|
| l'élargissement vient du départ des six points | rupture fixée à 0,475 : IC [−1,948 ; −1,714], largeur 0,234 contre 0,229 groupé (+2 %). Ré-estimée à chaque tirage : [−2,040 ; −1,713], largeur 0,327 (+43 %). L'élargissement, et avec lui l'inclusion de −2, vient de l'incertitude de la rupture |
| le plancher a produit l'exclusion de −2 | les six points « de plancher » ont une pente MCO de −2,58 ; bout à bout, ils baissent de 6,5 % là où −2 prédit 6,1 % |
| le segmenté est préféré, faiblement | il ne l'est pas : F(1,15) = 0,85, p = 0,37 ; AIC et BIC préfèrent la loi à un morceau |

Le bootstrap R-8 a d'abord été rejoué à l'identique (graine `BOOT_SEED + 6`, IC [−2,0399 ; −1,7132] reproduit), puis le diagnostic a été ajouté au pipeline, pas calculé à côté : `_segmented_fit` / `_bootstrap_segmented` reçoivent un paramètre `fixed_k` (réutilisation, pas de nouvelle fonction), graine `BOOT_SEED + 8`. Les clés existantes du gate sont inchangées, `evidence_bell.csv` et `blindspot_map.csv` sont identiques octet pour octet, et deux relances donnent le même SHA-256. Le bloc `post_hoc` porte la mention « computed after the R-8 verdict was read; not pre-registered ». Le manuscrit ne cite de ce bloc aucun chiffre ; il cite `sse_gain` (5,4 %, déjà pré-enregistré comme quantité à rapporter) et les deux déclins, qui sont de l'arithmétique sur la grille et les médianes commitées.

**Défaut du pré-enregistrement R-8, déclaré par erratum** (`docs/prompts/… - 45 - …`, ligne ajoutée, lignes existantes intactes). « Un segmenté qui n'améliore pas ne se publie pas » ne fixait aucun seuil. Le tour H a lu 5,4 % comme une amélioration et 0,2 % (HAT) comme une absence d'amélioration : la ligne a été tracée après lecture.

### 2.2 R8-B — quatre erreurs de fait, dont une duplication

| élément de R8-B | fait (`s10_dual_mode.json`, panneaux c–f) |
|---|---|
| « precision peaks at 0.24 on gradual_balanced » | 0,24 est la valeur à λ = 95, premier point au-delà de λ_FA = 88,8. Le pic vaut **0,333**, à λ = 135 et 200 |
| « at the grid points that reach or approach those levels » | sur *reoccurring*, λ_FA = 231,8 est **hors grille** (maximum 200) ; aucun point ne l'atteint |
| « Correction 3 — le remède manque » | la phrase du remède était **déjà** dans la v65. Ton bloc SEARCH s'arrêtait avant elle, donc R8-B appliqué tel quel l'aurait **dupliquée** |
| « Ajout gratuit » : axe p₀, ProteuS « every threshold passes » | ProteuS : rappel **0** pour λ ≥ 15, fenêtre admissible [5 ; 8] seulement. INSECTS : `rem:flooding` établit que les alarmes d'inondation ne sont **pas** des fausses alarmes du régime nul ; le mécanisme est la loi post-changement, pas p₀. L'unification contredit le manuscrit |
| « visible independently of the rule in the post-change error » | mesuré sur *gradual* seulement (`s2_flooding_retrodiction.json`, 0,50 contre 0,058) ; rien de commité pour *abrupt* ni *reoccurring* |

S'y ajoute un défaut du texte du tour H, relevé en vérifiant R8-B : « recall stays near 1 » est faux sur *abrupt* (0,71 à λ = 135 ; 0,61 à λ = 200) et sur *gradual* (0,20 et 0,27 à λ = 45 et 65).

Paragraphe publié, en substance : la précision reste sous 0,5 à tout seuil de la grille (au plus 0,41 / 0,33 / 0,22 sur *abrupt* / *gradual* / *reoccurring*) ; monter jusqu'au niveau à une fausse alarme ne rouvre pas la fenêtre (0,24 au premier point au-delà sur *gradual*, 0,33 au plus ensuite ; 0,22 à λ = 200 sur *reoccurring*, dont le niveau est hors grille) ; la cause est l'inondation de `rem:flooding`, mesurée sur *gradual* ; la fenêtre vide est le pendant « inondation » du plancher de détectabilité, qui vide l'ensemble admissible par le rappel quand l'inondation le vide par la précision ; le remède (désarmer après détection) est séparé de la condition de portée (flux dont l'erreur revient à son niveau pré-changement).

### 2.3 R8-D — ta charge réintroduisait le défaut qu'I5 cherchait

« their detection is governed by the contrast available inside the window they read » : c'est l'affirmation non restreinte que S2ter-B restreint (« mean-field boundary », 62/80 et 36/40 sur les grilles pilotées par classifieur). `\ref{sec:coverage}` n'existe pas : c'était une référence indéfinie. Enfin « fitted » : aucun paramètre n'est ajusté.

`rem:predicate_scope` publiée : le budget A est ce que dépense un moniteur dont la fenêtre peut couvrir le transitoire (statistiques cumulatives, ADWIN) ; un test à deux échantillons à fenêtre fixe lit au plus `min(W, n_stat)` pas, et sa condition est le contraste de `eq:Rkswin_contrast`, frontière de champ moyen dont `rem:window_requirement` mesure la portée ; la généralisation pré-enregistrée n'a pas été retenue. **Placement** : entre `\end{definition}` et « Definition~\ref{def:blindspot} compares… », parce que ce second paragraphe ouvre le REPLACE appliqué de S8-6 ; l'insérer après lui aurait déplacé un payload de plus.

### 2.4 R8-E et T1 — le motif n°3 est faux, le verdict tient

« it reproduced the measurements less well than the family-specific pair » : faux. Le prédicat généralisé et le prédicat de contraste coïncident sur **les 3 960 cellules** (`test_generalised_predicate_is_the_contrast_predicate_on_every_cell`). La règle E1 comparait l'accord groupé (3673/3960) à l'accord de la seule grille contrôlée (3575/3840), pas à la paire. La scission a donc exactement le même 0,9275. Ton motif n°3 (« publier une forme unique à 0,9275 serait pire que la scission ») et l'analogie avec le fit monolithe ne tiennent pas : les deux formes prédisent la même chose, cellule pour cellule.

**Le verdict « assumer » tient**, pour une autre raison : la scission est la sortie par défaut de la règle, qui n'accorde pas l'unification, pas un gain d'accord. Le paragraphe publié le dit : la généralisation prédit exactement ce que prédit la paire ; la règle exigeait que les 93,1 % de la grille contrôlée tiennent sur les trois grilles groupées ; les grilles pilotées par classifieur (62/80, 36/40) les font passer dessous ; le déficit appartient à la condition fenêtrée et publier la paire séparément ne le supprime pas. Le bloc `~~~~~~~~~` parasite de ta charge n'est pas repris.

### 2.5 R8-C — le constat était juste, la liste d'abréviations non

ARF, CUSUM, ADWIN et PHT n'apparaissent pas dans le résumé. Les vraies abréviations non définies étaient **ARMA–GARCH** et **BAF**, toutes deux retirées. Ton constat de fond est confirmé et aggravé : au compteur B, le résumé commité faisait **251** mots. Il dépassait la limite de 250, là où le tour H annonçait 249.

---

## 3. Corrections hors liste (arbitrage opérateur : « corriger maintenant »)

### 3.1 `rem:exponent`

Retiré : « saturates on a floor … no longer responds to the drift at all », « Points of zero local slope pull a pooled fit toward zero », « then a floor of 29.8 steps … where the onset no longer responds », « what the pooled fit excluded was the floor's contribution ».

Publié :
- le fit à un morceau, −1,77 [−1,90 ; −1,67] ;
- « That interval carries the sampling noise of the medians, not the uncertainty of the model » ;
- le modèle à deux morceaux pré-enregistré, rupture 0,475 [0,436 ; 0,492], flanc −1,82 [−2,04 ; −1,71] ;
- « The grid does not choose between the two models », avec le gain de 5,4 % pour un paramètre de plus et la baisse de 6,5 % contre 6,1 % prédits ;
- le verdict : « the distance of the onset exponent to the Hoeffding bound is not established on this grid ».

### 3.2 S13-G, `sec:hydra`, R7-C, R7-D

- **S13-G.** Ton argument (le minimum d'une famille d'échelle i.i.d. préserve l'exposant) est juste. Sa prémisse est contredite par le manuscrit lui-même : le rapport des médianes Kaplan–Meier mono-membre/ensemble passe de 5,32× à Δe = 0,14 à 3,10× à 0,33 (`sec:hydra`), et les ancres γ_M valent 4,12× [3,45 ; 4,96] et 7,99× [6,40 ; 9,72], intervalles disjoints. Les délais ne forment pas une famille d'échelle, donc le minimum peut déplacer l'exposant ajusté. La remarque le dit désormais et garde le min-of-ten comme candidat, à côté de la phase d'avertissement et de l'arbre de fond.
- **`sec:hydra`.** « Onset acceleration thus operates as a constant factor » devient « Over the full grid, onset acceleration thus reads as a change of prefactor, not of complexity class; it is not a constant factor across magnitudes — the two anchors above differ by a factor of two — and Remark~\ref{rem:exponent} bounds what the full-grid fits can carry ».
- **R7-C retirée.** « both arms saturate » (faux pour l'ARF), « where the exponent is zero » (faux), « cleanest demonstration … acts on the constant » (contredit par le même paragraphe). Le « ~50 » HAT était sourcé sur `tau_segmented_hat.floor`, paramètre d'un modèle que la règle pré-enregistrée excluait (gain 0,2 %, rupture à la borne de recherche 0,4916).
- **R7-D retirée.** La cloche descend dès Δe ≈ 0,25 (`res:bell`), loin de la « rupture » à 0,475 ; la saturation ne pouvait pas expliquer ce flanc.

---

## 4. Le résumé (R8-C)

Deux compteurs, cible ≤ 225 sur chacun (consigne de l'opérateur, 25 mots de marge sous 250). `texcount` est absent de l'environnement `tex` ; aucune dépendance n'a été ajoutée.

| compteur | règle | commité | ce tour |
|---|---|---|---|
| A | source, macros développées, formule = 1 mot, tirets = espace — figé par `tests/test_manuscript_integrity.py::test_abstract_within_springer_limit` (150–250) | 246 | **223** |
| B | couche texte du PDF compilé (PyMuPDF), coupures de ligne recollées | 251 | **225** |

**Cadrage restitué dans la phrase 1** : « a residual the classifier reacts to: fault detection on an endogenous residual, where the monitor's evidence is bounded by adaptation, not the horizon ».

**Retirés à ce tour.**
- Numéraux : « 8,000 » ; la bande [13,9 ; 18,3] ; λ_op = 21,93 et son IC ; « with precision 1.000 » ; « 0 of 1,080 / 1,080 of 1,080 », remplacé par « misses all 1,080 … detects each ».
- Abréviations non définies : « ARMA–GARCH », remplacé par « heteroscedastic » ; « (BAF, INSECTS) ».
- Compression syntaxique : « composes … that reads » → « pairs … reading » ; « the classifier itself reacts » → « the classifier reacts » ; « directly » ; « not to a detector family » → « not a detector family » ; « measured evidence ceiling » → « measured ceiling » ; la dernière phrase.

Aucun cadrage ni aucune contribution n'est retiré.

---

## 5. Payloads et gardes

- **Recensement** (état (ancres hors remplacement, remplacements) de chaque payload S2bis, S8, S9, S10, S2ter), identique avant et après les modifications du manuscrit. Aucune insertion de ce tour n'a déplacé un payload.
- **Deux payloads déplacés, déjà là.** S8-2 (`rem:first_swap`, séparé de son ancre par `res:bell`/`res:skillfloor`, stream S13) et S10-C (« Label latency », séparé par le paragraphe INSECTS, tour H). Leur partie ajoutée figure exactement une fois ; une ré-application littérale aurait défini `rem:first_swap` deux fois ou imprimé « Label latency » deux fois.
- **Durcissement.** Les cinq gardes exigent (0, 1) ; S8-2 et S10-C sont déclarés « displaced » par nom, avec un contrôle que l'ancre et la partie ajoutée figurent chacune une fois. La boucle « pending anchors » de `test_S2ter_predicate`, devenue sans objet, est supprimée et le test renommé `test_transfer_S2ter_payloads_are_applied`. `CLAUDE.md` est mis à jour.
- **Contre-épreuve par mutation** (en mémoire, fichiers intacts) : S10-C ré-appliqué → la garde échoue ; S10-A ramené à son ancre → la garde échoue. Avant le durcissement, le second cas passait.
- **Errata** (archives non réécrites) : `transfer_S9.md` §F (S9-F appliqué avec S2ter-B), `transfer_S2ter.md` (sept payloads appliqués), `transfer_S8.md` (S8-2 déplacé), `S10_transfer.md` §C (S10-C déplacé), pré-enregistrement R-8 (§2.1).
- **Amendement de test déclaré.** `test_s10_writes_only_inside_its_perimeter` refusait toute occurrence de « S10 » dans le registre des déviations. L'entrée du stream S13 déclarant la re-composition de la Table 7 l'aurait fait échouer sans que S10 ait rien écrit. Le test lit désormais l'en-tête « Stream S10 » : l'intention (S10 n'a déclaré aucune déviation) est conservée, sans maquiller le libellé du registre.

---

## 6. E9 — corps et débordements

| objet | avant | après |
|---|---|---|
| Table 7 (`tab:real_data_summary`) | corps **4,48 pt** (facteur ≈ 0,45) | **7,21 pt** — en-tête à deux niveaux (F1 et p₀ groupés, « Sign test » monté d'une ligne), libellés INSECTS sans `_balanced` (précisé en légende), `\tabcolsep` 2 pt, légende « ARF at c = 1 » |
| Table 8 (`tab:family_order`) | 5,78 pt | **inchangée** — voir ci-dessous |
| `Overfull \hbox` | 15, dont 7 au-dessus de 10 pt (max **37,3 pt**, `v65:460`) | **1** (2,2 pt, titre de `res:starvation`) — `\emergencystretch` 2em au préambule, `\path` pour un chemin insécable (`framework_v2.tex`), tuple mathématique mis en texte (`protocol_v2.tex`), `@{}lll@{}` pour le tableau de statut de l'annexe |

**Table 7.** Le `.tex` est re-rendu par `s10_p0.table2_with_p0` depuis `s10_p0.json::summary` et `table2_values.csv`. L'ancien en-tête se re-rend d'abord octet pour octet ; les six lignes numériques sont identiques ; la copie manuscrit est re-copiée. Déclaré dans `authorized_deviations.txt` (hors liste gelée, aucune déviation consommée, précédent S11-b).

**Table 8, délibérément laissée à 5,8 pt.** Son bloc est la charge S2ter-I, verrouillée par `test_transfer_S2ter_payloads_are_applied`, qui exige le REPLACE verbatim (adaptation une-colonne déclarée) et le rapprochement ligne à ligne avec `family_table_latex()`. La re-composer exige d'amender cette adaptation déclarée : décision de périmètre, posée au prompt 51.

---

## 7. Les cinq portes (I9)

| porte | résultat |
|---|---|
| 1. `pytest tests/ -q` | **190 passed** (188 + 2 nouveaux) |
| 2. `sha256sum -c …/artifacts_sha256_pre_ssot.txt` | **27 OK, 7 FAILED**, ensemble identique à la liste autorisée. `s13_gate.json` et `s10_table2_p0.tex` ne sont pas dans la liste gelée (contrôlé avant modification) |
| 3. compilation `tectonic -X compile` | sortie 0, **zéro référence indéfinie**, 63 pages A4 |
| 4. recensement des charges | §1 : I1–I9 traités, I10 différée par arbitrage |
| 5. `git status --porcelain` | vide après commit ; bac à sable supprimé avant le contrôle |

Déterminisme : S13 relancé deux fois, SHA-256 identiques (`s13_gate.json` `bdb42652…`). Aucun push.

---

## 8. H10 — différée, et deux décisions qui t'appartiennent

1. **L'artefact public.** Tu exiges « le PDF et le dépôt public », mais « aucun `docs/` ». Or `origin` contient `docs/` (prompts, rapports, transferts). Il faut définir l'artefact de soumission : export du dépôt sans `docs/prompts`, `docs/reports`, `docs/theory`, `docs/editorial`, `docs/plans`, ni `CLAUDE.md`.
2. **L'isolation.** Un sous-agent Claude Code lancé dans le dépôt charge `CLAUDE.md` et la mémoire du projet, qui décrivent les streams. Proposition : un export `git archive` filtré dans un répertoire hors dépôt, le PDF figé à côté, cinq sous-agents à profil (P1–P5 de ton §7) lancés depuis ce répertoire. Livrable : objections localisées (page, ancrage, sévérité, verdict). L'isolation reste une consigne, pas une garantie technique ; à dire dans le rapport H10.

---

## 9. Auto-critique — mes défauts aux tours précédents

- **Rapport 42** : j'ai lu 31, 31, 29,5, 29, 29, 29 comme un « plancher structurel » sans passer en échelle logarithmique. Tout le récit R7/R8 est parti de là, et tu l'as construit sur ma lecture.
- **Rapport 46** :
  - j'ai lu 5,4 % de SSE comme une amélioration sans pénalité de paramètre ;
  - j'ai rédigé le libellé causal faux de R7-B ;
  - j'ai sourcé le plancher HAT sur un modèle que la règle excluait ;
  - j'ai vérifié E9 sur le placement au lieu du corps ;
  - j'ai écrit « recall stays near 1 » ;
  - j'ai annoncé 249 mots pour un résumé qui en rend 251 ;
  - j'ai déclaré S9-F pending sur la foi du document de transfert, sans regarder l'arbre.
- **Même famille que ton conseil stratégique** : un état écrit (rapport, transfert, lecture à l'œil) pris pour l'état mesuré.

---

## 10. Fichiers modifiés

| fichier | nature |
|---|---|
| `docs/manuscript/articleA_blindspot_v65_mlj.tex` | résumé ; `rem:exponent` ; `sec:hydra` (facteur constant qualifié, R7-C retirée) ; paragraphes INSECTS et « Two predicates rather than one » ; légende et enveloppe de la Table 7 ; `\emergencystretch` |
| `docs/manuscript/sections/framework_v2.tex` | `rem:predicate_scope` ; R7-D retirée de `res:bell` ; `\path` |
| `docs/manuscript/sections/protocol_v2.tex`, `sections/dependence_v2.tex` | débordements |
| `docs/manuscript/tables/s10_table2_p0.tex`, `results/S10_external_validity/tables/s10_table2_p0.tex`, `experiments/S10_external_validity/s10_p0.py` | Table 7 re-composée |
| `experiments/S13_evidence_bell/s13_evidence_bell.py`, `results/S13_evidence_bell/s13_gate.json` | `fixed_k`, clés dérivées, bloc `post_hoc` |
| `results/audit_S7/_baseline/authorized_deviations.txt` | entrée du stream S13, tour I |
| `tests/test_S13_bell.py`, `tests/test_manuscript_integrity.py` | deux tests nouveaux |
| `tests/test_S2bis_calibration.py`, `test_S8_generality.py`, `test_S9_coverage.py`, `test_S10_external_validity.py`, `test_S2ter_predicate.py`, `CLAUDE.md` | gardes durcies, test S10 amendé |
| `docs/theory/transfer_S9.md`, `transfer_S2ter.md`, `transfer_S8.md`, `S10_transfer.md`, `docs/prompts/… - 45 - …` | errata |
| `docs/prompts/… - 49 - …`, `docs/prompts/… - 51 - …`, ce rapport | nouveaux |

## 11. Ce que je n'ai pas vérifié

- Le rapport des médianes naïves HAT/ARF par amplitude (≈ 4,6 → 8,5 → 1,7) a été calculé en session depuis `R6_hat_instrumented.parquet` et `evidence_bell.csv`, et **n'est pas commité**. Le manuscrit ne s'appuie que sur les médianes Kaplan–Meier déjà publiées.
- La corrélation rupture/pente à travers les tirages (≈ 0,69) est un calcul de session, non commité. Le mécanisme est établi par l'intervalle à rupture fixée, qui est commité.
- La limite de 250 mots de *Machine Learning* n'a pas été relue à la source ce tour (confirmée au tour H et par toi).
- Le rapport 46 existe en double, dans `docs/prompts/` et dans `docs/reports/`. Je n'en ai supprimé aucune copie.

## [Strategic Advice]

**Le défaut de ce cycle n'était pas statistique, il était visuel.** Un plateau lu sur un axe linéaire, dans une grille resserrée près de 0,5, a produit deux tours de charges, un pré-enregistrement et trois remarques publiées. Le garde-fou le moins cher est une règle : toute affirmation de régime (plancher, saturation, rupture) passe par la pente locale en échelle log et par une comparaison pénalisée, avant d'être écrite.

**Le pré-enregistrement protège du choix du résultat, pas du choix du modèle.** R-8 a été exécuté exactement comme pré-enregistré, et son modèle était faux. Un pré-enregistrement de modèle à régimes doit fixer le critère d'amélioration (F, AIC ou BIC) en même temps que l'estimateur.

**H10 reste le seul point capable de surprendre**, et il est prêt dès que tu valides les déviations et l'artefact public.
