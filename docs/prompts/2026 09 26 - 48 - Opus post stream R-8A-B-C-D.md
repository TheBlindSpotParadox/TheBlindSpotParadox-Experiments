# TROIS RELECTURES · ARBITRAGE T1 · CONFIRMATIONS · LANCEMENT H10

---

## 1. Vérification de cohérence demandée au §3 du rapport

Faite, et elle tient. La rupture estimée à `Δe* = 0,475` place du côté constant exactement les six amplitudes dont R7-A cite les médianes — `0,482255`, `0,487707`, `0,491644`, `0,494428`, `0,496355`, `0,497661`, de médianes `31`, `31`, `29,5`, `29`, `29`, `29`. Le point `0,47486` reste du côté loi de puissance, conformément à la convention pré-enregistrée. Douze points sur le flanc, six sur le plancher, dix-huit au total. La coupure n'a pas été choisie pour tomber là, et elle tombe là.

R-9 : verdict favorable, et il fallait le vérifier. Les deux bras cadencent à `clock = 1`. Le plancher HAT n'est pas un artefact d'horloge, le rapport 50/29 est interprétable, R7-C est autorisée.

---

## 2. Relecture 1 — R7-B

**Ne pas valider tel quel.** Le dernier membre inverse une causalité et omet le fait qui protège l'énoncé.

**Le défaut logique.** « what the pooled fit excluded was the floor's contribution, not the responsive regime's » — le fit groupé n'a pas exclu la contribution du plancher, il l'a **incluse**, et c'est cette inclusion qui a produit l'exclusion de −2. La phrase dit le contraire de ce qui s'est passé.

**Le fait manquant, et il est décisif.** Le point estimé bouge peu : `−1,774` groupé contre `−1,82` de flanc, soit `0,046`. Ce qui change, c'est la largeur : demi-intervalle `0,115` groupé contre `0,165` de flanc, un élargissement de 44 % dû à la perte de six points sur dix-huit. **L'inclusion de −2 vient majoritairement de l'élargissement honnête, pas d'un déplacement de la pente.**

Ne pas l'écrire laisse un relecteur découvrir que `−1,82` n'est pas beaucoup plus proche de `−2` que `−1,77`, et conclure que la révision est cosmétique. L'écrire est plus fort : le fit groupé donnait une précision qu'il n'avait pas.

Et le gain de SSE de 5,4 % mérite d'être dit. La règle pré-enregistrée l'a accepté ; un lecteur qui ne le voit pas croira à une amélioration franche.

### Charge R8-A — `rem:exponent`, dernier membre

**Target file: `docs/manuscript/articleA_blindspot_v65_mlj.tex`**
<<< SEARCH
~~~~~~~~~latex
The flank interval contains $-2$: the distance to the Hoeffding bound is not established on this grid --- what the pooled fit excluded was the floor's contribution, not the responsive regime's.
~~~~~~~~~

=== REPLACE WITH >>>
~~~~~~~~~latex
The flank interval contains $-2$, so the distance to the Hoeffding bound is not
established on this grid. What separates the two readings is precision rather
than location: the flank estimate sits $0.046$ from the pooled one, while its
interval is $44\%$ wider, the six floor points having left the fit. The pooled
exclusion of $-2$ was therefore produced by the floor, which contributes points
of zero local slope, and the segmented model is preferred only weakly, by
$5.4\%$ of residual sum of squares. Reporting the pooled fit alone would have
claimed a precision the responsive regime does not support.
~~~~~~~~~
>>> END OF BLOCK

Les trois chiffres — `0,046`, `44 %`, `5,4 %` — se dérivent de `tau_exponent` et `tau_segmented` déjà au gate. **Contrainte :** les deux premiers sont des quantités dérivées, pas des clés. Les ajouter au gate (`delta_estimate`, `ci_width_ratio`) avant d'appliquer la charge, sinon le manuscrit porte deux nombres calculés à la main.

---

## 3. Relecture 2 — le paragraphe INSECTS

**Structure juste, trois corrections.** J'ai lu le texte en place.

**Correction 1 — l'objection évidente n'est pas fermée.** Le paragraphe écrit que les points publiés sont sous les seuils à une fausse alarme, `20,4 < 88,8` et `77,7 < 231,8`. Un lecteur en conclut immédiatement : il suffit donc de monter le seuil jusqu'à `λ_FA`. La mesure dit non — S10 l'établit et le paragraphe ne le reprend pas : **même aux niveaux qui atteignent ou approchent `λ_FA`, la précision plafonne à 0,24 sur *gradual_balanced* et 0,22 sur *incremental_reoccurring_balanced***. Sans cette phrase, l'argument s'effondre sur la première question.

