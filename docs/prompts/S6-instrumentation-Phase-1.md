Phase 0 validée avec succès (G0 à G3 PASS).
Passe à la PHASE 1 : Construction du harnais, contrat Parquet et validation par smoke test.

RÉSOLUTION DES ARBITRAGES POUR LA PHASE 1 :
1. Bras factoriels causaux : Le runner doit supporter les 4 bras définis dans la spécification d'architecture :
   - 'full' : ARF nominale avec apprentissage et swaps.
   - 'no_swap' : à tau_swap^(1/M), copie profonde ; stubs inertes sur détecteurs internes (drift et warning). L'apprentissage continue, les remplacements cessent.
   - 'frozen' : à tau_swap^(1/M), copie profonde ; learn_one() n'est plus appelé.
   - 'static' : Random Forest non adaptative (référence R3).
2. Traçabilité des arbres froids (découverte G2) : Dans traces.parquet, intègre n_nodes_mean et n_active_leaves_mean pour documenter la reconstruction physique de la forêt post-swap.
3. Définitions opérationnelles : Respecte strictement s6_defs.py :
   - tau_swap^(q) calculé sur les arbres DISTINCTS via le diff de clés de _drift_tracker (jamais sur sum(values)).
   - tau_err(rho) avec hystérésis H = W/2 consécutifs sous le seuil.
   - tau_erase = argmax de A_unrefl sur [tau*, tau* + T_h].
   - Décomposition : A, A_rect, A_refl.

TÂCHES DE CODAGE :
1. experiments/S6_synchronized_traces/s6_defs.py : Métriques d'arrêt et intégrales de preuve.
2. experiments/S6_synchronized_traces/s6_detectors.py : Implémentation unique de StrictCUSUM (alignée sur config.experiment_ssot.DELTA_P), et wrappers unifiés pour PHT, ADWIN, KSWIN exposant .statistic().
3. experiments/S6_synchronized_traces/s6_runner.py : Boucle de simulation pas-à-pas avec fork par deepcopy au premier swap pour les bras 'no_swap' et 'frozen'.
4. experiments/S6_synchronized_traces/s6_writer.py : Écriture déterministe Parquet (runs.parquet et traces.parquet partitionné par delta_e) avec compression zstd et tri strict.
5. tests/test_S6_traces.py : Suite de tests vérifiant :
   - Reproductibilité octet-à-octet des Parquet sur rejeu d'une graine.
   - Monotonie de swaps_cum et err_cum.
   - A_refl >= A_unrefl à tout pas t.
   - Invariant 'no_swap' : zéro swap supplémentaire et n_nodes en croissance stricte.
   - Invariant 'frozen' : zéro swap et n_nodes strictement constant post-fork.
6. tests/test_S7_consistency.py : Ajoute un test assertant le verdict PASS sur les 4 JSON de gates/.

EXÉCUTION DU SMOKE TEST (Validation avant campagne) :
Exécute une campagne smoke restreinte :
- 5 graines x 3 magnitudes (0.10, 0.25, 0.40) x 4 bras ('full', 'no_swap', 'frozen', 'static').
- Valide l'intégrité des Parquet générés et le passage de pytest tests/test_S6_traces.py.

RÈGLE D'ARRÊT :
Arrête-toi après la réussite de la suite de tests et la génération des Parquet du smoke test.
Affiche le résumé d'exécution et la structure des Parquet. Ne lance pas la campagne complète (8 000 runs) sans validation.