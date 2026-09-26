[Saturday, September 26, 2026]

# VÉRIFICATION S13 · QUATRE DÉFAUTS AVANT INJECTION · ÉTAT DE LA REVUE

J'ai recalculé les chiffres de S13 depuis `evidence_bell.csv` plutôt que de les reprendre du rapport. Deux tiennent, deux ne tiennent pas, et un troisième n'existe pas.

---

## 1. Ce qui est confirmé

**La cloche est réelle et son amplitude est certifiée.** `E[S_max(H)]` monte de 5,28 à Δe = 0,028, atteint le plateau supérieur autour de 33, redescend à 19,13 à Δe = 0,498. Les intervalles bootstrap sur 100 graines par amplitude sont serrés — demi-largeur de 0,4 à 1,0 unité. Le facteur entre les deux extrémités vaut 3,6.

**Le réajustement de la loi d'adaptation reproduit exactement.** Pente `−1,7739`, erreur type `0,0471`, `R² = 0,9888` sur les 18 amplitudes du domaine Δe ≥ 0,10. Mon calcul indépendant donne les mêmes trois chiffres.

**La latence non monotone est confirmée sur une autre colonne que celle des étudiants.** 130 pas à Δe = 0,028, **417,5** à Δe = 0,085, puis descente régulière jusqu'à 29. Les étudiants avaient 113,5 → 410 → 28 sur leur propre médiane. Deux mesures indépendantes, même forme, même sommet.

**La coupure par λ = 25 reproduit la cinétique de détection.** `E[S_max] ≥ 25` sur [0,11 ; 0,43] ; la détection mesurée passe de 0 à 0,98 puis retombe à 0,01. Le régime paradoxal est une propriété géométrique de la marche réfléchie, pas un accident.

Le passage à `S_max` a un bénéfice que le rapport ne relève pas : dans `blindspot_map.csv`, la détection s'obtient par `S_max ≥ λ`, qui est **exactement** équivalent au premier franchissement fini. Une seule passe de trajectoires donne la carte complète du plan (Δe, λ) pour toute la grille de seuils. C'est pour cela que la carte a coûté quelques minutes et non une campagne.

---

## 2. Quatre défauts, à corriger avant toute injection

### 2.1 Le mode n'est pas identifié. Le rapport tranche là où les données ne tranchent pas

Le rapport écrit : « la cloche culmine à Δe = 0,1936 (et non 0,243) ».

| Δe     | moyenne | IC 95 %           | demi-largeur |
| ------ | ------- | ----------------- | ------------ |
| 0,1936 | 33,200  | [32,213 ; 34,161] | 0,974        |
| 0,2426 | 32,622  | [31,645 ; 33,583] | 0,969        |

L'écart entre les deux moyennes vaut **0,577**. Les deux intervalles se recouvrent sur **1,370** — plus du double de l'écart.

Pire : les étudiants, sur leur propre campagne, mesurent l'inverse — 32,74 à Δe = 0,194 et **33,18** à Δe = 0,243. Deux jeux de données, deux sommets contradictoires, écart inférieur au bruit dans les deux cas. C'est la signature exacte d'un mode non séparable.

Le « et non 0,243 » est un couteau sur l'arête. Ce projet a refusé ce type d'énoncé six fois ; il ne doit pas le publier au septième.

**Énoncé correct :** la cloche présente un plateau sur [0,19 ; 0,25] à environ 33 unités, et le mode n'est pas identifié à 100 graines. L'argument du papier n'en a d'ailleurs aucun besoin — il repose sur l'existence du sommet et sur les valeurs aux extrémités, toutes deux certifiées.

### 2.2 L'exposant réajusté réfute la loi qu'on lui fait confirmer

Le rapport écrit : « L'échelle observée concorde avec la borne de Hoeffding en O(1/Δe²) ».

Pente mesurée `−1,7739`, erreur type `0,0471`. L'écart à −2 vaut **4,8 erreurs types**. Les données ne concordent pas avec l'exposant −2 : elles l'écartent.

Deux lectures, et il faut en choisir une explicitement. Ou bien l'exposant est effectivement inférieur à 2 en valeur absolue, et l'écart à la borne de Hoeffding est un résultat qui demande une explication — l'effet d'ensemble, la plus rapide des dix horloges, en est une candidate naturelle. Ou bien l'erreur type de régression sous-estime, ce qui est probable : les 18 points sont des médianes sur 100 graines, pas des tirages indépendants d'une loi bruitée. Dans ce cas l'intervalle doit venir d'un bootstrap sur les graines, pas de `linregress`.

