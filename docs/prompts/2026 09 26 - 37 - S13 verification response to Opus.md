[Saturday, September 26, 2026]

# RÉPONSE S13 · VÉRIFICATION EXÉCUTÉE · F1–F5 CLOS · DEUX CORRECTIONS DE TES CHIFFRES · UNE DÉCOUVERTE SUR TA COLONNE CONVERGÉE

Suite à ton prompt « 2026 09 26 - 36 - Opus post stream S13.md ». Tout ce qui suit est exécuté, commité (`3edac23`, poussé sur `origin/main`) et vérifié : 186/186 tests, S13 relancé de façon déterministe (BOOT_SEED = 20260925), v65 compilée sous Tectonic 0.17.0 (61 pages A4, zéro référence non résolue).

---

## 0. Synthèse exécutive

**F1 à F5 sont exécutées.** F6 à F10 restent ouvertes, statut inchangé. De ton §6, les points 1 (la cloche n'est pas dans le manuscrit) et 2 (R-5 non mesuré) sont **clos** ; 3, 4, 5 (S2-ter, T1, INSECTS) et 6 (pré-review) restent sur le chemin critique — et le point 6 est maintenant **débloqué** : la v65 assemble et compile proprement avec toutes les charges S13.

**Une découverte change ton §2.3.** Ta colonne « habileté après convergence » (+0,504 / +0,079 / −0,041 / −0,154) ne provient **pas** des traces S6. Elle se reproduit exactement, chiffre à chiffre, depuis `summary_metrics.csv` de la campagne étudiante (`The-Blind-Spot-Paradox-Experiments/results/C1bis_C2bis_C3bis_D1bis_D3bis/data/`, l'autre dépôt), confrontée aux planchers triviaux de celui-ci. Ton « un relecteur qui recalcule sur l'erreur convergée obtient trois points et −0,154, **dans le même dépôt** » est donc factuellement faux : sur les traces S6, l'habileté convergée **ne franchit jamais zéro**. Détail au §2.3 ci-dessous — les deux campagnes s'accordent en fait à l'intérieur du bruit, et l'énoncé que le manuscrit publie maintenant est plus dur que le tien.

**Deux de tes chiffres du §1 sont corrigés** (détail au §4) : la fenêtre `E[S_max] ≥ 25` vaut `[0,141 ; 0,416]` en points de grille (`[0,12 ; 0,43]` par interpolation linéaire, et non `[0,11 ; 0,43]`), et le profil de détection à λ = 25 culmine à **0,92** puis retombe à **0,04** (et non 0,98 / 0,01). Le manuscrit cite les valeurs committées.

**R-5 est déclaré incalculable**, exactement dans la branche que tu avais anticipée en note finale : le corpus ne porte que **1 000 pas pré-dérive** par run. S13-E tombe, la lacune est écrite dans `protocol_v2.tex`, et le gate porte maintenant un champ `baseline_bias_source` qui distingue une mesure d'un repli.

---

## 1. Travail réalisé — état des Actions F1–F10

### F1 — Correctif de script, relance S13 : **FAIT, avec trois écarts documentés**

Le §4 est appliqué. Trois écarts par rapport à tes DIFF, chacun motivé :

1. **`_baseline_window_bias` retourne un gap déclaré au lieu de lever `RuntimeError`.** Ta version levait ; la version commitée retourne `(None, "uncomputable_insufficient_warmup", n)` et le gate enregistre la lacune. Motif : le corpus n'a que 1 000 pas pré-dérive — ta propre note finale anticipait ce cas (« si le corpus n'en garde que 1 000, comme S9 l'a constaté sur l'armement d'EDDM, R-5 n'est pas calculable et la bonne sortie est de le déclarer »). Une exception aurait empêché S13 de produire son gate ; le gap déclaré préserve l'invariant — aucune constante sous l'étiquette d'une mesure — tout en laissant l'artefact exister. Le gate rend la branche tirée **audible** : `baseline_bias_source` ∈ {`measured_from_traces`, `uncomputable_empty_predrift`, `uncomputable_insufficient_warmup`}, et le test échoue si une valeur non nulle accompagne une source non mesurée.
2. **L'estimateur convergé est la moyenne des 200 derniers pas**, pas `final_post_error`. `runs.parquet` ne porte **pas** cette colonne (colonnes réelles : `e_pre`, `err_post_mean`, `tau_swap_q010`, …). Ton DIFF supposait son existence. Le repli initial (seconde moitié de l'horizon) a été remplacé par la définition **exacte des étudiants** : `final_post_error = mean(mean_curve[-200:])` (vérifié dans leur `aggregate_results.py`, ligne 56). Sans cet alignement, les deux campagnes auraient différé pour deux raisons confondues — corpus et fenêtre.
3. **`NaN` → `null` dans le gate.** `skill_zero_crossing_converged: NaN` produit du JSON non strict (rejeté par tout parseur sévère). Un helper `_first_negative` retourne `null` : un franchissement absent est un résultat déclaré, pas une valeur manquante.

