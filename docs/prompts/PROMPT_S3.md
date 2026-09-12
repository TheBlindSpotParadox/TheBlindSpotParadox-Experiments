# STREAM S3 — PROPOSITION 9, M_crit, DÉPENDANCE INTER-ARBRES (F24)

## Rôle
Instance secondaire. Tu prends S3 après S2, même chaîne théorique. Tu es
probabiliste : statistiques d'ordre, dépendance, risques concurrents, censure.

## OBLIGATION D'ACCÈS ET COPIE FAISANT FOI
Identiques au prompt S2. Manuscrit vivant :
docs/manuscript/articleA_blindspot_v64_camera_ready.tex. Vérifie `res:tension`.

## À CHARGER
docs/sections/framework_v2.tex
docs/theory/notation_map_v63_to_v2.md  (prop:starvation_boundary MODIFIED,
                                        cor:mcrit VOID)
docs/theory/S6_causal_evidence.md
results/audit_S7/hydra_survival.csv    (RMST, IC, cas complets, par Delta_e)
results/S6_synchronized_traces/data/runs.parquet
results/R9_mcrit/data/                  (tau_HAT, M=1 ; lecture OBLIGATOIRE avec
                                         float_precision='round_trip')

## État du défaut, littéralement
prop:starvation_boundary v63 :
    tau_det* := lambda / (Delta_e - delta_P)          -- DÉTERMINISTE
    P_miss = P(tau_ARF < tau_det*) = 1 - [1 - F(tau_det*)]^M   -- signe « = »
Le paragraphe « Correlation disclaimer » énonce que l'indépendance conditionnelle
rend min_i tau_i stochastiquement plus petit, donc que la formule SURESTIME
P_miss. La direction est correcte. Elle n'est pas démontrée. C'est précisément
l'objection du reviewer #3 : « positive pairwise correlation alone does not
generally establish the claimed independence upper bound ».

## T3.1 — Démonstration de la borne d'indépendance
Voie recommandée, à éprouver et non à recopier :
  - conditionner sur la réalisation COMPLÈTE du flux S ; l'aléa propre à chaque
    arbre (poids de Poisson, tirage de sous-ensembles de variables, bris
    d'égalité) est indépendant entre arbres
  - soit G_S(s) = P(tau_i > s | S) la survie conditionnelle ; par indépendance
    conditionnelle et échangeabilité, P(min_i tau_i > s | S) = G_S(s)^M
  - Jensen sur x -> x^M, convexe sur [0,1] :
        P(min tau_i > s) = E_S[G_S(s)^M] >= (E_S[G_S(s)])^M = (1 - F(s))^M
  - donc P(min <= s) <= 1 - (1 - F(s))^M
CONSÉQUENCE RÉDACTIONNELLE : remplacer « = » par « <= » dans Eq. (pmiss), et
promouvoir le disclaimer au rang de corollaire démontré.
VÉRIFIE L'HYPOTHÈSE D'INDÉPENDANCE CONDITIONNELLE avant de l'utiliser. G2 de S6
rapporte que `model.data[i].rng is model._rng` — River file UN générateur à
travers toute la forêt. Si l'aléa des arbres n'est pas indépendant
conditionnellement au flux, cette voie tombe et il faut la borne de Boole seule.
Ce point est décisif : ne le traite pas par confiance.

## T3.2 — Borne sans hypothèse de dépendance
Fournis en complément la borne de Boole, valide quelle que soit la dépendance :
    P(min_i tau_i <= s) <= min(1, M · F(s))
Deux bornes encadrant P_miss, l'une distribution-free, l'autre sous indépendance
conditionnelle. C'est ce qui rend l'énoncé inattaquable.

## T3.3 — Temps d'arrêt externe aléatoire
Supprime tau_det*. Formule la course comme un modèle de RISQUES CONCURRENTS avec
censure : l'événement d'intérêt est {tau_ARF < tau_det}, la censure administrative
est l'horizon de tolérance. Estimation non paramétrique de la fonction
d'incidence cumulée, bandes de confiance. Intègre sur la distribution empirique
de tau_det disponible en R1/R2.
NOTE MÉTHODE : sous censure administrative unique à horizon commun, Kaplan-Meier
se réduit à la survie empirique et RMST(t_c) = mean(min(tau, t_c)) exactement.
S7 a vérifié cette identité à 9.1e-13 sur 40 cellules. Réutilise le même cadre
plutôt que d'en introduire un autre.

## T3.4 — Taille d'ensemble effective
La formule d'indépendance surestime l'accélération Hydra. Définis
    M_eff = M / (1 + (M-1)·rho_hat)
rho_hat estimé sur la corrélation intra-run des temps de swap. Données : R6
(M=1), R2 (M=10), runs.parquet de S6.
Confronte M_eff au facteur Hydra mesuré sous censure : 4.12x [3.45, 4.96] à
Delta_e = 0.14 et 7.99x [6.40, 9.72] à Delta_e = 0.33, verdict BORNE INFÉRIEURE
(bras ARF non censuré partout). Le ratio des MÉDIANES est divergent : 5.32x et
3.10x. La revendication porte sur des espérances ; un run typique montre ~3x.
Rapporte les deux et dis lequel le manuscrit doit citer.

## T3.5 — Statut de M_crit
ATTENTION, incohérence de statut à lever d'abord : cor:mcrit est marqué VOID
dans docs/theory/notation_map_v63_to_v2.md, mais il est VIVANT dans le manuscrit
de référence, converti à la convention r par S7-bis
(« at the reliability target r = 0.95 », M_crit = 0). Un énoncé void dans la
carte et vivant dans le .tex est exactement le type d'incohérence que le
reviewer #3 a déjà relevé une fois. Tranche, et aligne les deux supports.
NOTE : R9 a été régénéré sous A1 avec R9_DELTA_P = CUSUM_DELTA_P, donc
tau_det* = lambda/(Delta_e - 0.01) et non 0.005. Vérifie que le numéral
F_hat(tau_det*) = 0.49 du manuscrit fait partie des trois numéraux corrigés par
A1 ; s'il ne l'est pas, il est faux.
Deux sorties admissibles :
  a) reconstruction en quantité de conception calibrée empiriquement, encadrée
     par l'enveloppe distribution-free de T3.2, avec intervalle ;
  b) retrait pur et simple, remplacé par la courbe P_miss(M) mesurée.
