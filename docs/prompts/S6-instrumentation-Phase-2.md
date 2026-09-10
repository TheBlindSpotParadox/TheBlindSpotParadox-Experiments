Phase 1 validée et commitée (16 tests verts, smoke test opérationnel).
Passe à la PHASE 2 : Campagne complète, analyse statistique et livrables finaux.

RECTIFICATIONS PRÉALABLES OBLIGATOIRES :
1. Correction de l'horizon de troncature (tau_erase) :
   Passe l'horizon post-drift T_h à 2500 pas (au moins pour delta_e <= 0.15) afin que l'argmax de A_unrefl ne bute pas sur la frontière droite de la fenêtre.
2. Bras 'static' : Conserve le bras 'static' issu de R3 pour continuité historique, mais documente explicitement dans docs/theory/S6_causal_evidence.md le biais de capacité (8 nœuds vs 30-100 nœuds).

TÂCHES DE LA PHASE 2 :

1. Exécution de la campagne complète :
   Lance la simulation complète sur la grille canonique (100 seeds x 20 magnitudes x 4 bras causaux 'full', 'no_swap', 'frozen', 'static').
   Écris les résultats dans results/S6_synchronized_traces/data/ (runs.parquet et traces.parquet partitionné).

2. experiments/S6_synchronized_traces/s6_predictive_power.py :
   - Corrélation de rang de Spearman entre tau_swap^(1/M) et A, tau_erase, tau_err(rho).
   - Ajustement d'un modèle AFT log-normal avec censure à droite via scipy.optimize.minimize sur la log-vraisemblance exacte.
   - Génération de la table LaTeX : results/S6_synchronized_traces/tables/first_swap_predictive_power.tex.

3. experiments/S6_synchronized_traces/s6_causal.py :
   - Régression segmentée de A_unrefl(t) pour localiser le point de rupture de pente et le comparer à tau_swap^(1/M).
   - Calcul des contrastes de preuve A et tau_erase entre 'full' et 'no_swap' (test de signe au niveau graine).
   - Quantification de la part d'effacement attribuée au premier swap vs aux swaps ultérieurs.

4. experiments/S6_synchronized_traces/s6_figure.py :
   - Génère la figure de synthèse à 3 colonnes (starvation, safe zone, flooding) x 3 panneaux empilés (swaps cumulés, erreur ensembliste, statistique du détecteur), axe temporel partagé, avec marqueurs verticaux (tau*, tau_swap^(1/M), tau_erase, tau_det).
   - Sortie : results/S6_synchronized_traces/figures/Fig_S6_synchronized.png.

5. Rédaction du rapport de verdict :
   Rédige docs/theory/S6_causal_evidence.md résumant :
   - Le verdict sur F6 (ratio premier swap vs adaptation totale).
   - Le verdict sur F7 (invalidation du rectangle A_rect).
   - Le verdict causal sur Hydra (le test contrefactuel no_swap vs full).
   - Les divergences de protocole relevées (notamment le docstring de R8 et le warm-up).

RÈGLE D'ARRÊT :
Exécute l'ensemble de la Phase 2, vérifie la complétude des tables et figures, et affiche un résumé textuel des résultats statistiques majeurs (valeur du Spearman, p-value du test no_swap vs full, et statut des critères de falsification a, b, c du §10).