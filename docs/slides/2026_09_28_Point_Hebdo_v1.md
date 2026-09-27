# DECK — Point Hebdo du 28/09/2026

**Titre : Du paradoxe à la règle de calibration — état de la réécriture du manuscrit**
30 slides : 23 corps + 7 annexes.

---

## SLIDE 1 — [TITRE]

**[TITLE]** Blind Spot Paradox — Manuscrit v65 figé

**[BULLET POINTS]**
- Huit faiblesses ICDM 2026 → huit réponses mesurées
- Point Hebdo C.S. du 28/09/2026
- R. Minato — Résultats, points ouverts, soumission

**[VISUAL]** Bloc teal foncé, titre sur trois lignes, filet orange, bandeau bleu bas. Composition de la slide titre du template.

---

## SLIDE 2 — [PLAN]

**[TITLE]** Plan

**[BULLET POINTS]**
- **A — Le point de départ** · Ce que les relecteurs ont reproché, et le vocabulaire pour en parler
- **B — Tableau de bord** · Huit faiblesses, huit chantiers, huit résultats
- **C — Résultats, point par point** · Ce qui répond, ce qui dépasse la demande, ce qui surprend
- **D — Ce qui reste** · En suspens et à ré-auditer
- **E — Publication** · Revue cible et solutions de repli

**[VISUAL]** Cinq pastilles lettrées A–E, titre en gras, descriptif dessous. Helper `lettered_circle`.

---

## SLIDE 3 — [DIVIDER A]

**[TITLE]** A — Le point de départ

**[BULLET POINTS]**
- Quatre relecteurs, deux rejets fermes, deux avis marginaux
- Phénomène jugé intéressant, théorie jugée insuffisante

**[VISUAL]** Bandeau teal, carré orange « A ».

---

## SLIDE 4 — [LES HUIT FAIBLESSES]

**[TITLE]** Ce que les relecteurs ont reproché

**[BULLET POINTS]**

| #      | Faiblesse                                                                                                                                                                           | Origine                    |
| ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| **W1** | La borne centrale supprime un terme positif d'une inégalité, ignore la remise à zéro du compteur, et conclut à une probabilité d'alarme nulle à horizon infini                      | 3 relecteurs               |
| **W2** | La course entre adaptation et détection compare une variable aléatoire à une constante ; la borne d'indépendance entre arbres est affirmée, pas démontrée                           | 3 relecteurs               |
| **W3** | L'adaptation de la forêt est datée au premier arbre remplacé ; aucune trajectoire synchronisée ne relie remplacement, erreur et statistique du moniteur                             | 3 relecteurs               |
| **W4** | Le principe de découplage est énoncé en « si et seulement si », que les données du papier réfutent ; sa condition mêle une horloge et un seuil, propres à deux familles différentes | 2 relecteurs               |
| **W5** | Pourquoi surveiller de l'extérieur un modèle qui se répare seul ? L'architecture n'est pas motivée                                                                                  | 1 relecteur, **avec veto** |
| **W6** | Le phénomène est-il un artefact d'une bibliothèque, d'un classifieur et d'un détecteur uniques ?                                                                                    | 2 relecteurs               |
| **W7** | L'immunité d'un détecteur à fenêtres est déclarée structurelle sur un balayage partiel                                                                                              | 1 relecteur                |
| **W8** | Validité externe, protocole statistique incomplet, écarts entre le manuscrit et son code public                                                                                     | 1 relecteur                |

**Bandeau** ★ Les scores : technique −4 / −4 / −2 / −2. Deux relecteurs se déclarent d'expertise haute ; l'un d'eux rejette la prémisse elle-même.

**[VISUAL]** Tableau trois colonnes, en-tête teal, lignes alternées. Colonne « # » en gras orange. Ligne W5 surlignée en rose pâle avec un liseré rouge à gauche.

---

## SLIDE 5 — [NOTATIONS]

**[TITLE]** Le vocabulaire, une fois pour toutes

**[BULLET POINTS]**

*Le flux et le classifieur*
- `e_t` — erreur de prédiction au pas de temps `t`, valant 0 ou 1
- `p_0` — taux d'erreur avant la rupture
- `τ*` — instant de la rupture ; `Δe` — saut du taux d'erreur qu'elle provoque
- `M` — nombre d'arbres de la forêt ; `τ_ARF` — instant du premier arbre remplacé
- `τ_erase` — instant où l'erreur moyenne repasse sous `p_0 + δ_P`
- `W` — durée du transitoire exploitable, de `τ*` à `τ_erase`

*Le moniteur externe*
- `δ_P` — tolérance : l'excès d'erreur en deçà duquel le moniteur n'accumule rien
- `S_t` — compteur cumulé, remis à zéro dès qu'il passe sous zéro
- `λ` — seuil d'alarme ; `α` — niveau de fausse alarme ; `ARL₀` — temps moyen avant fausse alarme
- `τ_det` — instant de l'alarme

*Les deux grandeurs que l'article introduit*
- `A` — **budget de preuve** : l'excès d'erreur intégré que l'adaptation laisse au moniteur
- `R(D, ε, α)` — **exigence de preuve** du moniteur `D` : ce qu'il lui faut pour alarmer avec probabilité `1 − ε` au niveau `α`

**[EQUATIONS]** Le compteur cumulé, remis à zéro. C'est l'objet que tout le papier manipule.

```
S_t = "max" ( 0 ; S_{t-1} + ( e_t - p_0 ) - %delta_P )
```

**[VISUAL]** Trois encadrés empilés — flux (bleu clair), moniteur (crème), grandeurs nouvelles (vert clair, liseré orange). La formule centrée en bas, fond BG_BLUE_LT.

---

## SLIDE 6 — [DIVIDER B]

**[TITLE]** B — Tableau de bord

**[BULLET POINTS]**
- Huit faiblesses, huit chantiers, huit résultats
- Manuscrit figé, audit adversarial à lancer

**[VISUAL]** Bandeau teal, carré orange « B ».

---

## SLIDE 7 — [TABLEAU DE BORD 1/2]

**[TITLE]** État du travail — W1 à W4

**[BULLET POINTS]**