**Correction 2 — la clause finale surjoue.** « a calibration rule that returned an admissible threshold there would be the wrong rule » affirme sans critère indépendant. Le critère existe et il est déjà à moitié cité : l'erreur post-changement ne revient pas à son niveau pré-changement. La vacuité est une propriété du flux, mesurable ailleurs que par la règle. Dire cela vaut mieux que l'assertion.

**Correction 3 — le remède manque.** Le quatrième point de votre rapport — désarmement après détection, ou flux dont l'erreur revient à sa loi nulle — n'est pas dans le texte publié. Une limitation qui nomme son remède est plus solide qu'une limitation qui s'arrête. S10 avait identifié la période réfractaire comme le levier suivant.

**Ajout gratuit qui unifie.** ProteuS a `p₀ = 0` : aucun budget de fausses alarmes, donc tout seuil passe. INSECTS a `p₀` entre `0,16` et `0,26` : un budget large, donc aucun seuil ne passe. Les deux extrêmes du même axe, et `p₀` est la colonne que (C4) porte désormais. Le rapprochement coûte une phrase et relie la limitation au cadre.

### Charge R8-B — `sec:limitations`, paragraphe INSECTS

**Target file: `docs/manuscript/articleA_blindspot_v65_mlj.tex`**
<<< SEARCH
~~~~~~~~~latex
a monitor re-armed after each alarm crosses again under the post-change law, so no threshold the grid resolves buys precision $0.5$ while recall survives. The empty window is the real-stream counterpart of the detectability floor, below which the boundary itself leaves the admissible set empty; a calibration rule that returned an admissible threshold there would be the wrong rule.
~~~~~~~~~

=== REPLACE WITH >>>
~~~~~~~~~latex
a monitor re-armed after each alarm crosses again under the post-change law, so no
threshold the grid resolves buys precision $0.5$ while recall survives. Raising the
threshold to the one-false-alarm level does not repair it: at the grid points that
reach or approach those levels, precision peaks at $0.24$ on \emph{gradual\_balanced}
and $0.22$ on \emph{incremental\_reoccurring\_balanced}. The emptiness is therefore a
property of these streams and not of the rule, and it is visible independently of the
rule in the post-change error itself. The two ends of the same axis are measured here:
on ProteuS $p_0 = 0$, no threshold is bought at a false-alarm cost and every threshold
passes; on INSECTS $p_0$ runs from $0.164$ to $0.262$ and none does. The empty window
is the real-stream counterpart of the detectability floor, below which the boundary
itself leaves the admissible set empty. What the rule does not supply on these streams
is a remedy, and two are open: disarming the monitor after a detection rather than
re-arming it, and streams whose post-change error returns to its null law. Both are
left to future work.
~~~~~~~~~
>>> END OF BLOCK

Les chiffres `0,24`, `0,22`, `0,164`, `0,232`, `0,262` sont dans `s10_dual_mode.json`, tableaux `precision` et clés `p0` des panneaux d, e, f. Vérifier que `0,262` correspond bien au panneau *abrupt* avant d'écrire la plage.

---

## 4. Relecture 3 — le résumé

**Je ne valide pas la coupe, et le motif est de fond.**

La limite 150–250 mots est la règle de maison Springer, standard chez l'éditeur. Elle porte aussi une contrainte que le rapport ne mentionne pas : le résumé ne doit contenir aucune abréviation non définie ni référence non spécifiée. À vérifier : ARF, CUSUM, ADWIN, PHT dans un résumé de 249 mots.

**Ce qui a été sacrifié à tort.** Le cadrage « fault detection on an endogenous residual » est la réponse au veto du reviewer #2 — celui qui a coché « intérêt pour la communauté : non » avec confiance haute, et dont l'objection a coûté le rejet. C'est la seule addition du projet qui réponde à sa question, elle est en tête de (C1), et elle a été retirée de la seule page qu'il lira en premier. Le corps la porte, dites-vous ; il ne l'atteindra pas.

Les trois autres sacrifices sont bons. La plage de grille, les treize ordres de grandeur et Page–Hinkley dans la phrase GARCH sont des numéraux que le corps récupère.

**Deux conséquences.**

La règle de coupe est à inverser : **couper des numéraux, jamais du cadrage.** Un chiffre retiré du résumé reste lisible six pages plus loin ; un cadrage retiré ne se reconstruit pas.

