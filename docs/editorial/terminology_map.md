# Table de traduction terminologique v64 → v2

## Règle de conservation

Un nom propre n'est conservé que si les trois conditions tiennent :
1. il désigne un **objet** ou un **mécanisme dérivé**, jamais une conséquence
   observée ni une quantité mesurée ;
2. aucun terme standard de SPC, de théorie du changement de point ou de FDI ne
   le recouvre ;
3. sa suppression obligerait à renommer l'article.

Deux termes satisfont les trois conditions. Tous les autres sont traduits.

## Termes conservés

| Terme        | Statut                                                  | Justification                                                                                                                                                                                                                                                                              |
| ------------ | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `blind spot` | conservé, minuscules, non emphatisé après la définition | Désigne la région de l'espace de conception où la fenêtre se ferme avant l'arrivée de la preuve. C'est un objet, il est défini formellement, il figure au titre. Aucun équivalent standard : « blind spot » en FDI désigne un défaut non observable, ce qui est proche mais pas identique. |
| `starvation` | conservé, minuscules                                    | Désigne le mécanisme : troncature de la fenêtre d'observation en deçà du besoin de preuve. C'est le seul objet théorique que l'article dérive. Le terme SPC voisin — insuffisance de puissance — est descriptif mais ne nomme pas la cause de la troncature.                               |

## Termes supprimés

| v64                        | v2                                                                                                        | Motif                                                                                                                                                                                        |
| -------------------------- | --------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Hydra Effect               | facteur d'accélération d'ensemble $\gamma_M := \tau_{\mathrm{erase}}^{(1)} / \tau_{\mathrm{erase}}^{(M)}$ | Quantité mesurée. Une quantité mesurée reçoit un symbole, pas un nom. Le nom masquait en outre que la mesure reposait sur le premier remplacement d'arbre, ce que trois reviewers rejettent. |
| Zombie Alarm               | alarme post-récupération                                                                                  | Conséquence observée, entièrement décrite par « l'alarme survient après le retour de l'erreur dans la tolérance ».                                                                           |
| Decoupling Principle       | condition de réactivité (suffisante)                                                                      | Réfuté comme condition nécessaire par les données de l'article (ADWIN+ARF à horloges égales). Un principe réfuté ne conserve pas son nom propre.                                             |
| Fundamental Tension        | ensemble admissible vide / région de calibrage infaisable                                                 | Décrit un fait de calibrage, énonçable en une phrase.                                                                                                                                        |
| fundamental race condition | concurrence entre effacement et accumulation                                                              | « fundamental » n'est pas démontré ; « race condition » importe une métaphore de concurrence logicielle sans contrepartie formelle.                                                          |
| blind spot **paradox**     | blind spot                                                                                                | Le suffixe « paradox » présentait comme contre-intuitif ce que la théorie de la détection transitoire prédit. Retirer le suffixe est le geste central du repositionnement.                   |

## Superlatifs et affirmations non démontrées

| v64                        | v2                                                                        | Motif                                                                                                                                                                                                      |
| -------------------------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| « permanently erasing »    | « effacé sur la fenêtre d'observation », horizon fini explicité           | **Factuellement faux** depuis la correction de la Proposition 3 : un CUSUM réfléchi à seuil fini franchit son seuil avec probabilité non nulle sur horizon infini. Reviewers #1, #3, #4 le signalent tous. |
| « single root cause »      | « mécanisme dominant sur la grille testée »                               | Non démontré ; la cause unique n'est pas identifiée expérimentalement.                                                                                                                                     |
| « structurally fail »      | « échouent sur la grille testée »                                         | Portée limitée à ce qui est mesuré.                                                                                                                                                                        |
| « perfect detection »      | « rappel de 1,00 sur la grille testée »                                   | Un chiffre remplace un superlatif.                                                                                                                                                                         |
| « escapes this outright »  | « n'est pas soumis à la même contrainte d'accumulation »                  | Énoncé mécanique et non triomphal.                                                                                                                                                                         |
| « structurally immune »    | « hors de la boucle d'erreur » ou « constante d'intégration plus courte » | Reviewer #3 : l'immunité de KSWIN n'est pas établie ; tout détecteur à fenêtre échoue si le transitoire est plus court que sa fenêtre.                                                                     |
| « entirely inoperative »   | « recall nul sur les configurations testées »                             | Idem.                                                                                                                                                                                                      |
| « ADWIN hyper-reactivity » | « constante de temps du correcteur interne »                              | Reviewer #2, commentaire 3 : attribuer le phénomène à un mécanisme interne unique détruit la généralité. Le recadrage boucle fermée le remplace.                                                           |

## Escalade vers l'instance primaire

Le titre contient `Defeat Drift Detectors`. Le verbe est de la même famille que
les superlatifs supprimés et sera lu comme tel par un reviewer qui a coché
« présentation : below average ». Trois options, décision hors périmètre S5 :

1. `Monitoring Under Closed-Loop Adaptation: When Self-Repair Starves Drift Detectors`
2. `The Adaptive Blind Spot: Transient-Change Detection on an Endogenous Error Stream`
3. `Self-Repair Is Not Self-Report: Drift Monitoring for Adaptive Stream Classifiers`

L'option 3 place la réponse au reviewer #2 dans le titre. L'option 2 est la plus
neutre et la plus lisible par un comité orienté théorie du changement de point.