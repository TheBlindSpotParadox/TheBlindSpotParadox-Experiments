# STREAM S11-b — ASSEMBLAGE v65

## Rôle
Instance secondaire, rédacteur et intégrateur. Tu produis le manuscrit v65.
C'est le chantier bloquant du projet depuis cinq tours.

## PRÉCONDITIONS — ne commence pas si l'une manque
  1. S9, S11-a et S8 fusionnés sur main, suite à 154 tests, arbre propre.
  2. Arbitrage MLJ / DAMI rendu.
  3. Générateur de record tranché (canonique ou rotation).
  4. S2-ter clos : le prédicat de point aveugle tranché, l'audit de W fait sur
     les quatre artefacts, (C4) réécrit.
  5. `thesis_v4.md` révisé sur \LearnShare (98.6), (C1) et (C4).
Sans la 4 et la 5, tu assembles un document dont l'énoncé central est périmé.

## ORDRE IMPOSÉ — la conversion de classe PRÉCÈDE l'assemblage
`IEEEtran -> svjour3` d'abord. Ce n'est pas une préférence :
  - elle invalide tout réglage de flottants, donc tout desserrage appliqué sous
    IEEEtran serait à refaire ;
  - elle rend `\usepackage{cite}` inadapté et change le style bibliographique,
    ce qui peut déplacer des clés et rouvrir la garde A6 ;
  - `\IEEEoverridecommandlockouts`, `\IEEEkeywords` et l'environnement
    `IEEEkeywords` n'existent pas sous svjour3 et sont dans
    `STANDARD_ENVIRONMENTS` de tests/test_manuscript_integrity.py ;
  - les trois sections v2 compilent aujourd'hui contre le préambule IEEEtran ;
    la garde `test_sections_assemble_into_the_main_document` suivra la
    conversion, mais seulement si elle est faite d'abord.
Assembler puis convertir, c'est payer deux fois et rouvrir trois gardes.

## ORDRE IMPOSÉ — les 44 sites de dette se traitent PAR ZONE, pas par section
  1. Les 2 sites `GENERATED` (légende Table I) — édition Python PLUS
     régénération, donc une entrée à authorized_deviations.txt et deux hachages
     qui bougent DANS LA MÊME PASSE. `test_manuscript_assets_match_the_pipeline`
     compare les deux copies par SHA-256.
  2. Les 38 sites `editable`.
  3. Les 4 sites `EXCLUDED` — par suppression, quand framework_v2.tex remplace
     les sous-sections. Ne les patche pas : ils disparaissent.
Patcher du texte qui sera supprimé est le gaspillage que cet ordre évite.

## DEUX PAIRES CONTRADICTOIRES, une édition chacune
`rem:bgswap` contre `rem:envelope`, et l'annonce de M_crit contre `cor:mcrit`.
Dans les deux cas une moitié est `editable` et l'autre `EXCLUDED`. Corriger la
moitié accessible seule laisse le document se contredire à l'intérieur de
lui-même — ce qu'il fait déjà aujourd'hui. Traite chaque paire en une passe.

## LES CHARGES À APPLIQUER
  - 2 différées S-SYNC : T-A(ii) à .tex L431, T-B à L314. Elles vivent dans une
    table de rapport que rien n'oblige à relire. Ne les perds pas.
  - transfer_S8.md : réattribution de \LearnShare, causalité du premier swap,
    bascule haute absente, générateur rotation.
  - transfer_S9.md : 8 charges, dont la condition de contraste, la purge de
    l'immunité KSWIN à .tex:500, la colonne d'armement d'EDDM.
  - transfer_S2ter.md si S2-ter en produit.
Re-grep chaque ancre sur le fichier vivant avant application : le document aura
bougé sous la conversion de classe.

## POINTS À RATIFIER, PAS À DÉCOUVRIR
  - `\LearnShare` comme quatrième numéral du résumé : deux lectures défendables
    sont écrites dans thesis_v4.md §T11a.3. Ratifie-en une.
  - Cinq littéraux du résumé sans macro : 33.5, 19.2, 36.6, 59.3, 31.2.
    Cinq `\newcommand` suffisent, sous la règle de source unique qui gouverne
    les 55 autres constantes.
  - `ARCHIVED_MAIN_TEX = set()` à tests/test_manuscript_integrity.py:52 : toute
    v65 déposée fera échouer la suite tant que v64 n'y est pas déclarée. À
    traiter dans la passe de création, pas après.
  - La figure d'ontologie passe de ~55 mm à ~100 mm. Rejoue l'arbitrage espace de
    space_constraints_audit.md contre cette taille.
  - Candidat de titre B : c'est le seul qui ferme la disjonction A8, et la
    condition trois de terminology_map.md n'est plus satisfaite depuis A8 sans
    que la table l'enregistre. Tranche l'incohérence de la carte terminologique.

## PORTE DE SORTIE
  - v65 déposée, CURRENT repointé, ARCHIVED_MAIN_TEX renseigné.
  - `tectonic` exit 0, zéro référence indéfinie, zéro Overfull introduit.
  - Suite complète verte, total mesuré.
  - `sha256sum -c` : les déviations ajoutées, si ajout il y a, égales à
    authorized_deviations.txt (`comm -3` vide).
  - Les 44 sites du registre traités : appliqué, supprimé ou déclaré sans objet,
    chacun avec son statut.
  - Zéro revendication du manuscrit contredite par un artefact du dépôt.