[Saturday, September 26, 2026]

# PRÉ-ENREGISTREMENT R-8 · RÉGRESSION SEGMENTÉE DE LA LOI D'ONSET À RUPTURE ESTIMÉE

Écrit **avant** tout calcul du fit segmenté, conformément à la charge H3 du plan d'Opus (« 2026 09 26 - 44 - Opus post stream R-7A-B-C-D.md », §4 et §7). Estimateur, données, règle de décision et critère de publication fixés avant lecture. Aucun fit segmenté — pente de flanc, niveau de plancher, position de rupture — n'a été calculé au moment de cette écriture.

---

## 1. Condition d'entrée : R-9 (horloges) — résolue

La charge H3 n'inclut le bras HAT que si R-9 rend les horloges identiques. **R-9 est exécuté avant ce pré-enregistrement et son verdict est « horloges identiques »** : les deux bras construisent `ARFClassifier` avec `drift_detector = ADWIN(clock = 1)` et `warning_detector = ADWIN(clock = 1)` (S6 bras `full` via `make_arf(safe_seed, 10, C_INT)` ; R6 via `ARFClassifier(n_models=1, …, clock=R6_C_INT)`), et tous les autres paramètres sont des défauts River 0.23.0 identiques et non épinglés : `delta = 0,002`, `min_window_length = 5`, `grace_period` ADWIN = 10, `grace_period` ARF = 50. La seule différence entre bras est `n_models` (10 vs 1). Le verdict est consigné au gate (`detector_clocks`). **Le bras HAT est donc inclus dans R-8.**

## 2. Données

- Bras ARF : médianes `tau_swap_q010` par amplitude des traces S6 (bras `full`), domaine valide Δe ≥ 0,10, 18 amplitudes — via `evidence_bell.csv` (`tau_arf_median`), committé.
- Bras HAT : médianes `tau_hat` par amplitude de `R6_hat_instrumented.parquet`, graines non censurées (2 censurées sur 1 800), même domaine.

## 3. Modèle pré-enregistré

- `log τ_med(Δe) = a + b·log Δe` pour `Δe ≤ Δe*` ;
- `log τ_med(Δe) = c` pour `Δe > Δe*`, avec **continuité imposée** en `Δe*` : `c = a + b·log Δe*` ;
- trois paramètres libres : `a`, `b`, `Δe*`.

## 4. Estimation

1. **`Δe*`** : balayage exhaustif sur les points de grille du domaine valide, minimisation de la somme des carrés résiduels, avec un minimum de **trois points de chaque côté** (la rupture appartient au côté loi de puissance : `Δe ≤ Δe*`). Pour chaque candidat, `(a, b)` se résout par moindres carrés sur le dessin augmenté (côté gauche à `log Δe_i`, côté droit à `log Δe*`). Aucune coupure choisie a priori.
2. **Intervalles** : bootstrap sur graines, **2 000 répliques**, rééchantillonnage des 100 graines avec remise par amplitude, médianes recalculées à chaque tirage (graines non censurées pour HAT), modèle **ré-estimé rupture comprise** à chaque réplique. Percentiles 2,5 / 97,5 sur `b`, sur le niveau du plancher `c` et sur `Δe*`. Graine distincte par usage (ARF : `BOOT_SEED + 6` ; HAT : `BOOT_SEED + 7`).
3. **Comparaison de modèles** : somme des carrés résiduels du modèle segmenté contre le modèle à un morceau (le fit groupé déjà committé) sur les mêmes médianes. **Un segmenté qui n'améliore pas ne se publie pas.**

## 5. Règle de décision, fixée avant lecture

- Si l'intervalle bootstrap de `b` (bras ARF) **contient −2** : la distance à la borne de Hoeffding est **déclarée non établie** et la remarque le dit.
- S'il **l'exclut** : la distance est un résultat sur le régime réactif, énoncée avec `Δe*` et son intervalle.
- Si l'intervalle de `Δe*` couvre **plus de la moitié du domaine valide** (étendue [0,10 ; 0,4977], donc une largeur > 0,199) : la rupture est **déclarée non identifiable** et seul le fit groupé survit, avec la saturation nommée comme aujourd'hui (charge R7-A).
- Le bras HAT est estimé avec le même protocole et publié comme description du régime, pas comme test : la question de discrimination est close depuis R-7 (non discriminant, pré-enregistré).

## 6. Sortie

Gate `s13_gate.json` : entrée `tau_segmented` (bras ARF) et `tau_segmented_hat` (bras HAT) — `de_star`, `exponent`, `floor`, intervalles bootstrap des trois, `sse_segmented`, `sse_pooled`. Les chiffres committés au gate sont la seule base admissible de la charge R7-B.

*Erratum, round I (report 50).* « Un segmenté qui n'améliore pas ne se publie pas » ne fixait aucun seuil ; le tour H a lu 5,4 % de SSE comme une amélioration (ARF) et 0,2 % comme une absence d'amélioration (HAT), ligne tracée après lecture. Une comparaison pénalisée, calculée après coup et déclarée comme telle dans `s13_gate.json :: tau_segmented.post_hoc` (F(1,15) = 0,85, p = 0,37 ; AIC et BIC en faveur de la loi à un morceau), ne préfère pas le modèle segmenté. Les lignes ci-dessus ne sont pas modifiées.
