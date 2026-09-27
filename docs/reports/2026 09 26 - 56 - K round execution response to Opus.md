[Sunday, September 27, 2026]

# RÉPONSE K1–K9 · ROBUSTESSE AU GATE · SOURCES ASSAINIES · METHODS.md · DÉCLARATION IA · L'EXPORT S'AUTO-VÉRIFIE · GEL SUSPENDU PAR L'HISTORIQUE DE RÉVISION DU TEXTE

Suite à ton prompt « 2026 09 26 - 55 - Opus post K7 K8.md ». K1 à K9 sont exécutés et poussés : commits `c3d5bde` et `5d1ff11`, `22ee53b..5d1ff11`. Dépôt : 192/192 tests. Depuis l'export seul : 173 passés, 15 sautés, 0 échec. `sha256sum -c` à 27 OK / 7 FAILED, ensemble inchangé. v65 : 63 pages, zéro référence non résolue.

**Pas de tag de gel ni de PDF gelé**, par arbitrage de l'opérateur. Le texte imprimé raconte encore sa révision, en 41 phrases ; l'inventaire verbatim est annexé (§8). K7 et K8 ont été vérifiés à la source par l'opérateur : *Machine Learning* est en simple aveugle, et Springer Nature exige la divulgation de l'usage des LLM.

---

## 0. Synthèse exécutive

- **K1–K2.** La robustesse de c2 est au gate, recalculable et testée. Les quatre sous-ensembles excluent 0 en IC bootstrap sur graines, et les blocs disjoints aussi.
- **K3.** Les sources livrées ne portent plus aucune étiquette de processus. Le nettoyage a touché deux payloads appliqués dont le REPLACE contenait ces commentaires ; les gardes durcies l'ont détecté immédiatement, ce qui est leur rôle, et l'amendement est déclaré par nom (§3).
- **K4–K6.** `docs/METHODS.md` résout les renvois morts. Le README explique les 15 sauts. L'archive v64 est étiquetée et ré-épinglée à découvert.
- **K7.** La section Declarations existe, avec la divulgation dans les termes fixés par l'opérateur.
- **Blocage pour le gel.** 41 phrases du corps renvoient à la version soumise, à la v63, à sa revue, ou racontent un retrait. Elles attendent tes blocs de réécriture.

---

## 1. K1–K2 — `curvature.robustness`

Même tirage que `quadratic_ci` (`BOOT_SEED + 9`) ; la valeur publiée est inchangée au bit près. Source : `s13_gate.json :: curvature.robustness`.

| sous-ensemble | n | c2 | erreur type MCO | IC 95 % bootstrap |
|---|---|---|---|---|
| tous | 18 | 0,500 | 0,047 | [0,296 ; 0,759] |
| sans le point de gauche | 17 | 0,474 | 0,087 | [0,181 ; 0,738] |
| sans les six plus grandes amplitudes | 12 | 0,592 | 0,038 | [0,348 ; 0,887] |
| sans les deux | 11 | 0,669 | 0,069 | [0,279 ; 0,967] |

Blocs disjoints (points 1–6 et 7–12 de la grille valide) : pentes −2,048 et −1,322, écart −0,726, IC [−1,195 ; −0,225].

Tes chiffres (c2, t) se reproduisent exactement. Le retrait du point de gauche élargit nettement l'intervalle bootstrap, que l'erreur type MCO sous-estime : ce sous-ensemble est le plus fragile des quatre, mais il exclut 0. Un test (`test_curvature_robustness_is_recomputable`) recalcule chaque entrée depuis `evidence_bell.csv` et exige des IC de c2 strictement positifs. Déclaration ajoutée à l'entrée « Stream S13 » du registre des déviations.

## 2. K3 — sources du manuscrit

