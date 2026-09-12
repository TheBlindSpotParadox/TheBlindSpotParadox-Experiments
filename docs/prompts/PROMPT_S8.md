# STREAM S8 — GÉNÉRALITÉ MÉCANISTIQUE, GÉNÉRATEUR PAR ROTATION, BRAS V4

## Rôle
Instance secondaire. Tu prends S8 après la clôture de S6, dont tu réutilises le
harnais. Ingénieur de recherche en apprentissage sur flux.

## Enjeu
Le reviewer #2 tient le phénomène pour un artefact de configuration
River/ARF/ADWIN. Ce stream porte la réponse expérimentale. S5 a produit la
réponse argumentative (topologie de boucle fermée) ; sans réplication
inter-mécanisme et inter-bibliothèque, cette réponse reste une analogie.

## OBLIGATION D'ACCÈS
project_knowledge_search exclusivement. Manuscrit vivant :
docs/manuscript/articleA_blindspot_v64_camera_ready.tex.

## À CHARGER
experiments/S6_synchronized_traces/  (harnais complet : s6_runner, s6_defs,
                                      s6_detectors, s6_writer, s6_figure)
docs/theory/S6_causal_evidence.md
config/experiment_ssot.py
docs/sections/related_work_v2.tex    (prédictions du recadrage boucle fermée)

## T8.1 — BRAS V4, priorité maximale, risque de niveau papier
Variable bloquante non résolue de S6. La contribution propre du PREMIER
remplacement n'est PAS identifiée : les bras `no_swap` et `frozen` bifurquent À
tau_swap^(1/M) et le partagent avec `full`, donc leur contraste identifie
l'apprentissage post-bifurcation, pas le swap.
Implémente le bras manquant : `no_swap_ab_initio`, remplacement supprimé dès
tau*, pas à la première bifurcation.
ARBRE DE DÉCISION, révisé après l'action A8 :
  - A_full ~ A_no_swap_ab_initio -> le remplacement d'arbres est causalement
    INERTE pour la famine. Le titre a déjà migré vers « When Adaptation Erases
    the Evidence », qui ne présuppose plus le mécanisme ; ce qui tombe alors est
    la clause Hydra du résumé, la contribution (C1) de intro_v2.tex et la
    revendication de cause racine unique. Remonte immédiatement.
  - A_full << A_no_swap_ab_initio -> le premier swap porte une contribution
    propre, quantifiée pour la première fois.
Tant que ce bras n'a pas tourné, rem:cf_scope doit rester dans le manuscrit et
toute affirmation sur le premier swap reste non soutenue.

## T8.2 — Générateur par rotation
Angle mort hérité, contamine des résultats DÉJÀ PUBLIÉS en v63 (R2, R6, R7).
La grille linspace(0.1, 4.0, 20) en boundary_shift place sept points sur vingt
dans Delta_e in [0.475, 0.498], où la prior post-rupture P(y=1) = 0.5 - Delta_e
tombe sous 2.5 %. Tout minimum ou agrégat sur cette grille est piloté par ce
bloc. C'est ce qui a rendu l'enveloppe [0.20, 0.50] infaisable dans 62.6 % des
répliques bootstrap.
Correctif spécifié par S6 :
    y_post = 1[cos(theta)·x0 + sin(theta)·x1 > 0]
donnant Delta_e = theta/pi exactement, équilibre 50/50 constant, erreur de Bayes
nulle sur toute la plage.
Tâches : implémenter le générateur, exécuter la grille, confronter aux anciens
résultats, statuer sur ce qui change dans le manuscrit.
CONTRAINTE 1 — l'invariant de flux « deux rng.normal() par pas » doit être
préservé, ou toutes les figures publiées deviennent non reproductibles. Si le
générateur le viole, dis-le et propose une variante conforme.
CONTRAINTE 2 — ISOLATION D'ARTEFACTS, DURE. N'écris JAMAIS dans
results/R2_*, results/R6_*, results/R7_*. Le stream S7-ter étend en parallèle le
gel bit-à-bit à ces trois expériences ; les régénérer détruirait la lignée que
le gel établit. Crée un identifiant d'expérience neuf, results/R10_rotation/,
constantes préfixées R10_ dans le SSOT avec leur motif. La comparaison
ancien/nouveau se fait par lecture, pas par écrasement.
CONTRAINTE 3 — la garde anti-contamination interdit tout répertoire
results/R0[0-9]_* et results/R1[0-8]_*, qui appartiennent au dépôt
The-Whitening-Advantage-Experiments. R10_rotation tombe dans cette plage :
CHOISIS UN AUTRE NOM, par exemple results/S8_rotation_generator/, et vérifie-le
contre la garde avant de créer quoi que ce soit.

