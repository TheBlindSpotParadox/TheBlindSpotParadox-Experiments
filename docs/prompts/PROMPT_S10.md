# STREAM S10 — VALIDITÉ EXTERNE, DOUBLE MODE, RETARD D'ÉTIQUETAGE

## Rôle
Instance secondaire, ingénieur de campagne. Tu fermes le dernier volet
expérimental avant l'assemblage.

## OBLIGATION D'ACCÈS ET BASE
Identiques au prompt S2-ter. Vérifie 154 tests avant de commencer.

## À CHARGER
docs/theory/S9_detector_coverage.md, transfer_S9.md, transfer_S8.md
docs/editorial/thesis_v4.md §T11a.5 (cadrage de la Table I)
results/S9_detector_coverage/, results/S8_rotation_generator/
experiments/S6_synchronized_traces/ (harnais), experiments/R5_real_world_evaluation/

## CE QUI EST DÉJÀ ACQUIS, À NE PAS REFAIRE
  - BAF est un contrôle négatif PROUVÉ : l'erreur du modèle gelé égale le taux de
    fraude BAF bit pour bit sur les trois variantes (0.010985555, 0.011005555,
    0.010981111). L'arbre gelé est un prédicteur de classe majoritaire pur. Aucun
    pipeline à base de Hoeffding Tree n'acquiert de signal.
  - L'oracle Δe est INUTILISABLE sur INSECTS au préchauffage prescrit.
  - Le flooding INSECTS tombe de 10.570 à 1.270 au budget de portée (89.9 % du
    log-ratio attribuable au seuil sur la variante gradual).
  - Le nul de ProteuS est DEGENERATE, prouvé sur le générateur, 24 combinaisons.

## T10.1 — Sensibilité au retard d'étiquetage
Jamais mesurée, et c'est la dernière objection opérationnelle non traitée. Le
détecteur externe lit un flux d'erreur qui exige des étiquettes. Mesure l'effet
d'une latence l sur le taux de détection et sur le budget disponible, pour
l ∈ {0, 10, 50, 100, 500} pas, sur au moins deux flux dont un à nul non dégénéré.
Prédiction à écrire AVANT mesure : la latence décale τ_det de l et ne décale pas
τ_erase, donc elle réduit mécaniquement la fenêtre exploitable. Vérifie-la.

## T10.2 — Le double mode, énoncé sur une grandeur unique
La taxonomie de l'article oppose famine et inondation. Les deux sont désormais
des faits de placement du seuil par rapport au budget disponible. Produis la
figure unique qui porte les deux régimes sur un même axe — seuil en abscisse,
rappel et précision en ordonnée — avec la fenêtre admissible surlignée, sur au
moins trois flux. C'est la figure qui remplace la dichotomie par une courbe.

## T10.3 — Flux réels à ruptures multiples
INSECTS complet plutôt que trois variantes. Rapporte pour chaque flux le socle
d'erreur p0 : c'est la colonne sans laquelle l'ordonnancement des familles
ordonne des flux et non des familles (S9 D9).

## T10.4 — Correction pour comparaisons multiples, portée élargie
La correction de Holm à α = 0.05 ne conserve pas INSECTS abrupt_balanced
(p = 0.043 contre α/2 = 0.025). Applique la même correction à la famille élargie
par ce stream, et rapporte ce qui ne survit pas. Une affirmation retirée par une
correction déclarée vaut mieux qu'une affirmation conservée sans correction.

## PÉRIMÈTRE
Écriture : experiments/S10_*/, results/S10_*/, docs/theory/S10_*.md,
           tests/test_S10_*.py, bloc SSOT append-only banneré `# S10 —`
Interdit : toute écriture sous results/S6_*, results/S8_*, results/S9_*,
           results/R*_*, et toute entrée nouvelle à authorized_deviations.txt

## PORTE DE SORTIE
- Sensibilité au retard mesurée sur >= 2 flux, prédiction confrontée.
- Figure du double mode livrée sur >= 3 flux.
- p0 rapporté pour chaque flux réel.
- Correction multiple appliquée, retraits déclarés.