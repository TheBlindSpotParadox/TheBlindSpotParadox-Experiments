# VÉRIFICATION DU TOUR S13-bis · DEUX ERREURS DE MA PART · UN DÉFAUT DE PUISSANCE · UNE ERREUR THÉORIQUE DANS LE MANUSCRIT

---

## 1. Ce que je valide

J'ai relu le gate et les tests dans le dépôt. Quatre choses sont faites correctement et méritent d'être dites.

**R-5 est mort de la bonne façon.** `baseline_bias_1000_vs_3000: null`, `baseline_bias_source: "uncomputable_insufficient_warmup"`, `baseline_bias_n: 1000`, `baseline_bias_area_units: null`. Le `0,007` n'existe plus nulle part. Le test à deux branches est meilleur que le mien : ma version exigeait la mesure et aurait échoué sur le corpus réel ; la version commitée accepte la lacune **à condition qu'elle soit nommée** et que les deux valeurs soient nulles. L'invariant est renforcé, pas contourné. Le choix de retourner un gap déclaré plutôt que de lever est le bon : une exception aurait empêché l'artefact d'exister, et l'artefact est ce qui rend la lacune auditable.

**Le mode est quantifié au lieu d'être tranché.** `mode_posterior` : 0,7985 à Δe = 0,1936, 0,1955 à 0,2426, 0,006 à 0,2871. Le manuscrit publie le plateau. Le test bloque le point tant que les deux candidats se recouvrent.

**L'exposant a son intervalle honnête.** Bootstrap sur graines, `[−1,898 ; −1,669]`. Il exclut −2, et il exclut aussi −1. La voie (a) tient : l'écart à Hoeffding est un fait, pas un artefact d'erreur type. `rem:exponent` publie les deux bornes exclues — c'est la bonne forme.

**Les intervalles d'habileté convergée sont dans le pipeline.** L'affirmation « avantage indétectable » cite un intervalle commité, pas un calcul de session. C'était l'ajout à faire.

---

## 2. Deux erreurs de ma part, et elles sont de la même famille

La correction du §2.3 est fondée. Ma colonne « habileté après convergence » venait de `summary_metrics.csv` de la campagne étudiante, divisée par les planchers triviaux de ce dépôt-ci. J'avais écrit dans mon propre script de vérification un dictionnaire `etu = {...}` rempli à la main depuis leur CSV, puis présenté le résultat comme reproductible « dans le même dépôt ». C'est faux, et la phrase était précisément celle qui donnait du poids à l'argument.

**Le même défaut s'est produit une seconde fois dans la même réponse.** Mon « la détection passe de 0 à 0,98 puis retombe à 0,01 » à λ = 25 vient de la colonne `det25` de `amplitude_metrics.csv` — encore la campagne étudiante. Le profil commité culmine à **0,92** et retombe à **0,04**. Et ma fenêtre `E[S_max] ≥ 25` sur `[0,11 ; 0,43]` ne correspond ni aux points de grille — `[0,141 ; 0,416]` — ni à l'interpolation — `[0,12 ; 0,43]`.

Deux quantités, deux corpus croisés, une seule réponse. Ce n'est pas un accident isolé : j'ai vérifié les chiffres des étudiants avec soin, puis je les ai cités comme s'ils sortaient de S6. La règle qui manquait est simple et je l'adopte : **toute grandeur que je cite porte le nom du fichier d'où elle sort.** Une vérification qui croise deux campagnes doit le dire dans la phrase, pas dans une note.

Sur le fond, la correction améliore l'article. Les valeurs étudiantes tombent à l'intérieur des intervalles S6 — les deux campagnes s'accordent, et l'énoncé publié (avantage indétectable, trois intervalles à cheval sur zéro) est plus dur que le franchissement négatif que je proposais, parce qu'il ne dépend pas d'un signe tiré dans le bruit.

---

## 3. Le défaut qui reste dans `res:skillfloor` : la mesure n'a pas la puissance de son énoncé

La colonne convergée est la moyenne des 200 derniers pas de l'horizon. À l'extrémité droite de la grille, cette fenêtre ne contient presque rien.

À Δe = 0,4977, le plancher trivial vaut 0,00234 et l'erreur convergée mesurée vaut 0,0023. Sur 200 pas et 100 graines, cela fait **46 erreurs attendues au total**, toutes trajectoires confondues. Un quart d'erreur par run et par centaine de pas.

L'intervalle `[−0,26 ; +0,29]` ne dit donc pas que l'ensemble et le prédicteur constant sont à égalité. Il dit que **la fenêtre est trop courte pour distinguer quoi que ce soit** à un taux de base de 0,23 %. Les trois dernières amplitudes sont dans ce régime.

