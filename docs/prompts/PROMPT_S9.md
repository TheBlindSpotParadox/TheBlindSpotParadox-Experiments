# STREAM S9 — COUVERTURE DÉTECTEURS, RÉGION D'ÉCHEC KSWIN, BRAS ESPACE D'ENTRÉE

## Rôle
Instance secondaire. Tu portes la contribution (C4) annoncée par l'introduction
v2 et le test le plus discriminant du repositionnement S5.

## Enjeu, en trois points
1. Le manuscrit revendique que KSWIN est « structurally immune » et atteint
   F1 = 1.00. Le reviewer #3 juge la conclusion trop large : tout détecteur
   fenêtré échoue si le transitoire est court devant sa fenêtre. Un balayage en
   alpha seul sur ProteuS ne fonde pas une immunité structurelle.
2. V7 de S6 : seul CUSUM est instrumenté. PHT, ADWIN et KSWIN n'ont AUCUNE
   trajectoire synchronisée. L'immunité revendiquée n'est pas instrumentée.
3. S5 a annoncé en contribution (C4) un bras input-space. Sans ce stream, (C4)
   est une promesse non tenue et l'introduction doit être amendée.

## OBLIGATION D'ACCÈS
project_knowledge_search exclusivement. Manuscrit vivant :
docs/manuscript/articleA_blindspot_v64_camera_ready.tex.

## À CHARGER
docs/sections/framework_v2.tex        (def:requirement : R(D, eps, alpha))
docs/sections/related_work_v2.tex     (ordonnancement des familles de moniteurs)
docs/sections/intro_v2.tex            (formulation exacte de (C4))
experiments/S6_synchronized_traces/   (harnais)
config/experiment_ssot.py
results/S6_synchronized_traces/data/traces.parquet
  -> permet de RECALCULER S_t pour tout lambda et tout delta_P sans resimuler.
     Utilise-le avant toute nouvelle exécution.

## T9.1 — Instrumentation des familles manquantes (V7)
L'INTERFACE EXISTE DÉJÀ. experiments/S6_synchronized_traces/s6_detectors.py
expose PHT, ADWIN et KSWIN derrière un contrat unique : .update(x),
.drift_detected, .statistic(), .threshold, .alarm_sense. Ne la réécris pas.
Ce qui manque est l'exécution : aucune campagne de traces ne les a fait tourner.
Trois particularités documentées, à respecter et à reporter dans le texte :
  - statistic() retourne la quantité de test PROPRE au détecteur, non rescalée ;
  - KSWIN a un sens d'alarme INVERSÉ (p-value contre alpha). Le recodage
    monotone d'une p-value en échelle d'évidence est un acte éditorial, pas une
    mesure : ne le fais pas, déclare le sens ;
  - ADWIN ne publie AUCUNE quantité de test scalaire — sa coupe se décide sur la
    structure de buckets. statistic() retourne la moyenne de fenêtre et
    threshold vaut None. C'est une lacune documentée, pas une équivalence ;
    toute figure comparative doit la porter en légende.
Utilise results/S6_synchronized_traces/data/traces.parquet pour tout ce qui se
recalcule hors ligne avant d'engager une simulation.
Consomme ssot.CUSUM_DELTA_P pour la famille CUSUM et ssot.DELTA_P pour les
autres : la scission est l'arbitrage A1, elle n'est pas un oubli.

La formule à instancier pour T9.2 est DÉJÀ dérivée dans framework_v2.tex :
  R_KSWIN = sqrt(n_stat * ln(2/alpha)) + sqrt((W/2) * ln(1/eps))
à comparer à
  R_CUSUM = lambda(alpha) + sqrt((W/2) * ln(1/eps))
  R_ADWIN = sqrt((W/2) * ln(4W/alpha)) + sqrt((W/2) * ln(1/eps))
cor:split énonce que le prix de la fausse alarme entre ADDITIVEMENT et
indépendamment de W dans R_CUSUM, et SOUS une racine de W dans les deux autres.
C'est de là que se dérive la région d'échec de KSWIN : elle existe là où
n_stat * ln(2/alpha) devient grand devant le budget A disponible, donc pour
n_stat élevé et transitoire court. Écris la prédiction quantitative AVANT
d'exécuter, et commite-la.