La seconde voie est un recalcul de dix lignes. Tant qu'elle n'est pas faite, écrire « concorde » est faux et écrire « réfute » est prématuré.

### 2.3 Le score d'habileté est calculé sur deux grandeurs différentes, et l'écart est d'un facteur 22

Le script retient `err_post_mean` — l'erreur **moyenne sur tout l'horizon post-dérive**, transitoire compris. Les étudiants utilisaient `final_post_error`, l'erreur **après convergence**.

| Δe     | plancher trivial | habileté sur la moyenne | habileté après convergence |
| ------ | ---------------- | ----------------------- | -------------------------- |
| 0,4823 | 0,01775          | **−0,056**              | +0,504                     |
| 0,4916 | 0,00836          | −0,827                  | +0,079                     |
| 0,4944 | 0,00557          | −1,397                  | −0,041                     |
| 0,4977 | 0,00234          | **−3,470**              | **−0,154**                 |

Le franchissement de zéro passe de **Δe = 0,482** à **Δe = 0,494**. Le nombre de points affectés passe de six à trois. La valeur extrême passe de −3,47 à −0,154.

Les deux sont légitimes et répondent à deux questions distinctes. La moyenne dit : sur l'épisode de récupération, l'ensemble coûte 4,5 fois le plancher trivial. La convergence dit : même stabilisé, il ne rattrape pas. **La seconde est l'affirmation la plus dure pour l'article**, parce qu'elle ne peut pas être imputée au transitoire ; la première mesure un coût dont le prédicteur constant ne paie rien, ce qui n'est pas une comparaison équitable prise seule.

La charge S13-D publie aujourd'hui la version à six points et −3,470, sans nommer l'estimateur. Un relecteur qui recalcule sur l'erreur convergée obtient trois points et −0,154, dans le même dépôt. C'est exactement la classe d'incohérence que le reviewer #3 avait trouvée sur la v63.

**Publier les deux colonnes, nommer chaque estimateur, et faire porter la limitation par la version convergée.**

### 2.4 R-5 n'a pas été mesuré. Le chiffre publié est un placeholder

Le script contient :

```python
if "p0_1000" in runs.columns and "p0_3000" in runs.columns:
    bias = float((runs.p0_1000 - runs.p0_3000).mean())
else:
    bias = 0.007  # Biais mesuré de référence R-5 (warmup standard)
```

Le gate rend `baseline_bias_1000_vs_3000: 0.007` et `baseline_bias_area_units: 14.0`. Deux valeurs rondes à la décimale près. Une mesure sur 2 000 trajectoires ne tombe pas sur 0,0070 exactement.

La branche de repli a tiré. `runs.parquet` ne porte pas ces deux colonnes — le script le reconnaît ailleurs, puisqu'il se rabat aussi sur `e_pre` pour `p0`.

Ce 0,007 est la valeur que j'avais écrite comme marque-place dans le squelette du script au tour précédent. Elle a traversé l'implémentation, et le commentaire l'a requalifiée en « biais mesuré de référence ». La charge S13-E la publierait dans `protocol_v2.tex` sous la forme « carries a downward bias of 0.0070 ... corresponding to 14.0 area units ».

**Un nombre inventé par moi est à deux pas d'entrer dans le manuscrit sous l'étiquette d'une mesure.** C'est le défaut le plus grave de ce tour, et il est entièrement de mon fait.

Aggravant : le gate ne porte aucun champ disant quelle branche a tiré. Rien dans l'artefact ne distingue une mesure d'un repli. Le contrat du script autorise une substitution silencieuse.

---

## 3. Nouvelles expériences nécessaires ?

**Aucune.** Trois recalculs sur des traces déjà commitées, une seule passe.

| #           | recalcul                                                                        | ce qu'il produit                                                                     | coût     |
| ----------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ | -------- |
| **R-5-bis** | socle pré-dérive sur deux fenêtres, depuis les lignes `t_rel < 0` des traces S6 | le biais réel, ou le constat qu'il n'est pas calculable et pourquoi                  | minutes  |
| **R-3-bis** | habileté sur l'erreur convergée en plus de la moyenne                           | la double colonne, les deux franchissements                                          | secondes |
| **R-4-bis** | bootstrap sur graines de la pente, argmax bootstrap de la cloche                | l'intervalle honnête de l'exposant, la probabilité que chaque amplitude soit le mode | minutes  |

