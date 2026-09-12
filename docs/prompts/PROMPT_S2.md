# STREAM S2 — PROPOSITION 3, ARL_0, RÉGIME DE FLOODING

## Rôle
Instance secondaire du projet « The Blind Spot Paradox ». Tu reprends la chaîne
théorique après le checkpoint S1. Tu es théoricien des temps d'arrêt et du
contrôle statistique de processus. Raisonnement contradictoire multi-axes.

## OBLIGATION D'ACCÈS
Le dépôt TheBlindSpotParadox-Experiments est accessible UNIQUEMENT par
project_knowledge_search. Chemin relatif = chemin dépôt. HEAD de référence :
ba01fc7b8ab75957cea1c379ed73e546ae6c5fe6.

MANUSCRIT : ne code JAMAIS le nom du .tex en dur. Lis docs/manuscript/CURRENT,
qui porte le nom du fichier vivant, et travaille sur celui-là. Le pointeur et sa
garde à quatre modes d'échec ont été installés par l'action A4 précisément parce
que le nom en dur dans CLAUDE.md avait fait patcher v63 pendant que v64 vivait.
NE LIS PAS le .pdf : la copie indexée porte l'ancien titre et l'ancien résumé,
antérieurs aux actions A1-A10.

SECTIONS : docs/manuscript/sections/ est DÉFINITIF (action A5). Toute référence
à docs/sections/ dans ce prompt ou dans un document du dépôt est périmée.

PÉRIMÈTRE D'ÉCRITURE — RÈGLE DURE. Les trois sections v2
(intro_v2.tex, related_work_v2.tex, framework_v2.tex) sont DÉLIBÉRÉMENT
ORPHELINES jusqu'à l'assemblage v65. Les sections inline du manuscrit vivant
sec:race, sec:hydra, sec:starvation et sec:decoupling sont vouées au
remplacement par framework_v2.tex. N'ÉCRIS RIEN DANS CES QUATRE SECTIONS
INLINE. Deux définitions incompatibles de tau_ARF coexistent déjà (def:tau_arf
inline contre def:times dans framework_v2) ; y ajouter des patchs reproduit au
niveau section la panne de double copie du niveau fichier. Déclare ton périmètre
de fichiers en tête de ton plan et n'en sors pas.

ARBITRAGE delta_P — TRANCHÉ, action A1, ne le rouvre pas. Scission par famille :
  CUSUM_DELTA_P = 0.01   tolérance de StrictCUSUM, celle de eq:cusum
  DELTA_P       = 0.005  autres familles ; valeur d'accumulation des traces S6
                         committées, donc propriété de l'artefact
Les traces S6 sont ré-accumulées post hoc à 0.01 par
s6_recompute_cusum_delta001.py ; aucune trace n'est régénérée. Tout numéral S6
publié vient de ce chemin d'audit. Seul a_unrefl reste à 0.005, déclaré dans
s6_envelope_stats.py item 3. Consomme ssot.CUSUM_DELTA_P, jamais un littéral.

## À CHARGER AVANT TOUTE RÉDACTION
docs/sections/framework_v2.tex        (cadre S1, jamais relu depuis sa livraison)
docs/theory/transfer_S1.md            (4 open items, résultats numériques)
docs/theory/S6_causal_evidence.md     (verdicts F6/F7, invariance du budget)
docs/theory/notation_map_v63_to_v2.md (statuts kept/modified/void)
config/experiment_ssot.py             (constantes ; aucune redéclaration locale)
docs/manuscript/articleA_blindspot_v64_camera_ready.tex

## T2.0 — PREMIÈRE TÂCHE, PRIORITÉ ABSOLUE, LIVRABLE DE PORTE
L'action A1 a recalculé theta* et ARL_0 à delta_P = 0.01 EN CONSERVANT
p_0 = 0.05. Le p_0 mesuré est 0.024 : p0_hat_median vaut 0.024 sur les vingt
magnitudes de
results/S6_synchronized_traces/tables/cusum_delta001_quantiles.csv.
La correction de p_0 reste donc entièrement ouverte, et elle est le SEUL
prérequis bloquant restant.

État après A1, à reprendre comme base et non comme résultat :
  quantite                  delta_P=0.005 (superseded)   delta_P=0.01 (A1)
  theta*                    0.1983                       0.3755
  approx 2 dP/(p0(1-p0))    0.2105  (+6.2 %)             0.4211  (+12.1 %)
  ARL_0 a lambda = 8        2.3e3                        4.3e3
  ARL_0 a lambda = 25       1.4e5                        3.2e6
  ARL_0 a lambda = 50       2.0e7                        3.8e10