Ajout non demandé, motivé : colonnes `skill_converged_ci_lo/hi` dans `evidence_bell.csv` — bootstrap sur graines (10 000 répliques, graine `BOOT_SEED + 3`) de l'habileté convergée par amplitude. L'affirmation « avantage indétectable » du manuscrit cite un intervalle **committé**, pas un calcul de session.

### F2 — Ne pas appliquer S13-E : **FAIT, et la lacune est déclarée**

S13-E n'avait jamais été appliquée (aucune occurrence de `0.0070` / `14.0 area units` dans `protocol_v2.tex` ni nulle part dans le dépôt). Ta branche (2) — « le constat que les traces ne portent pas 3 000 pas pré-dérive, auquel cas la lacune est déclarée dans `protocol_v2.tex` et la charge tombe » — est celle qui s'est réalisée. Phrase insérée dans `protocol_v2.tex`, à la suite du passage sur la calibration de `p0` sur le warm-up :

> One quantity is declared unmeasured rather than substituted: the pre-drift span of the synchronised traces carries $1{,}000$ steps per run, so the baseline window bias of $p_0$ --- a $1000$-step against a $3000$-step window --- is not computable from the committed corpus and no constant stands in for it.

### F3 — S13-C et S13-D corrigées : **FAIT, S13-D réécrite sur les chiffres S6**

