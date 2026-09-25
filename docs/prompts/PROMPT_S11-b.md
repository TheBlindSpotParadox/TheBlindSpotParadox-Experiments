# STREAM S11-b — ASSEMBLAGE v65 DU MANUSCRIT

## Rôle
Instance d'assemblage et intégration. Tu produis le manuscrit v65.

## PRÉCONDITIONS VALIDÉES :
1. Dépôt fusionné sur main (commits S8, S9, S11-a, S2-ter, S10 intégrés), 179 tests réussis, arbre 100 % propre.
2. Revue cible actée : MLJ (Machine Learning Journal, classe Springer `svjour3`).
3. Générateur de record acté : Canonique en record historique, rotation (S8, eta=0.05) en référence d'invariance et de robustesse.
4. S2-ter clos : généralisation Am formulée, table des 7 acceptions de W livrée, payloads (C4) livrés dans transfer_S2ter.md.
5. S10 clos : retard M1/M2 mesuré, figure du double mode livrée, colonnes p0 prêtes, transferts dans S10_transfer.md.

## ORDRE IMPOSÉ DES PHASES :

### Phase 1 — Conversion de classe LaTeX (`IEEEtran -> svjour3`)
- Créer `docs/manuscript/articleA_blindspot_v65_mlj.tex` depuis `articleA_blindspot_v64_camera_ready.tex`.
- Remplacer `\documentclass[10pt,conference]{IEEEtran}` par `\documentclass[smallextended]{svjour3}`.
- Adapter les blocs d'en-tête (commandes auteurs/affiliations `svjour3`, supprimer `\IEEEoverridecommandlockouts` et adapter l'environnement de mots-clés).
- Retirer `\usepackage{cite}` si incompatible avec natbib sous `svjour3`.
- Mettre à jour `tests/test_manuscript_integrity.py` : déclarer la v64 dans `ARCHIVED_MAIN_TEX` et pointer `docs/manuscript/CURRENT` sur la v65.
- Valider la compilation via Tectonic (exit 0).

### Phase 2 — Traitement des 44 sites du registre de dette (`docs/editorial/debt_register.md`)
Traiter par ZONE, jamais au hasard :
1. Les 2 sites `GENERATED` (légende Table I) : mise à jour Python dans `experiments/R4_proteus_evaluation/exp_R4_main_table.py` + régénération locale des tables + mise à jour des hachages dans `results/audit_S7/_baseline/authorized_deviations.txt` et `artifacts_sha256_pre_ssot.txt`.
2. Remplacement des 4 sous-sections `EXCLUDED` : intégrer `docs/manuscript/sections/framework_v2.tex` (qui purge automatiquement les 4 sites exclus).
3. Les 38 sites `editable` : application stricte des corrections répertoriées dans `debt_register.md`.
4. Traitement synchronisé des paires contradictoires (`rem:bgswap` vs `rem:envelope`, et annonce de `M_crit` vs `cor:mcrit`).

### Phase 3 — Application des charges de transfert cumulées
Appliquer les charges SEARCH/REPLACE vérifiées octet par octet :
- S-SYNC (charges différées 5 et 6 : T-A(ii) `res:tension` et T-B arme R1).
- transfer_S8.md (réattribution de \LearnShare à 98.6 %, premier remplacement à 0.71 %, bascule haute).
- transfer_S9.md (KSWIN, condition de contraste, EDDM armement).
- transfer_S2ter.md (payloads S2ter-D à S2ter-I : réécriture de C4, table p0 long-format).
- S10_transfer.md (S10-A multiplicité/Holm, S10-C retard d'étiquetage, S10-D figure dual-mode, S10-E colonnes p0).

### Phase 4 — Titre et Résumé v65
- Adopter le Titre B (ou A avec le sous-titre acté) fermant la disjonction de terminologie.
- Appliquer l'abstract v4 de `thesis_v4.md` §T11a.3 intégrant la décomposition S8 (`\LearnShare` = 98.6 %).
- Définir les 5 macros manquantes dans le préambule (33.5, 19.2, 36.6, 59.3, 31.2).

### Phase 5 — Portes de sortie et validation finale
- `tectonic docs/manuscript/$(cat docs/manuscript/CURRENT)` : exit 0, zéro undefined reference/citation.
- `PYTHONHASHSEED=0 python -m pytest tests/ -q` : 100 % vert.
- `sha256sum -c` : strict respect des déviations autorisées (`comm -3` vide).
- Les 44 ancres du registre de dette vérifiées.
- Arbre de travail Git propre.