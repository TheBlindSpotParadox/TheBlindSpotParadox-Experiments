# S5 — Transfert d'état vers l'instance primaire

## Périmètre exécuté

T1 à T8 traités. Livrables 1 à 7 produits. Porte de sortie franchie sur les
quatre critères : réponse au veto de #2 en première phrase du premier
paragraphe ; zéro citation non vérifiée ; deux termes nommés ; T3–T6 présents
dans le texte.

## Thèse du repositionnement

Le manuscrit v64 défendait un phénomène. Le v2 défend un **problème de
dimensionnement**. La chaîne est : l'adaptation ferme la boucle sur le signal
mesuré → le changement persistant devient transitoire → la théorie de la
détection transitoire fournit le critère → la conception devient un calcul de
fenêtre. La généralité ne repose plus sur l'étendue expérimentale mais sur la
topologie de la boucle, ce qui neutralise l'objection 2 du reviewer #2
(« configuration-specific »).

## Faits établis, opposables

- **SR 11-7 abrogé le 17/04/2026**, remplacé par Fed SR 26-2 / OCC 2026-13.
  Toute occurrence de SR 11-7 dans les autres streams doit être corrigée.
- **EU AI Act Art. 15(4)** impose de traiter les boucles de rétroaction des
  systèmes qui continuent d'apprendre. C'est la citation la plus forte du
  dossier : le régulateur nomme le danger que l'article étudie.
- **Isermann (2006)** : sous-titre réel « to Fault Tolerance ».
- Le masquage de défaut sous rétroaction est **documenté**, y compris pour des
  correcteurs adaptatifs. Le recadrage T3 n'est pas une analogie improvisée.

## Contrats d'interface — bloquants pour d'autres streams

| #   | Objet                                                                                                                                                                                                                              | Stream concerné | Nature                   |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- | ------------------------ |
| I1  | `intro_v2.tex` référence `\label{sec:blindspot}`, `sec:starvation`, `sec:experiments`, `sec:discussion`, `sec:related`. Les labels doivent être préservés lors de la reconstruction théorique.                                     | S1, S2          | Contrat de nommage       |
| I2  | `\tau_{\mathrm{erase}}` est défini dans l'intro comme **retour de l'erreur d'ensemble dans la tolérance**, jamais comme premier remplacement d'arbre. S1 emploie déjà `tau_erase`. Notation alignée.                               | S1, S6          | Notation                 |
| I3  | L'intro annonce en (C2) « une condition de dimensionnement à horizon fini » et « un plancher de détection ». S1 doit livrer les deux, ou (C2) est réécrit.                                                                         | S1              | Dépendance de contenu    |
| I4  | L'intro annonce en (C3) des traces synchronisées et **la corrélation entre comptage de remplacements et récupération de l'erreur**. C'est la demande explicite des reviewers #1, #3, #4. Sans S6, (C3) est une promesse non tenue. | S6              | Dépendance expérimentale |
| I5  | L'intro annonce en (C4) un **bras input-space**. Le volet expérimental est confié à S9. Si S9 n'aboutit pas, (C4) se replie sur une contribution d'analyse et la §II-E reste, mais l'intro doit être amendée.                      | S9              | Dépendance expérimentale |
| I6  | Le préambule requiert TikZ (DIFF fourni).                                                                                                                                                                                          | Compilation     | Structurel               |
| I7  | `articleA_biblio_v2.bib` = v64 ++ additions. La concaténation n'est pas faite.                                                                                                                                                     | Intégration     | Action manuelle          |

## Points laissés ouverts

1. **Titre.** Trois options proposées dans `terminology_map.md`. Décision hors
   périmètre S5. Le verbe « Defeat » relève de la même famille que les
   superlatifs supprimés ; le conserver rouvre le grief de présentation.
2. **Abstract.** Non traité par S5, mais il concentre six des sept termes
   supprimés et l'affirmation « permanently erasing », factuellement fausse. À
   affecter — le plus cohérent est de l'attacher à S5 en second tour, l'abstract
   étant la contraction de l'introduction.
3. **Réserve Digital Omnibus.** Les articles 15 et 72 de l'AI Act ont été
   amendés ; le texte publié sur le portail officiel n'est pas à jour.
   Revérifier avant soumission.
4. **Conclusion et §Discussion.** Le reviewer #3 demande que la distinction
   *starvation* (synthétique) / *flooding* (données réelles) apparaisse dans
   l'abstract et la conclusion. L'introduction v2 la porte ; les deux autres
   emplacements ne sont pas couverts par S5.

## Critères de falsification du repositionnement

Le recadrage boucle fermée est faux si l'une de ces conditions est observée :

- la sévérité de la starvation ne dépend pas monotonement du rapport entre
  vitesse d'effacement et constante d'intégration du détecteur, à
  $\mathrm{ARL}_0$ fixé ;
- un classifieur adaptatif à mécanisme interne différent d'ADWIN, à
  $\tau_{\mathrm{erase}}$ comparable, ne produit pas de blind spot comparable ;
- un détecteur opérant sur $P(X)$ subit une dégradation corrélée à
  $\tau_{\mathrm{erase}}$, alors qu'il ne lit pas $e_t$.

Le troisième test est le plus discriminant et relève de S9.