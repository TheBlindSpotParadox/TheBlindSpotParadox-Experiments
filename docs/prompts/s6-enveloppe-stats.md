Crée experiments/S6_synchronized_traces/s6_envelope_stats.py.

Entrées : results/S6_synchronized_traces/data/runs.parquet,
          results/S6_synchronized_traces/data/traces.parquet,
          config/experiment_ssot.py.

Calcule et écris results/S6_synchronized_traces/tables/envelope_stats.json :

1. lambda_op_bootstrap : 10 000 rééchantillonnages au niveau graine (bloc par
   magnitude, n=100 avec remise) de min_{Delta_e in E} q05(S_max) pour
   E = [0.20, 0.50] et E = [0.20, 0.40], a delta_P = 0.01, T_h = 2500.
   Sortie : estimate, ci_lo_2p5, ci_hi_97p5, fraction_below_15.

2. crossing_counts : pour chaque (arm, delta_e), le COMPTE entier de runs avec
   S_max >= 15 et S_max >= 50. Puis, pour l'enveloppe Delta_e >= 0.20 :
   test exact de Fisher d'homogenéité sur la table 2 x 16 (arm='full',
   lambda=50), et intervalle de Clopper-Pearson exact sur le total agrégé
   uniquement si le test ne rejette pas a 5 %.

3. horizon_stability : recalcule tau_erase = argmax_t A_unrefl(t) et
   A_swap = max_t A_unrefl(t) sur T_h dans {1250, 2500, 5000} (5000 tronque
   au trace horizon disponible). Rapporte, par magnitude, la variation
   relative mediane de A_swap et la fraction de runs dont l'argmax tombe
   dans les 10 % terminaux de la fenêtre.

Contraintes : pas de nouvelle dependance, pas de simulation, determinisme
(seed bootstrap fixe a 12345), PYTHONHASHSEED=0.
Affiche un resume console et arrete-toi.

*Remarque:*
>Seuils de décision, fixés AVANT lecture des sorties :
>- Si `ci_lo_2p5(lambda_op[0.20,0.50]) < 15,00` → le régime knife-edge n'est pas publiable ; appliquer la variante « encadrement » de la section 3.4 DIFF 5 telle quelle.
>- Si `fraction_below_15 > 0,05` → idem.
>- Si la variation relative médiane de `A_swap` entre T_h = 1250 et 5000 dépasse 10 % → `tau_erase = argmax` est dépendant de l'horizon ; basculer sur un arrêt à drawdown fixe et revenir vers S1.