- **Préambule de la v65.** Les cinq titres « % ── Stream S… » deviennent des titres neutres. « (transfer\_S1 label 0.33) » et « Action 4 » sont retirés. Le commentaire de `\RepoURL` sur l'anonymisation et la « venue » est retiré. La provenance « Source: results/… » est conservée.
- **En-têtes de fragments.**
  - `protocol_v2.tex` : « stream S7-ter, LOT A. Answers reviewer #3's… » disparaît ;
  - `framework_v2.tex` : « Section III v2 … stream S1 … v63 » disparaît ;
  - `prop3_v2.tex` : « Stream S2, deliverable 1 » disparaît ;
  - `dependence_v2.tex` : « Stream S3 … v63 … F22 » disparaît ;
  - `figures/fig_ontology.tex` : « stream S11-a, thesis v4 », « S5 », « IEEEtran » disparaissent.
- **`.bib`.** « STREAM S5 ADDITIONS — merged here by action A6 … docs/editorial/source_verification.md » devient « % Additional references. ».
- **Contrôle depuis l'export** : zéro commentaire de processus dans les sources livrées, v64 archivée exceptée.

## 3. L'incident de K3, et ce qu'il confirme

Deux payloads appliqués, **S8-1** (bloc de macros « ab initio ») et **S2bis-2** (bloc « equal-false-alarm-budget »), portaient dans leur REPLACE les commentaires « % ── Stream S8… » et « % ── Stream S2-bis… ». Les neutraliser a fait passer leur état de (0, 1) à (1, 0). La porte 1 a échoué : `test_S8_generality` et `test_S2bis_calibration`, durcis au tour I, refusaient désormais cet état.

Correction selon le patron établi :
- amendement déclaré par nom dans chaque garde (`S8_NEUTRALISED_COMMENTS`, et le remplacement équivalent dans `test_S2bis_calibration`) ;
- une ligne d'erratum à côté de chaque payload, dans `transfer_S8.md` et `transfer_S2bis.md` ;
- recensement des payloads identique avant et après, avec les amendements.

Sans le durcissement, le changement serait passé en silence, avec deux payloads « en attente » qu'une ré-application aurait dupliqués.

## 4. K4–K6 — `METHODS.md`, README, v64

- **`docs/METHODS.md`**, livré. Il décrit la convention : une règle citée a été écrite et commitée avant la mesure qu'elle gouverne, et ses verdicts appartiennent à un vocabulaire fermé. Il dit aussi pourquoi les fichiers de règles et les notes internes ne sont pas livrés : ce sont des notes de travail qui entremêlent règles, correspondance, brouillons dépassés et instructions à l'assistant IA déclaré. Enfin, il montre que rien de nécessaire à la reproduction n'y figure : la règle s'applique dans le script qui la cite, le verdict est stocké dans le fichier de résultat, et `tests/` vérifie. Il explique aussi les identifiants de lot (« streams ») et le mot « payloads ».
- **README, §6 « Submission Artifact »** : l'artefact, les 15 sauts et leurs trois motifs (13 documents internes, 1 hors dépôt git, 1 registre des sources), et l'étiquette de la v64.
- **v64** : en-tête de trois lignes (« ARCHIVED EARLIER VERSION -- not submitted … superseded »). SHA ré-épinglé `8718fb74…` → `315c59fa…` dans `tests/test_manuscript_integrity.py`, l'ancien hash cité dans le commentaire de déclaration. `CLAUDE.md` est mis à jour.

## 5. K7–K8 — Declarations

`\section*{Declarations}`, entre la Conclusion et `\appendix` :
- **Use of generative AI.** « Anthropic's Claude (Claude Opus models) was used to assist with mathematical formalisation, critical review, and the refactoring of the experimental code and of the \LaTeX{} manuscript, under the supervision and sole responsibility of the human authors. Every number the paper reports comes from a committed result file, and the repository's test suite checks those files. No language model is an author of this work. » Outils et rôles fixés par l'opérateur : Claude seul ; Gemini, outil ponctuel de recherche documentaire hors chaîne, n'est pas cité.
- **Code and data availability.** Le dépôt (`\RepoURL`) et les jeux publics cités là où ils servent.

