# Cible de publication — Action A9

**Tranché.** La cible éditoriale est le **Journal Track ECML PKDD**, en soumission directe à
**Machine Learning (Springer, MLJ)** ou **Data Mining and Knowledge Discovery (DAMI)**.

La contrainte des 8 pages est **abandonnée définitivement**. Elle appartenait à la soumission
ICDM 2026 et n'a plus de portée.

## Motif

Le volume théorique et expérimental consolidé l'exclut :

| bloc | ce qu'il porte |
|---|---|
| Cadre formel | `docs/manuscript/sections/framework_v2.tex` — 8 énoncés numérotés, dont un théorème de plancher universel et un corollaire de séparation par famille de détecteur, actuellement sans preuves complètes |
| Traces S6 | 100 graines × 20 magnitudes × 4 bras, 402 Mo de trajectoires synchronisées ; le certificat `prop:certificate`, le plancher `Δe_c = 0.120 [0.114, 0.127]` et l'enveloppe `λ_op = 21.93 [19.88, 22.40]` en sortent |
| ProteuS | Table I, flux ARMA–GARCH hétéroscédastiques, plus un balayage de sensibilité KSWIN sur quatre valeurs d'α |
| Réel | Table II — 3 variantes BAF, 3 variantes INSECTS, avec la décomposition famine / inondation |
| Ablations | R6 facteur Hydra, R7 désaccord d'horloge, R8 sensibilité à la chauffe, R9 taille critique d'ensemble |

Neuf pipelines expérimentaux, 1 h 58 de reproduction mesurée hors R5 (`docs/ENVIRONMENT.md`).

## Implications structurelles pour l'assemblage v65

1. **Réintégration des preuves complètes.** `framework_v2.tex` énonce sans démontrer. `prop:order`
   est désormais adossée à une condition mesurée (action A7) ; `thm:floor`, `cor:split` et
   `prop:invariance` restent à démontrer en corps de texte plutôt qu'en annexe compressée.
2. **Séparation en sections dédiées.** Les trois sections v2 (`intro_v2`, `related_work_v2`,
   `framework_v2`) existent sous `docs/manuscript/sections/` et sont **délibérément orphelines**
   jusqu'à l'étape d'assemblage. Elles compilent contre le préambule actuel sans erreur dure
   (garde `tests/test_manuscript_integrity.py::test_sections_assemble_into_the_main_document`).
3. **Suppression des compressions graphiques.** Inventaire exhaustif dans
   `docs/editorial/space_constraints_audit.md`. Le point dur est la fusion de la Figure 4 dans la
   Figure 2, déclarée en commentaire dans le `.tex`.
4. **Contenu déporté en note de bas de page à remonter.** Trois notes, dont une de 598 caractères
   portant les trois calibrations de λ et une de 410 caractères portant les critères d'exclusion
   INSECTS. Ce sont des choix méthodologiques, pas des apartés.
5. **Résumé.** 254 mots aujourd'hui, calibré sur un format conférence. Il annonce encore un
   ensemble admissible vide et une immunité KSWIN que le corpus a retirées ; sa réécriture est
   indépendante de la cible mais conditionnée par elle en longueur.

## Ce que ce document ne tranche pas

- Le choix final entre MLJ et DAMI.
- Le format exact (Springer `svjour3` contre la classe IEEEtran actuelle), qui imposera une
  conversion de préambule et invalidera les réglages de flottants.
- Le sort de l'étiquette `ICDM 2026`, encore affirmée dans 12 fichiers du dépôt
  (`config/experiment_ssot.py`, `exp_R5_config.py`, `run_all.sh`, les 9 `run_experiment_R*.sh`).
  Elle est factuellement périmée dès la présente action ; la correction est un `sed` d'une ligne,
  laissée en attente d'instruction plutôt qu'appliquée unilatéralement.
