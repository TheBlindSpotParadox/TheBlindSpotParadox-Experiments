# STREAM S2-ter — LE PRÉDICAT DE POINT AVEUGLE SE GÉNÉRALISE-T-IL OU SE SCINDE-T-IL ?

## Rôle
Instance secondaire, théoricien de la détection séquentielle. Tu tranches un
arbitrage de cadre que S9 a remonté et qu'aucun stream aval ne peut trancher à
sa place.

## OBLIGATION D'ACCÈS
project_knowledge_search. Manuscrit via `docs/manuscript/CURRENT`, jamais le PDF.
Base : après la passe de sauvegarde et de fusion (S9, S11-a, S8 sur main).
Vérifie `pytest tests/ -q` = 154 avant de commencer.

## À CHARGER
docs/theory/S9_detector_coverage.md      (D0-D10, 371 lignes)
docs/theory/transfer_S9.md               (8 charges)
docs/prompts/s9-decision-rules.md        (dérivation B1-B4, 414 lignes)
docs/manuscript/sections/framework_v2.tex (def:blindspot, def:requirement, eq:R*)
docs/theory/transfer_S2.md, S2_arl0_recomputation.md
results/S2bis_calibration/s2bis_proteus_gate.json

## LE FAIT À TRAITER
S9 a réfuté `eq:Rkswin` par la mesure (D2 = REFUTED : accord 0.863 canonique,
0.850 grille contrôlée, 0.850 rotation, contre le seuil 0.90 pré-enregistré).
La direction de la réfutation n'est pas celle qui était prédite : B1 prédit un
manqué sur 100 % des cellules, et KSWIN détecte 85-100 % des runs en haut de
grille. Le mécanisme est mesuré : quand Δe monte, le budget disponible tombe de
24.0 à 1.2 et la détection monte de 0.00 à 1.00.

Le modèle qui survit, à 93.1 % d'accord sur la grille entière contre 85.0 % :
    détection  <=>  min(W, n_stat) · Δe  >=  k*(α, n_stat)
Il est quantitativement juste aux frontières : à n_stat=30, α=0.005, k*=14, il
prédit la transition à W≈20 pour Δe=0.70 (observé 0.53→0.95 entre W=20 et 25)
et à W≈14 pour Δe=1.0 (observé 0.86 à W=15).

**Un test à deux échantillons ne dépense pas une intégrale. Il dépense du
contraste.** `eq:Rkswin` reste le prix de la fausse alarme ; ce à quoi on le
compare cesse d'être A.

## T1 — L'arbitrage, à rendre avant tout le reste
`def:blindspot` s'énonce aujourd'hui `A < R(D, ε, α)`. Deux sorties admissibles,
à argumenter et à trancher, pas à laisser ouvertes :
  (a) GÉNÉRALISATION — un prédicat unique dont `A < R` et le modèle de contraste
      sont deux instanciations. Il faut alors exhiber la grandeur commune et
      montrer qu'elle se réduit correctement dans les deux cas.
  (b) SCISSION PAR FAMILLE — deux prédicats, un par type de statistique
      (accumulation intégrée / contraste à deux échantillons), avec un critère
      explicite d'affectation d'un détecteur à l'une ou l'autre famille.
Contrainte : quelle que soit la sortie, la forme retenue doit prédire les trois
grilles mesurées par S9 au moins aussi bien que le modèle de contraste seul
(93.1 %), sinon elle n'est pas retenue.

## T2 — Dériver l'exigence de la famille fenêtrée en Δe
La dérivation actuelle exprime R en unités de preuve intégrée. Pour la famille
fenêtrée, dérive l'exigence en amplitude de contraste, et confronte-la à
`eq:Rkswin`. Dis où les deux coïncident et où elles divergent, en fonction de W
et de n_stat, avec la frontière `W = n_stat` explicite.

## T3 — Audit de portée du symbole W, EN UNE PASSE
`W = 57.4` est `tau_swap^(1/M)` (mesuré 57.38), pas le W de `def:times` (médiane
1995.5 au même point). Conséquence : R_KSWIN 22.68 → 68.08, et le plafond mesuré
33.5115 cesse de le satisfaire. C'est la cinquième acception du symbole, non
prévue par la table A.1.
Quatre artefacts portent la confusion. Corrige-les TOUS ou aucun :
  results/S2bis_calibration/s2bis_proteus_gate.json
  docs/theory/transfer_S2.md
  docs/theory/S2_arl0_recomputation.md
  docs/manuscript/sections/framework_v2.tex   (rem:split_measured)
Produis une table de correspondance des cinq acceptions de W, et une convention
de nommage qui les distingue. La table A.1 doit la porter.

## T4 — (C4) réécrit ou restreint
`thesis_v4.md` §T11a.4 énonce (C4) sur une loi d'échelle « racine carrée pour les
deux autres familles ». C'est la branche réfutée. Livre le texte de remplacement,
en anglais, prêt à insérer. Contraintes mesurées à honorer :
  - l'égalisation du niveau de fausses alarmes fait DESCENDRE le fenêtré
    distributionnel (0.458 → 0.337) et MONTER le fenêtré adaptatif (0.885 →
    0.926, délai 28 → 15), les deux à zéro fausse alarme. D5 = LOST.
  - le rang d'EDDM est une fonction du socle d'erreur du flux : jamais armé à
    p0 = 0, premier à p0 = 0.024 (0.974 détection, 0.020 FA), dernier à
    p0 = 0.069 (0.022 détection, 0.930 FA).
  - **toute table qui ordonne des familles porte p0 en colonne**, sinon elle
    ordonne des flux. C'est une contrainte de forme, pas une recommandation.
N'édite aucune section : livre les payloads dans ton document de transfert.

## PÉRIMÈTRE D'ÉCRITURE
Écriture : docs/theory/S2ter_*.md, docs/prompts/s2ter-decision-rules.md,
           docs/theory/transfer_S2ter.md, tests/test_S2ter_*.py,
           les quatre artefacts de T3 (correction d'étiquette uniquement)
Lecture seule : le manuscrit vivant, toutes les sections sous
           docs/manuscript/sections/, tout results/ hors T3
Interdites : les quatre sous-sections inline exclues par CLAUDE.md

## RÈGLE DE DISCIPLINE
Règles de décision commitées avant toute mesure, avec déclaration d'honnêteté sur
ce que la phase de planification a déjà lu.

## PORTE DE SORTIE
- Arbitrage T1 rendu, argumenté, une seule sortie retenue.
- Forme retenue validée à >= 93.1 % d'accord sur les trois grilles S9.
- Les quatre artefacts de T3 corrigés en une passe, table des cinq acceptions
  livrée.
- (C4) réécrit avec p0 en colonne.