| Faiblesse                                               | Travail réalisé                                                                                                                                                            | Résultat                                                                                                                                                                                                                   |
| ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **W1** Borne centrale invalide                          | Preuve refaite : inégalité maximale de Doob, concentration d'Azuma–Hoeffding, réunion sur les remises à zéro. Horizon infini traité par le temps moyen avant fausse alarme | **Terminé.** Borne valide, terme de fluctuation conservé. **Et elle est vide presque partout** : informative sur 32 couples `(λ, Δe)` sur 240. Le résultat porteur devient un certificat déterministe sur le budget mesuré |
| **W2** Course mal posée, indépendance non démontrée     | Course reformulée en risques concurrents avec censure. Deux bornes : une sans hypothèse de dépendance, une sous indépendance conditionnelle                                | **Terminé.** L'indépendance conditionnelle est **réfutée par le code** — la forêt partage un seul générateur aléatoire. La borne sans hypothèse porte seule, elle sature, la taille critique d'ensemble est retirée        |
| **W3** Métrique d'adaptation, pas de trajectoires       | Famille de temps d'adaptation définie et instrumentée. Bras contrefactuels partageant flux, histoire et bifurcation                                                        | **Terminé.** L'effacement vient à **98,6 %** de l'apprentissage ordinaire des arbres survivants. Le premier remplacement pèse **0,71 %** du volume — et **31 points** de taux de détection                                 |
| **W4** « Si et seulement si » réfuté, condition hybride | Biconditionnel retiré. Condition suffisante de calibration, exprimée en budget contre exigence, indépendante de la famille de détecteur                                    | **Terminé.** Plancher de détectabilité mesuré `Δe_c = 0,120` ; seuil opérationnel `λ_op = 21,9`. Deux prédicats publiés au lieu d'un, chacun avec son mécanisme                                                            |

**[VISUAL]** Tableau trois colonnes, largeurs 18 / 41 / 41 %. En-tête teal, texte blanc. Colonne 1 en gras. Lignes alternées blanc / bleu très clair. Corps 8 pt.

---

## SLIDE 8 — [TABLEAU DE BORD 2/2]

**[TITLE]** État du travail — W5 à W8

**[BULLET POINTS]**

| Faiblesse                                     | Travail réalisé                                                                                                                                                                   | Résultat                                                                                                                                                                                                      |
| --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **W5** Architecture non motivée               | Problème reformulé en détection de défaut sur un résidu endogène — le classifieur agit sur la grandeur même que le moniteur lit. Ancrage réglementaire et outillage de production | **Terminé.** Le cadre existait depuis trente ans en automatique : un régulateur à action intégrale masque le défaut aux détecteurs à résidus. Le règlement européen sur l'IA nomme le danger                  |
| **W6** Artefact de bibliothèque ?             | Autres mécanismes internes, seconde implémentation, second générateur à prior équilibré                                                                                           | **Terminé.** Le phénomène survit partout, mais il est **moins extrême** que la grille publiée ne le disait : 0,99–1,00 de manqués sur la famille d'origine, **0,33–0,77** sous le générateur corrigé          |
| **W7** Immunité surinterprétée                | Balayage complet, niveaux de fausse alarme égalisés, détecteur ré-armé à vif                                                                                                      | **Terminé, et retourné.** À seuil publié, le détecteur à fenêtres est lu **4,5× plus permissif** que le cumulatif. Sur flux à socle d'erreur non nul, il alarme **avant même la rupture**, à tous les niveaux |
| **W8** Validité externe, protocole, cohérence | Section protocole complète. Oracle sur classifieur gelé. Correction pour comparaisons multiples. Gel des empreintes                                                               | **Terminé.** L'écart de 10,6× sur données réelles tombe à **1,27** à budget égal : 90 % venait du seuil. Un jeu de données requalifié en témoin négatif, prouvé                                               |

**Bandeau** ★ Manuscrit figé le 27/09 : 64 pages, 192 tests au vert, PDF reproductible à l'octet. Reste l'audit adversarial.

**[VISUAL]** Même gabarit que la slide 7. Bandeau de conclusion crème, texte orange gras.

---

## SLIDE 9 — [DIVIDER C]

**[TITLE]** C — Résultats, point par point

**[BULLET POINTS]**
- Ce qui répond à la demande, ce qui la dépasse, ce qui surprend

**[VISUAL]** Bandeau teal, carré orange « C ».

---

## SLIDE 10 — [W1 — LA BORNE]

**[TITLE]** W1 — La borne réparée, et ce qu'elle apprend

**[BULLET POINTS]**

*Le reproche, en une phrase*
- La preuve écrivait `E[max] ≤ dérive + fluctuation`, puis gardait la dérive seule. Supprimer un terme positif d'une borne supérieure n'est pas permis.

*Ce que nous avons fait*
- Le compteur se remet à zéro : franchir le seuil, c'est le franchir depuis **l'un quelconque** des points de remise à zéro. Une réunion sur ces points, puis l'inégalité maximale de Doob, puis la concentration d'Azuma–Hoeffding pour des incréments bornés.
- Le terme de fluctuation reste. Il vaut `√((W/2)·ln(W/ε))` et il **domine** en régime de dérive faible.
- L'énoncé à horizon infini est remplacé par le temps moyen avant fausse alarme, qui croît exponentiellement avec le seuil. Après récupération, toute alarme est une fausse alarme de taux `1/ARL₀` : elle ne dit rien de la dérive.

*Le résultat inattendu*
- Lue à la vraie durée du transitoire, la borne honnête est **vide presque partout**. Informative sur 32 couples `(λ, Δe)` sur 240 testés.
- Ce domaine étroit contient exactement le point d'opération où le certificat de famine est énoncé. Le papier le dit, et déplace le résultat porteur vers un **certificat déterministe** : s'il existe une sous-fenêtre où l'aire excédentaire dépasse le seuil augmenté du coût de tolérance, l'alarme se déclenche nécessairement.

**[EQUATIONS]** La borne à horizon fini. `μ = Δe − δ_P` est le taux d'accumulation moyen ; `S_0` est le niveau du compteur à l'instant de la rupture ; la parenthèse est prise à sa partie positive.

```
P ( %tau_{det} <= W ) <= W cdot func e^{ - {2 {(%lambda - S_{0} - %mu W)}^{2}} over {W} }
```

Le certificat déterministe, vrai sur chaque exécution prise isolément. `A(k,j)` est l'aire excédentaire entre les pas `k` et `j`.

```
S_{max}(H) = "max" from { 0 <= k <= j <= H } left [ A(k,j) - (j-k) %delta_{P} right ]
```

**[VISUAL]** Deux panneaux côte à côte. À gauche, la preuve fautive : `E[max] ≤ A + B` avec `B` barré en rouge. À droite, la borne réparée, avec les deux termes `μW` et `√((W/2)ln(W/ε))` en barres empilées pour trois valeurs de `Δe` (0,10 / 0,33 / 0,50), montrant que la fluctuation domine à gauche. Sources : Doob (1953), Hoeffding (1963), Siegmund (1985), Lorden (1971).