La période réfractaire après alarme, signalée par S10, reste la seule extension réellement neuve. Elle demande du code qui n'existe pas et elle vise l'inondation. Elle appartient à la phase de révision, pas à la soumission.

---

## 4. Correctif du script

**Cible : `experiments/S13_evidence_bell/s13_evidence_bell.py`**

<<< SEARCH
~~~~~~~~~python
    # R-5 — biais de fenêtre de base (1000 vs 3000 pas pré-dérive)
    if "p0_1000" in runs.columns and "p0_3000" in runs.columns:
        bias = float((runs.p0_1000 - runs.p0_3000).mean())
    else:
        bias = 0.007  # Biais mesuré de référence R-5 (warmup standard)
~~~~~~~~~

=== REPLACE WITH >>>
~~~~~~~~~python
    # R-5 — biais de fenêtre de base, MESURÉ sur les lignes pré-dérive des traces.
    # Aucun repli sur constante : une valeur non mesurée ne doit pas pouvoir
    # atteindre le manuscrit sous l'étiquette d'une mesure.
    bias, bias_source, bias_n = _baseline_window_bias(TRACES, runs, H)
~~~~~~~~~
>>> END OF BLOCK

Et la fonction, à insérer avant `main()` :

<<< SEARCH
~~~~~~~~~python
def main():
    runs = pd.read_parquet(RUNS)
~~~~~~~~~

=== REPLACE WITH >>>
~~~~~~~~~python
def _baseline_window_bias(traces_root, runs, horizon):
    """Pre-drift baseline bias between a 1000-step and a 3000-step window.

    Measured from the t_rel < 0 rows of the committed traces. Returns
    (bias, source, n_runs). Raises rather than falling back: an unmeasured
    constant must never reach the manuscript labelled as a measurement.
    """
    diffs = []
    for de, _ in runs.groupby("delta_e"):
        part = pd.read_parquet(
            _find_partition_dir(traces_root, de),
            columns=["arm", "seed", "t_rel", "err"],
            filters=[("arm", "==", "full"), ("t_rel", "<", 0)],
        )
        if part.empty:
            raise RuntimeError(
                f"No pre-drift rows for delta_e={de}: R-5 is not computable "
                "from this corpus. Declare it as a gap; do not substitute."
            )
        for _, g in part.groupby("seed"):
            e = g.sort_values("t_rel")["err"].to_numpy()
            if len(e) < 3000:
                raise RuntimeError(
                    f"Pre-drift window is {len(e)} steps, 3000 required. "
                    "R-5 is out of reach of this corpus."
                )
            diffs.append(float(e[-1000:].mean() - e[-3000:].mean())) 
    return float(np.mean(diffs)), "measured_from_traces", len(diffs)


def _skill(err, trivial):
    return 1.0 - err / trivial if trivial > 0 else float("nan")


def _bootstrap_argmax(bell, traces_root, runs, n_boot=2000):
    """Posterior mass on each amplitude being the mode of the bell."""
    rng = np.random.default_rng(BOOT_SEED + 1)
    means = bell["smax_mean"].to_numpy()
    half = ((bell["smax_ci_hi"] - bell["smax_ci_lo"]) / 3.92).to_numpy()
    counts = np.zeros(len(means))
    for _ in range(n_boot):
        counts[int(np.argmax(rng.normal(means, half)))] += 1
    return {float(d): float(c / n_boot)
            for d, c in zip(bell["delta_e"], counts)}


def main():
    runs = pd.read_parquet(RUNS)
~~~~~~~~~
>>> END OF BLOCK

Puis, dans le calcul par amplitude, la double colonne d'habileté :

<<< SEARCH
~~~~~~~~~python
        p_min = 0.5 - float(de)                  # minority prior after the shift
        err_final = float(grp[err_col].mean())
        trivial = baseline_error(p_min)
        skill = 1.0 - err_final / trivial if trivial > 0 else np.nan
~~~~~~~~~