Et 249 sur 250 n'est pas une marge. Les compteurs divergent sur les composés à trait d'union, le mode mathématique et les marqueurs de citation — un écart d'un ou deux mots est ordinaire. **Cible : 235 mots.**

### Charge R8-C — le résumé

Je ne prescris pas de texte : je n'ai pas le résumé courant sous les yeux, et une réécriture à l'aveugle d'une face avant de 249 mots produirait une quatrième version non relue. Prescription sous forme de contrainte, à exécuter et à me soumettre :

1. Restituer le cadrage en résidu endogène, en une proposition, **dans les deux premières phrases**.
2. Atterrir à **235 mots au plus**, comptés par `texcount` et par le compteur de Springer si accessible.
3. Les mots trouvés viennent de numéraux, jamais d'un cadrage ni d'une contribution.
4. Zéro abréviation non définie.
5. Me soumettre la version avec le décompte et la liste de ce qui a été retiré à ce tour.

---

## 5. Arbitrage T1 — assumer la scission, ne rien financer

**Verdict : assumer.** Trois raisons, dans l'ordre de poids.

**La généralisation n'a pas été refusée par un écart scientifique.** `0,9275` contre un seuil de `0,9310`, sur 3 960 cellules : trois dixièmes de point. Financer un décideur pour trancher cela avant soumission est le pire usage du temps restant.

**La scission a un mécanisme, et il est mesuré.** Une statistique cumulative dépense une intégrale ; un test à deux échantillons dépense du contraste. S9 l'a établi en réfutant `eq:Rkswin` et en lui substituant le modèle de contraste à 93,1 % d'accord. La scission n'est pas un défaut d'unification, c'est le reflet de deux mécanismes de lecture distincts.

**Publier une forme unique à 0,9275 serait pire que la scission.** Ce serait une unification qu'aucun des deux mécanismes ne soutient, défendue par un chiffre d'accord groupé — c'est-à-dire exactement le défaut que le dossier vient de passer deux tours à retirer de l'exposant : un fit monolithe sur deux régimes.

Les deux décideurs restent de la future work, et ils se nomment eux-mêmes.

**Emplacement : les deux, asymétriquement.** La portée doit se lire au moment où le prédicat est rencontré, sinon `def:blindspot` paraît universel pendant quarante pages. Le motif chiffré va en limitations, où le relecteur qui veut le nombre le trouve.

### Charge R8-D — note de portée après `def:blindspot`

**Target file: `docs/manuscript/sections/framework_v2.tex`**

Insertion après `def:blindspot`. **Avant d'appliquer, re-grepper `rem:window_requirement`** : le payload S2ter-A l'a posée avant `cor:split` et elle peut déjà porter une partie de cet énoncé. Fusionner plutôt que dupliquer.

```latex
\begin{remark}[Scope of the predicate]\label{rem:predicate_scope}
  Definition~\ref{def:blindspot} states the blind spot as a deficit of integrated
  budget against integrated requirement. It is the predicate of the monitors that
  spend an integral --- cumulative statistics on the error stream. Fixed-window
  two-sample monitors do not spend one: their detection is governed by the contrast
  available inside the window they read, and Section~\ref{sec:coverage} states and
  measures their predicate separately. We publish the two predicates rather than a
  single form covering both; the generalisation was pre-registered, fitted and
  refused (Section~\ref{sec:limitations}).
\end{remark}
```

### Charge R8-E — le motif chiffré, en limitations

**Target file: `docs/manuscript/articleA_blindspot_v65_mlj.tex`**

À poser à la suite du paragraphe INSECTS, après application de R8-B.

```latex
\textbf{Two predicates rather than one.} We do not publish a single blind-spot
predicate covering both monitor families. A generalised form was pre-registered and
fitted over three grids; it reproduced the measurements less well than the
family-specific pair, and the pre-registered rule refused it. We report the refusal
with its margin rather than adopting a unified statement the mechanisms do not
support: a cumulative statistic spends an integral of excess error, a fixed-window
two-sample test spends contrast inside its window, and no quantity we measured is
consumed by both in the same way. Two routes could still decide the question and
neither is taken here: a reliability margin for the windowed family derived at the
window scale, and the readable budget evaluated on the traces of the
classifier-driven grids.
~~~~~~~~~
```

**Contrainte de chiffre.** Le texte ci-dessus ne porte volontairement **aucun numéral**. Les valeurs `0,9275` et `0,9310`, ainsi que les trois accords par grille, figurent dans le rapport S2-ter mais je n'ai pas vérifié qu'elles vivent dans un artefact commité. Deux issues :

