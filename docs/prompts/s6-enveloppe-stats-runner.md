Ajoute a config/experiment_ssot.py :

S6_REFINE_DELTA_E = [0.095, 0.105, 0.115, 0.125, 0.135, 0.145]
S6_REFINE_N_SEEDS = 300
S6_REFINE_ARMS = ("full",)

Lance s6_runner.py sur cette grille de raffinement, bras 'full' uniquement,
T_h = 2500, meme schema de verrou RNG que la campagne (safe_seed = seed %
(2**31 - 1), random.seed, np.random.seed, default_rng).
Ecris dans results/S6_synchronized_traces/data_refine/.

Puis rejoue s6_recompute_cusum_delta001.py sur ce repertoire et rapporte
Delta_e_c = inf{ Delta_e : q05(S_max) >= 15.00 }, avec intervalle bootstrap
au niveau graine (10 000 tirages, seed 12345).

Cout attendu : 1 800 runs, environ 15 % du temps de la campagne complete.