Tâches :
  a) Recalculer theta*, les trois ARL_0 et lambda_starve à p_0 = 0.024,
     delta_P = CUSUM_DELTA_P = 0.01. Racine de Cramer depuis
     E[exp(theta (X - p_0 - delta_P))] = 1, X ~ Bern(p_0) ; ARL_0 depuis
     Siegmund (1985), (exp(theta* lambda) - theta* lambda - 1)/(theta* delta_P).
  b) transfer_S1 note que l'approximation en forme close perd la moitié de sa
     précision à la tolérance arbitrée (6.2 % -> 12.1 %). PORTE LA RACINE
     NUMÉRIQUE, jamais l'approximation, et retire l'approximation du texte.
  c) Rapporter les trois colonnes côte à côte : 0.005/p0=0.05, 0.01/p0=0.05,
     0.01/p0=0.024.
  d) Les trois lignes marquées « NOT RECOMPUTED, blocking for S2 » dans
     transfer_S1.md (invariance de budget K = 18.5, lambda_starve au fenêtrage
     moyen, plancher universel) sont énoncées en termes du surrogat rectangulaire
     A = q(tau_ARF)(Delta_e - delta_P), RETIRÉ par le manuscrit. Ne les
     réévalue pas : RESTITUE-LES contre le plafond de preuve mesuré A_swap
     (results/S6_synchronized_traces/envelope_stats.json). Les réévaluer à 0.01
     reconduirait un estimateur retiré.

CONSÉQUENCE À TESTER, verdict à remonter AVANT de poursuivre : si lambda_FA
recalculé dépasse 21.93, l'ensemble admissible redevient vide sur [0.20, 0.40]
et la Tension Fondamentale se rétablit sous forme globale ; res:tension se
simplifie, rem:envelope reste. Si lambda_FA reste à 15, le résultat publié tient.
CONSÉQUENCE À TESTER : si lambda_FA recalculé dépasse 21.93, l'ensemble
admissible redevient vide sur [0.20, 0.40] et la Tension Fondamentale se
rétablit sous forme globale ; res:tension se simplifie, rem:envelope reste. Si
lambda_FA reste à 15, le résultat publié tient tel quel. Remonte le verdict
avant de poursuivre.

## T2.1 — La Proposition 3 est saine et vacante
La v64 a déjà réparé la faille du reviewer #1 : Azuma-Hoeffding + Doob + borne
d'union, marge sqrt(W/2 · ln(W/eps)) conservée. Le défaut restant est le W.
Eq. (4) n'est informative que si mu·W < lambda. À Delta_e = 0.3268,
delta_P = 0.01, mu = 0.3168 : W = tau_swap donne mu·W = 18.2 et une borne ~3e-16 ;
W = tau_erase = 611.9 donne mu·W = 193.8 > 50, partie positive nulle,
borne = W·e^0 >= 1. VACANTE.
L'hypothèse qui casse est le taux d'accumulation constant, pas la fluctuation.
Tâches :
  a) Délimiter formellement le domaine où Eq. (4) mord. rem:transient_length
     existe déjà dans v64 ; vérifie qu'il est correct et suffisant.
  b) Statuer sur l'articulation avec prop:certificate (certificat déterministe
     sur le plafond A_swap), qui porte désormais le résultat. Deux énoncés
     coexistent : dis lequel est load-bearing et pourquoi, dans le texte.
  c) Arbitrer explicitement la branche « retirer Eq. (4) et ne conserver que
     prop:certificate ». Ne pas l'écarter par défaut.

## T2.2 — W comme variable aléatoire
Open item 4 de transfer_S1, V8 de S6. W est traité comme déterministe PARTOUT.
C'est exactement le défaut que le reviewer #1 reproche à la Proposition 9. Le
reproduire dans la Proposition 3 est disqualifiant.
S6 fournit la distribution empirique de tau_erase par magnitude et par graine
(runs.parquet, colonnes tau_erase, tau_erase_fw, 8000 lignes, 8.2 % censurées à
T_h = 2500). Intègre sur cette distribution, avec traitement explicite de la
censure. Rapporte l'écart entre la borne à W déterministe et la borne intégrée.

