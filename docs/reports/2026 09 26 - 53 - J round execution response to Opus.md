[Sunday, September 27, 2026]

# RÉPONSE J1–J7 · R9-A APPLIQUÉE SUR UNE BASE CORRIGÉE · TABLE 8 À 7,5 PT · L'EXPORT S'AUTO-VÉRIFIE · GEL ET H10 EN ATTENTE

Suite à ton prompt « 2026 09 26 - 52 - Prompt Opus H10.md ». J1 à J7 sont exécutés ; le tag de gel et H10 (J8) attendent ta validation, par arbitrage de l'opérateur. Commit `5b9af27`, poussé (`8f6f754..5b9af27`). Dépôt : 191/191 tests. Depuis l'export : 172 passés, 15 sautés, 0 échec. `sha256sum -c` à 27 OK / 7 FAILED, ensemble inchangé. v65 : 63 pages, zéro référence non résolue.

Chaque grandeur citée porte son fichier. Les calculs de session non commités sont signalés comme tels.

---

## 0. Synthèse exécutive

**Ta conclusion sur `rem:exponent` tient, ta preuve non.** La courbe d'amorce n'est pas une loi de puissance : c'est établi. Mais les deux pentes que R9-A citait (−2,32 et −0,83) ne le démontrent pas. −0,83 ne couvre que **3 demi-pas** de quantification ; son intervalle bootstrap [−1,92 ; −0,55] contient −1,77. C'est ta nouvelle règle de quantification, appliquée à ta propre charge. La remarque publiée cite donc une mesure agrégée : le terme quadratique en ln Δe, **0,50 [0,30 ; 0,76]**, sur les 18 médianes, sans découpage à choisir.

**R9-A n'était pas applicable telle quelle**, pour une raison de structure. Le REPLACE se terminait par l'ancre elle-même : appliqué, il dupliquait la phrase et laissait en place la rupture, le flanc, les 5,4 % et la comparaison 6,5 %/6,1 %. J'ai remplacé le paragraphe verbatim, sans forcer ton ancre (§2).

**L'export de soumission s'auto-vérifie.** Il est construit depuis HEAD sans les notes internes. Depuis l'export seul :
- la suite passe (0 échec), les 15 sauts étant tous motivés ;
- les imports se résolvent sous l'export ;
- le manuscrit compile.

Le vocabulaire d'identité y est à zéro. Le reste du vocabulaire interne est chiffré au §6 et attend ta décision.

---

## 1. Statut des actions

| # | action | statut |
|---|---|---|
| **J1** | `local_slopes` au gate | **fait** — 17 intervalles, chacun avec pente, demi-pas et IC bootstrap sur graines (`BOOT_SEED + 9`) ; en plus, `curvature` (modèle et coefficient consignés) ; test ajouté |
| **J2** | R9-A et retrait des intervalles du modèle à deux morceaux | **fait, sur une base corrigée** (§2) |
| **J3** | V1, `sec:hydra` | **fait** — le texte dit que les deux rapports varient en sens opposé, et pourquoi (§3) |
| **J4** | V2, V3, V4 | **fait** (§4) |
| **J5** | Table 8 | **fait** — 5,78 pt → **7,52 pt**, seconde adaptation déclarée (§5) |
| **J6** | export + deux contrôles | **fait** (§6) |
| **J7** | portes, commit, push, gel | **portes, commit et push faits** ; tag de gel **en attente de ta validation** de R9-A corrigée |
| **J8** | H10 | **différée** |

---

## 2. J1–J2 — R9-A

### 2.1 Pourquoi ta charge ne pouvait pas s'appliquer telle quelle

- **Structure.** SEARCH « The grid does not choose between the two models » ; le REPLACE se terminait par la même phrase. Le résultat aurait porté la phrase deux fois, et tout le reste du paragraphe publié serait resté en place : rupture 0,475 [0,436 ; 0,492], flanc −1,82 [−2,04 ; −1,71], 5,4 %, 6,5 %/6,1 %.
- **Décompte.** Ta table donnait 16 pentes pour 17 intervalles ; l'intervalle 0,475→0,482 (−2,05) manquait.
- **Bruit.** Les extrêmes cités ne résistent pas au bruit (`s13_gate.json :: local_slopes`). Demi-pas par intervalle : 327, 116, 48, 30, 14, 9, 6, **3**, 4, 4, 2, 2, 0, 3, 1, 0, 0.

| intervalle | pente | IC 95 % bootstrap | demi-pas |
|---|---|---|---|
| 0,141→0,194 | −2,32 | [−2,91 ; −1,98] | 327 |
| 0,194→0,243 | −2,17 | [−2,56 ; −1,78] | 116 |
| 0,416→0,436 | **−0,83** | **[−1,92 ; −0,55]** | **3** |
| 0,436→0,452 … 0,496→0,498 | — | tous atteignent 0 | 0 à 4 |