- **elles y sont** — remplacer « less well than » par « at $0.9275$ pooled agreement against a pre-registered threshold of $0.9310$ » et citer les trois accords par grille ;
- **elles n'y sont pas** — laisser le texte tel quel, et les faire entrer au gate avant de les écrire.

Vérifier avant d'appliquer. C'est la règle que vous avez rappelée en contrainte, et elle s'applique à ma prescription comme au reste.

---

## 6. Confirmations de moindre portée

**R7-C, la déviation.** **Validée.** Une auto-référence à l'intérieur de sa propre section est une faute, `γ_M` est défini au même endroit. Une condition : vérifier que la clause qui empêche la confusion a survécu — le texte doit toujours dire que `γ_M` est un rapport de moyennes restreintes sous censure sur toute la grille, faute de quoi le rapport de planchers ~1,7 et le facteur 4,1–8,0 se lisent comme la même grandeur. C'était l'unique raison d'être de R7-C.

**E9.** Votre vérification porte sur le placement ; la spécification portait sur autre chose. E9 vient du rapport S11-b : *« La Table II redimensionnée est en très petit corps, et quelques lignes de texte débordent de 37 pt au plus. »* Corps de caractère et débordements, pas scission ni page. À confirmer : le facteur de `\resizebox` appliqué, le corps effectif résultant, et la persistance des débordements de 37 pt. Springer impose un corps minimal lisible ; une table à 5 pt passe la compilation et échoue à la production. Après cela, E9 est close.

**E5.** Je verse la formulation d'origine ci-dessous. À déposer telle quelle dans `docs/prompts/`, datée, comme source de la reconstruction :

> **E5 — arbitrage INSECTS.** Sur les trois variantes INSECTS, aucun seuil n'est admissible jusqu'à λ = 200, la précision restant sous 0,5. Un article dont la contribution principale est une règle de calibration publie donc un jeu de données réelles où cette règle ne produit aucun réglage acceptable. Assumé et expliqué, c'est une frontière du domaine de validité. Laissé dans un rapport de stream, c'est la première question d'un évaluateur qui ouvre le dépôt. Arbitrage : écrire la frontière dans `sec:limitations`, comme sortie correcte de la règle et non comme son échec.

**Le résumé.** Limite confirmée comme règle Springer. La marge d'un mot est insuffisante : cible 235.

**S9-F / S2ter-B.** **Pas hors périmètre — à vérifier avant le figement.** S2ter-B est le texte qui *restreint* l'affirmation de S9-F selon laquelle le contraste « gouverne » la détection. Si S9-F est pending, deux états possibles et ils ne se valent pas : ou bien l'affirmation non restreinte n'est pas dans la v65, et S9-F est sans objet, à marquer superseded ; ou bien elle y est, et le manuscrit porte une revendication que sa propre charge de correction attend. Un `grep` décide. **Ne pas lancer H10 avant.**

---

## 7. H10 — ordre confirmé, et les cinq profils

**Ordre confirmé.** Relectures rendues (elles le sont), R8-A à R8-E appliquées, vérification S9-F, document figé, puis H10 seule.

**Deux règles d'exécution, non négociables.** La pré-review se fait **sur le PDF de 62 pages**, jamais sur les sources. Et l'instance qui la conduit **n'a accès à aucun rapport de stream, à aucun document de transfert, à aucun `docs/`** — seulement au PDF et au dépôt public. Un relecteur ne dispose de rien d'autre ; une pré-review qui lit les rapports trouve ce qu'on lui a dit de trouver.

**Les cinq profils.**

| #      | profil                                               | mandat                                                                                                                                                                                                            |
| ------ | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **P1** | Théoricien des temps d'arrêt — absent du panel ICDM  | Chaque proposition, chaque borne, chaque preuve. Il aurait trouvé la Proposition 3 en dix minutes ; il cherche la suivante. Cibles naturelles : `prop:certificate`, les bornes de dépendance, le prédicat scindé  |
| **P2** | Successeur du reviewer #2 — prémisse et généralité   | Pourquoi ce moniteur externe existe-t-il ? Le recadrage en boucle fermée tient-il ? Une seconde implémentation et un second générateur suffisent-ils ? Il a rejeté l'article sur la prémisse avec confiance haute |
| **P3** | Successeur du reviewer #3 — auditeur d'artefact      | Ouvre le dépôt public, recoupe chaque numéral du manuscrit contre le fichier qui le porte, cherche la divergence manuscrit/artefact. Il en a trouvé deux sur la v63                                               |
| **P4** | Successeur du reviewer #4 — conception expérimentale | La mesure mesure-t-elle ce qu'elle prétend ? Les bras comparés sont-ils comparables ? Les fenêtres, les censures, les unités de rééchantillonnage                                                                 |
| **P5** | Éditeur associé MLJ / praticien du flux              | La règle de calibration est-elle déployable ? Le papier livre-t-il ce que le résumé promet ? Les 62 pages sont-elles justifiées ?                                                                                 |