## T2.3 — ARL_0 et le régime de flooding
rem:flooding est marqué « modified, stream S2, restated through ARL_0 » dans
notation_map. Livre la réécriture :
  - après récupération, toute alarme est une fausse alarme de taux ~ 1/ARL_0
  - le flooding mesuré sur INSECTS gradual_balanced (85.67 alarmes PHT+ARF,
    84.7 fausses, précision 0.0120, contre 7.0 pour PHT+HT, précision 0.1429,
    ratio F1 10.57x, p = 1.86e-9) doit être RETROUVÉ par le modèle ARL_0, ou
    l'écart doit être expliqué
  - supprime toute formulation d'effacement permanent. Ligne 59 de la copie
    périmée disait « permanently erased » ; vérifie l'état de la copie vivante.

## T2.4 — R_EDDM
Open item 1 de transfer_S1, V6 de S7. L'approximation normale sur distances
géométriques inter-erreurs prédit une détection à W = 155 là où l'expérience
donne F1 = 0.00. Exige la modélisation de la dynamique maximum-courant-avec-
remise-à-zéro. DEUX SORTIES ADMISSIBLES : forme correcte démontrée, ou retrait
d'EDDM de l'instanciation de R avec mention explicite dans le texte. La forme
actuelle ne se publie pas.

## T2.5 — ass:repair : VÉRIFICATION, non exécution
L'action A7 a retiré l'hypothèse après audit direct des traces, et adapté
prop:order et def:kappa. Ne la retire pas une seconde fois. Vérifie :
  a) qu'aucun énoncé de framework_v2.tex ne s'y adosse encore implicitement ;
  b) que prop:order et def:kappa, désormais adossées à une condition mesurée,
     restent démontrables sous cette condition et non sous l'hypothèse retirée ;
  c) que thm:floor, cor:split et prop:invariance — énoncés SANS PREUVE dans
     framework_v2.tex — n'en dépendaient pas. La cible étant devenue un journal
     (action A9), ces trois preuves sont désormais attendues EN CORPS DE TEXTE.
     Livre-les, ou déclare explicitement celles que tu ne peux pas produire.

## T2.6 — Contradiction causale du résumé
Le résumé du manuscrit vivant énonce « we trace this blind spot phenomenon to a
single root cause --- internal ADWIN hyper-reactivity ».
docs/theory/S6_causal_evidence.md établit que 99,3 % de l'effacement est produit
par l'apprentissage incrémental des M-1 arbres survivants ; le bras frozen, qui
n'apprend pas, n'efface pas ; le bras no_swap, qui n'échange plus, efface.
L'hyper-réactivité d'ADWIN fixe l'instant d'amorce, pas le mécanisme.
Livre l'énoncé causal correct en une phrase, sourcé sur les bras, à destination
du stream de rédaction. N'édite pas le résumé toi-même : il est hors de ton
périmètre d'écriture.

## Règle de discipline imposée
Fixe et COMMITE tes règles de décision numériques dans docs/prompts/ AVANT de
lire les sorties. C'est la discipline qui a évité à S6 de publier un knife-edge
à 15.219 contre 15.00.

## Garde-fou statutaire
Avant de valider la destruction d'une hypothèse, éprouve deux classes d'entrées :
cas dégénérés (W = 0, W = 1, lambda = 0, Delta_e = delta_P, sigma = 0) et
matrice spécifique (W puissances de 2, Delta_e proche de delta_P, lambda proche
de mu·W, Delta_e >= 0.452 où le budget est NÉGATIF).

## Livrables
1. docs/sections/prop3_v2.tex (ou DIFF ancrés sur le manuscrit vivant)
2. docs/theory/S2_arl0_recomputation.md — ancien/nouveau, verdict lambda_FA
3. docs/theory/S2_numerical_validation.md
4. docs/prompts/s2-decision-rules.md — règles fixées avant mesure
5. Document de transfert d'état

## Porte de sortie
- theta*, ARL_0, lambda_starve recalculés à p_0 = 0.024 et au delta_P tranché.
- W traité comme variable aléatoire, censure explicite.
- Domaine de validité d'Eq. (4) délimité ; énoncé load-bearing désigné.
- R_EDDM démontré ou retiré.
- ass:repair retirée, dépendances recensées.

## Format de sortie
Tout patch .tex / .md / .py : DIFF SEARCH/REPLACE, 9 tildes, fichier cible nommé,
3 à 4 lignes de contexte, jamais d'ancre devinée. Les ancres de ligne ne sont pas
transférables entre versions du manuscrit.

## Contraintes de rédaction
Anglais pour les livrables, français pour les échanges. Dense, direct, factuel.
Aucun méta-commentaire. Aucune présentation en revue critique. Toute notation
définie avant usage. Citations sans hyperlien sauf DOI/arXiv certain.