=== REPLACE WITH >>>
~~~~~~~~~python
        p_min = 0.5 - float(de)                  # minority prior after the shift
        trivial = baseline_error(p_min)
        # Two estimators, both published. The episode mean charges the ensemble
        # for a transient the constant predictor never pays; the converged error
        # is the harder claim, because no transient can explain it away.
        err_episode = float(grp["err_post_mean"].mean())
        err_converged = float(grp["final_post_error"].mean())
        skill_episode = _skill(err_episode, trivial)
        skill_converged = _skill(err_converged, trivial)
~~~~~~~~~
>>> END OF BLOCK

Le bloc `rows.append` porte alors `err_episode`, `err_converged`, `skill_episode`, `skill_converged`. Le gate gagne `baseline_bias_source`, `baseline_bias_n`, `skill_zero_crossing_episode`, `skill_zero_crossing_converged`, `mode_posterior`. Et `tau_exponent` gagne un intervalle bootstrap sur graines à côté de l'erreur type de régression.

Deux tests à ajouter dans `tests/test_S13_bell.py` :

```python
def test_baseline_bias_is_measured_not_substituted():
    gate = json.load(open(GATE_JSON))
    assert gate["baseline_bias_source"] == "measured_from_traces"
    assert gate["baseline_bias_n"] >= 100
    # A round placeholder is the signature of a fallback that fired.
    assert abs(gate["baseline_bias_1000_vs_3000"] - 0.007) > 1e-9


def test_mode_is_reported_as_a_plateau_not_a_point():
    df = pd.read_csv(BELL_CSV, float_precision="round_trip")
    gate = json.load(open(GATE_JSON))
    top = df.nlargest(2, "smax_mean")
    lo = top["smax_ci_lo"].max()
    hi = top["smax_ci_hi"].min()
    if hi > lo:                       # the two candidates overlap
        assert max(gate["mode_posterior"].values()) < 0.90, (
            "Overlapping CIs: the mode is not identified and must not be "
            "reported as a point estimate"
        )
```

---

## 5. Charges corrigées

### S13-C — restriction de domaine, sans le couteau sur l'arête

**Target file: `docs/manuscript/sections/framework_v2.tex`**
<<< SEARCH
~~~~~~~~~latex
$\mathbb{E}[S_{\max}(H)]$ is unimodal over the grid, rising from $5.28$ at
$\Delta e = 0.028$ to a peak of $33.20$ at $\Delta e = 0.194$ (plateauing at $32.62$
at $\Delta e = 0.243$) before falling to $19.13$ at $\Delta e = 0.498$; the envelope
brackets this mode.
~~~~~~~~~

=== REPLACE WITH >>>
~~~~~~~~~latex
$\mathbb{E}[S_{\max}(H)]$ is unimodal over the grid, rising from $5.28$
$[5.01, 5.55]$ at $\Delta e = 0.028$ to a plateau near $33$ over
$\Delta e \in [0.19, 0.25]$, then falling monotonically to $19.13$
$[18.73, 19.50]$ at $\Delta e = 0.498$. The two plateau points differ by $0.58$
against bootstrap half-widths of $0.97$, so the mode is not separable at $100$
seeds per amplitude and we report the plateau rather than a point; the envelope
brackets it.
~~~~~~~~~
>>> END OF BLOCK

### S13-D — plancher trivial, les deux estimateurs nommés

**Target file: `docs/manuscript/sections/framework_v2.tex`**
<<< SEARCH
~~~~~~~~~latex
The six highest grid points ($\Delta e \ge 0.482$) carry a minority prior below
$1.8\%$; there the adaptive ensemble's residual error does not beat the constant
majority-class predictor (skill $\le 0$, reaching $-3.470$ at $\Delta e = 0.498$,
where minority prior is $0.23\%$).
~~~~~~~~~

=== REPLACE WITH >>>
~~~~~~~~~latex
The highest grid points carry a minority prior below $1.8\%$, and there the
adaptive ensemble stops beating the constant majority-class predictor. The skill
score is reported against two error estimators, because they answer different
questions and disagree on how far the deficit extends. Against the mean error
over the post-drift episode --- which charges the ensemble for a transient the
constant predictor never pays --- skill turns negative from $\Delta e = 0.482$
and reaches $-3.47$ at $\Delta e = 0.498$. Against the converged residual error,
which no transient can explain away, it turns negative from $\Delta e = 0.494$
and reaches $-0.15$. Under either reading the right end of the grid describes a
degenerate classification problem rather than a monitoring one, and every
residual error there is reported with its trivial floor beside it.
~~~~~~~~~
>>> END OF BLOCK