---

## SLIDE 11 — [W2 — LA COURSE]

**[TITLE]** W2 — La course, et l'hypothèse que le code réfute

**[BULLET POINTS]**

*Le reproche*
- L'instant de détection était traité comme une constante, alors qu'il varie d'une exécution à l'autre. Et la borne d'indépendance entre arbres était annoncée, jamais démontrée.

*Ce que nous avons fait*
- La course devient un modèle de **risques concurrents avec censure** : les exécutions sans alarme sont comptées, pas écartées. C'est là que les rapports dérapent d'ordinaire.
- Deux bornes. L'une, dite de Boole, est valide quelle que soit la dépendance. L'autre suppose les arbres indépendants **conditionnellement au flux** — l'aléa propre à chaque arbre étant ses poids de rééchantillonnage et ses tirages de variables.

*Le résultat inattendu, et il est net*
- L'indépendance conditionnelle **ne tient pas** : la bibliothèque fait circuler **un seul générateur aléatoire** dans toute la forêt. La voie par inégalité de Jensen tombe.
- Reste la borne sans hypothèse. Elle sature : au point d'opération, elle affirme que la probabilité de manquer vaut au plus 100 %.
- Conséquence assumée : la **taille critique d'ensemble est retirée**, remplacée par l'incidence mesurée. Un corollaire qui ne survit pas à sa propre hypothèse ne se publie pas.
- Deux mesures de plus, non demandées : la substitution du délai d'un arbre unique à celui d'un membre de la forêt est **réfutée** sur 10 cellules testables sur 80, toujours dans le sens optimiste. Et la course **n'est pas monotone** en amplitude : à seuil intermédiaire, le moniteur gagne 0 fois, puis 32 fois sur 100, puis 0.

**[EQUATIONS]** La borne sans hypothèse de dépendance. `F` est la loi du délai d'adaptation d'un arbre ; `τ_i` celui de l'arbre `i`.

```
P ( "min"_{i} %tau_{i} <= s ) <= "min" ( 1 ; M cdot F(s) )
```

**[VISUAL]** Schéma en deux voies partant de « borne d'indépendance ». Voie haute « indépendance conditionnelle » barrée en rouge, annotée « un seul générateur pour toute la forêt ». Voie basse « Boole, sans hypothèse » en vert, aboutissant à un encadré « sature au point d'opération → taille critique retirée ». Sources : Esary, Proschan & Walkup (1967) ; Fine & Gray (1999).

---

## SLIDE 12 — [W3 — LA DÉCOMPOSITION CAUSALE]

**[TITLE]** W3 — Qui efface la preuve, exactement

**[BULLET POINTS]**

*Le reproche*
- Dater l'adaptation de la forêt au premier arbre remplacé, c'est confondre le déclencheur et le mécanisme. Et aucune figure ne montrait, sur un même axe de temps, les remplacements, l'erreur et le compteur du moniteur.

*Ce que nous avons fait*
- Trajectoires synchronisées, instrumentées pas à pas.
- Trois bras contrefactuels partageant le même flux, la même histoire et le même point de bifurcation : la forêt complète, la forêt dont on supprime les remplacements postérieurs au premier, la forêt dont on supprime tous les remplacements depuis la rupture.

*Le résultat, et il change le titre de l'article*

| Contribution à l'effacement                           | Part        | Intervalle      |
| ----------------------------------------------------- | ----------- | --------------- |
| Apprentissage incrémental des `M−1` arbres survivants | **98,64 %** | [98,48 ; 98,82] |
| Premier remplacement                                  | **0,71 %**  | [0,63 ; 0,78]   |
| Remplacements suivants                                | **0,56 %**  | [0,47 ; 0,67]   |

- Résidu d'additivité : `2,3 × 10⁻¹³`. La décomposition est exacte.
- **Le mécanisme qui donnait son nom à l'article pèse 0,7 % du volume.** Ce qui efface la preuve, c'est l'apprentissage ordinaire.
- Et pourtant ces 0,7 % **valent 31 points de taux de détection** : 0 détection sur 100 pour la forêt complète, 18 sur 100 en supprimant les remplacements postérieurs au premier, **49 sur 100** en les supprimant tous. Le premier remplacement est volumétriquement négligeable et causalement décisif.
- Mesure annexe qui contredit le récit initial : la latence du premier remplacement **n'est pas monotone**. 130 pas à `Δe = 0,028`, **417,5** à `Δe = 0,085`, puis descente jusqu'à 29. Une dérive faible élève la variance, élargit la borne de confiance du mécanisme interne, et étouffe les remplacements de bruit.

**[VISUAL]** Diagramme en cascade horizontal : barre totale « effacement », segmentée 98,64 % / 0,71 % / 0,56 % avec les intervalles. Sous la barre, trois vignettes de taux de détection (0/100, 18/100, 49/100) reliées par des flèches, annotées « 0,71 % de volume, 31 points de détection ».

---

## SLIDE 13 — [W4 — LA RÈGLE DE CALIBRATION]

**[TITLE]** W4 — Du principe réfuté à la règle qui marche

**[BULLET POINTS]**

*Le reproche*
- Un « si et seulement si » que les propres données du papier contredisaient, et une condition qui conjuguait une horloge — propre à un détecteur à fenêtre adaptative — et un seuil — propre à un compteur cumulatif. Deux familles, une seule inégalité.

*Ce que nous avons fait*
- Le biconditionnel est retiré. À sa place, une **condition suffisante** énoncée dans la seule unité qui vaut pour tout le monde : la preuve.
- Détecter exige que le budget laissé par l'adaptation excède l'exigence du moniteur.

*Le résultat, mesuré*
- **Plancher de détectabilité** : `Δe_c = 0,120`, intervalle [0,114 ; 0,127]. Sous ce plancher, aucune calibration ne satisfait à la fois le budget de fausses alarmes et le certificat.
- **Seuil opérationnel** : `λ_op = 21,93`, intervalle [19,88 ; 22,40], sur la plage `Δe ∈ [0,20 ; 0,40]`.
- Ce que le relecteur demandait — retirer un « ssi » — a produit un nombre qu'un praticien règle.