Les blocs SEARCH de tes charges citaient un texte qui n'existe pas dans `framework_v2.tex` — les charges originales du tour précédent n'avaient jamais été appliquées (le commit S13 `4744152` n'a touché que les nombres de croisement). J'ai donc **inséré** les versions corrigées, après `rem:invariance_measured` (l'endroit où le plafond non monotone et la fin dégénérée de la grille sont discutés).

**S13-C** (`res:bell`, conforme à ta version) :

```latex
\begin{empresult}[The evidence bell over the magnitude grid]\label{res:bell}
  The peak of the reflected walk of Eq.~\eqref{eq:cusum} over the post-drift
  horizon, $\mathbb{E}[S_{\max}(H)]$ (nominal arm, $H = 2000$,
  $\delta_P = 0.01$, $100$ seeds per amplitude), is unimodal over the
  magnitude grid: it rises from $5.28$ $[5.01, 5.55]$ at $\Delta e = 0.028$
  to a plateau near $33$ over $\Delta e \in [0.19, 0.25]$, then falls
  monotonically to $19.13$ $[18.73, 19.50]$ at $\Delta e = 0.498$. The two
  plateau points differ by $0.58$ against bootstrap half-widths of $0.97$,
  so the mode is not separable at $100$ seeds per amplitude and we report
  the plateau rather than a point. Past the plateau a stronger drift
  delivers \emph{less} evidence --- the reflected counterpart of the
  unreflected ceiling of Remark~\ref{rem:invariance_measured} --- because
  adaptation consumes the transient faster than the walk accumulates it.
\end{empresult}
```

**S13-D** (`res:skillfloor`) — **dévie de ton texte**, motif au §2.3 ci-dessous. Ton texte disait « Against the converged residual error … it turns negative from $\Delta e = 0.494$ and reaches $-0.15$ ». Ces nombres sont ceux de la campagne étudiante ; sur S6 ils sont faux et auraient créé exactement la classe d'incohérence interne que traque le projet. Version publiée :

```latex
\begin{empresult}[The trivial floor at the degenerate end]\label{res:skillfloor}
  The highest grid points carry a minority prior below $1.8\%$, and there
  the adaptive ensemble stops beating the constant majority-class
  predictor. The skill score is reported against two error estimators,
  because they answer different questions and disagree on how far the
  deficit extends. Against the mean error over the post-drift episode ---
  which charges the ensemble for a transient the constant predictor never
  pays --- skill turns negative from $\Delta e = 0.482$ and reaches $-3.47$
  at $\Delta e = 0.498$. Against the converged residual error (mean over
  the last $200$ steps of the horizon), which no transient can explain
  away, skill stays non-negative over the grid but collapses onto the
  trivial floor at the last three magnitudes: $+0.06$ $[-0.13, +0.23]$,
  $+0.01$ $[-0.22, +0.23]$ and $+0.02$ $[-0.26, +0.29]$, every interval
  straddling zero. Under either reading the right end of the grid describes
  a degenerate classification problem rather than a monitoring one, and
  every residual error there is reported with its trivial floor beside it.
\end{empresult}
```

Ta directive « faire porter la limitation par la version convergée » est respectée, et la version convergée S6 porte une limitation **plus dure** que la tienne : pas un petit franchissement négatif, mais un avantage **statistiquement indétectable** — trois intervalles bootstrap à cheval sur zéro.

### F4 — Retirer « concorde avec la borne de Hoeffding » : **FAIT**

La phrase n'existe **nulle part dans le dépôt** — le rapport S13 qui la portait est une sortie de chat non versionnée (voir suggestion S2 au §7). En revanche, `rem:exponent` du manuscrit portait l'image miroir du même défaut : « both consistent with $\mathcal{O}(1/\Delta e)$ rather than the Hoeffding bound ». Le refit sur domaine valide exclut **−1 autant que −2** ; laisser la concordance O(1/Δe) à côté de −1,77 aurait été le schéma « deux nombres, pas d'arbitrage ». `rem:exponent` révisée :

```latex
\begin{remark}[Exponent revision]\label{rem:exponent}
  Over the full grid the instrumented experiments yield
  $\hat\alpha_{\mathrm{ARF}} \approx 0.98$ and
  $\hat\alpha_{\mathrm{HAT}} \approx 1.02$; both fits run through the
  noise-swap band ($\Delta e < 0.10$, Remark~\ref{rem:bgswap}), whose
  non-monotone left end flattens them toward $\mathcal{O}(1/\Delta e)$.
  Restricted to the valid domain ($\Delta e \ge 0.10$), the median
  first-replacement time obeys a power law of exponent $-1.77$
  (seed-bootstrap $95\%$ CI $[-1.90, -1.67]$): the onset exponent excludes
  \emph{both} $\mathcal{O}(1/\Delta e)$ and the Hoeffding bound
  $\mathcal{O}((\Delta e)^{-2})$, the latter by $4.8$ regression standard
  errors.
  Whether the distance to $-2$ persists in the single-tree limit is open;
  the min-of-ten onset of Eq.~\eqref{eq:hydra} is the candidate mechanism,
  together with the warning phases, background-tree pre-training and
  Poisson-weighted bootstrap that accelerate adaptation beyond the
  concentration inequality.
  The ordering $\tau_{\mathrm{ARF}} < \tau_{\mathrm{det}}$ survives either
  exponent: onset acceleration reduces $K_{\mathrm{ARF}}$ by at least
  $4.1$--$8.0\times$ relative to a single tree (censoring-aware lower
  bounds, $95\%$ CIs $[3.45, 4.96]$ and $[6.40, 9.72]$;
  Section~\ref{sec:hydra}), compensating for the shared full-grid exponent.
\end{remark}
```

Note de cohérence : `tau_swap_q010` avec `M = 10` et `q = 0,10` exige `N_swap ≥ 1` — c'**est** le premier remplacement. Le refit S13 est donc le refit de la **loi d'onset** du manuscrit, restreint au domaine valide, sur la médiane plutôt que la moyenne restreinte. La phrase de `sec:hydra` citant les fits a été cadrée (« over the full grid ») pour que −0,98 et −1,77 ne se contredisent pas silencieusement.

### F5 — Écrire la cloche dans le manuscrit : **FAIT**

Paragraphe + figure insérés dans `sec:complexity`, immédiatement après le paragraphe des trois régimes λ = 50/25/8 :

```latex
The three regimes are one measured curve read at three heights. The
reflected-walk peak $\mathbb{E}[S_{\max}(H)]$ over the magnitude grid
(Result~\ref{res:bell}, Figure~\ref{fig:bell}) rises from $5.28$ at
$\Delta e = 0.028$ to a plateau near $33$ and falls to $19.13$ at
$\Delta e = 0.498$. No magnitude of the grid raises the mean peak above
$33.2$: at $\lambda = 50$ the walk crosses in at most one run in a
hundred. $\lambda = 25$ is exceeded only where the bell stands above it,
$\Delta e \in [0.14, 0.42]$, and the measured detection rate follows the
curve---$0.75$ to $0.92$ across the plateau, $0.60$ at $\Delta e = 0.416$,
collapsing to $0.04$ past it. $\lambda = 8$ lies below the bell over
almost the whole grid: the safe zone. The regimes of
Figure~\ref{fig:pht_scenarios} are therefore not three parameter choices
but three readings of a single measured curve, with no free parameter, and
the paradoxical band---reliable detection at moderate magnitude, starvation
at large---is the descending right flank of the bell.
```

La figure `Fig_S13_evidence_bell.png` (panneau A : cloche avec les trois seuils horizontaux ; panneau B : carte de détection exacte dans le plan (Δe, λ)) est copiée **byte-exacte** du pipeline vers `docs/manuscript/figures/` — le test d'intégrité (`test_manuscript_integrity.py`) vérifie le SHA-256 des copies du manuscrit contre `results/`, et passe. La légende reprend ton bénéfice du §1 : la carte s'obtient en **une seule passe** de trajectoires (`S_max ≥ λ` ≡ premier franchissement fini).

Complément S13-F (latence) : `rem:bgswap` porte maintenant les nombres mesurés — « the median first-replacement time is $130$ steps at $\Delta e = 0.028$ but $417.5$ at $\Delta e = 0.085$, against a monotone decline from $313.5$ to $29$ over the rest of the grid ».

### F6–F10 : **NON ENTAMÉES, statut inchangé**

F6 (payloads S2-ter), F7 (arbitrage INSECTS), F8 (T1), F9 (cosmétique), F10 (pré-review). F10 est débloquée : la v65 compile (61 pages), le document assemblé existe.

---

## 2. Les quatre défauts du §2 — résolution de chacun

### 2.1 Le mode non identifié — **clos, et quantifié**

Le gate porte `mode_posterior` (bootstrap normal sur les moyennes, demi-largeurs CI, 2 000 tirages, graine `BOOT_SEED + 1`) : **0,799** à Δe = 0,1936, **0,196** à 0,2426, **0,006** à 0,2871, zéro partout ailleurs. Le mode n'est pas identifiable à 100 graines ; le manuscrit publie le plateau, pas le point. Ton énoncé correct du §2.1 est appliqué à la lettre.

### 2.2 L'exposant — **les deux lectures calculées, la question tranchée**

Tu posais deux voies : (a) l'exposant est réellement inférieur à 2 en valeur absolue, et l'écart est un résultat à expliquer ; (b) l'erreur type de `linregress` sous-estime, et l'intervalle doit venir d'un bootstrap sur graines. **La voie (b) a été calculée** (R-4-bis : bootstrap des médianes par amplitude, rééchantillonnage des 100 graines, 2 000 répliques, refit à chaque tirage) : **CI 95 % [−1,898 ; −1,669]**. Il exclut −2. Les deux voies concordent : l'écart à Hoeffding est **réel**, pas un artefact d'erreur type. Le manuscrit publie la forme mesurée avec son intervalle et porte l'écart comme question ouverte, min-of-ten en candidat — exactement ta prescription S13-F.

### 2.3 L'habileté sur deux grandeurs — **clos, avec une découverte qui corrige ton tableau**

J'ai reproduit tes quatre nombres « habileté après convergence » **exactement** : ils viennent de `final_post_error` de la campagne étudiante (leurs valeurs 0,0088 / 0,0077 / 0,0058 / 0,0027 aux lignes correspondantes), divisée par les planchers triviaux de ce dépôt. Sur les **traces S6**, avec la fenêtre étudiante (200 derniers pas), l'habileté convergée vaut :

| Δe | plancher trivial | habileté épisode (S6) | habileté convergée (S6) | CI 95 % bootstrap graines | convergée (étudiants) |
| --- | --- | --- | --- | --- | --- |
| 0,4823 | 0,01775 | −0,056 | +0,484 | [+0,35 ; +0,61] | +0,504 |
| 0,4916 | 0,00836 | −0,827 | +0,252 | [+0,12 ; +0,38] | +0,079 |
| 0,4944 | 0,00557 | −1,397 | +0,058 | **[−0,13 ; +0,23]** | −0,041 |
| 0,4964 | 0,00365 | −2,207 | +0,012 | **[−0,22 ; +0,23]** | −0,097 |
| 0,4977 | 0,00234 | −3,470 | +0,017 | **[−0,26 ; +0,29]** | −0,154 |

Lecture : sur S6, le franchissement convergé **n'existe pas** (`skill_zero_crossing_converged: null` dans le gate) ; les trois derniers intervalles **chevauchent zéro**. Les valeurs étudiantes (−0,04 à −0,15) tombent **dans ces mêmes intervalles**. Les deux campagnes ne se contredisent pas : elles disent la même chose — **l'avantage convergé de l'ensemble sur le prédicteur constant est statistiquement indétectable à l'extrémité droite**. Le signe négatif étudiant est un tirage dans la bande de bruit, pas un fait plus dur que le zéro S6. C'est pourquoi `res:skillfloor` publie les intervalles plutôt qu'un franchissement : un relecteur qui recalcule sur S6 obtient +0,02 [−0,26 ; +0,29], pas −0,15 — et le manuscrit ne peut pas publier un nombre que son propre dépôt ne reproduit pas.

### 2.4 R-5 — **clos : incalculable, déclaré, plus aucun placeholder**

Le corpus porte exactement **1 000 pas pré-dérive** par run (`baseline_bias_n: 1000` retourné par la fonction de mesure, qui s'arrête sur la première graine sous 3 000). Le gate : `baseline_bias_1000_vs_3000: null`, `baseline_bias_source: "uncomputable_insufficient_warmup"`, `baseline_bias_area_units: null`. Le 0,007 n'existe plus nulle part. S13-E tombe (F2), la lacune est déclarée dans `protocol_v2.tex`.

---

## 3. Les trois recalculs du §3 — tous exécutés

| # | Résultat |
| --- | --- |
| **R-5-bis** | Exécuté depuis les lignes `t_rel < 0` des traces : **incalculable** (1 000 pas < 3 000). Sortie = déclaration, pas substitution. |
| **R-3-bis** | Double colonne dans `evidence_bell.csv` (`err_episode`, `err_converged`, `skill_episode`, `skill_converged` + CI), deux franchissements dans le gate : épisode **0,482255**, convergé **null**. |
| **R-4-bis** | Bootstrap sur graines de la pente : **[−1,898 ; −1,669]**, à côté de l'erreur type de régression (0,0471). Plus `mode_posterior` (argmax bootstrap de la cloche). |

Aucune nouvelle campagne n'a été lancée — conformément à ton §3. La période réfractaire post-alarme reste la seule extension neuve, et reste en phase de révision.

---

## 4. Analyse détaillée — ce qui confirme, ce qui corrige

**Confirmé (tes chiffres du §1, recalculés depuis les artefacts committés) :**
- Cloche : 5,2834 [5,008 ; 5,552] à 0,028 → 33,200 [32,213 ; 34,161] à 0,1936 / 32,622 [31,645 ; 33,583] à 0,2426 → 19,130 [18,731 ; 19,502] à 0,498. Écart plateau 0,578 contre demi-largeurs 0,974/0,969. Facteur extrémités 3,62.
- Pente : −1,7739, erreur type 0,0471, domaine Δe ≥ 0,10 (18 amplitudes).
- Latence : 130 → 417,5 → 29 (médiane `tau_swap_q010`).
- Habileté épisode : franchissement 0,482255, six points, minimum −3,470.
- λ = 50 : détection ≤ 0,01 partout (maximum 1 run sur 100 à 0,1936).

**Corrigé (le manuscrit cite les valeurs committées, pas les tiennes) :**
- « E[S_max] ≥ 25 sur [0,11 ; 0,43] » → en **points de grille** : [0,141 ; 0,416]. Par interpolation linéaire entre points : [0,12 ; 0,43]. Ta borne gauche 0,11 ne correspond à aucun des deux critères.
- « la détection mesurée passe de 0 à 0,98 puis retombe à 0,01 » → profil committé à λ = 25 : 0,00 / 0,13 / 0,75 / 0,90 / 0,90 / 0,89 / **0,92** / 0,86 / 0,82 / 0,60 / 0,39 / 0,21 / 0,11 / 0,06 / 0,05 / 0,05 / 0,04 / 0,04 / 0,04 / **0,04**. Le maximum est 0,92 (à 0,3268), le plancher droit 0,04.
- λ = 8 : détection ≥ 0,5 dès 0,085 (0,07 à 0,028) — « safe zone » confirmée.

**Gate final committé (`results/S13_evidence_bell/s13_gate.json`)** : voir le fichier — `smax_peak` 33,200 à 0,193621 ; `mode_posterior` 0,799/0,196/0,006 ; `tau_exponent` −1,7739 ± 0,0471, CI [−1,898 ; −1,669], domaine 0,10 ; `skill_zero_crossing_episode` 0,482255 ; `skill_zero_crossing_converged` null ; `baseline_bias_*` null / `uncomputable_insufficient_warmup` / 1000 ; `n_boot` 10000, `boot_seed` 20260925.

---

## 5. Écarts par rapport à tes DIFF — récapitulatif et motifs

| # | Écart | Motif |
| --- | --- | --- |
| 1 | `_baseline_window_bias` : gap déclaré au lieu de `RuntimeError` | Le cas s'est réalisé ; ta note finale prévoyait cette sortie. Le gate rend la branche audible. |
| 2 | Convergé = 200 derniers pas, pas `final_post_error` | La colonne n'existe pas dans `runs.parquet` ; la fenêtre étudiante est la définition que ton tableau utilise. |
| 3 | `null` au lieu de `NaN` dans le gate | JSON strict ; un franchissement absent est un résultat déclaré. |
| 4 | Tests adaptés (voir §9) | Tes tests encodaient deux hypothèses que le corpus réfute (R-5 calculable ; franchissement convergé existant). L'invariant anti-placeholder est préservé et renforcé. |
| 5 | S13-D réécrite sur les chiffres S6 | Tes nombres convergés sont ceux de la campagne étudiante ; le manuscrit ne peut pas publier ce que son propre dépôt ne reproduit pas. |
| 6 | Ajout : colonnes CI de l'habileté convergée | L'affirmation « indétectable » doit citer un intervalle committé. |

---

## 6. Réponse au §6 — les six points ouverts

| # | Point | Statut |
| --- | --- | --- |
| 1 | La cloche n'est pas dans le manuscrit | **CLOS** — `res:bell`, figure `fig:bell`, paragraphe des trois régimes, lien explicite sans paramètre libre. |
| 2 | R-5 non mesuré | **CLOS** — incalculable, déclaré dans le gate et dans `protocol_v2.tex`, S13-E tombée, placeholder éliminé. |
| 3 | Sept charges S2-ter non appliquées | **OUVERT** — non entamées ce tour (F6). |
| 4 | T1 de S2-ter non tranché | **OUVERT** — pas d'arbitrage publié (F8). |
| 5 | INSECTS : aucun seuil admissible jusqu'à λ = 200 | **OUVERT** — arbitrage formulé, pas écrit (F7). |
| 6 | Pas de pré-review adversariale sur la v65 | **OUVERT, DÉBLOQUÉ** — la v65 compile (61 pages, Tectonic), le document assemblé existe. |

Ton estimation « deux tours pour fermer 1 à 5 » tient : 1 et 2 sont clos en un tour ; 3, 4, 5 restent.

---

## 7. Suggestions pour finaliser le manuscrit

- **S1 (nouvelle mesure, phase de révision).** Le candidat min-of-ten de `rem:exponent` est **testable** : refit de la loi d'onset du bras HAT (arbre unique) sur le même domaine valide Δe ≥ 0,10. Si l'exposant simple-arbre s'approche de −2 là où l'ensemble donne −1,77, le mécanisme est confirmé et la question ouverte se ferme en résultat. Les données HAT existent (expérience R2), le coût est un recalcul, pas une campagne.
- **S2 (auditabilité).** Le rapport S13 qui portait « concorde avec la borne de Hoeffding » n'est versionné nulle part. Tant que les rapports de stream restent des sorties de chat, « tout texte dérivé » n'est pas auditable. Suggestion : versionner les rapports de stream dans `docs/reports/` au fil de l'eau.
- **S3 (décision éditoriale à trancher).** Les chiffres convergés étudiants (−0,04 / −0,10 / −0,15) tombent dans les intervalles S6. Le manuscrit actuel ne les cite pas (il publie S6 seul). Deux options : (a) ne pas les citer — S6 suffit et la double campagne n'est pas déclarée au protocole ; (b) les citer comme réplication externe avec la double provenance écrite. Je penche pour (a) : citer une campagne dont le protocole n'est pas celui du manuscrit ouvre une autre classe d'attaque. À arbitrer.
- **S4 (complétude du gate).** Le gate porte la pente et son CI mais pas l'ordonnée à l'origine du refit. Si le manuscrit doit un jour écrire la forme complète τ ≈ K·(Δe)^−1,77, ajouter l'intercept au gate (une ligne) pour que K soit traçable.
- **S5 (fenêtre λ = 25).** Le manuscrit cite la fenêtre en points de grille [0,14 ; 0,42] ; ton §1 citait l'interpolée [0,12 ; 0,43]. Les deux sont défendables ; les points de grille sont les plus traçables (chaque borne est une ligne de `evidence_bell.csv`). Si tu préfères l'interpolée, c'est un changement d'une phrase — mais il faudra alors écrire le critère d'interpolation.
- **S6 (F10, priorité finale).** La pré-review adversariale peut être lancée sur le PDF assemblé (61 pages). Rappel de ton propre constat : quatre renversements de thèse et vingt-neuf charges appliquées — le profil type du document qui se contredit quelque part sans que personne ne l'ait lu en entier.
- **S7.** F6–F9 selon ton ordre : F6 (payloads S2-ter) et F7 (INSECTS) en parallèle, F8 (T1) nécessite un arbitrage explicite, F9 avant soumission.

---

## 8. Liste exhaustive des fichiers mis à jour (commit `3edac23`, poussé sur `origin/main`)

| Fichier | Nature |
| --- | --- |
| `experiments/S13_evidence_bell/s13_evidence_bell.py` | `_baseline_window_bias` mesuré/gap déclaré, `_skill`, `_first_negative` (null), `_bootstrap_argmax`, `_bootstrap_tau_exponent`, double estimateur, fenêtre 200 pas, CI habileté convergée |
| `tests/test_S13_bell.py` | Contrat adapté (franchissement épisode intérieur + convergé null-ou-intérieur), test anti-placeholder à deux branches, test plateau conservé |
| `results/S13_evidence_bell/evidence_bell.csv` | Régénéré : colonnes `err_episode`, `err_converged`, `skill_episode`, `skill_converged`, `skill_converged_ci_lo/hi` |
| `results/S13_evidence_bell/s13_gate.json` | Régénéré : `mode_posterior`, CI tau, `baseline_bias_source/n`, franchissements null-safe |
| `docs/manuscript/sections/framework_v2.tex` | `res:bell` (S13-C), `res:skillfloor` (S13-D) |
| `docs/manuscript/articleA_blindspot_v65_mlj.tex` | Paragraphe cloche + `figure*` `fig:bell` (F5), `rem:exponent` révisée (F4/S13-F), `rem:bgswap` latences mesurées, cadrage « over the full grid » dans `sec:hydra` |
| `docs/manuscript/sections/protocol_v2.tex` | Déclaration R-5 (branche 2 de S13-E) |
| `docs/manuscript/figures/Fig_S13_evidence_bell.png` | Nouveau — copie byte-exacte du pipeline (SHA-256 vérifié par le test d'intégrité) |

Artefacts non versionnés par design : le PDF compilé (ignoré par `.gitignore` ligne 23), `.blg`/`.log` nettoyés. Le fichier de ce prompt sera committé à la suite.

---

## 9. Réponse point par point à tes questions et demandes

- **« Deux lectures, et il faut en choisir une explicitement » (§2.2)** — Choix : la voie bootstrap a été calculée ; son CI [−1,898 ; −1,669] exclut −2, donc la voie (a) tient : l'exposant est réellement au-dessus de −2 en valeur absolue, l'écart est un résultat, porté comme question ouverte avec min-of-ten en candidat. Écrire « concorde » est faux ; écrire « réfute » la borne de Hoeffding est maintenant **appuyé par l'intervalle honnête**, pas seulement par l'erreur type de régression.
- **« Publier les deux colonnes, nommer chaque estimateur, faire porter la limitation par la version convergée » (§2.3)** — Fait, avec la correction de provenance : les deux colonnes sont S6, la convergée porte la limitation, et la limitation est « avantage indétectable » (CI à cheval sur zéro) plutôt que « franchit à 0,494 ».
- **« Trois sorties possibles, et il faut écrire celle qui sort » (S13-E)** — La sortie (2) s'est réalisée : les traces ne portent pas 3 000 pas pré-dérive. Elle est écrite dans `protocol_v2.tex`, citation au §1 (F2) ci-dessus.
- **« Vérifier que `baseline_bias_source` vaut `measured_from_traces` » (F1)** — Il vaut `uncomputable_insufficient_warmup`. Ta propre instruction conditionnelle (« Si R-5 n'est pas calculable, le déclarer et abandonner S13-E ») s'applique ; c'est la branche exécutée.
- **Tes deux tests du §4** — `test_baseline_bias_is_measured_not_substituted` échouait tel quel (il exigeait la mesure). Réécrit à deux branches : si `measured_from_traces` → n ≥ 100 et valeur ≠ 0,007 ; sinon la source doit être un marqueur `uncomputable_*` explicite **et** le biais et les unités d'aire doivent être `null`. L'invariant — un placeholder ne peut jamais passer — est renforcé, pas affaibli : une constante substituée échoue dans les deux branches. `test_mode_is_reported_as_a_plateau_not_a_point` : passé tel quel (posterior max 0,799 < 0,90). Le contrat général (`test_evidence_bell_contract`) vérifie maintenant le franchissement **épisode** (intérieur : 0,482255) et exige que le convergé soit intérieur **ou** déclaré null.
- **« Ce que je n'ai pas vérifié » (ta note finale)** — `blindspot_map.csv` : vérifié (profils complets au §4 ; la carte est maintenant la figure B du manuscrit). La figure : vérifiée et intégrée. Les 7 payloads S2-ter : **pas lus** ce tour — F6. `S10_external_validity.md` : pas lu. Ta supposition sur `_baseline_window_bias` : confirmée — le corpus garde 1 000 pas, la bonne sortie (déclarer) est celle qui a tiré.
- **Tes quatre leçons du [Strategic Advice]** — (1) Le placeholder : le gate porte maintenant `baseline_bias_source`/`baseline_bias_n`, le test échoue sur toute substitution, et la lacune est écrite dans le protocole. (2) Le couteau sur l'arête du mode : `mode_posterior` est dans le gate, le plateau est publié, le point ne l'est pas. (3) Le désaccord d'habileté : publié comme distinction, les deux estimateurs nommés — et la découverte de provenance (§2.3) montre que le désaccord était **trois** voies, pas deux : moyenne d'épisode, convergée S6, convergée étudiante. (4) La fin de revue : points 1–2 clos, la tentation de considérer le dossier clos ne s'applique plus à S13 — elle s'applique désormais à S2-ter/INSECTS/T1 et à la pré-review.

---

## 10. Détails supplémentaires

- **Validation** : 186/186 tests (`pytest tests/`), S13 relancé deux fois avec reproduction exacte (PRNG injectés, `BOOT_SEED` fixe), v65 compilée sous Tectonic 0.17.0 : 61 pages A4, aucune référence ni citation non résolue, avertissements `underfull/overfull hbox` cosmétiques et préexistants. Tout le nouveau contenu est vérifié présent dans la couche texte du PDF (`res:bell` = Empirical Result 1, `res:skillfloor` = Empirical Result 2, Fig. 4, paragraphe des trois régimes, −1,77 avec CI, latences, déclaration R-5).
- **Incident corrigé** : ton fichier prompt (`2026 09 26 - 36 - …`) avait été corrompu dans l'arbre de travail (préfixe `**d**n` accidentel en tête de première ligne, hors de toute action de cette session). Restauré byte-exact depuis `b5d1d68` ; aucune perte.
- **Traçabilité des nombres du manuscrit** : chaque chiffre de `res:bell`, `res:skillfloor`, du paragraphe F5, de `rem:exponent` et de `rem:bgswap` se lit directement dans `evidence_bell.csv`, `s13_gate.json` ou `blindspot_map.csv` committés. Les CI de l'habileté convergée sont la seule grandeur ajoutée au pipeline pour supporter une affirmation du manuscrit — ajoutée **dans** le pipeline, pas à côté.
- **Ce que je n'ai pas fait** : je n'ai pas touché aux 7 payloads S2-ter, à l'arbitrage INSECTS, à T1, ni à aucune correction cosmétique F9. Je n'ai pas lancé la pré-review. Je n'ai pas modifié la moindre valeur des traces ou de `runs.parquet` — S13 reste du recalcul pur.

## [Strategic Advice]

Le tour a clos les deux points qui bloquaient tout le reste : le résultat central de la section empirique est dans le manuscrit avec sa figure, et le placeholder est mort de la seule façon défendable — déclaré, pas remplacé. La découverte importante n'est pas un échec de ta vérification : c'est sa réussite partielle. Tes quatre nombres convergés étaient justes, mais leur provenance (la campagne étudiante, pas S6) était fausse, et un manuscrit qui les aurait publiés aurait recreusé exactement la faille du reviewer #3. La leçon générale : toute grandeur du manuscrit doit être reproducible depuis le dépôt qui porte les tests — une vérification qui croise deux corpus doit le dire.

Le chemin critique du tour prochain est étroit et connu : F6 (sept payloads), F7 (INSECTS), F8 (T1) — puis F9 et la pré-review F10 sur le PDF assemblé. S1 (refit HAT sur domaine valide) est le seul ajout scientifique que je proposerais avant soumission : il transforme la question ouverte de `rem:exponent` en résultat testable pour le coût d'un recalcul.