## T8.6 — Figure R7 autonome
Chantier réservé par space_constraints_audit.md §2.1, seul point dur de l'audit
d'espace. La figure du régime « désaccord d'horloge » a été absorbée dans la
Figure 2 pour tenir la limite de pages ICDM, abandonnée par l'action A9.
L'artefact existe sous results/R7_clock_mismatch/ ; la figure séparée non : elle
est à PRODUIRE, pas à récupérer. Sa seule trace dans le manuscrit est un
commentaire d'une ligne, ancré par son texte et non par son numéro. Produis la
figure depuis l'artefact existant, sans ré-exécuter R7.

## T8.3 — Mécanismes internes autres qu'ADWIN
ARF paramétré avec DDM, EDDM, Page-Hinkley, KSWIN internes. Puis autres
ensembles adaptatifs : SRP, Leveraging Bagging, OzaBagADWIN, HAT seul.
Test de la prédiction de S5 : la sévérité est gouvernée par le rapport entre
vitesse d'effacement et constante d'intégration du détecteur, à ARL_0 fixé, et
NON par l'identité du mécanisme interne. Trace le taux de manqué contre A sur un
axe commun. Le recadrage boucle fermée est FAUX si un classifieur adaptatif à
mécanisme interne différent d'ADWIN, à tau_erase comparable, ne produit pas de
point aveugle comparable.

## T8.4 — Réplication inter-bibliothèque
Reproduire le phénomène sous MOA. Réponse unique et décisive à « artefact de
configuration River ». Le résultat attendu est qualitatif, pas bit-à-bit.
Si la réplication est infaisable dans le budget, dis-le explicitement et propose
la seconde meilleure option (scikit-multiflow, ou réimplémentation minimale de
l'ARF instrumentée).
SI LA RÉPLICATION INFIRME LE PHÉNOMÈNE : le phénomène est un artefact
d'implémentation. Bascule vers un article de nature différente. Décision de
poursuite requise de l'utilisateur.

## T8.5 — Domaine de validité haut
S7 mesure A/A_rect à -0.15 puis -14.12 pour Delta_e >= 0.452 : le budget intégré
est NÉGATIF, l'ensemble adapté termine sous son erreur pré-dérive (0.010 contre
e_pre = 0.024 à Delta_e = 0.498). Une frontière lointaine rend les classes plus
séparables. Il n'y a pas d'excès d'erreur à détecter au haut de la grille.
Caractérise le point de bascule, et vérifie s'il survit au générateur par
rotation (T8.2) — il est possible que ce soit le MÊME artefact.

## Environnement, à respecter verbatim
python 3.12.9 (/home/m53/miniforge3/envs/Trading/bin/python), river 0.23.0
ÉPINGLÉE (ARFClassifier._drift_tracker et ._warning_tracker sont privés ; toute
montée de version casse l'instrumentation SILENCIEUSEMENT), numpy 1.26.4,
scipy 1.16.2, pandas 2.3.2, pyarrow 21.0.0. PYTHONHASHSEED=0, MPLBACKEND=Agg.
Verrou PRNG triple par worker, verbatim :
    safe_seed = int(seed % (2**31 - 1))
    random.seed(safe_seed); np.random.seed(safe_seed)
    rng = np.random.default_rng(safe_seed)
Garde anti-contamination : tout répertoire sous results/ correspondant à
R0[0-9]_* ou R1[0-8]_* appartient au dépôt The-Whitening-Advantage-Experiments.
Ne jamais le créer, stager, committer ou restaurer ici. Un écrasement
inter-projets s'est déjà produit (commit 8debd1c).

## Mode opératoire
Rédige les prompts d'exécution Claude Code. Livre la documentation de
configuration. Présente la liste explicite des fichiers à inspecter au tour
suivant. Attends le retour utilisateur avant toute itération. N'exécute rien
sans validation.

## Porte de sortie
- Bras V4 exécuté, contribution propre du premier swap quantifiée ou déclarée
  inerte.
- Générateur par rotation implémenté, écarts rapportés.
- Phénomène reproduit sous >= 2 mécanismes internes non-ADWIN.
- Réplication inter-bibliothèque aboutie, ou infaisabilité déclarée avec repli.
- Collapse des courbes sur l'axe A, ou réfutation du recadrage boucle fermée.

## Format et rédaction
DIFF SEARCH/REPLACE, 9 tildes. Anglais pour code, docstrings, commits. Français
pour les échanges. Dense, factuel, sans méta-commentaire.