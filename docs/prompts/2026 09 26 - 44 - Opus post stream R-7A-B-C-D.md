# ARBITRAGES SUR L'EXPOSANT · UNE VÉRIFICATION BLOQUANTE NON SOULEVÉE · CHEMIN CRITIQUE

---

## 1. Arbitrage 1 — `rem:exponent`

**Verdict : traitement 2, mais pas sous la forme proposée.** La révision ne consiste pas à arbitrer entre deux valeurs d'exposant. Elle consiste à changer l'objet publié.

### 1.1 Pourquoi « conserver tel quel » n'est pas tenable

L'affirmation n'est pas fausse sous son estimateur déclaré — le fit sur 18 amplitudes a été pré-enregistré en S13 et son intervalle est commité. Elle est devenue **indéfendable pour une autre raison** : on connaît désormais la direction de son biais.

Un régime saturé contribue des points où `τ` est constant en `Δe`, donc de pente locale nulle. Six points sur dix-huit. Le fit groupé est mécaniquement tiré vers zéro, et le tableau du §4 le montre point par point : −2,11 sur le flanc, −1,99, −1,94, puis −1,77 à mesure que le plancher entre.

Publier un nombre dont on sait le sens du biais sans le dire, c'est exactement la faille F1 de la Proposition 3 originelle — supprimer un terme dont on connaît le signe. Le dossier est mort d'avoir fait ça une fois.

La question n'est plus de pré-enregistrement. Elle est de divulgation.

### 1.2 Pourquoi « publier le fit de flanc » n'est pas la solution non plus

Choisir une coupure parmi trois, c'est remplacer un estimateur biaisé par un degré de liberté caché. Le rapport le voit et pose la question ; la réponse est qu'il ne faut pas choisir.

**La rupture s'estime, elle ne se choisit pas.** Une régression segmentée à deux morceaux — une loi de puissance à gauche, une constante à droite — avec le point de rupture `Δe*` estimé par minimisation de la somme des carrés résiduels sur les points de grille, rend simultanément :

- l'exposant du flanc, avec son intervalle bootstrap sur graines ;
- le niveau du plancher, avec le sien ;
- **la position de la rupture, avec le sien** — donc le degré de liberté devient un paramètre mesuré au lieu d'un choix caché.

C'est pré-enregistrable sans rien savoir du résultat : on spécifie l'estimateur, pas la coupure. Et c'est exactement le traitement que le dossier a déjà appliqué au mode de la cloche — refuser l'argmax monolithe sur une courbe à régimes, publier la structure. La cohérence interne plaide seule pour cette forme.

### 1.3 Ce qui entre au manuscrit maintenant, ce qui attend

Le manuscrit ne peut pas attendre un tour de plus avec une phrase réfutée et une affirmation dont on connaît le biais. Mais les chiffres du §4 ne sont pas commités et ne doivent pas entrer.

**Découpage :** la charge A rétablit la vérité avec des chiffres **déjà commités uniquement** — les six médianes `tau_arf_median` de `evidence_bell.csv` et le `tau_exponent_hat` du gate. Elle rétrograde l'exclusion de −2 au rang de propriété de l'estimateur groupé, nomme la saturation, et déclare l'ouverture. La charge B, qui publiera la structure segmentée, attend R-8.

---

## 2. Une vérification bloquante que le rapport n'a pas soulevée : l'horloge

Avant toute lecture du plancher, une question décide de tout.

River résout un `drift_detector` non fixé en `ADWIN(delta=0.001, clock=32)`. Les bras épinglés du dépôt utilisent `clock = c`, et l'ARF de R2 tourne à **c = 1**. Avec `clock = k`, aucune coupe n'est tentée avant `k` observations, et en pratique aucune avant quelques multiples de `k`.

Un plancher à **~50 pas pour le HAT** et **~29 pour l'ARF** est parfaitement compatible avec un HAT à `clock = 32` et un ARF à `clock = 1`. Dans ce cas :

- le plancher n'est pas une complexité d'échantillon, c'est une **période d'échantillonnage du test** ;
- le rapport 50/29 n'est pas un effet d'ensemble, c'est un **artefact d'horloge** ;
- et la comparaison d'exposants entre les deux bras compare deux détecteurs différemment cadencés.

Le rapport §9 annonce que le mécanisme est déduit des données et non lu dans le source. C'est plus grave que « à vérifier avant d'écrire *structural* » : c'est à vérifier avant d'écrire **quoi que ce soit** sur le plancher, y compris la comparaison inter-bras du §4 que la Note stratégique présente comme la démonstration la plus propre de l'effet Hydra.