## T9.2 — Prédire PUIS démontrer la région d'échec de KSWIN
Ordre imposé, non négociable. À partir de R(KSWIN, eps, alpha) fourni par S1 :
  a) DÉRIVER la région d'échec prédite : durée de transitoire, taille de fenêtre,
     stat_size, alpha, calendrier de test. Écris la prédiction et COMMITE-la dans
     docs/prompts/ AVANT toute exécution.
  b) Balayer la grille complète exigée par le reviewer #3 : grille Bernoulli
     entière, tailles de fenêtre, stat_size, alpha, durées de transitoire,
     tailles d'ensemble M, largeurs de drift graduel.
  c) Confronter prédiction et mesure.
Configuration de départ au registre : KSWIN(alpha=0.005, window_size=100,
stat_size=30), KSWIN_LAG = 15.
Une surinterprétation convertie en test de falsification réussi vaut davantage
qu'une correction. Si la prédiction échoue, R(KSWIN) est faux et cela remonte
à S1/S2.

## T9.3 — Bras espace d'entrée, contribution (C4)
Détecteurs opérant sur P(X) et non sur le flux d'erreur : HDDDM, PCA-CD, MD3,
D3, plus tout candidat que la revue de S5 aura retenu. Ils ne lisent pas e_t,
donc la boucle d'adaptation ne se referme pas sur leur mesure.
TEST LE PLUS DISCRIMINANT DU REPOSITIONNEMENT S5, cité textuellement :
« un détecteur opérant sur P(X) subit une dégradation corrélée à tau_erase,
alors qu'il ne lit pas e_t » -> si cela est observé, le recadrage boucle fermée
est FAUX.
Mesure donc explicitement la corrélation entre dégradation du détecteur
input-space et tau_erase. L'absence de corrélation est le résultat attendu ET le
plus fort ; sa présence invalide la thèse de l'article et doit remonter
immédiatement.
Coût à déclarer : les détecteurs input-space ne détectent que le drift covariable.
Un drift de P(Y|X) à P(X) constant leur est invisible. Le générateur Bernoulli du
papier déplace la FRONTIÈRE, donc P(Y|X), à P(X) fixe. Ce bras peut donc être
structurellement aveugle au drift étudié. VÉRIFIE-LE AVANT D'IMPLÉMENTER, et si
c'est le cas, dis-le : c'est un résultat, pas un échec — il délimite l'espace de
conception au lieu de le peupler.

## T9.4 — Ordonnancement des familles
Produire la table qui porte (C4) : famille de moniteur x exposition à la boucle
x coût payé. Trois familles ordonnées par exposition : cumulatif sur le flux
d'erreur, fenêtré sur le flux d'erreur, distributionnel sur l'espace d'entrée.
Chaque ligne doit porter un chiffre mesuré, pas un argument.

## Environnement
Identique au prompt S8. river 0.23.0 épinglée. Verrou PRNG triple verbatim.
Garde anti-contamination results/R0[0-9]_* et R1[0-8]_*.

## Mode opératoire
Prompts d'exécution Claude Code. Documentation de configuration. Liste explicite
des fichiers à inspecter au tour suivant. Attente du retour utilisateur avant
itération. Règles de décision numériques commitées AVANT lecture des sorties.

## Porte de sortie
- PHT, ADWIN, KSWIN instrumentés, trajectoires synchronisées disponibles.
- Région d'échec KSWIN prédite avant exécution, puis observée ou réfutée.
- Toute revendication d'immunité structurelle supprimée du texte, remplacée par
  un domaine de validité mesuré.
- Bras input-space exécuté, ou son inapplicabilité au drift étudié démontrée.
- Verdict explicite sur le troisième critère de falsification de S5.

## Format et rédaction
DIFF SEARCH/REPLACE, 9 tildes. Anglais pour les livrables, français pour les
échanges. Dense, factuel, sans méta-commentaire.