**Livrable attendu de H10 :** une liste d'objections, chacune avec sa page, son ancrage textuel, sa sévérité, et le verdict — réparable avant soumission, à déclarer en limitation, ou bloquante. Pas de synthèse, pas de note globale : des objections localisées.

---

## 8. Actions

| #       | action                                                                                                                                    | priorité               |
| ------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| **I1**  | Ajouter `delta_estimate` et `ci_width_ratio` au gate, puis appliquer **R8-A**                                                             | **Haute**              |
| **I2**  | Vérifier `0,262` au panneau *abrupt*, puis appliquer **R8-B**                                                                             | **Haute**              |
| **I3**  | **R8-C** — résumé : restituer le cadrage en résidu endogène, cible 235 mots, me soumettre la version avec décompte et liste des retraits  | **Haute**              |
| **I4**  | Vérifier la présence de `0,9275` / `0,9310` dans un artefact commité, puis appliquer **R8-D** et **R8-E** dans la variante correspondante | **Haute**              |
| **I5**  | `grep` sur l'affirmation non restreinte de S9-F dans la v65. Si présente : appliquer S9-F et S2ter-B. Sinon : marquer superseded          | **Bloquante pour H10** |
| **I6**  | Vérifier la clause « restricted-mean ratio over the whole grid » de R7-C                                                                  | Moyenne                |
| **I7**  | E9 : facteur de `\resizebox`, corps effectif, débordements de 37 pt                                                                       | Moyenne                |
| **I8**  | Verser E5 dans `docs/prompts/`, daté                                                                                                      | Faible                 |
| **I9**  | Commiter par chemins explicites, cinq portes, figer                                                                                       | Après I1–I7            |
| **I10** | Lancer **H10** sur le PDF figé, cinq profils, sans accès aux rapports                                                                     | **Dernier**            |

I1 à I4 sont parallélisables. I5 précède I9. I10 seule, après.

---

## [Strategic Advice]

**La coupe du résumé est la décision la plus coûteuse du tour, et elle a été prise pour tenir un compteur.** Le cadrage en résidu endogène est ce que le projet a mis six mois à construire pour répondre au seul relecteur qui a rejeté la prémisse. Il a été retiré de la première page pour gagner quatorze mots. Un numéral retiré d'un résumé se retrouve six pages plus loin ; un cadrage retiré ne se retrouve pas, parce que le lecteur qui en avait besoin a déjà décidé. La règle à retenir dépasse ce tour : sous contrainte de longueur, on coupe ce que le corps récupère.

**La découverte que les sept payloads S2-ter étaient déjà appliqués mérite une ligne de suivi.** Le transfert les déclarait pending, l'arbre disait le contraire, et le test passait dans les deux états. C'est le quatrième tour où un document d'état diverge de l'état réel — le `.tex` racine périmé, les trois streams non commités, S9-F aujourd'hui. Le correctif n'est pas de vérifier plus : c'est que tout test de charge échoue sur l'état `pending` quand la cible est atteinte, au lieu de l'accepter. Un test qui accepte les deux états ne mesure rien.

**Sur T1, je tranche « assumer » sans hésitation et je note pourquoi c'est confortable.** Le dossier vient de passer deux tours à retirer un fit monolithe sur deux régimes. Publier un prédicat unique à 0,9275 sur deux familles de statistiques dont les mécanismes de lecture diffèrent serait la même faute, sur un autre objet. La scission est le résultat, pas le pis-aller.

**Ce que je n'ai pas vérifié.** Je n'ai lu ni le résumé courant, ni `rem:exponent` dans son état post-R7-B, ni `transfer_S9.md`, ni `S10_external_validity.md` en entier. Les chiffres de R8-A sont dérivés des valeurs du rapport, pas lus au gate — d'où l'exigence de les y faire entrer avant de les écrire. Le paragraphe INSECTS, lui, je l'ai lu verbatim, et les trois corrections portent sur ce texte-là.