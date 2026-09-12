# STREAM S7-ter — PROTOCOLE EXPÉRIMENTAL, WARNING DETECTOR, ORACLE Delta_e

## Rôle
Instance secondaire. Tu clos les trois éléments de la spécification S7 qui n'ont
jamais été portés au plan d'exécution. Auditeur de reproductibilité et
statisticien appliqué.

## Pourquoi ce stream existe
S7 est clos sur son plan, pas sur sa spécification. Trois éléments manquent, dont
une cause de rejet nommée par le reviewer #3, ouverte depuis le premier tour.

## OBLIGATION D'ACCÈS
Dépôt accessible UNIQUEMENT par project_knowledge_search. Manuscrit vivant :
docs/manuscript/articleA_blindspot_v64_camera_ready.tex (vérifie `res:tension`).
Toute copie racine est périmée.

## À CHARGER
results/audit_S7/config_matrix.md        (matrice R1-R9 x 12 colonnes, file:line)
results/audit_S7/reconciliation_report.md (D-1 a D-12)
results/audit_S7/regeneration_spec.md    (spec écrite non exécutée)
results/audit_S7/hydra_survival.csv
config/experiment_ssot.py
tests/test_S7_consistency.py
CLAUDE.md

## LOT A — Section « Experimental Protocol » (Lot 3, jamais produit)
Demande nominative du reviewer #3. Aucun calcul requis : tous les éléments
existent. C'est le livrable le plus rentable du projet.
Livrable : docs/sections/protocol_v2.tex
Contenu obligatoire :
  - unité exacte de rééchantillonnage des intervalles de confiance (la graine ;
    hydra_survival.csv porte le schéma apparié, BOOT_SEED = 20260906,
    N_BOOT = 10000)
  - procédure d'agrégation inter-graines
  - traitement des 12 transitions ProteuS
  - hyperparamètres complets détecteurs et forêts (config_matrix.md)
  - correction pour comparaisons multiples, ou justification explicite de son
    absence
  - TRAITEMENT DES SÉPARATIONS COMPLÈTES. Point technique : p = 1.86e-9 est la
    butée de résolution du test des signes à n = 30, pas une estimation. À
    rapporter comme p <= 2^-29 accompagné d'une taille d'effet. Toute cellule à
    F1 = 0.00 contre F1 = 1.00 relève du même traitement.
  - légitimité du bootstrap apparié : R2, R6, R7 et R9 consomment exactement
    deux rng.normal() par pas depuis default_rng(safe_seed) ; les flux de
    covariables sont bit-identiques pour un couple (boundary_shift, seed)
  - verrou PRNG triple par worker, reproduit verbatim, avec son motif (les
    chemins Cython de River lisent le singleton NumPy global)

## LOT B — F16 / T2.2 : unification du warning_detector
R3 et R4 laissent le détecteur d'avertissement au défaut river ADWIN(clock=32)
là où R1, R2, R5, R6, R7, R8 et R9 épinglent les deux. Le reviewer #3 le dit
explicitement : ce détecteur contrôle la disponibilité des arbres de
remplacement, donc la durée du transitoire.
Contexte aggravant mesuré par S6 (G2) : 100 % des remplacements installent un
arbre n'ayant rien appris (47/47 et 36/36), et les deux ADWIN d'un membre sont
des clones alimentés à l'identique qui déclenchent au même pas. La configuration
d'avertissement est donc mécaniquement déterminante ET actuellement inerte dans
la configuration testée. Les deux faits doivent coexister dans le texte.
Tâches :
  a) Unifier sur le SSOT.
  b) Ré-exécuter R3 et R4.
  c) Rapporter l'avant/après sur toute valeur du manuscrit issue de R3 ou R4,
     Table I incluse.
  d) Si un numéral du manuscrit bouge, produire le DIFF ancré.

## LOT C — F21 / T2.4 : oracle Delta_e par classifieur gelé
Spécifié, jamais implémenté. C'est l'angle mort scientifique du dossier.
Le bras synthétique utilise Delta_e THÉORIQUE, au motif explicite du manuscrit
que la mesure empirique est contaminée par l'adaptation (« at b = 4.0, empirical
Delta_e ~ 0.02 vs theoretical ~ 0.50 »). Le bras réel utilise un Delta_e
« adaptive » mesuré sur un flux déjà en adaptation, donc exactement la grandeur
contaminée. Les Delta_e BAF sortent à -0.0009, -0.0000, +0.0001 avec des IC
couvrant zéro : ce que produirait un estimateur aveugle au drift qu'il mesure.
Implémentation :
  - exécuter en parallèle sur le même flux un classifieur GELÉ (adaptation
    désactivée après la chauffe), qui donne le saut d'erreur réel non contaminé
  - S6 dispose déjà du bras `frozen` : réutilise sa mécanique (fork deepcopy),
    ne la réinvente pas
  - recalculer Delta_e sur les trois variantes BAF et les trois INSECTS