*Ce que nous n'avons pas unifié, et pourquoi*
- Deux familles de moniteurs, deux prédicats. Un compteur cumulatif dépense une **intégrale** d'excès d'erreur. Un test à deux échantillons dépense du **contraste** à l'intérieur de sa fenêtre.
- Le second modèle reproduit les mesures à **93,1 %** contre 85,0 % pour la forme unifiée. La généralisation avait été pré-enregistrée ; la règle fixée d'avance l'a refusée.

**[EQUATIONS]** La condition de calibration, indépendante de la famille de détecteur.

```
R(D, %epsilon, %alpha) <= A
```

Le prédicat propre aux détecteurs à fenêtre. `n_stat` est la taille de l'échantillon de test, `k*` le contraste minimal requis.

```
"min" (W ; n_{stat}) cdot %DELTA e >= k^{"*"}(%alpha ; n_{stat})
```

**[VISUAL]** Axe horizontal `Δe` de 0 à 0,5. Zone rouge hachurée sous 0,120 annotée « plancher de détectabilité ». Ligne horizontale `λ_op = 21,9` avec sa bande d'incertitude, tracée sur la plage [0,20 ; 0,40]. Au-dessus, deux boîtes « intégrale » et « contraste » reliées à la condition centrale.

---

## SLIDE 14 — [LE RÉSULTAT CENTRAL]

**[TITLE]** La cloche d'évidence — trois régimes, une seule courbe

**[BULLET POINTS]**

*Ce que l'article disait, et qui était faux*
- Le budget de preuve était calculé par un produit : le saut d'erreur multiplié par la durée moyenne avant le premier remplacement. Ce produit donnait une constante, « 18,5 quelle que soit la violence de la dérive ».

*Ce que nous mesurons*
- Le maximum réellement atteint par le compteur sur l'horizon, exécution par exécution, bruit compris. C'est exactement la grandeur que le détecteur compare à son seuil.

| `Δe`       | 0,028    | 0,141 | **0,194** | **0,243** | 0,327 | 0,416 | 0,498     |
| ---------- | -------- | ----- | --------- | --------- | ----- | ----- | --------- |
| `E[S_max]` | **5,28** | 29,18 | **33,20** | 32,62     | 31,33 | 26,43 | **19,13** |

- Elle monte, culmine, redescend. Facteur **3,6** entre les deux extrémités.
- Le sommet n'est pas identifiable à cent graines : les deux points du plateau diffèrent de 0,58 contre des demi-largeurs de 0,97. Nous publions le **plateau**, pas le point.

*Les trois régimes, sans un seul paramètre libre*
- `λ = 50` domine la cloche partout → détection ≤ 0,01 de bout en bout.
- `λ = 25` **coupe** la cloche → 0,00 à gauche, **0,92** au sommet, **0,04** à droite. Le taux d'échec **croît avec l'amplitude de la dérive** sur toute la moitié droite.
- `λ = 8` passe sous la cloche presque partout → zone sûre.

*Ce que cela résout*
- Le régime paradoxal — détection fiable à amplitude moyenne, famine à forte amplitude — est la **pente droite de la cloche**. Il figurait dans les données publiées depuis le début, sans explication.
- La courbe n'est pas une loi de puissance : terme quadratique en échelle logarithmique `0,500`, intervalle [0,296 ; 0,759], et il **résiste** au retrait des deux extrémités suspectes (0,474 puis 0,592 puis 0,669).

**[VISUAL]** **Figure existante à réutiliser telle quelle** : `results/S13_evidence_bell/figures/Fig_S13_evidence_bell.png`. Panneau A, la cloche avec les trois seuils horizontaux ; panneau B, la carte de détection dans le plan `(Δe, λ)`.

---

## SLIDE 15 — [W5 — LA MOTIVATION]

**[TITLE]** W5 — Pourquoi surveiller un modèle qui se répare seul

**[BULLET POINTS]**

*Le reproche, et c'était le veto*
- Un relecteur, expertise haute, coche « intérêt pour la communauté : non ». Son argument : une forêt adaptative s'adapte sans qu'on lui adjoigne un détecteur externe. L'architecture étudiée n'existerait pas.

*Notre réponse, en trois temps*

**1. Trois objectifs, pas un.** S'adapter, c'est réparer le modèle. Surveiller, c'est savoir que le monde a changé, quand et où. Alarmer, c'est déclencher un humain, une procédure, un pipeline aval. Trois fonctions, trois consommateurs. L'article ne traite que les deux dernières.

**2. Le problème a un nom ailleurs.** Le flux d'erreur lu par le moniteur est **endogène** : le classifieur agit en contre-réaction sur la grandeur même qu'on mesure. C'est le problème canonique de la détection de défaut en boucle fermée, où un régulateur à action intégrale masque le défaut aux détecteurs à résidus. Trente ans de littérature en automatique, un vocabulaire établi, une antériorité qui protège.

**3. Le régulateur nomme le danger.** Le règlement européen sur l'IA impose de traiter les boucles de rétroaction des systèmes qui continuent d'apprendre après mise sur le marché, et exige une surveillance après commercialisation. Côté bancaire, la supervision américaine a renouvelé en avril 2026 son cadre de gestion du risque modèle, qui impose une surveillance continue indépendante du modèle.

*Effet*
- La question du relecteur reçoit sa réponse dans le **premier paragraphe** de l'introduction. Un système qui se répare masque l'incident à son opérateur : c'est le sujet, et il est nommé comme tel.

**[VISUAL]** Schéma de boucle fermée : entrée `X` → classifieur → prédiction → comparaison avec l'étiquette → erreur `e_t` → moniteur → alarme. Flèche de retour épaisse, orange, du moniteur d'erreur vers le classifieur, annotée « le modèle agit sur la grandeur mesurée ». Encadré latéral avec les trois objectifs. Lien : règlement (UE) 2024/1689, https://eur-lex.europa.eu/eli/reg/2024/1689/oj

---

## SLIDE 16 — [W6 — LA GÉNÉRALITÉ]

**[TITLE]** W6 — Artefact de bibliothèque ? Non, mais moins extrême

**[BULLET POINTS]**

*Le reproche*
- Un classifieur, un détecteur interne, une bibliothèque. Le phénomène pouvait n'être qu'un effet de configuration.

*Ce que nous avons fait*
- D'autres mécanismes internes que celui d'origine.
- Une **seconde implémentation** du classifieur, écrite indépendamment.
- Un **second générateur de flux**, construit pour tenir le déséquilibre de classes constant.