`res:skillfloor` écrit aujourd'hui « skill stays non-negative over the grid but collapses onto the trivial floor at the last three magnitudes […] every interval straddling zero ». La deuxième moitié est vraie, la première suggère une mesure qui conclut. Un relecteur qui divise 0,0023 par 200 pas trouve la réponse en trente secondes, et l'objection est facile à formuler : vous comparez deux classifieurs sur quarante-six événements.

**Deux correctifs, tous deux à coût de recalcul.**

Élargir la fenêtre convergée. Sur les 1 000 derniers pas plutôt que 200, le nombre d'événements passe de 46 à environ 230 et l'intervalle se resserre d'un facteur 2,2. Le prix est que la fenêtre mord un peu plus tôt dans l'horizon ; à ces amplitudes le transitoire est terminé depuis longtemps — `tau_swap_q010` vaut 29 pas — donc le biais est nul en pratique et se vérifie en comparant les deux fenêtres.

Publier le décompte. Toute affirmation d'égalité doit porter le nombre d'événements sur lequel elle repose. Une colonne `n_errors_converged` dans `evidence_bell.csv` règle la question définitivement.

Et si, après élargissement, les intervalles chevauchent toujours zéro, l'énoncé devient solide : ce n'est plus une limite de mesure, c'est un résultat.

**Note secondaire, même section.** `_bootstrap_argmax` tire des normales de moyennes `smax_mean` et d'écarts `(ci_hi − ci_lo)/3,92`. C'est une approximation normale posée sur un intervalle non paramétrique. Le 0,7985 en hérite. Un argmax bootstrap direct sur les valeurs par graine coûte le même temps et évite l'étage paramétrique. À faire si le chiffre entre un jour dans le manuscrit ; aujourd'hui il ne sert qu'à garder un test, et cela suffit.

---

## 4. Une erreur théorique dans `rem:exponent`, déjà dans le manuscrit

La remarque écrit que l'écart entre l'exposant mesuré et la borne de Hoeffding est ouvert, et nomme `the min-of-ten onset of Eq.~\eqref{eq:hydra}` comme mécanisme candidat.

**Le minimum de dix ne peut pas produire un écart d'exposant.** Si chaque arbre adapte en `τ_i = K · Δe^(−2) · ξ_i`, avec `ξ_i` positifs et identiquement distribués, alors

```
min_i %tau_i = K cdot {%DELTA e}^{-2} cdot min_i %xi_i
```

La dépendance en Δe sort du minimum. L'opération divise la constante par `E[ξ]/E[min ξ]`, et laisse l'exposant intact. C'est précisément ce qui rend l'effet Hydra mesurable comme un facteur — 4,1× à 8,0× — et non comme une pente.

Les mécanismes qui déplacent un exposant sont ceux dont le bénéfice dépend de l'amplitude : la phase d'avertissement, qui se déclenche d'autant plus tôt que la dérive est forte, et l'arbre de fond pré-entraîné, dont l'avance croît avec elle. Le tirage de Poisson et le sous-échantillonnage de variables jouent sur la capacité par arbre, donc sur la constante et éventuellement sur l'exposant par arbre — mais pas par l'effet d'ensemble.

**Conséquence sur la suggestion S1, que j'endosse et qui devient décisive.** Le refit de la loi d'onset sur le bras HAT au même domaine valide n'est pas un test de confirmation, c'est un test de discrimination, et sa prédiction se pré-enregistre :

| issue mesurée         | lecture                                                                                                                                                                                                                               |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| HAT ≈ ARF ≈ −1,77     | l'écart à −2 est une propriété **par arbre**. Le minimum de dix explique la constante, pas la pente. La phrase de `rem:exponent` est fausse et l'explication est à chercher du côté de la phase d'avertissement et de l'arbre de fond |
| HAT ≈ −2, ARF ≈ −1,77 | l'écart est un **effet d'ensemble** — et alors le minimum de dix ne peut pas en être la cause, puisqu'il préserve les exposants. Un mécanisme dépendant de l'amplitude doit être nommé                                                |

Dans les deux cas, la phrase actuelle tombe. Le coût est un recalcul sur des données R2 déjà commitées.

C'est le seul point de cette série qui touche un énoncé du manuscrit assemblé plutôt qu'un artefact.

---

## 5. De nouvelles expériences sont-elles nécessaires ?

**Non.** Deux recalculs, sur des traces déjà au dépôt.

| #       | recalcul                                                                                    | ce qu'il produit                                                          | coût    |
| ------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | ------- |
| **R-6** | habileté convergée sur 1 000 pas en plus de 200, plus la colonne `n_errors_converged`       | un énoncé qui porte sa puissance, ou un résultat d'égalité solide         | minutes |
| **R-7** | refit de la loi d'onset du bras HAT sur Δe ≥ 0,10, prédiction pré-enregistrée avant lecture | tranche entre effet par arbre et effet d'ensemble, corrige `rem:exponent` | minutes |