**Conséquences de K8 (simple aveugle), à trancher par les auteurs, non traitées :**
- le bloc auteur est encore « Anonymous Author(s) » / « Anonymous Affiliation(s) » ;
- `\RepoURL` pointe vers un miroir anonyme (anonymous.4open.science) ;
- financement, conflits d'intérêts et contributions manquent dans les Declarations.

**Effet sur l'export.** Le contrôle d'identité de `make_submission_export.sh` a bloqué la divulgation elle-même (« Claude Opus »). Il ignore désormais la seule ligne `\paragraph{Use of generative AI.}` et signale les autres lignes fautives (commit `5d1ff11`). Dans l'export, cette ligne est la seule occurrence.

## 6. K9 — export et contrôles

| contrôle | résultat |
|---|---|
| construction depuis HEAD | réussie ; seule occurrence d'identité : la déclaration |
| `pytest tests/` depuis l'export | **173 passés, 15 sautés, 0 échec** ; motifs conformes au README |
| imports | `ROOT_DIR` sous l'export |
| manuscrit compilé depuis l'export | 63 pages, zéro référence indéfinie |
| sources du manuscrit | zéro commentaire de processus (v64 exceptée, étiquetée) |
| `docs/METHODS.md` | présent |

Vocabulaire laissé (bloc 3), désormais expliqué par `METHODS.md` : « stream S… » 83 lignes, « payload » 218, renvois `docs/…` 65 (dont ceux de `METHODS.md` et du README), « decision-rules » 15. Aucun de ces renvois ne se trouve dans les sources du manuscrit.

## 7. Portes

| porte | résultat |
|---|---|
| 1. pytest (dépôt) | **192 passed** |
| 2. `sha256sum -c` | **27 OK, 7 FAILED**, ensemble inchangé |
| 3. compilation | zéro référence indéfinie, 63 pages ; un seul débordement, 2,2 pt |
| 4. recensement | K1–K9 faits ; K10 sans tag ; K11 différée |
| 5. `git status --porcelain` | vide après suppression du bac à sable et de l'export |

Gate S13 : deux relances, SHA identiques (`a5c55fb1…`) ; clés existantes et CSV inchangés.

## 8. Bloquant pour le gel — l'historique de révision dans le texte imprimé

*Machine Learning* ne connaît pas la soumission ICDM. Le corps du papier y renvoie pourtant 21 fois explicitement (« the submitted version », « v63 », « earlier versions », une sous-section « Status of the v63 statements » avec sa table, et « A reviewer of the submitted version faulted it… »). Il raconte en outre 20 retraits (« withdraw », « retract »). C'est le défaut que tu as nommé pour `protocol_v2.tex:2`, mais dans le texte imprimé. H10 le relèverait en quelques secondes.

L'inventaire ci-dessous donne, pour chaque occurrence, le fichier, la ligne et **la phrase source complète**, espaces normalisés. Les fragments de sections sont coupés en lignes : j'appliquerai chaque ancre sur le texte réel, re-greppé, sans forcer. Ta règle du prompt 52 est respectée : tu écris sur du texte lu verbatim dans ce tour.

Sur le fond, trois familles de traitement semblent se dessiner, à toi de trancher :
- **supprimer** la référence quand la phrase tient sans elle ;
- **réécrire en énoncé direct** (« we do not assume X ; the measurement shows Y ») quand la phrase oppose l'ancien et le nouveau ;
- **décider du sort de `sec:dep_status`**, sous-section entière qui liste des dispositions à l'égard de la v63.

## [Strategic Advice]

**Les gardes durcies ont servi dès le premier tour qui les touchait.** Un nettoyage purement cosmétique de commentaires a déplacé deux payloads appliqués ; sans le refus de l'état (1, 0), le changement aurait été invisible. Le coût du durcissement se paie en déclarations explicites, et c'est le prix correct.