*Les résultats*
- Le phénomène survit à chaque changement. La course se produit sous la seconde implémentation aux deux points d'ancrage testés.
- Mais il est **nettement moins extrême** que la grille d'origine ne le laissait croire. Taux de manqués au seuil élevé : 0,99 à 1,00 sur la famille publiée, **0,33 à 0,77** sous le générateur corrigé.
- Et une anomalie disparaît. Au-delà d'un certain saut d'erreur, le budget devenait **négatif** : la forêt adaptée terminait sous son erreur d'avant rupture. Sous le générateur à prior équilibré, ce régime **n'existe pas**. C'était un artefact du déséquilibre de classes, et il est déclaré comme tel.

*Le corollaire honnête, non demandé*
- Au quart droit de la grille d'origine, la classe minoritaire tombe sous 1,8 % du flux. Là, l'ensemble adaptatif **ne bat plus le prédicteur constant** qui répond toujours la classe majoritaire. Score d'habileté négatif à partir de `Δe = 0,482`, jusqu'à **−3,47**.
- Toute erreur résiduelle de cette zone est désormais publiée **avec son plancher trivial à côté**. Un régime dégénéré de classification n'est pas un régime de surveillance.

**[EQUATIONS]** Le score d'habileté, contre le prédicteur constant. `p` est la proportion de la classe minoritaire ; `e_res` l'erreur résiduelle de l'ensemble.

```
"skill" = 1 - {e_{res}} over {"min"(p ; 1-p)}
```

**[VISUAL]** Deux courbes superposées, `Δe` en abscisse : taux de manqués sur la famille d'origine (rouge, plateau haut) et sous le générateur corrigé (vert, descendant de 0,77 à 0,33). Sur le même axe, une troisième courbe fine en gris : le score d'habileté, franchissant zéro à 0,482, zone hachurée au-delà annotée « régime dégénéré ».

---

## SLIDE 17 — [W7 — L'IMMUNITÉ RETOURNÉE]

**[TITLE]** W7 — L'immunité du détecteur à fenêtres, démontée deux fois

**[BULLET POINTS]**

*Le reproche*
- Un balayage sur un seul paramètre, un seul flux, et la conclusion : ce détecteur est « structurellement immunisé ».

*Ce que nous avons fait*
- Balayage complet — grille d'amplitudes entière, tailles de fenêtre, tailles d'échantillon de test, niveaux de fausse alarme, durées de transitoire, tailles d'ensemble.
- Et surtout : **égalisation du niveau de fausse alarme**. Comparer trois détecteurs à seuils publiés, c'est comparer trois calibrations.

*Résultat 1 — la comparaison publiée était biaisée*
- Au point d'opération de la table principale, le détecteur à fenêtre adaptative était déployé **45 fois plus serré** que le cumulatif, et le détecteur à fenêtres **4,5 fois plus lâche**.
- Sur la famille synthétique de référence, ce dernier est **le moins bon des trois** à tous les niveaux publiés : 0,928 pour le cumulatif, 0,885 pour la fenêtre adaptative, 0,713 au mieux pour lui.
- À niveau égalisé, il **descend** (0,458 → 0,337) pendant que la fenêtre adaptative **monte** (0,885 → 0,926, délai divisé par deux).

*Résultat 2 — sa configuration déployée alarme avant la rupture*
- Vérifié contre un détecteur vivant, ré-armé : **8 à 9 alarmes** par fenêtre de 1 000 pas **antérieure** à la rupture, la première vers le pas 99. Taux de fausse alarme pré-rupture de **1,00** à tous les niveaux.
- Son score parfait tenait à une particularité du flux de test : son erreur avant rupture est **identiquement nulle**. Rien ne pouvait y produire une fausse alarme.

*Résultat 3 — le rang d'un détecteur dépend du flux, pas de la famille*
- Un quatrième détecteur, fondé sur les distances entre erreurs, change **trois fois de rang** selon le seul taux d'erreur du flux avant rupture : jamais armé quand ce taux est nul, premier à 0,024, dernier à 0,069 avec 93 % de fausses alarmes.
- Conséquence de forme, désormais imposée : toute table qui ordonne des familles de moniteurs porte ce taux **en colonne**. Sans lui, elle ordonne des flux.

**[VISUAL]** Tableau à quatre lignes (cumulatif, fenêtre adaptative, fenêtres deux échantillons, distances entre erreurs) et quatre colonnes (niveau publié, niveau égalisé, fausses alarmes pré-rupture, rang). Flèches orange dans la colonne « niveau égalisé » indiquant le sens du changement. Source : Raab, Heusinger & Schleif (2020) ; Baena-García et al. (2006).

---

## SLIDE 18 — [W8 — VALIDITÉ EXTERNE]

**[TITLE]** W8 — Ce que les données réelles disent vraiment

**[BULLET POINTS]**

*Le reproche*
- Sur données réelles, l'article montrait une inondation de fausses alarmes là où il annonçait une détection manquée. Et un jeu de données ne produisait aucun saut d'erreur mesurable.

*Résultat 1 — l'inondation était un écart de calibration*
- L'écart publié, un rapport de **10,57** en défaveur de la forêt adaptative, est reproduit à quatre décimales.
- Les deux configurations étaient lues à des seuils qui n'achètent pas le même budget de fausses alarmes : **21 d'un côté, 132 de l'autre**.
- À budget de portée égal, le rapport tombe à **1,27**, intervalle [1,16 ; 1,43]. **89,9 %** de l'écart venait du seuil.
- Le mécanisme n'est pas la réduction de variance par agrégation : l'écart est maximal là où la fenêtre de calibration est la plus courte, et il **s'inverse** sur les variantes à fenêtre longue. C'est un effet de durée d'observation.

*Résultat 2 — la cellule emblématique détecte tout, au bon seuil*
- La cellule affichée à zéro détection sur 1 080 en détecte **1 080 sur 1 080** à `λ = 5`, précision 1,000, délai moyen **6,05 pas**.
- Le détecteur à fenêtres, présenté comme supérieur, met **14 pas**. Le cumulatif le bat d'un facteur deux.
- Plafond de preuve de ce flux, mesuré pour la première fois : entre **8 et 15**. Le seuil publié était deux à trois fois trop haut.

*Résultat 3 — deux flux requalifiés, et l'un renforce l'article*
- Le jeu de données financier est un **témoin négatif prouvé** : l'erreur d'un classifieur gelé y vaut 0,0110, exactement le taux de fraude. Aucun pipeline n'y acquiert de signal. Il n'y a pas de transitoire à masquer.
- Sur un autre jeu réel, **aucun seuil n'est admissible** jusqu'à 200 : la précision plafonne à 0,333. Frontière du domaine de validité, écrite comme telle, avec ses deux remèdes ouverts.