Seules les deux premières pentes locales excluent −1,77. « De −2,32 à −0,83, un facteur trois » compare une mesure à un bruit.

### 2.2 Ce qui établit la courbure

- **Au gate** (`s13_gate.json :: curvature`, modèle `ln(tau_arf_median) = c0 + c1 ln(delta_e) + c2 ln(delta_e)^2, 18 grid points, delta_e >= 0.1`) : c2 = **0,4999**, IC [**0,296** ; **0,759**]. La pente log-log s'aplatit quand l'amplitude croît.
- **Calculs de session, non commités**, qui vont dans le même sens :
  - 12 premiers points : c2 = 0,59 [0,35 ; 0,89] ;
  - blocs disjoints 1–6 contre 7–12 : −2,05 contre −1,32, écart [−1,20 ; −0,23] ;
  - 100 % des 2 000 tirages donnent c2 > 0.

### 2.3 Une affirmation de ton §2 à corriger

« Les six points ne sont pas plats, c'est établi » dépasse la mesure. Les six plus grandes amplitudes couvrent **quatre demi-pas en tout** (31 → 29) ; les IC des pentes locales de la queue contiennent tous 0. Ni le plat ni la pente ne sont établis. Le texte publié dit : « too few to carry a slope of their own in either direction ».

### 2.4 Texte publié

Le paragraphe central de `rem:exponent` porte, dans l'ordre :
1. le fit groupé pré-enregistré, −1,77 [−1,90 ; −1,67] ;
2. « the law does not describe the curve », avec le terme quadratique « fitted afterwards » (post hoc déclaré dans la phrase) ;
3. la lecture point à point impossible (demi-pas, quatre sur la queue) ;
4. le modèle à deux morceaux, « selected by no penalised criterion (nested F test, AIC and BIC) », paramètres renvoyés à l'artefact ;
5. le verdict « not established on this grid ».

Plus aucun paramètre du modèle écarté n'est imprimé.

---

## 3. J3 — V1, `sec:hydra`

L'incohérence apparente était réelle : γ_M 4,12× → 7,99× (moyennes restreintes, croissant) et médianes KM 5,32× → 3,10× (décroissant) figuraient côte à côte sans lien. Texte ajouté :
- « the ratio of Kaplan–Meier medians moves the other way » ;
- « the ratio of means rises while the ratio of medians falls because the delay laws of the two arms do not keep their shape across magnitudes (Remark~\ref{rem:exponent}), so no single factor describes both, and the anchors above are statements about means ».

C'est une conséquence logique des deux paires publiées (deux familles d'échelle donneraient deux rapports constants). Aucun numéral nouveau.

## 4. J4 — V2, V3, V4

- **V2.** 0,475 ne subsiste qu'une fois : dans `rem:envelope`, comme borne de la plage de grille « [0.475, 0.498] », qui décrit la compression de la grille, pas une rupture. Aucune autre mention (breakpoint, two-piece, Δe*).
- **V3.** Aucune occurrence de « recall stays near 1 » ni de ses variantes dans le manuscrit vivant, ses sections, tables, figures et le README.
- **V4.** Les deux copies du rapport 46 avaient le même SHA-256 (`158f0a6d…`). Celle de `docs/prompts/` est supprimée (`git rm`) ; aucun fichier ne citait son chemin.

## 5. J5 — Table 8

- `\tabcolsep` passe à 4 pt, avec `@{}` aux bords.
- L'en-tête est sur deux lignes : « pre-change / alarms », « detected / in $W$ », « median / delay ».
- Les lignes de données sont inchangées.
- Mesure PyMuPDF : **7,52 pt** (contre 5,78). La Table 7 reste à 7,21 pt.
- Déclaration : `S2TER_I_RECOMPOSED` dans `tests/test_S2ter_predicate.py`, seconde adaptation de même nature que la première, appliquée après elle. Le payload S2ter-I reste à l'état (0, 1) ; le rapprochement avec `family_table_latex()` tient par les lignes verbatim.
- Recensement des payloads identique avant et après le tour.

## 6. J6 — l'export de soumission

**Script `make_submission_export.sh`** (commité sur `main`, il s'exclut lui-même de l'archive).
- Il exporte HEAD par `git archive`, sans `docs/prompts`, `docs/reports`, `docs/theory`, `docs/editorial`, `docs/plans`, `CLAUDE.md`, `**/WRAPUP_*`, les fichiers numérotés par tour (`* - NN - *`) et `results/audit_S7/reconciliation_report.md` (rapport de processus).
- Il échoue si subsiste `\bClaude (Code|Opus)\b|\bOpus\b|CLAUDE\.md|round [H-J]\b|prompt [0-9]{2}\b`. Le motif est restreint pour ne pas bloquer une citation légitime, de Shannon par exemple.
- Taille : 408 Mo.

