Mandat : Implémentation du stream S6 (Harnais de trajectoires synchronisées et test causal).
Scope immédiat : PHASE 0 EXCLUSIVEMENT (Portes G0 à G3).

RECALAGE PAR RAPPORT À LA SPÉCIFICATION D'ORIGINE :
1. Le stream S7 EST LIVRÉ ET COMMITTÉ sur main (c24dc7e). Nous travaillons sur la branche stream/S6-instrumentation.
2. Ne cherche PAS configs/protocol.yaml. Le Single Source of Truth du projet est le fichier Python existant : config/experiment_ssot.py.
3. Les failles couvertes sont formellement identifiées :
   - F6 : tau_ARF = min_i tau_i (premier swap) est un proxy contesté de l'adaptation ensembliste.
   - F7 : La trajectoire transitoire réelle n'est pas rectangulaire ; A_rect de R8 doit être confronté au budget d'erreur intégré A.
   - F25 : R1/R8 ont omis predict_one(), interdisant l'observation simultanée de l'erreur ensembliste et des statistiques internes.

ENVIRONNEMENT ET INVARIANTS :
- Interpréteur : Python 3.12, river==0.23.0, numpy==1.26.4, scipy==1.16.2.
- Verrou RNG strict (schéma R2/R6/R7) dans chaque worker :
  safe_seed = int(seed % (2**31 - 1))
  random.seed(safe_seed); np.random.seed(safe_seed); rng = np.random.default_rng(safe_seed)
- Tout paramètre global doit être importé depuis config.experiment_ssot.

TÂCHE : Créer experiments/S6_synchronized_traces/gates/ et exécuter les 4 portes de vérification :

1. g0_predict_one_neutrality.py :
   Tester 50 seeds x Delta_e in {0.10, 0.25, 0.40}. Exécuter l'ARF avec et sans predict_one() sous verrou RNG identique.
   Vérifier si les instants de premier swap tau_swap^(1/M) sont STRICTEMENT identiques.
   Émettre gates/g0_report.json.

2. g1_deepcopy_fidelity.py :
   Effectuer un copy.deepcopy() d'une ARF à t_rel = 100. Alimenter l'original et la copie sur 500 pas identiques.
   Asserter l'égalité stricte des séquences d'erreurs et des compteurs de swaps.
   Émettre gates/g1_report.json.

3. g2_river_introspection.py :
   Sonder dynamiquement dans River 0.23.0 les chemins d'accès aux attributs privés :
   - Compteur de remplacement par arbre (ARFClassifier._drift_tracker).
   - Détecteurs internes de dérive et d'avertissement par arbre.
   - Disponibilité des arbres de fond (background trees).
   Émettre gates/g2_api_map.json avec le mapping exact. Lever RuntimeError si un attribut manque.

4. g3_throughput.py :
   Micro-benchmark de 10 000 pas instrumentés. Extrapoler la durée de la campagne complète (4 bras factoriels) sur cette machine (48 cœurs).
   Émettre gates/g3_report.json.

RÈGLE D'ARRÊT :
Exécute ces 4 portes, affiche une synthèse lisible des résultats de G0, G1, G2, G3 dans le terminal, et ARRÊTE-TOI COMPLÈTEMENT.
N'entame pas la Phase 1 (le harnais) avant ma validation explicite.