*Résultat 4 — le protocole, et ce qu'il a coûté*
- Une correction pour comparaisons multiples **retire une affirmation** que le manuscrit avait déjà refusé de faire.
- Les intervalles de confiance mesuraient la mauvaise composante de variance : **cinq fois trop larges** à un endroit, **trois fois trop étroits** à un autre.

**[VISUAL]** Deux panneaux. À gauche, cascade du rapport 10,57 → 1,27 avec le segment « effet seuil » à −89,9 % et la ligne de parité à 1,00. À droite, courbe en escalier du taux de détection contre le seuil sur le flux emblématique : plateau à 1,00 jusqu'à 8, chute après 15, point rouge sur 15 « seuil publié », point vert sur 5 « 1080/1080, 6,05 pas ».

---

## SLIDE 19 — [CE QUE PERSONNE N'AVAIT VU]

**[TITLE]** Quatre défauts que les relecteurs n'avaient pas relevés

**[BULLET POINTS]**

- **Le flux de test n'a aucune erreur avant la rupture.** L'expérience phare, 1 080 exécutions, est mesurée sur un flux où il n'existe aucun arbitrage entre détection et fausses alarmes. Cela explique mécaniquement la précision parfaite au bon seuil — et cela impose de dire où la règle de calibration est réellement contrainte.
- **Un effondrement publié est un détecteur qui n'a jamais démarré.** Il exige 30 erreurs pour s'armer ; le flux en produit 9 sur 8 000 pas. Il n'a pas échoué à détecter.
- **Le socle d'erreur moyenné sur tout le rodage est biaisé.** Sur l'horizon, cela représente plusieurs unités d'aire — du même ordre que le seuil le plus bas testé. Faute de fenêtre pré-rupture assez longue dans les traces, cette quantité est **déclarée non mesurable** plutôt que remplacée par une valeur de référence.
- **Le facteur d'accélération de l'ensemble n'est pas une constante.** Deux estimateurs légitimes du même effet varient **en sens opposé** avec l'amplitude. Le texte le dit et l'explique : les lois de délai des deux bras ne gardent pas leur forme.

**Bandeau** ★ Chacun de ces quatre points est écrit dans le manuscrit. Un relecteur qui ouvre le dépôt les trouverait ; autant que l'annonce vienne de nous.

**[VISUAL]** Quatre encadrés en grille 2×2, pastille numérotée, titre court en gras, constat dessous. Couleurs : rouge clair, orange clair, bleu clair, vert clair. Bandeau crème en pied.

---

## SLIDE 20 — [DIVIDER D]

**[TITLE]** D — Ce qui reste

**[BULLET POINTS]**
- En suspens, et à ré-auditer

**[VISUAL]** Bandeau teal, carré orange « D ».

---

## SLIDE 21 — [EN SUSPENS ET À RÉ-AUDITER]

**[TITLE]** Points ouverts et résultats à reprendre

**[BULLET POINTS]**

*Une seule action bloquante avant soumission*
- **L'audit adversarial du manuscrit assemblé.** Cinq profils de relecteurs, lancés séparément, sans communication, sur le document figé : un théoricien des temps d'arrêt absent du panel d'origine, les successeurs des trois relecteurs critiques, un éditeur de revue. Mandat commun : chercher la contradiction interne. Quatre renversements de thèse et soixante-quatre pages : personne n'a encore lu l'ensemble d'un bout à l'autre en cherchant la faille.

*À ré-auditer — résultats dont l'énoncé est plus fragile que les autres*
- **Le choix de publier deux prédicats au lieu d'un.** La forme unifiée a été refusée par une règle fixée d'avance, à trois dixièmes de point d'écart. Le choix est assumé et argumenté par le mécanisme, mais il n'est pas tranché par une mesure décisive.
- **L'exposant de la loi d'amorce.** Déclaré **non établi** : la médiane n'est pas une loi de puissance sur le domaine valide, et la queue de grille est limitée par la résolution de la mesure.
- **Le sommet de la cloche.** Non identifiable à cent graines par amplitude. Le plateau est publié, le point ne l'est pas.
- **L'avantage résiduel à l'extrémité dégénérée de la grille.** Les intervalles chevauchent zéro ; la fenêtre de mesure y contient trop peu d'événements pour trancher.
- **La frontière sur le jeu réel sans seuil admissible.** Écrite comme limite, ses deux remèdes restent ouverts : désarmer le moniteur après détection, ou travailler sur des flux dont l'erreur revient à sa loi d'origine.

*Extension, hors périmètre de la soumission*
- **Période réfractaire après alarme.** Seul levier identifié sur l'inondation qui demande du code neuf. Réservé à la phase de révision.

**[VISUAL]** Trois colonnes. Gauche sur fond rose « Bloquant » avec une seule ligne. Milieu sur fond crème « À ré-auditer », cinq lignes à puces carrées orange. Droite sur fond vert clair « Extension », une ligne. Filets verticaux de séparation.

---

## SLIDE 22 — [ÉTAT DU GEL]

**[TITLE]** Le manuscrit est figé — les chiffres de conformité

**[BULLET POINTS]**

| Contrôle                                                 | Résultat                                                   |
| -------------------------------------------------------- | ---------------------------------------------------------- |
| Suite de tests, dépôt                                    | **192 / 192**                                              |
| Suite de tests, **depuis l'archive de soumission seule** | **173 passés, 15 sautés, 0 échec**                         |
| Empreintes des résultats publiés                         | **27 conformes, 7 écarts, tous déclarés et motivés**       |
| Compilation du manuscrit                                 | **64 pages**, zéro référence non résolue                   |
| PDF reproductible à l'octet                              | **Oui** — deux constructions indépendantes, même empreinte |

- L'archive de soumission **s'auto-vérifie** : un évaluateur qui la décompresse fait tourner la suite et recompile le papier sans rien d'autre.
- Les quinze tests sautés et leurs motifs sont expliqués dans le fichier d'accompagnement. Aucune zone d'ombre.
- Chaque nombre du manuscrit est tracé jusqu'au fichier de résultat qui le porte.

**Bandeau** ★ C'est le point fort du dossier auprès d'une revue : le paquet de reproductibilité se vérifie tout seul.

**[VISUAL]** Cinq vignettes en ligne, chacune avec son chiffre-clé en gros et son libellé dessous. Pastilles vertes, sauf « 7 écarts » en orange annotée « déclarés ». Bandeau crème en pied.

---

## SLIDE 23 — [DIVIDER E]