**Le dernier défaut du texte n'est ni scientifique ni typographique : il est de destinataire.** Le papier répond encore à ses relecteurs ICDM. Une passe de réécriture sur les 41 phrases, guidée par tes blocs, suffit. Après elle : tag, PDF depuis l'export, H10.

---

## Annexe — inventaire verbatim

### A. Renvois explicites à la version soumise, à la v63 ou à sa revue (21 phrases)

- `articleA_blindspot_v65_mlj.tex:216`

  ```latex
  \paragraph{What the first replacement does, and what it does not.} Counterfactual arms sharing one stream, one history and one fork separate two mechanisms that earlier versions of this work conflated.
  ```

- `articleA_blindspot_v65_mlj.tex:298`

  ```latex
  \textcolor{red}{\textbf{Red}}: first replacement before the alarm, post-recovery alarms included ($\tau_{\mathrm{ARF}}{<}\tau_{\mathrm{det}}$; labelled `Blind Spot' in the legend after the ordering of the submitted version, not Definition~\ref{def:blindspot}).
  ```

- `articleA_blindspot_v65_mlj.tex:411`

  ```latex
  \paragraph{Retraction of the single-tree instantiation.} Earlier versions evaluated Eq.~\eqref{eq:mcrit} with $F$ read from the empirical CDF $\widehat{F}$ of the single-tree delays $\tau_{\mathrm{HAT}}$ ($M = 1$), obtaining at $\Delta e = 0.33$, $\lambda = 50$: $\mathbb{E}[\tau_{\mathrm{HAT}}] = 463$, $\widehat{F}(158) = 0.49$ and $M_{\mathrm{crit}} = 0$ at $r = 0.95$.
  ```

- `articleA_blindspot_v65_mlj.tex:427`

  ```latex
  That configuration is consistent with~\eqref{eq:decoupling} and was not with the strict biconditional of the submitted version, which we withdraw.
  ```

- `articleA_blindspot_v65_mlj.tex:432`

  ```latex
  The rectangular surrogate $q_{\alpha}(\tau_{\mathrm{ARF}})\cdot(\Delta e - \delta_P)$ used in the submitted version assumes a constant accumulation rate over a transient of length $\tau_{\mathrm{ARF}}$; synchronised instrumentation invalidates both halves of that assumption and the surrogate is withdrawn.
  ```

- `articleA_blindspot_v65_mlj.tex:627`

  ```latex
  The infeasibility claim of the submitted version held only because the envelope reached below the detectability floor.
  ```

- `sections/framework_v2.tex:120`

  ```latex
  \begin{remark}[The ordering is measured; the assumption behind it is withdrawn]\label{rem:order} The submitted version derived the inequality from an assumption of \emph{no recovery without replacement}: $\bar{e}_t > p_0 + \delta_P$ pointwise on $[\tau^*, \tau_{\mathrm{swap}}^{(1/M)})$.
  ```

- `sections/framework_v2.tex:141`

  ```latex
  The converse bound $\tau_{\mathrm{erase}} \le \tau_{\mathrm{swap}}^{(1)}$ of the submitted version did not follow from that assumption in the first place, and is withdrawn on its own evidence: it holds in $55.3\%$ of the runs where both sides are defined, and $\tau_{\mathrm{swap}}^{(1)}$ is itself undefined in $11.3\%$ of runs, the sweep of all $M$ trees never completing within the horizon.
  ```

- `sections/framework_v2.tex:154`

  ```latex
  The first swap is retained as an instrumented lower bound on $W$; $\kappa$ is measured, never assumed --- the submitted version asserted $\kappa \ge 1$ inside the definition, which is a claim about measured quantities and not a definition.
  ```

- `sections/framework_v2.tex:548`

  ```latex
  The submitted version stated the split in $W$ alone and placed the $\alpha$-price of $R_{\mathrm{KSWIN}}$ ``inside a square root of $W$'', which~\eqref{eq:Rkswin} contradicts: that term carries no $W$.
  ```

- `sections/prop3_v2.tex:62`

  ```latex
  That is a narrow domain --- and it contains the operating point at which the starvation certificate is stated. The proposition is not vacuous where it is used; it is vacuous almost everywhere else, and the submitted version said neither.
  ```

- `sections/prop3_v2.tex:66`

  ```latex
  A reviewer of the submitted version faulted it for treating a random window as a constant.
  ```

- `sections/protocol_v2.tex:41`

  ```latex
  \begin{remark}[Correction to the submitted resampling unit of Table~\ref{tab:results_concept}]\label{rem:boot_unit} The submitted version resampled the 360 \emph{runs} of a cell with replacement, off the global NumPy state seeded once before aggregation, while the caption asserted the seed as the unit of statistical independence.
  ```

- `sections/protocol_v2.tex:188`

  ```latex
  The submitted version pinned only the drift detector on the ProteuS and crossover arms, so their warning detector ran at $\delta = 0.01$ and clock $32$ while the instrumented arms pinned both at $\delta = 0.002$ and clock $c$.
  ```

- `sections/protocol_v2.tex:414`

  ```latex
  The regime-crossover experiment draws its covariates from the legacy \texttt{RandomState} (MT19937) generator rather than the modern one, deliberately, to reproduce the streams of the submitted version bit-for-bit; pairing is unaffected, since both arms read the same legacy stream, but its draws are not comparable with those of the other experiments.
  ```

- `sections/dependence_v2.tex:10`

  ```latex
  The submitted version of Proposition~\ref{prop:starvation_boundary} asserted an \emph{equality} for $P_{\mathrm{miss}}$ under a conditional independence of the per-tree delays that was never demonstrated, against a \emph{deterministic} accumulation time $\tau_{\mathrm{det}}^*$.
  ```

- `sections/dependence_v2.tex:143`

  ```latex
  No numeral of Eq.~\eqref{eq:pmiss} is therefore published through $\widehat{F}$, and the numerical example of the v63 section is retracted rather than recomputed.
  ```

- `sections/dependence_v2.tex:161`

  ```latex
  That is strictly weaker than the v63 statement and is published as such.
  ```

- `sections/dependence_v2.tex:233`

  ```latex
  Read as a quantitative null, the parallel-chart analogy~\cite{tartakovsky_2005_multichart} predicts $10\times$ at $M = 10$, and the submitted version attributed the measured shortfall to positive inter-tree correlation.
  ```

- `sections/dependence_v2.tex:245`

  ```latex
  \subsection{Status of the v63 statements}\label{sec:dep_status}
  ```

- `sections/dependence_v2.tex:249`

  ```latex
  \begin{center}\begin{tabular}{@{}lll@{}} \toprule object & v63 form & disposition \
  ```

### B. « withdraw / retract » qui racontent une correction (20 phrases)

- `articleA_blindspot_v65_mlj.tex:411`

  ```latex
  The instantiation is retracted rather than recomputed.
  ```

- `articleA_blindspot_v65_mlj.tex:461`

  ```latex
  The adaptation-time fits $\tau_{\mathrm{ARF}} \approx 18.5(\Delta e)^{-0.98}$ and $\tau_{\mathrm{HAT}} \approx 102(\Delta e)^{-1.02}$ describe the measured race of Section~\ref{sec:starvation_boundary}; they do not support the single-tree instantiation of the boundary, which is retracted there.
  ```

- `sections/framework_v2.tex:108`

  ```latex
  The universal quantifier over $s \ge t$ is what carries the argument, and it is why the ordering does not need the withdrawn pointwise assumption of Remark~\ref{rem:order}: a transient dip of $\bar{e}$ below $p_0 + \delta_P$ at some $t < t_1$ does not make $t$ admissible unless the error stays there, so it cannot move $\tau_{\mathrm{err}}$.
  ```

- `sections/framework_v2.tex:202`

  ```latex
  \begin{remark}[Both hypotheses are measured, and both are contradicted]\label{rem:invariance_measured} Hypothesis~(i) is the rectangular surrogate that synchronised instrumentation withdraws: $A/A_{\mathrm{rect}}$ spans $2.70$ to $-14.12$ over the magnitude grid and \emph{changes sign} at $\Delta e \ge 0.452$, where the adapted ensemble ends the window below its pre-change error rate.
  ```

- `sections/framework_v2.tex:213`

  ```latex
  The withdrawal of hypothesis~(i) does not depend on the generator; the sign change does.
  ```

- `sections/prop3_v2.tex:152`

  ```latex
  The rule fixed before the domain table was computed retains it on a non-empty informative domain and withdraws it on an empty one.
  ```

- `sections/prop3_v2.tex:202`

  ```latex
  Hypothesis~(i) is the rectangular surrogate, withdrawn on measurement: $A/A_{\mathrm{rect}}$ spans $2.70$ to $-14.12$ and changes sign.
  ```

- `sections/prop3_v2.tex:208`

  ```latex
  The proposition is thus a true statement about a model the repository has withdrawn, and it explains $3\%$ of a $90\%$ effect.
  ```

- `sections/prop3_v2.tex:255`

  ```latex
  No $R_{\mathrm{EDDM}}$ is delivered, and the requirement is withdrawn from the family of \S\ref{sec:requirement}.
  ```

- `sections/prop3_v2.tex:257`

  ```latex
  The reasons are stated so that the withdrawal is not read as an oversight.
  ```

- `sections/prop3_v2.tex:284`

  ```latex
  This closed form does not reproduce the measured collapse, and the rule fixed in advance makes withdrawal the outcome in that case.
  ```

- `sections/prop3_v2.tex:305`

  ```latex
  The \emph{empirical} EDDM result is untouched by this: $0$ detections in $1{,}080$ runs against $882$ for the same detector on a non-adaptive learner, sign test $p \approx 1.9\times10^{-9}$, is a measurement and stands on its own. What is withdrawn is the claim that a requirement $R_{\mathrm{EDDM}}$ of the form of Eqs.~\eqref{eq:Rcusum}--\eqref{eq:Rkswin} governs it.
  ```

- `sections/prop3_v2.tex:322`

  ```latex
  $R_{\mathrm{EDDM}}$ & NOT PRODUCED & withdrawn; the empirical result stands \
  ```

- `sections/protocol_v2.tex:324`

  ```latex
  The rise of detection under a shared label latency on the rotation family ($p = 0.16$) is withdrawn; its canonical counterpart is retained.
  ```

- `sections/dependence_v2.tex:145`

  ```latex
  \subsection{Critical ensemble size, withdrawn}\label{sec:dep_mcrit}
  ```

- `sections/dependence_v2.tex:147`

  ```latex
  \begin{remark}[Why $M_{\mathrm{crit}}$ does not survive]\label{rem:mcrit_withdrawn} Corollary~\ref{cor:mcrit} inverts Eq.~\eqref{eq:pmiss} in $M$.
  ```

- `sections/dependence_v2.tex:156`

  ```latex
  It is withdrawn, and replaced by the measured incidence of Section~\ref{sec:dep_race}.
  ```

- `sections/dependence_v2.tex:162`

  ```latex
  We note for completeness that the alternative --- withdrawing the proposition entirely --- was considered: $\mathrm{Prop.}$~\ref{prop:certificate} is deterministic, carries no distributional hypothesis, and already routes the published result through $A_{\mathrm{swap}}$ (Definition~\ref{def:decoupling}, Empirical Result~\ref{res:tension}).
  ```

- `sections/dependence_v2.tex:256`

  ```latex
  Cor.~\ref{cor:mcrit} & live corollary & \textbf{withdrawn} (Rem.~\ref{rem:mcrit_withdrawn}) \
  ```

- `sections/dependence_v2.tex:257`

  ```latex
  numerical example & $M_{\mathrm{crit}} = 0$ at $r = 0.95$ & retracted with the plug-in \
  ```

