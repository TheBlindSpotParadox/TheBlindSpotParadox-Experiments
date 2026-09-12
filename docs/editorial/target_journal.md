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
5. **Résumé — réécrit dans le même lot, ne reste que la longueur.** Le contenu périmé est purgé
   (actions A8/A9 puis M1) : l'ensemble admissible est désormais énoncé vide *sous* le plancher
   mesuré et non vide au-dessus, KSWIN est qualifié d'observation restreinte au régime testé et
   non d'immunité, et la revendication de cause unique est remplacée par la décomposition
   onset / effacement / verrou. 339 mots aujourd'hui contre 254 avant le lot : la contrainte de
   longueur conférence est levée, mais un résumé de journal reste à calibrer sur les limites de
   la revue retenue, seul point encore ouvert sur ce bloc.

## Contrainte d'ordonnancement — la conversion de classe précède l'assemblage (M8)

**`IEEEtran → svjour3` doit être faite AVANT l'assemblage v65, pas après.** Ce n'est pas une
préférence de séquence, c'est une dépendance :

- elle invalide tout réglage de flottants — largeurs `figure*`/`table*`, `\columnsep`, placement —
  donc tout desserrage appliqué sous IEEEtran serait à refaire ;
- elle rend `\usepackage{cite}` inadapté : Springer n'emploie pas la compression `[1]-[3]`, et la
  bibliographie change de style (`spbasic`/`spmpsci` contre `IEEEtran`), ce qui peut déplacer des
  clés et rouvrir la garde A6 ;
- `\IEEEoverridecommandlockouts`, `\IEEEkeywords` et l'environnement `IEEEkeywords` n'existent pas
  sous `svjour3` : ils sont dans `STANDARD_ENVIRONMENTS` de
  `tests/test_manuscript_integrity.py`, qui devra être révisé dans le même mouvement ;
- les trois sections v2 compilent aujourd'hui contre le préambule IEEEtran. La garde
  `test_sections_assemble_into_the_main_document` les vérifie contre le document principal : elle
  suivra automatiquement la conversion, mais seulement si la conversion est faite d'abord.

Assembler puis convertir signifie payer deux fois le desserrage et rouvrir trois gardes. Convertir
puis assembler ne coûte qu'une passe.

## Ce que ce document ne tranche pas

- **Le choix final entre MLJ et DAMI — escaladé, bloquant pour la séquence ci-dessus.** La
  conversion de classe ne peut pas commencer sans lui, et l'assemblage ne peut pas commencer sans
  la conversion. C'est donc le premier arbitrage du Lot 3, pas un détail de forme. Il commande
  aussi la limite de mots du résumé, seul point resté ouvert sur ce bloc.
- Le sort de l'étiquette `ICDM 2026`, encore affirmée dans 12 fichiers du dépôt
  (`config/experiment_ssot.py`, `exp_R5_config.py`, `run_all.sh`, les 9 `run_experiment_R*.sh`).
  Elle est factuellement périmée dès la présente action ; la correction est un `sed` d'une ligne,
  laissée en attente d'instruction plutôt qu'appliquée unilatéralement.