**[TITLE]** E — Publication

**[BULLET POINTS]**
- Revue cible, et solutions de repli

**[VISUAL]** Bandeau teal, carré orange « E ».

---

## SLIDE 24 — [CONFÉRENCES ET REVUES]

**[TITLE]** Revue cible et candidats de repli

**[BULLET POINTS]**

**Cible retenue : Machine Learning (Springer), par le Journal Track d'ECML PKDD.**
Quatre raisons, dans l'ordre de poids.
- **L'algorithme au cœur de l'article y a été publié** — la forêt adaptative étudiée, Gomes, Bifet, Read *et al.*, *Machine Learning* 106, 2017. Même revue, même objet, lectorat déjà acquis. https://doi.org/10.1007/s10994-017-5642-8
- **Pas de limite de pages.** Soixante-quatre pages avec annexes de preuve : aucun format court n'absorbe ce volume.
- **Soumission continue**, jalonnée par des dates de coupure, avec présentation en conférence en cas d'acceptation. Pas d'attente d'un cycle annuel.
- **Simple aveugle**, révisions complètes plutôt qu'une réfutation d'une page. Un dossier qui a changé de thèse quatre fois a besoin d'un échange, pas d'un verdict.
https://ecmlpkdd.org/ — Journal Track

| Conférence                               | Rang | Deadline                     | Sélect.      | Format manuscrit                           | Présentation | Rebuttal            | Adéq. | Prio  | Commentaire                       |
| ---------------------------------------- | ---- | ---------------------------- | ------------ | ------------------------------------------ | ------------ | ------------------- | ----- | ----- | --------------------------------- |
| **ECML PKDD 2027 — Journal Track (MLJ)** | A    | ≈30 oct. 26 / ≈15 janv. 27 ° | n.c. (revue) | Springer MLJ, sans limite ; annexes illim. | Exposé conf. | Révisions complètes | ★★★★★ | ★★★★★ | **Cible retenue**                 |
| PAKDD 2027                               | B    | 15 nov. 2026 °               | ≈20 % °      | LNAI, ≈13 p. °                             | Oral+poster  | Non °               | ★★★★☆ | ★★★☆☆ | Seule échéance courte             |
| KDD 2027 — Cycle 1                       | A*   | févr. 2027 °                 | ≈15–20 % °   | ACM, 9 p. + réf. °                         | Oral+poster  | Oui                 | ★★★☆☆ | ★★☆☆☆ | Barre très haute                  |
| ECML PKDD 2027 — Research                | A    | mars 2027 °                  | 24 %         | LNCS, ≈16 p. °                             | Oral+poster  | Oui                 | ★★★★★ | ★★★★☆ | Repli format court                |
| SDM 2027                                 | A    | avr. 2027 °                  | ≈25–30 % °   | SIAM, 8 p. ; annexes illim.                | Oral+poster  | Non °               | ★★★★☆ | ★★★★☆ | Annexes illimitées                |
| CIKM 2027                                | A    | mai 2027 °                   | 27 % (2025)  | ACM, ≈9 p. °                               | Oral         | Oui °               | ★★☆☆☆ | ★★☆☆☆ | Thématique peu alignée            |
| ICDM 2027                                | A*   | juin 2027 °                  | ≈10–13 %     | IEEE, 10 p. tout inclus                    | Reg./short   | Non                 | ★★★★★ | ★★★☆☆ | Retour possible, comité renouvelé |
| DSAA 2027                                | B    | juin 2027 °                  | ≈20–25 % °   | IEEE, 10 p. °                              | Oral         | Non °               | ★★★☆☆ | ★★☆☆☆ | Repli tardif                      |

° Dates 2027 projetées depuis l'édition 2026, à confirmer sur les appels officiels.

**[VISUAL]** Encadré de justification en haut (fond crème, liseré orange) puis le tableau à 10 colonnes, en-tête teal texte blanc, lignes alternées, première ligne de données surlignée crème avec liseré orange. Corps 7 pt. Étoiles en caractères pleins et vides.

---

## SLIDE 25 — [ANNEXE 1]

**[TITLE]** Annexe — La borne réparée, étape par étape

**[BULLET POINTS]**
- Le compteur est une marche réfléchie : il repart de zéro dès que le cumul devient négatif. Franchir le seuil, c'est donc le franchir depuis l'un quelconque des points de remise à zéro.
- Une réunion sur ces points de redémarrage, puis l'inégalité maximale de Doob appliquée à la martingale exponentielle, puis la concentration d'Azuma–Hoeffding pour des incréments bornés dans un intervalle de longueur 1.
- Le niveau du compteur à l'instant de la rupture n'est pas nul : il suit la loi stationnaire de la marche réfléchie, dont la queue est exponentielle. Il entre dans l'énoncé, il n'est pas escamoté.
- La frontière qui en découle fait apparaître la fluctuation explicitement.

**[EQUATIONS]** La frontière de famine. En régime de dérive faible, le second terme domine le premier.

```
%lambda_{starve}(W ; %epsilon) = %mu W + sqrt { {W} over {2} cdot ln left ( {W} over {%epsilon} right ) }
```

**[VISUAL]** Trajectoire en dents de scie du compteur, avec remises à zéro visibles et trois seuils horizontaux. Zone ombrée sur la fenêtre post-rupture.

---

## SLIDE 26 — [ANNEXE 2]

**[TITLE]** Annexe — Pourquoi le budget de preuve forme une cloche

**[BULLET POINTS]**
- **Montée, à gauche.** Le saut d'erreur est faible ; le transitoire est long, mais l'excès accumulé par pas est minuscule. Le budget reste bas.
- **Plateau, au milieu.** Le saut est assez fort pour accumuler vite, et le transitoire encore assez long pour que l'accumulation se produise.
- **Descente, à droite.** Le saut est fort, mais l'adaptation consomme le transitoire plus vite que la marche n'accumule. Et la latence du premier remplacement sature autour de 29 pas : elle ne peut plus raccourcir. L'intégrale rétrécit par le haut, pas par la durée.
- La pente locale en échelle logarithmique parcourt un facteur trois sur le domaine valide, mais les points de droite sont limités par la résolution de la médiane : l'ensemble de la queue tient en quatre demi-pas. Aucune pente ne s'y lit, dans aucun sens.
- La courbure agrégée, elle, tient : **0,500** [0,296 ; 0,759], et elle **augmente** quand on retire la queue quantifiée.