La période réfractaire après alarme reste la seule extension neuve, et reste en phase de révision.

---

## 6. Charges

### S13-G — `rem:exponent`, retirer le mécanisme qui ne peut pas être le bon

**Target file: `docs/manuscript/articleA_blindspot_v65_mlj.tex`**
<<< SEARCH
~~~~~~~~~latex
  Whether the distance to $-2$ persists in the single-tree limit is open;
  the min-of-ten onset of Eq.~\eqref{eq:hydra} is the candidate mechanism,
  together with the warning phases, background-tree pre-training and
  Poisson-weighted bootstrap that accelerate adaptation beyond the
  concentration inequality.
~~~~~~~~~

=== REPLACE WITH >>>
~~~~~~~~~latex
  Whether the distance to $-2$ persists in the single-tree limit is open, and
  the min-of-ten onset of Eq.~\eqref{eq:hydra} is not a candidate explanation
  for it: if each member adapts in $\tau_i = K (\Delta e)^{-2} \xi_i$ with
  i.i.d.\ $\xi_i > 0$, the magnitude factors out of the minimum, so
  $\min_i \tau_i$ carries the same exponent and a smaller constant. Taking the
  minimum of ten clocks moves $K$, not $\alpha$ --- which is why the Hydra
  effect is measurable as a factor and not as a slope. The candidates that can
  move an exponent are those whose benefit grows with the magnitude: the warning
  phase, which trips earlier the stronger the drift, and the pre-trained
  background tree, whose head start grows with it. The single-tree refit on the
  valid domain discriminates between a per-member and an ensemble origin.
~~~~~~~~~
>>> END OF BLOCK

### S13-H — `res:skillfloor`, porter la puissance de la mesure

À appliquer **après R-6**, les trois intervalles étant à recalculer. La phrase à insérer avant la conclusion du résultat :

```latex
At the last three magnitudes the converged window carries few events: at
$\Delta e = 0.498$ the trivial floor is $0.23\%$, so the last $200$ steps of
$100$ runs contain some $46$ errors in total. The intervals above are therefore
reported with their event counts, and the comparison is widened to the last
$1000$ steps, where the same amplitudes carry about $230$ events.
```

### S13-I — la clé héritée du gate

`skill_zero_crossing` vaut aujourd'hui `null` parce qu'elle est aliasée sur `skill_converged`. Elle valait `0,482255` — l'épisode — dans le gate précédent. Aucun consommateur ne casse aujourd'hui, le test ne lit que les clés explicites. Mais une clé qui change de sens sans changer de nom est exactement le mécanisme qui a produit les sept acceptions de `W`.

Deux sorties : la supprimer, ou la figer sur l'épisode pour rester compatible. Je recommande la suppression, avec la même discipline appliquée à `err_final` et `skill`, dupliqués dans `evidence_bell.csv` sous deux noms pour la même colonne.

---

## 7. La revue est-elle terminée ?

**Non. Il reste un tour de travail et une lecture.**

| #   | point                                        | statut           |
| --- | -------------------------------------------- | ---------------- |
| 1   | La cloche dans le manuscrit                  | **clos**         |
| 2   | R-5                                          | **clos**         |
| 3   | Sept charges S2-ter                          | ouvert           |
| 4   | T1 de S2-ter                                 | ouvert           |
| 5   | INSECTS, aucun seuil admissible              | ouvert           |
| 6   | Pré-review adversariale                      | ouvert, débloqué |
| 7   | Puissance de la colonne convergée            | **nouveau**      |
| 8   | `rem:exponent` nomme un mécanisme impossible | **nouveau**      |

Les points 7 et 8 sont des recalculs et une charge. Ils ne rouvrent rien.

Ce qui reste n'est plus de la recherche. Sept charges à appliquer, deux arbitrages à écrire, deux recalculs, quatre corrections cosmétiques, et une lecture complète avec l'intention de casser. Le point 6 est le seul qui puisse encore produire une surprise, et c'est pour cela qu'il doit être le dernier et qu'il ne doit pas être sauté.

---

## 8. Actions