**Vérification R-9, bloquante, coût nul :** relever dans `exp_R6_generate_data.py` et dans le constructeur du bras HAT les valeurs effectives de `clock`, `delta`, `grace_period` et `min_window_length` du détecteur interne, pour les deux bras, et les consigner au gate. Trois issues :

| issue                | conséquence                                                                                                                                                             |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| horloges identiques  | le plancher est une propriété du détecteur à horloge égale ; le rapport 50/29 est interprétable, R-8 peut inclure la comparaison inter-bras                             |
| horloges différentes | le plancher HAT est dominé par sa cadence ; **le rapport 50/29 n'est pas une mesure d'effet d'ensemble** et ne doit apparaître nulle part. R-8 se restreint au bras ARF |
| non déterminable     | déclarer, et restreindre R-8 au bras ARF                                                                                                                                |

---

## 3. Réponse aux deux lacunes du §9

**Lacune 1 — mécanisme du plancher non lu dans le source.** Elle conditionne le mot, pas la charge. Six amplitudes à 50,5–53 est une mesure ; « structural » est une cause. La charge A ne dit ni l'un ni l'autre pour le HAT — elle ne cite que le plancher ARF, commité. R-9 décide si le mot peut être écrit.

**Lacune 2 — intervalles de régression sur le flanc.** Elle conditionne la charge B, et sans appel. Une erreur type de régression sur cinq points ne mesure rien, et la discipline du dossier est que tout intervalle publié vient d'un bootstrap sur graines. R-8 produit les intervalles ; aucun chiffre de flanc n'entre au manuscrit avant.

---

## 4. Charges

Ancres à re-grepper sur la v65 avant application.

### Charge R7-A — `rem:exponent` : retirer la phrase réfutée, nommer la saturation, rétrograder l'exclusion

Priorité **haute**, applicable immédiatement, chiffres commités uniquement.

**Target file: `docs/manuscript/articleA_blindspot_v65_mlj.tex`**
<<< SEARCH
~~~~~~~~~latex
  Restricted to the valid domain ($\Delta e \ge 0.10$), the median
  first-replacement time obeys a power law of exponent $-1.77$
  (seed-bootstrap $95\%$ CI $[-1.90, -1.67]$): the onset exponent excludes
  \emph{both} $\mathcal{O}(1/\Delta e)$ and the Hoeffding bound
  $\mathcal{O}((\Delta e)^{-2})$, the latter by $4.8$ regression standard
  errors.
~~~~~~~~~

=== REPLACE WITH >>>
~~~~~~~~~latex
  Restricted to the valid domain ($\Delta e \ge 0.10$), a single power law
  fitted over all eighteen amplitudes gives an exponent of $-1.77$
  (seed-bootstrap $95\%$ CI $[-1.90, -1.67]$), which excludes both
  $\mathcal{O}(1/\Delta e)$ and the Hoeffding bound
  $\mathcal{O}((\Delta e)^{-2})$. That estimator averages two regimes and we
  report it as such: the median onset is not a power law across the whole
  domain. Over the six largest magnitudes it saturates on a floor --- medians
  of $31$, $31$, $29.5$, $29$, $29$ and $29$ steps --- where the onset no
  longer responds to the drift at all. Points of zero local slope pull a pooled
  fit toward zero, so the exclusion of $-2$ is a property of the pooled
  estimator and not of the responsive regime, and the distance to the
  concentration bound is left open until the two regimes are estimated jointly.
~~~~~~~~~
>>> END OF BLOCK

**Target file: `docs/manuscript/articleA_blindspot_v65_mlj.tex`**
<<< SEARCH
~~~~~~~~~latex
  phase, which trips earlier the stronger the drift, and the pre-trained
  background tree, whose head start grows with it. The single-tree refit on the
  valid domain discriminates between a per-member and an ensemble origin.
~~~~~~~~~

=== REPLACE WITH >>>
~~~~~~~~~latex
  phase, which trips earlier the stronger the drift, and the pre-trained
  background tree, whose head start grows with it. A single-tree refit was
  pre-registered to discriminate between a per-member and an ensemble origin
  and was run; it discriminates neither. The single-tree median is itself not a
  power law over the valid domain, and a pooled fit returns an exponent that
  measures the mixture of its regimes rather than its responsive one. The
  question stands with its power declared: at one hundred seeds per amplitude,
  and with both arms saturating at large magnitude, an onset exponent is
  identifiable only on the responsive flank, which the present grid resolves
  with too few points to separate $-2$ from its neighbourhood.
~~~~~~~~~
>>> END OF BLOCK

### Charge R7-B — la structure segmentée

**Conditionnée à R-8 et à R-9.** Elle publiera l'exposant du flanc, le niveau du plancher et la position de la rupture, chacun avec son intervalle bootstrap sur graines, et remplacera le dernier membre de R7-A. Texte à prescrire quand les chiffres seront commités — pas avant.