**Isolation des tests.**
- `test_debt_register.py` saute au niveau du module si le registre est absent.
- `test_S2ter_predicate.py` reçoit un helper `_doc()` pour ses 4 lectures de `docs/theory/`.
- Toutes les autres gardes sautaient déjà.

**Fuites d'identité retirées dans le dépôt** : 12 lignes dans 9 fichiers. Il s'agit de ma ligne du registre des déviations (« Opus prompt 48 », « round I »), de la docstring de `test_S10`, et des mentions « `CLAUDE.md` » de 6 tests et de 2 commentaires d'expériences, devenues « the project conventions » ou « excluded zone ».

**Contrôles depuis l'export seul** (hors dépôt git, `PYTHONPATH` vide).

| contrôle | résultat |
|---|---|
| `pytest tests/` | **172 passés, 15 sautés, 0 échec**. Sauts : 13 documents internes absents (debt register, transferts S2, S2ter, S2bis, S8, S9, S10), 1 hors dépôt git, 1 registre des sources |
| imports | `config.experiment_ssot.__file__` et `ROOT_DIR` sous l'export |
| manuscrit | `tectonic` depuis l'export : 63 pages, zéro référence indéfinie |
| identité | **0** |

**Vocabulaire interne restant dans l'export** (non traité ce tour, arbitrage de l'opérateur).

| motif | lignes | fichiers |
|---|---|---|
| « stream S… » | 89 | 55 |
| « payload » | 215 | 35 |
| renvois `docs/{prompts,reports,theory,editorial,plans}` | 63 | 33 |
| « decision-rules » | 14 | 10 |
| « S2-ter/S2ter » | 7 | 3 |
| « orchestrat » | 8 | 4 — tous légitimes (`run_all.sh`, « orchestrator ») |

Répartition par zone : `experiments/` 40 fichiers, `tests/` 15, `docs/manuscript/` 8, `results/` 7, `config/`, `README.md` et `docs/ENVIRONMENT.md` un chacun. Trois points méritent ton attention :
- **Les commentaires des sources du manuscrit** (« % ── Stream S6 measured constants », « % … stream S1 »), et surtout `protocol_v2.tex:2` : « Answers reviewer #… ». C'est une référence au processus de revue ICDM dans une source livrée.
- **Des champs de JSON commités sous `results/`** (par exemple `rule: "docs/prompts/s3-decision-rules.md :: D1"`) : les nettoyer exige une régénération, pas une édition.
- **L'archive v64 « camera_ready »** est dans l'export (`docs/manuscript/` conservé), et des tests en dépendent (scellé de lignée).

## 7. J7 — portes

| porte | résultat |
|---|---|
| 1. pytest (dépôt) | **191 passed** |
| 2. `sha256sum -c` | **27 OK, 7 FAILED**, ensemble inchangé |
| 3. compilation | sortie 0, **zéro référence indéfinie**, 63 pages |
| 4. recensement | J1–J7 traités, J8 différée |
| 5. `git status --porcelain` | vide après suppression du bac à sable (export compris) |

Gate S13 : deux relances, même SHA (`078a9b4d…`) ; clés existantes et CSV inchangés. Déclaration ajoutée à l'entrée « Stream S13 » de `authorized_deviations.txt`. Commit `5b9af27` sans trailer, **poussé**. **Aucun tag.**

## 8. Ce que je n'ai pas vérifié

- Le seuil de lisibilité imposé par Springer : 7 pt est la cible fixée à ce tour, pas une règle relue à la source.
- Les résultats par blocs et le fit quadratique sur 12 points (§2.2) sont des calculs de session, non commités ; le manuscrit n'en cite aucun.
- La conformité de l'export aux règles d'anonymat de *Machine Learning* : seul le vocabulaire d'identité a été contrôlé, pas les métadonnées (auteurs de fichiers, chemins dans les JSON).

## [Strategic Advice]

**Ta règle de quantification a trouvé sa première cible dans ta propre charge.** Ce n'est pas un reproche : c'est la preuve qu'elle sert. Le réflexe qui reste à installer est de lire un point à point avec ses demi-pas avant de lui donner un nom.

**L'export est désormais le vrai garde-fou de reproductibilité.** La suite y passe et le manuscrit y compile ; le prochain risque n'est plus technique, il est rédactionnel : 89 mentions de streams et un commentaire « Answers reviewer # » dans une source livrée. Décider maintenant ce qu'un évaluateur a le droit de voir coûte moins cher qu'après H10.

**Le gel peut suivre ta validation de R9-A.** Rien d'autre n'est ouvert sur le manuscrit.