Contrainte dans les deux cas : la convention de fiabilité est r = 1 - P_miss,
RELIABILITY_TARGETS = [0.99, 0.95, 0.50]. À r = 0.95, M_crit = 0. `beta` est
banni, il a été employé dans deux sens opposés.
Produis la courbe P_miss(M) pour M dans {1, 2, 3, 5, 10, 20, 50} confrontée à la
simulation directe. Si la simulation exige une exécution, écris le prompt Claude
Code et attends validation.

## T3.6 — Contradiction interne sur l'exponentialité (F22)
sec:hydra fonde l'accélération sur les statistiques d'ordre et souligne que
« the M-fold acceleration is exact for exponential F ». Le paragraphe
« Numerical example » rapporte qu'un test KS (N=2000 bootstrap) REJETTE
l'ajustement exponentiel de tau_HAT à toutes les magnitudes (p < 0.05).
L'intuition qui porte la section est réfutée par le test de la section suivante.
Résous.

## T3.7 — Partition du périmètre d'écriture avec S2
S2 et toi écrivez dans le même fichier framework_v2.tex, en parallèle. Partition
imposée, non négociable :
  S2 possède : thm:floor, cor:split, prop:invariance, les instanciations
               R_CUSUM / R_ADWIN / R_KSWIN, prop:order, def:kappa.
  S3 possède : prop:starvation_boundary, cor:mcrit, et tout énoncé nouveau sur
               la dépendance inter-arbres.
Aucun DIFF ne doit ancrer sur un bloc appartenant à l'autre stream, contexte de
3-4 lignes inclus. Si une ancre unique t'oblige à mordre sur la zone de S2,
n'écris pas : remonte l'anchor collision à l'instance primaire.
Travaille dans un git worktree dédié.

## Règle de discipline imposée
Règles de décision numériques fixées et commitées dans docs/prompts/ AVANT
lecture des sorties.

## Livrables
1. DIFF ancrés sur docs/manuscript/articleA_blindspot_v64_camera_ready.tex
2. docs/theory/S3_dependence_bounds.md — les deux bornes, preuves, validation
3. docs/theory/S3_competing_risks.md — modèle, estimation, bandes
4. results/S3/pmiss_vs_M.csv + figure
5. docs/prompts/s3-decision-rules.md
6. Mise à jour de notation_map : lever le statut void
7. Document de transfert d'état

## Porte de sortie
- Aucune hypothèse d'indépendance non justifiée. Hypothèse d'indépendance
  CONDITIONNELLE explicitement vérifiée contre le partage de RNG de River.
- tau_det traité comme temps d'arrêt aléatoire, censure explicite.
- Courbe P_miss(M) validée contre simulation, écart sous tolérance déclarée.
- Statut de cor:mcrit levé, dans un sens ou dans l'autre.
- F22 résolue.

## Format et rédaction
Identiques au prompt S2.