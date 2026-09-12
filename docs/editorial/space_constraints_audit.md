# Audit des compressions d'espace — Action A9

Inventaire des artifices introduits pour tenir le format 8 pages d'ICDM 2026, à desserrer lors de
l'assemblage v65. Cible retenue : `docs/editorial/target_journal.md`.

Méthode : balayage de `docs/manuscript/articleA_blindspot_v64_camera_ready.tex` sur les commandes
d'ajustement de mise en page, les commentaires invoquant une contrainte d'espace, les réglages de
longueur et de fonte, et les tells indirects (contenu déporté en note, flottants fusionnés,
résumé calibré).

## 1. Ce qui est absent — le manuscrit est propre sur ce plan

Vérifié, aucune occurrence :

| artifice recherché | occurrences |
|---|---|
| `\enlargethispage` | 0 |
| `\vspace`, `\vskip`, sauts négatifs `\\[-…]` | 0 |
| `\setlength` sur `\textfloatsep`, `\floatsep`, `\intextsep`, `\columnsep`, `\abovedisplayskip`, `\belowdisplayskip` | 0 |
| `\linespread`, `\baselinestretch` | 0 |
| Réduction de fonte locale (`\footnotesize`, `\small`) pour faire tenir un bloc | 0 |

Les trois `\smallskip` (lignes 372, 380, 383) séparent les points (i), (i-bis) et (ii) de la
Définition 11 : ils sont structurels, pas compressifs. À conserver.

## 2. Ce qui est présent — à desserrer

### 2.1 Figure 4 fusionnée dans la Figure 2 — POINT DUR

`articleA_blindspot_v64_camera_ready.tex:292`, entre les sous-sections `sec:hardware` et
`sec:complexity` :

```latex
% Figure 4 merged with Figure 2 above to respect ICDM page limits.
```

Seule compression déclarée explicitement dans le fichier. La figure absorbée portait le régime
« désaccord d'horloge » (R7) ; elle est aujourd'hui indistincte des trois panneaux
`fig:pht_scenarios`. Le desserrage impose de régénérer une figure R7 autonome depuis
`results/R7_clock_mismatch/` — l'artefact existe, la figure séparée non.

### 2.2 Contenu méthodologique déporté en note de bas de page

Trois notes, dont deux portent des décisions méthodologiques qui appartiennent au corps :

| ligne | taille | contenu |
|---|---|---|
| 463 | 598 car. | Les trois calibrations de la PHT — `λ ∈ {8, 25, 50}` pour la sensibilité au seuil, `λ = 25` comme point neutre du croisement, `λ = 15` comme seuil opérationnel ProteuS — et la procédure de calibration « une fausse alarme par fenêtre de chauffe » |
| 489 | 410 car. | Critères d'exclusion de deux variantes INSECTS : `incremental_balanced` sans position de dérive discrète, `incremental_abrupt_balanced` écartée comme transition vers une tâche plus facile |
| 447 | 286 car. | Motif du report d'EDDM plutôt que DDM sous les seuils par défaut de River |

Les deux premières sont des choix de protocole : en format journal elles remontent en corps de
texte, la troisième peut rester en note.

### 2.3 Résumé calibré conférence

254 mots, un seul paragraphe. Contrainte de longueur levée. Indépendamment du format, son contenu
est périmé : il annonce encore un ensemble admissible vide et une immunité KSWIN que les streams
S6 et S7-bis ont retirées. Réécriture à traiter comme une action distincte, pas comme un
desserrage typographique.

### 2.4 Compression native des citations

`articleA_blindspot_v64_camera_ready.tex:5` charge `\usepackage{cite}`, qui condense les listes de
références (`[1]-[3]` plutôt que `[1],[2],[3]`). C'est une convention IEEE, pas un artifice ICDM,
mais elle est dépendante du format cible : Springer ne l'emploie pas. À réexaminer à la conversion
de classe, pas avant.

*(Le commentaire de cette ligne est en français dans un fichier source, contrairement à la
convention du dépôt. Signalé, non corrigé : hors périmètre A9.)*

## 3. Non mesuré

Le nombre de pages compilé n'a pas pu être extrait : le PDF produit par Tectonic 0.17.0 utilise
des flux d'objets compressés et aucun outil d'extraction n'est disponible dans les environnements
`Trading` ou `tex`. Il est consigné comme non mesuré plutôt qu'estimé. À relever manuellement
avant de dimensionner le desserrage.

## 4. Portée

Cet audit n'applique aucun desserrage. Il n'existe que pour que l'assemblage v65 n'ait pas à
redécouvrir ces points — en particulier §2.1, dont la seule trace est un commentaire d'une ligne
qu'une relecture rapide ne voit pas.