| #       | action                                                                                                                                                                                                                                                                                         | priorité            |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- |
| **G1**  | **R-6** : habileté convergée sur 1 000 pas, colonne `n_errors_converged`, intervalles régénérés. Puis appliquer **S13-H** avec les nouveaux chiffres                                                                                                                                           | **Haute**           |
| **G2**  | Appliquer **S13-G**. C'est une erreur théorique dans le manuscrit assemblé, pas un artefact                                                                                                                                                                                                    | **Haute**           |
| **G3**  | **R-7** : refit HAT sur Δe ≥ 0,10. Pré-enregistrer les deux lectures du §4 **avant** de lire le résultat, dans `docs/prompts/`                                                                                                                                                                 | Haute               |
| **G4**  | **F6** — appliquer les sept payloads S2-ter                                                                                                                                                                                                                                                    | Haute               |
| **G5**  | **F7** — écrire l'arbitrage INSECTS dans `sec:limitations`                                                                                                                                                                                                                                     | Haute               |
| **G6**  | **F8** — trancher T1, ou déclarer la scission par famille comme choix assumé avec son motif                                                                                                                                                                                                    | Moyenne             |
| **G7**  | **S13-I** — supprimer `skill_zero_crossing` et les colonnes dupliquées `err_final` / `skill`                                                                                                                                                                                                   | Moyenne             |
| **G8**  | **S3 du rapport** — ne pas citer la campagne étudiante dans le manuscrit. Je suis d'accord avec l'option (a) : citer une campagne dont le protocole n'est pas celui du manuscrit ouvre une classe d'attaque pour un gain nul, puisque S6 porte la même conclusion avec ses propres intervalles | Moyenne             |
| **G9**  | **S5 du rapport** — garder la fenêtre en points de grille `[0,14 ; 0,42]`. Chaque borne est une ligne du CSV ; l'interpolée exigerait d'écrire son critère                                                                                                                                     | Faible              |
| **G10** | **S4 du rapport** — ajouter l'ordonnée à l'origine du refit au gate                                                                                                                                                                                                                            | Faible              |
| **G11** | **S2 du rapport** — versionner les rapports de stream dans `docs/reports/`. Le rapport qui portait « concorde avec Hoeffding » n'était nulle part, donc « tout texte dérivé » n'était pas auditable                                                                                            | Faible, structurant |
| **G12** | **F9** — résumé MLJ, pagination Table II, citation Souza, étiquette ICDM                                                                                                                                                                                                                       | Avant soumission    |
| **G13** | **F10** — pré-review adversariale sur le PDF assemblé, 61 pages, cinq profils                                                                                                                                                                                                                  | **Dernier**         |

Ordre : G1, G2, G3 en tête, parallélisables entre elles. G4 et G5 en parallèle. G6 exige un arbitrage de votre part. G13 seul, à la fin, sur le document figé.

---

## 9. Notes stratégiques

**La correction que vous m'apportez vaut plus que ce que je vous ai apporté ce tour.** J'ai croisé deux corpus et présenté le résultat comme reproductible dans un seul — deux fois, dans la même réponse, sur deux quantités différentes. Ce n'est pas une inattention ponctuelle : c'est le réflexe de vérifier soigneusement une source puis de la citer sous le nom d'une autre. La règle qui manquait est d'écrire le fichier d'origine dans la phrase, pas dans une note de fin. Je l'applique à partir de maintenant.

**Le point 8 est le seul de cette série qui compte vraiment.** Une remarque du manuscrit assemblé nomme le minimum de dix comme explication candidate d'un écart d'exposant qu'il ne peut pas produire — le facteur sort du minimum, il déplace la constante et laisse la pente. Un relecteur théoricien le voit en une ligne, et c'est exactement le profil du panel qui a trouvé la faille de la Proposition 3. La correction est gratuite, et elle transforme le refit HAT d'une confirmation attendue en un test qui tranche.

**Le point 7 est le dernier endroit du dossier où un énoncé dépasse sa mesure.** Quarante-six événements ne permettent pas de conclure à une égalité entre deux classifieurs, et le manuscrit l'écrit aujourd'hui comme un résultat. Élargir la fenêtre coûte quelques minutes et donne soit une conclusion solide, soit une limite déclarée — les deux valent mieux que l'énoncé actuel.

**Sur la fin de la revue, je maintiens ce que j'ai écrit au tour précédent et j'insiste.** La tentation, quand les résultats sont là et que 186 tests passent, est de considérer que le document suit. Il ne suit pas tout seul : quatre renversements de thèse, vingt-neuf charges appliquées, six sections assemblées, soixante et une pages. Personne ne les a lues d'un bout à l'autre en cherchant la contradiction. La v63 a été rejetée sur des incohérences que ses auteurs n'avaient pas cherchées.

**Ce que je n'ai pas vérifié.** Je n'ai lu ni `res:bell` ni `res:skillfloor` dans le `.tex` — seulement les blocs cités dans votre rapport. Je n'ai pas lu le nouveau `evidence_bell.csv` ; les trois intervalles d'habileté convergée et le décompte de 46 événements viennent de mon calcul à partir de `trivial_error` et de `skill_converged` tels que votre rapport les donne. Les sept payloads S2-ter et `S10_external_validity.md` restent non lus, pour le troisième tour consécutif.