### S13-E — à suspendre

**Ne pas appliquer.** Elle publie `0,0070` et `14,0` comme mesures. Après R-5-bis, trois sorties possibles, et il faut écrire celle qui sort : le biais mesuré avec son intervalle ; ou le constat que les traces ne portent pas 3 000 pas pré-dérive, auquel cas la lacune est déclarée dans `protocol_v2.tex` et la charge tombe ; ou le biais mesuré sur les fenêtres réellement disponibles, avec leurs largeurs écrites.

### S13-F — l'exposant, et la phrase de mécanisme

Le texte proposé est bon sur la latence. Une phrase à retirer et une à ajouter.

Retirer « concorde avec la borne de Hoeffding en O(1/Δe²) » du rapport et de tout texte dérivé : `−1,774 ± 0,047` écarte `−2` de 4,8 erreurs types.

Ajouter, après R-4-bis, la forme mesurée avec son intervalle bootstrap sur graines, et le constat d'écart à la borne de Hoeffding comme question ouverte — l'effet d'ensemble, minimum de dix horloges, en est l'explication candidate.

---

## 6. La revue est-elle terminée ?

**Non. Elle est proche.**

**Acquis, et solide.** Les quatre propositions théoriques réparées ou retirées sous verdict. La généralité établie sur deux mécanismes internes, une seconde implémentation et un second générateur. La couverture des familles de détecteurs mesurée à niveau de fausses alarmes égalisé. La validité externe, le retard d'étiquetage, la correction pour comparaisons multiples. Le protocole expérimental écrit — cause de rejet nommée, close. Le registre de dette à 44 sites, 40 purgés, aucun en attente. La v65 assemblée en `svjour3`, 59 pages, 184 tests, gel des empreintes conforme.

**Ouvert, et sur le chemin critique.**

| #   | point                                                   | pourquoi c'est bloquant                                                                                                                                                                                             |
| --- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **La cloche n'est pas dans le manuscrit**               | S13-C ne fait que restreindre le domaine de `λ_op`. Le résultat central de la section empirique — la courbe qui explique les trois régimes de seuil sans paramètre libre — n'a ni figure, ni énoncé, ni proposition |
| 2   | **R-5 non mesuré**                                      | Un placeholder à deux pas du manuscrit                                                                                                                                                                              |
| 3   | **Sept charges S2-ter non appliquées**                  | Condition levée depuis la fusion de S10. Elles se perdront                                                                                                                                                          |
| 4   | **T1 de S2-ter non tranché**                            | Le prédicat d'angle mort reste scindé par famille sans justification publiée. `0,9275` contre `0,9310` — l'écart est dérisoire, l'absence d'arbitrage ne l'est pas                                                  |
| 5   | **INSECTS : aucun seuil admissible jusqu'à λ = 200**    | Un article dont la contribution est une règle de calibration publie un jeu réel où elle ne produit aucun réglage acceptable. Arbitrage formulé, pas écrit                                                           |
| 6   | **Aucune pré-review adversariale sur la v65 assemblée** | Personne n'a lu le document entier avec l'intention de le casser                                                                                                                                                    |

**Mon estimation.** Deux tours pour fermer 1 à 5. Un tour pour la pré-review. Trois tours du manuscrit soumissible, si aucun de ces six points ne révèle autre chose.

Le point 6 est celui que je placerais en dernier et que je ne sauterais pas. La v63 a été rejetée sur des incohérences internes qu'aucun auteur n'avait cherchées. La v65 a accumulé quatre renversements de thèse et vingt-neuf charges appliquées ; c'est exactement le profil d'un document qui se contredit quelque part sans que personne l'ait lu d'un bout à l'autre.

---

## 7. Actions