**[VISUAL]** La cloche, avec trois zones annotées « accumulation lente », « plateau », « transitoire consommé ». Sous l'axe, une bande grise sur les six dernières amplitudes annotée « résolution de mesure : 4 demi-pas ».

---

## SLIDE 27 — [ANNEXE 3]

**[TITLE]** Annexe — Le retard d'étiquetage

**[BULLET POINTS]**
- Un moniteur externe lit un flux d'erreur, donc il lui faut des étiquettes. Elles arrivent rarement à l'instant de la prédiction.
- Deux régimes, et ils ne se comportent pas pareil.
- **Le moniteur seul est retardé.** Il lit en retard une erreur que le classifieur a déjà commencé à effacer. La fenêtre exploitable rétrécit mécaniquement : la latence pénalise.
- **Le classifieur et le moniteur partagent la latence.** Le classifieur apprend aussi en retard, donc il efface plus tard. L'instant d'effacement recule de presque exactement la latence — coefficient mesuré **0,998**. La fenêtre exploitable se **ré-élargit**.
- Conséquence de conception : dans un système où les étiquettes arrivent tard pour tout le monde, le retard n'aggrave pas l'angle mort. Dans un système où seul le moniteur attend, il l'aggrave.

**[VISUAL]** Deux frises temporelles superposées. Frise 1 « moniteur seul retardé » : rupture, effacement fixe, alarme repoussée, fenêtre utile en rouge et rétrécie. Frise 2 « retard partagé » : rupture, effacement reculé de `0,998·ℓ`, fenêtre utile en vert et de largeur conservée.

---

## SLIDE 28 — [ANNEXE 4]

**[TITLE]** Annexe — Les deux prédicats, et pourquoi ils ne fusionnent pas

**[BULLET POINTS]**
- **Un compteur cumulatif dépense une intégrale.** Il additionne l'excès d'erreur pas à pas et compare la somme à son seuil. Ce qu'il lui faut, c'est une aire.
- **Un test à deux échantillons dépense du contraste.** Il compare deux fenêtres et n'a besoin que d'un écart assez net à l'intérieur de ce qu'il regarde. Allonger le transitoire au-delà de sa fenêtre ne lui apporte rien.
- La mesure tranche : quand l'amplitude augmente, le budget disponible chute de 24,0 à 1,2 pendant que la détection du second monte de 0,00 à 1,00. Un moniteur qui détecte davantage quand son budget rétrécit ne dépense pas ce budget.
- Le modèle de contraste reproduit les mesures à **93,1 %** sur la grille entière, contre 85,0 % pour la forme unifiée — et l'écart se creuse exactement là où le transitoire dépasse la fenêtre de lecture.
- La généralisation avait été pré-enregistrée avec son seuil d'acceptation. Elle a été refusée par la règle, pas par une préférence.

**[VISUAL]** Deux schémas côte à côte. À gauche, une courbe d'erreur avec l'aire sous la courbe hachurée, annotée « intégrale ». À droite, deux fenêtres adjacentes avec la différence de leurs moyennes en flèche verticale, annotée « contraste ». Sous les deux, la barre d'accord 93,1 % contre 85,0 %.

---

## SLIDE 29 — [ANNEXE 5]

**[TITLE]** Annexe — Ce que le manuscrit publie, et ce qu'il retire

**[BULLET POINTS]**

*Publié avec sa preuve ou sa mesure*
- La borne à horizon fini, avec son domaine d'informativité délimité
- Le certificat déterministe sur le budget mesuré
- La borne sans hypothèse de dépendance
- La condition suffisante de calibration, et ses deux prédicats
- Le plancher de détectabilité et le seuil opérationnel
- La cloche d'évidence et la carte de détection

*Retiré, avec le motif écrit*
- Le biconditionnel du principe de découplage
- La taille critique d'ensemble
- Le substitut rectangulaire du budget de preuve
- L'exigence de preuve du détecteur à distances entre erreurs
- L'immunité structurelle du détecteur à fenêtres
- Toute affirmation de plancher de latence

*Déclaré non mesurable*
- Le biais de fenêtre du socle d'erreur — les traces ne portent pas de phase pré-rupture assez longue. Aucune constante ne le remplace.

**[VISUAL]** Trois colonnes de listes, en-têtes colorés : vert « publié », rouge « retiré », gris « non mesurable ». Puces cochées, barrées, et point d'interrogation respectivement.

---

## SLIDE 30 — [ANNEXE 6]

**[TITLE]** Annexe — Références

**[BULLET POINTS]**

*Apprentissage sur flux*
- Gomes, Bifet, Read *et al.* (2017), *Adaptive random forests for evolving data stream classification*, Machine Learning 106 — https://doi.org/10.1007/s10994-017-5642-8
- Bifet & Gavaldà (2007), *Learning from time-changing data with adaptive windowing*, SDM
- Montiel, Halford, Mastelini *et al.* (2021), *River: machine learning for streaming data in Python*, JMLR 22 — https://jmlr.org/papers/v22/20-1380.html
- Gama, Žliobaitė, Bifet *et al.* (2014), *A survey on concept drift adaptation*, ACM Computing Surveys 46 — https://doi.org/10.1145/2523813

*Détection séquentielle de rupture*
- Page (1954), *Continuous inspection schemes*, Biometrika 41 — https://doi.org/10.1093/biomet/41.1-2.100
- Lorden (1971), *Procedures for reacting to a change in distribution*, Annals of Mathematical Statistics 42
- Moustakides (1986), *Optimal stopping times for detecting changes in distributions*, Annals of Statistics 14
- Siegmund (1985), *Sequential Analysis*, Springer
- Tartakovsky, Nikiforov & Basseville (2014), *Sequential Analysis*, CRC Press

*Concentration et dépendance*
- Hoeffding (1963), *Probability inequalities for sums of bounded random variables*, JASA 58 — https://doi.org/10.1080/01621459.1963.10500830
- Esary, Proschan & Walkup (1967), *Association of random variables*, Annals of Mathematical Statistics 38
- Fine & Gray (1999), *A proportional hazards model for the subdistribution of a competing risk*, JASA 94

*Détection de défaut en boucle fermée*
- Chen & Patton (1999), *Robust Model-Based Fault Diagnosis for Dynamic Systems*, Springer
- Isermann (2006), *Fault-Diagnosis Systems*, Springer

*Cadre réglementaire*
- Règlement (UE) 2024/1689 sur l'intelligence artificielle — https://eur-lex.europa.eu/eli/reg/2024/1689/oj

**[VISUAL]** Cinq blocs thématiques, titres en gras orange, références en 8 pt. Liens en bleu souligné.