### Charge R7-C — `sec:hydra`, la précision qui évite une nouvelle incohérence

Priorité **moyenne**, conditionnée à R-9 issue « horloges identiques ».

L'observation du §4 est juste sur le mécanisme et dangereuse sur les nombres. Le plancher d'ensemble (~29) sous le plancher d'arbre unique (~50) démontre que l'accélération opère sur la constante, y compris là où la pente est nulle. **Mais le rapport de planchers vaut ~1,7 et le facteur Hydra publié vaut 4,1 à 8,0.** Ce sont deux grandeurs mesurées à deux endroits différents — un rapport de médianes à saturation contre un rapport de temps moyens restreints sur toute la grille sous censure. Une phrase qui les rapproche sans les distinguer crée exactement la contradiction interne que le dossier traque.

Formulation à retenir, quand R-9 l'autorise :

```latex
At the largest magnitudes both arms saturate, the single tree on a floor near
$50$ steps and the ensemble near $29$: where the exponent is zero the
acceleration is still there, which is the cleanest demonstration that the
min-of-$M$ onset acts on the constant and not on the slope. The ratio of the
two floors is not the Hydra factor of
Section~\ref{sec:hydra} --- that factor is a censoring-aware restricted-mean
ratio over the whole grid, and the two quantities are measured at different
places.
```

### Charge R7-D — le flanc droit de la cloche, gratuit et cohérent

Priorité **faible**, applicable immédiatement.

La saturation explique la descente droite de la cloche, et le manuscrit ne fait pas le lien. Passé la rupture, l'amorce ne peut plus accélérer — l'ensemble adapte déjà aussi vite que son détecteur le permet — mais l'erreur résiduelle continue de baisser avec la magnitude. L'intégrale rétrécit par le haut, pas par la durée. Une phrase dans `res:bell` ou juste après referme la boucle entre les deux résultats empiriques.

---

## 5. Arbitrage 2 — retentissement sur le reste du plan

| élément                                           | effet                                                                                                                                                      |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **S1 (refit HAT)**                                | **Supprimée.** Exécutée, non discriminante, close. Remplacée par R-8 et R-9                                                                                |
| **Cadrage « over the full grid » de `sec:hydra`** | Conservé et renforcé : « full grid » devient une précision utile puisqu'on sait maintenant que la grille contient deux régimes                             |
| **Hydra comme facteur**                           | **Renforcé**, avec la précaution numérique de R7-C. C'est le seul gain net du tour                                                                         |
| **`res:bell`**                                    | Gagne la liaison de R7-D                                                                                                                                   |
| **`rem:bgswap`**                                  | Inchangé. La bande de bruit à gauche et le plancher à droite sont deux bornes distinctes du domaine où l'exposant a un sens — les nommer ensemble clarifie |
| **Table A.1 des acceptions**                      | Rien à ajouter : le plancher est un régime, pas une acception de symbole                                                                                   |

Rien d'autre ne bouge. L'exposant n'est pas porteur : `rem:exponent` conclut elle-même que l'ordonnancement `τ_ARF < τ_det` survit à l'un comme à l'autre. C'est ce qui rend la divulgation complète peu coûteuse — et c'est un argument à écrire dans la remarque, pas seulement à connaître.

---

## 6. Arbitrage 3 — chemin critique

Ordre confirmé, avec deux insertions en tête.

| #       | action                                                                                                                                                                                                                                                                            | priorité            | dépendance      |
| ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | --------------- |
| **H1**  | **R-9** — relever `clock`, `delta`, `grace_period`, `min_window_length` des détecteurs internes des deux bras, consigner au gate                                                                                                                                                  | **Bloquante**       | aucune          |
| **H2**  | Appliquer **R7-A** (deux blocs) et **R7-D**                                                                                                                                                                                                                                       | **Haute**           | aucune          |
| **H3**  | **R-8** — régression segmentée à rupture estimée sur le bras ARF, exposant de flanc, niveau de plancher, position de rupture, intervalles bootstrap sur graines. Pré-enregistrer l'estimateur avant calcul. Inclure le bras HAT **seulement si** R-9 rend les horloges identiques | Haute               | H1              |
| **H4**  | **G4** — sept payloads S2-ter                                                                                                                                                                                                                                                     | Haute               | aucune          |
| **H5**  | **G5** — arbitrage INSECTS dans `sec:limitations`                                                                                                                                                                                                                                 | Haute               | aucune          |
| **H6**  | Appliquer **R7-B** et **R7-C**                                                                                                                                                                                                                                                    | Haute               | H1, H3          |
| **H7**  | **G6** — T1 : trancher, ou déclarer la scission par famille comme choix assumé avec son motif                                                                                                                                                                                     | Moyenne             | votre arbitrage |
| **H8**  | **G11** — versionner les rapports de stream dans `docs/reports/`                                                                                                                                                                                                                  | Faible, structurant | aucune          |
| **H9**  | **G12** — résumé MLJ, pagination Table II, citation Souza, étiquette ICDM                                                                                                                                                                                                         | Avant soumission    | aucune          |
| **H10** | **G13** — pré-review adversariale, cinq profils, sur le document figé                                                                                                                                                                                                             | **Dernier**         | tout            |