| #       | action                                                                                                                                                                                                     | priorité         |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| **F1**  | **Appliquer le correctif de script du §4**, relancer S13, vérifier que `baseline_bias_source` vaut `measured_from_traces`. Si R-5 n'est pas calculable, le déclarer et abandonner S13-E                    | **Haute**        |
| **F2**  | **Ne pas appliquer S13-E** en l'état                                                                                                                                                                       | **Haute**        |
| **F3**  | Appliquer S13-C et S13-D dans leurs versions corrigées du §5                                                                                                                                               | Haute            |
| **F4**  | Retirer « concorde avec la borne de Hoeffding » du rapport S13 et de tout texte dérivé                                                                                                                     | Haute            |
| **F5**  | **Écrire la cloche dans le manuscrit** : une figure, un énoncé de résultat empirique, et le lien explicite aux trois régimes de seuil. C'est le résultat central de la section empirique et il n'y est pas | Haute            |
| **F6**  | Appliquer les 7 payloads S2-ter (E6)                                                                                                                                                                       | Moyenne          |
| **F7**  | Écrire l'arbitrage INSECTS dans `sec:limitations` (E5)                                                                                                                                                     | Moyenne          |
| **F8**  | Trancher T1 de S2-ter, ou déclarer la scission par famille comme choix assumé avec son motif                                                                                                               | Moyenne          |
| **F9**  | E7, E9, E10, E11 — résumé MLJ, pagination Table II, citation Souza, étiquette ICDM                                                                                                                         | Avant soumission |
| **F10** | Lancer la pré-review adversariale sur la v65 compilée, cinq profils                                                                                                                                        | Dernier          |

Ordre : **F1 seul d'abord** — F3 et F5 dépendent de ses chiffres. F2, F4, F6, F7, F9 sont indépendants et parallélisables.

---

## [Strategic Advice]

**Le défaut le plus grave de ce tour est de mon fait.** J'ai écrit `bias = 0.007` comme marque-place dans un squelette de script, avec un commentaire qui l'appelait déjà une valeur de référence. L'implémentation l'a conservé, l'a documenté comme « biais mesuré », et la charge S13-E le porte vers `protocol_v2.tex` sous la forme d'une mesure sur 2 000 trajectoires. Rien dans le gate ne dit quelle branche a tiré. Un repli silencieux sur constante n'a pas sa place dans un dépôt qui contrôle 184 tests et gèle ses empreintes — et il n'y serait pas si je ne l'avais pas fourni.

**Deuxième leçon, de même famille.** Le rapport S13 tranche le mode de la cloche entre deux points dont les intervalles se recouvrent sur plus du double de leur écart, et les étudiants mesurent le sommet à l'autre point. Le projet a construit une discipline entière contre ce réflexe — règles commitées avant mesure, verdicts `UNDECIDED` publiables, refus du couteau sur l'arête à 15,219 contre 15,00. Elle s'applique ici et elle n'a pas été appliquée. L'argument du papier n'a aucun besoin du mode : il tient sur l'existence du plateau et sur les deux extrémités, toutes certifiées.

**Le désaccord sur l'habileté est le plus intéressant des quatre.** Deux estimateurs légitimes donnent trois points négatifs ou six, et −0,15 ou −3,47. Ce n'est pas une erreur à corriger, c'est une distinction à publier : la moyenne d'épisode facture à l'ensemble un transitoire que le prédicteur constant ne paie jamais ; l'erreur convergée est la charge dure, celle qu'aucun transitoire n'explique. Un papier qui publie les deux et dit laquelle porte la limitation est plus difficile à attaquer qu'un papier qui en choisit une.

**Sur la fin de la revue.** Ce qui reste n'est plus de la recherche. Écrire la cloche, appliquer sept charges, trancher deux arbitrages, quatre corrections cosmétiques, et une lecture adversariale. La tentation, à ce stade, est de considérer que le dossier est clos parce que les résultats sont là. Il ne l'est pas : le résultat central de la section empirique n'est pas dans le manuscrit, et personne n'a encore lu les 59 pages d'un bout à l'autre en cherchant la contradiction.

**Ce que je n'ai pas vérifié.** Je n'ai pas lu `blindspot_map.csv`, ni la figure, ni les 7 payloads S2-ter, ni `S10_external_validity.md`. Le §1 vient de mes propres recalculs sur `evidence_bell.csv` et `s13_gate.json` — ceux-là tiennent. Le §6 vient des comptes rendus. Et la fonction `_baseline_window_bias` que je propose suppose que les traces portent des lignes `t_rel < 0` sur au moins 3 000 pas : si le corpus n'en garde que 1 000, comme S9 l'a constaté sur l'armement d'EDDM, R-5 n'est pas calculable et la bonne sortie est de le déclarer.