Dans `experiments/S6_synchronized_traces/s6_recompute_cusum_delta001.py`, modifie l'extraction pour calculer la statistique CUSUM réfléchie (S_t à delta_P = 0.01, fenêtrée à T_h = 2500 avec p̂_0 calibré sur les 1 000 pas pré-dérive) sur les TROIS bras : 'full', 'no_swap' et 'frozen'.

Exporte la table complète (60 lignes : 20 magnitudes x 3 bras) dans `results/S6_synchronized_traces/tables/cusum_delta001_quantiles_all_arms.csv`.

Affiche ensuite directement dans la console le résumé comparatif pour lambda=15 et lambda=50 (médianes de S_max, q05, q95, et taux de franchissement cross_rate_lambda15 et cross_rate_lambda50) pour les trois bras aux points clés :
- Delta_e = 0.028 (plancher de grille)
- Delta_e = 0.194 (sommet du signal)
- Delta_e = 0.327 (point canonique transfer_S1)
- Delta_e = 0.498 (plafond de grille)
Ainsi que le spread global (max / min des médianes de S_max) pour 'full' et pour 'frozen'.