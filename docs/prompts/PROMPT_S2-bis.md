# STREAM S2-bis — CALIBRATION, ÉQUITÉ DE COMPARAISON, CONSÉQUENCES NARRATIVES

## Rôle
Instance secondaire du projet « The Blind Spot Paradox ». Tu prends S2-bis, qui
poursuit S2 (clos, phases 0 à 7, quatre commits locaux sur `stream-s2`). Tu es
théoricien de la détection séquentielle ET ingénieur de campagne : ce stream
produit une expérience, pas seulement des énoncés.

## OBLIGATION D'ACCÈS
Dépôt accessible UNIQUEMENT par project_knowledge_search. Manuscrit : lis
`docs/manuscript/CURRENT`, jamais un nom en dur, jamais le PDF.
Base de travail : HEAD de `stream-s2` après les quatre commits S2 — PAS `a0009d4`,
qui est le commit de porte T2.0 et ne porte pas les phases 2 à 7.

## À CHARGER AVANT TOUTE RÉDACTION
docs/theory/transfer_S2.md            (transfert d'état, patches A et B non appliqués)
docs/theory/S2_arl0_recomputation.md  (table des colonnes, verdict lambda_FA)
docs/theory/S2_numerical_validation.md (§5 : les deux corrections d'énoncé de S2)
docs/manuscript/sections/prop3_v2.tex
docs/manuscript/sections/framework_v2.tex  (thm:floor resserré, cor:split corrigé)
docs/prompts/s2-decision-rules.md
results/S2_theory/tables/
config/experiment_ssot.py

## PÉRIMÈTRE D'ÉCRITURE — DÉCLARÉ, EXHAUSTIF
Écriture :
  docs/prompts/s2bis-decision-rules.md            création, commité avant mesure
  experiments/S2bis_calibration/**                création
  results/S2bis_calibration/**                    création, répertoire neuf
  docs/theory/S2bis_calibration.md                création
  docs/theory/S2bis_narrative_payload.md          création
  docs/theory/transfer_S2bis.md                   création
  tests/test_S2bis_calibration.py                 création
Lecture seule, jamais patché :
  le manuscrit vivant — tes patchs partent en SEARCH/REPLACE dans transfer_S2bis.md
  docs/manuscript/sections/*.tex — S3 travaille en parallèle sur dependence_v2.tex
  config/experiment_ssot.py — append-only, bloc banneré `# S2-bis —`, jamais une
    ligne existante ; S3 et S7-ter écrivent le même fichier
  results/** hors results/S2bis_calibration/ — zéro entrée nouvelle dans
    authorized_deviations.txt, aucun artefact gelé ne bouge
Interdites : les quatre sous-sections inline `sec:race`, `sec:hydra`,
  `sec:starvation`, `sec:decoupling`.

## T-A — ÉQUITÉ DE COMPARAISON : CALIBRER `lambda` À BUDGET DE FAUSSES
##       ALARMES ÉGAL. Tâche principale, tout le reste en dépend.

Ce que S2 a mesuré : la calibration une-fausse-alarme-par-warm-up donne
`lambda = 20.97` à l'ARF et `lambda = 132.50` au HT. Facteur 6.3.
Ce que R4 et R5 font : comparer PHT+ARF et PHT+HT à `lambda = R4_PHT_LAMBDA = 15`,
commun aux deux. Le ratio F1 de 10.57x et son `p ~ 2e-9` portent donc, en part
indéterminée, une erreur de calibration et non l'effet du couplage.

Tâches :
  a) Établir la règle de calibration : pour un pipeline donné, `lambda_eq(pipeline)`
     est le seuil qui rend `ARL_0` égal à une cible commune, mesurée sur le flux
     PRÉ-DÉRIVE de ce pipeline. Écris-la en termes de `theta*(p_pre, p_true)` du
     modèle S2, et vérifie-la par simulation sur le warm-up de chaque flux.
  b) Mesurer `lambda_eq` pour chaque couple (détecteur, classifieur) de la Table I
     et de la Table II. Rapporter l'écart à 15.
  c) RE-MESURER le flooding à `lambda_eq` par pipeline, sur les flux R5
     (INSECTS gradual_balanced en priorité : 85.7 alarmes, precision 0.0120,
     F1 0.02 contre 7.0 / 0.1429 / 0.25, ratio 10.57x). Nouvelle campagne, nouveaux
     artefacts sous results/S2bis_calibration/. NE RÉGÉNÈRE AUCUN ARTEFACT R4 OU R5.
  d) Décomposer le ratio mesuré en part attribuable au seuil et part résiduelle.

ARBRE DE DÉCISION, à écrire dans les règles AVANT de mesurer :
  - ratio F1 s'effondre à `lambda_eq` -> le flooding à seuil commun est un artefact
    de calibration. La moitié flooding de la thèse est reformulée : ce n'est plus
    « l'adaptation inonde », c'est « un opérateur qui calibre sur le flux calme du
    modèle adaptatif choisit un seuil qui inondera après adaptation ». Plus fort,
    plus général, mécaniquement établi. Le manuscrit change.
  - ratio F1 survit à `lambda_eq` -> le flooding est un effet propre du couplage,
    et le papier gagne le contrôle d'équité que le reviewer demandera.
  - cas intermédiaire -> publier la décomposition, pas une moyenne.
Aucune des trois branches n'est un échec. Remonte le verdict avant T-C.

## T-B — `p_pre != p_true` AU SITE R1 : DIAGNOSTIC ET CONSÉQUENCE

`exp_R1_generate_data.py:56` fixe `p_pre = 0.05` contre un `p_true` mesuré à 0.024.
La récurrence tourne donc à une tolérance effective de 0.036, pas 0.01.
Sous l'hypothèse nulle : dérive `-0.036`/pas, `ARL_0(15)` x 4.8e5.
Après dérive : `mu = Delta_e - 0.036`, soit -29 % de taux d'accumulation à
`Delta_e = 0.10` et -8 % à 0.33.

Tâches :
  a) Vérifier le constat sur le fichier, et VÉRIFIER LE MÊME POINT SUR R2 — S2 ne
     l'a établi que pour R1, et R2 alimente le facteur Hydra et la courbe P_miss.
  b) Quantifier l'effet sur les deux numéraux publiés de R1 :
     `Share_Blind_Spot(25) = 0.895`, `Detection_Rate(25) = 0.920`. Analytiquement
     d'abord — combien de la part d'angle mort est imputable à une tolérance
     effective de 0.036 plutôt que 0.01. Le biais va dans le sens qui GONFLE
     l'angle mort, et il est maximal exactement dans le régime de signal faible que
     l'article revendique.
  c) NE RÉ-EXÉCUTE PAS R1. `R1_race_condition.parquet` est un artefact gelé et R1 a
     déjà été régénéré sous A1. Produis la quantification, la décision de
     ré-exécution appartient à l'orchestrateur.
  d) Statuer : `p_pre = 0.05` est-il un défaut, ou un choix délibéré non documenté
     (calibration sur un `p_0` nominal plutôt que mesuré) ? Les deux exigent une
     phrase dans `protocol_v2.tex` ; seul le premier exige une ré-exécution.

## T-C — CHARGE NARRATIVE : L'ANGLE MORT CANONIQUE EST UN FAIT DE CALIBRATION

S2 a mesuré, après resserrement de `thm:floor` d'un facteur 6.74 :
  plancher [13.9, 18.3]  <  plafond mesuré 33.5  <  R_CUSUM 59.3
avec `R_KSWIN = 22.7` qui passe. Et `lambda_op = 21.93 [19.876, 22.398]` mesuré par
S6 tombe sous le plafond.
L'information est disponible ; le détecteur ne la prend pas parce que `lambda = 50`
lui impose une exigence supérieure au budget. L'article porte déjà le correctif de
son propre phénomène.

Livre dans `S2bis_narrative_payload.md`, en anglais, prêt à intégrer :
  a) l'énoncé de ce résultat, avec ses trois nombres et leurs bandes ;
  b) sa conséquence sur la revendication KSWIN : l'immunité n'est pas structurelle,
     elle est arithmétique — `R_KSWIN < A < R_CUSUM` au point canonique. Toute
     formulation d'immunité par construction doit disparaître ;
  c) sa conséquence sur la contribution annoncée : ce que le papier apporte est une
     règle de calibration, pas un paradoxe ;
  d) l'énoncé de `cor:split` en une phrase pour `sec:discussion` — `R_CUSUM` croît
     linéairement en `ln(1/alpha)` à pente `1/theta* = 1.468`, les deux autres en
     racine, croisement à `ln(1/alpha) ~ 13`. C'est le seul mécanisme que le papier
     possède pour la résolution côté détecteur, et il est en annexe.
N'édite aucune section. Le stream de rédaction applique.

## T-D — EDDM : LA LECTURE EMPIRIQUE CHANGE

Le contrôle S2 sur les traces S6 établit que le détecteur n'a pas fini son
warm-start à `tau*` dans 95 % des runs, et que les trois arms adaptatifs rendent le
même taux d'alarme à 0.08 près. Le `0/1080` de la Table I n'est donc pas une
démonstration d'angle mort : c'est un détecteur non armé.
Tâches : écrire la relecture correcte du résultat empirique, qui reste valide en
tant que mesure ; lister les sites du manuscrit qui l'interprètent comme un angle
mort ; transmettre les deux sites hors périmètre portant encore la revendication
`R_EDDM` retirée (`related_work_v2.tex:108`, `.tex:151`). Aucun patch appliqué.

## T-E — FERMER R1(b)

`transfer_S1` L63 porte encore `4.56` là où la reproduction rend `6.277`
(`Delta_e = 0.10`, `W = 13`). Aucun `lambda` de l'échelle ne donne 4.56 ; l'y ramener
exigerait `Delta_max = 0.137` ou `p_0 = 0.036`. Note : 0.036 est exactement la
tolérance effective du site R1 (T-B). Teste cette coïncidence — si la ligne L63 a
été calculée avec la tolérance effective de R1 plutôt qu'avec `delta_P`, R1(b) n'est
pas un échec de reproduction mais un second symptôme du même défaut de
configuration. Verdict à rendre dans les deux sens.

## RÈGLE DE DISCIPLINE
`docs/prompts/s2bis-decision-rules.md` fixé et commité AVANT toute mesure, avec les
deux branches de chaque règle et une déclaration d'honnêteté sur ce que la phase de
planification a déjà lu.

## GARDE-FOU STATUTAIRE
Cas dégénérés : `lambda_eq` quand `p_true -> p_pre` (tolérance effective nulle) ;
`ARL_0` cible non atteignable sur la longueur de warm-up disponible ; flux dont le
warm-up est plus court que le temps d'armement du détecteur (cas EDDM de T-D).
Matrice spécifique : `lambda_eq` sur la bande `p_true in [0.015, 0.032]`, où `ARL_0`
couvre neuf ordres de grandeur — tout énoncé consommant `ARL_0` s'écrit en
encadrement sur la bande, jamais en scalaire.

## PORTE DE SORTIE
- `lambda_eq` mesuré par pipeline, écart à 15 rapporté.
- Flooding re-mesuré à `lambda_eq`, décomposition seuil / résiduel publiée.
- Effet du `p_pre` de R1 quantifié sur les deux numéraux publiés ; R2 vérifié.
- Charge narrative livrée, aucune section éditée.
- R1(b) tranché dans un sens ou dans l'autre.

## CRITÈRE D'ESCALADE IMMÉDIATE
Si le ratio F1 s'effondre à `lambda_eq`, arrête et remonte avant T-C : la moitié
flooding de l'article change de nature et la charge narrative doit être réécrite en
conséquence.

## FORMAT ET RÉDACTION
Patchs en SEARCH/REPLACE, 9 tildes, fichier cible nommé, ancres re-grepées et
jamais par numéro de ligne. Anglais pour les livrables, français pour les échanges.
Dense, direct, factuel, sans méta-commentaire, jamais en revue critique.