ARBRE DE DÉCISION, à trancher sur mesure :
  - Delta_e_oracle ~ 0 sur les trois BAF -> BAF devient un contrôle négatif
    explicite dans le manuscrit, ce qui RENFORCE l'article. Argument corroborant
    déjà disponible : Table II montre F1 ~ 0.10 / 0.09 / 0.00 y compris pour
    PHT+HT NON adaptatif ; si la ligne de base non adaptative échoue aussi, il
    n'y a pas de point aveugle à démontrer sur BAF.
  - Delta_e_oracle >> 0 -> BAF est un flux à drift MASQUÉ par l'adaptation, et
    c'est la démonstration la plus forte du papier, actuellement invisible.
Ne tranche pas avant mesure. Remonte le verdict.

## LOT D — Hygiène restante
docs/manuscript/CURRENT et sa garde sont FAITS (action A4). La suite est passée
de 16 à 24 tests au lot A1-A10. Établis d'abord ce qui reste, puis exécute :
  - Recenser lesquels des cinq tests de non-régression R1 à R5 de
    regeneration_spec.md sont désormais couverts par les 8 tests ajoutés, et
    implémenter le solde. Table I (R4) et Table II (R5) sont les cibles
    prioritaires.
  - Gel bit-à-bit : établir la couverture actuelle après régénération de R1 et
    R9 sous A1. Étendre à R2, R3 et R7. Sur 48 coeurs le coût est faible et cela
    transforme la preuve AST statique en preuve empirique.
  - authorized_deviations.txt déclare 5 écarts de baseline sur 34. Vérifier que
    chacun correspond bien à un changement de constante voulu par A1 ou A2, et
    non à une dérive. Un écart motivé mais non tracé à une action est un défaut.
  - 18 jointures flottantes recensées. Toute lecture CSV concernée doit porter
    float_precision='round_trip' : sans lui, la jointure R6<->R9 perdait
    silencieusement 400 lignes sur 2000. Ajouter une garde statique.
  - sha256_pre.txt est déprécié sans consommateur (commit 271bf2e). Vérifier
    qu'aucun test ne le lit encore.

## LOT E — Fraîcheur des sources
docs/editorial/source_verification.md porte une date de vérification
(2026-09-06) et AUCUNE date de péremption. Trois réserves y sont calées sur un
calendrier conférence désormais abandonné : Digital Omnibus amendant l'AI Act
(Art. 15 et 72), acte d'exécution Art. 72, statut commercial de SageMaker Model
Monitor. La garde A10 couvre les sources proscrites, pas la fraîcheur des
sources citables. Les deux réserves réglementaires vieillissent vite et
l'Art. 15(4) est la citation la plus forte du dossier.
Tâches : ajouter une colonne expires_on par entrée ; ajouter un test qui échoue
au-delà ; revérifier les trois réserves et dater la revérification.

## Mode opératoire
Claude Code exclusif, un agent par worktree, parallélisme par git worktree jamais
par agents concurrents sur un checkout. Un agent ne tranche jamais une politique
de dépôt : il remonte. Aucune constante redéclarée en littéral local, sous peine
d'échec de test_S7_consistency.py.

## RÈGLE ANTI-DÉRIVE, IMPOSÉE
Clos ton prompt d'exécution par une table de correspondance explicite
SPÉCIFICATION -> PHASE DU PLAN. Tout élément de spécification non couvert doit
être DÉCLARÉ tel avant exécution, pas découvert après. Trois tours consécutifs
ont produit un rapport annonçant une complétion supérieure à l'état vérifiable ;
le mécanisme est constant, le plan devient le référentiel à la place de la
spécification.

## Porte de sortie
- protocol_v2.tex livré, six rubriques couvertes.
- warning_detector unifié, R3 et R4 ré-exécutés, écarts rapportés.
- Statut de BAF tranché sur mesure oracle.
- Cinq tests manquants implémentés, gel étendu à R2, R3, R7.

## Format et rédaction
DIFF SEARCH/REPLACE, 9 tildes, ancres jamais devinées. Anglais pour les
livrables, français pour les échanges. Dense, factuel, sans méta-commentaire.