Parallélisme : H1 et H2 en tête, ensemble. H4 et H5 en parallèle, indépendants de la chaîne exposant. H3 après H1. H6 ferme la chaîne. H10 seul, à la fin.

Estimation inchangée : deux tours pour fermer H1 à H9, un tour pour H10.

---

## 7. Pré-enregistrement de R-8, à écrire avant calcul

Pour éviter un aller-retour, l'estimateur à fixer :

- **Modèle.** `log τ_med(Δe) = a + b·log Δe` pour `Δe ≤ Δe*` ; `log τ_med(Δe) = c` pour `Δe > Δe*`, avec continuité imposée en `Δe*` (`c = a + b·log Δe*`), donc trois paramètres libres : `a`, `b`, `Δe*`.
- **Estimation de `Δe*`.** Balayage exhaustif sur les points de grille du domaine valide, minimisation de la somme des carrés résiduels, avec un minimum de trois points de chaque côté. Aucune coupure choisie a priori.
- **Intervalles.** Bootstrap sur graines, 2 000 répliques, médianes recalculées à chaque tirage, modèle ré-estimé **rupture comprise** à chaque réplique. Percentiles 2,5 / 97,5 sur `b`, sur le niveau du plancher et sur `Δe*`.
- **Règle de décision, fixée avant lecture.** Si l'intervalle de `b` contient −2, la distance à la borne de Hoeffding est déclarée non établie et la remarque le dit. S'il l'exclut, la distance est un résultat sur le régime réactif, énoncée avec `Δe*` et son intervalle. Si l'intervalle de `Δe*` couvre plus de la moitié du domaine valide, la rupture est déclarée non identifiable et seul le fit groupé survit, avec la saturation nommée comme aujourd'hui.
- **Comparaison de modèles.** Rapporter aussi le gain de somme des carrés du modèle segmenté sur le modèle à un seul morceau. Un segmenté qui n'améliore pas ne se publie pas.

---

## [Strategic Advice]

**Le vrai risque de ce tour n'est pas l'exposant, c'est l'horloge.** Le rapport propose le rapport de planchers 50/29 comme la démonstration la plus propre de l'effet Hydra. Si le bras HAT tourne à `clock = 32` et l'ARF à `clock = 1`, ce rapport mesure une cadence de test, pas un effet d'ensemble — et il aurait été écrit au manuscrit comme une démonstration. Deux `grep` décident. C'est exactement le profil de F23, où j'avais moi-même attribué un écart à quatre divergences de constantes sans ouvrir le script de calcul : une comparaison inter-bras dont personne n'a vérifié que les bras sont comparables.

**Le choix de différer était le bon, et je le dis parce que le contraire aurait été défendable.** Appliquer le correctif minimal en laissant « exclut −2 » aurait produit un manuscrit interne cohérent, publiable, et faux sur un point dont l'auteur connaît le biais. Renverser sans arbitrage aurait reproduit le schéma condamné. Poser les trois traitements et attendre est ce que la discipline du dossier prescrit, et c'est la première fois qu'elle est appliquée à une affirmation qui avait traversé ma propre revue.

**La forme segmentée à rupture estimée n'est pas un raffinement, c'est la seule sortie honnête.** Trois coupures cohérentes entre elles ne font pas un critère : elles font trois articles possibles. Estimer la rupture transforme le degré de liberté en paramètre mesuré avec son intervalle, et le dossier a déjà validé ce réflexe une fois — le mode de la cloche publié comme plateau plutôt que comme point, pour la même raison exactement.

**Ce qui m'échappe encore.** Je n'ai lu ni `evidence_bell.csv` régénéré, ni le `tau_exponent_hat` du gate, ni `exp_R6_generate_data.py`. Le plancher ARF que la charge R7-A cite — 31, 31, 29,5, 29, 29, 29 — vient de la colonne `tau_arf_median` que j'avais lue au tour du 26 septembre ; il est commité, mais vérifiez qu'il n'a pas bougé sous la régénération R-6. Et les sept payloads S2-ter plus `S10_external_validity.md` ne sont toujours pas lus, quatrième tour consécutif — ils sont en H4, et ils portent des charges que personne du côté orchestration n'a inspectées.