[Saturday, September 26, 2026]

# PROMPT POST R8 · I1–I9 EXÉCUTÉS SOUS FORME CORRIGÉE · UNE INVALIDATION À CONFIRMER · H10 EN ATTENTE DE DEUX DÉCISIONS

---

## 1. État des lieux

Ton plan du « 2026 09 26 - 48 » est exécuté de I1 à I9 ; **I10 (H10) est différée** par arbitrage de l'opérateur. 190/190 tests, `sha256sum -c` à 27 OK / 7 FAILED (ensemble autorisé inchangé), v65 compilée sous Tectonic : 63 pages A4, zéro référence non résolue. Commit local sur `main`, sans push. Le document n'est **pas figé** : il attend ta validation des écarts ci-dessous.

Mon rapport d'exécution et de revue critique est dans ta mémoire de projet : **`docs/reports/2026 09 26 - 50 - R8 execution and critical review response to Opus.md`**. Chaque chiffre y porte le fichier commité d'où il sort. La formulation E5 est versée dans `docs/prompts/2026 09 26 - 49 - E5 INSECTS arbitration original formulation.md` (I8).

**Aucune des cinq charges R8 n'était applicable telle quelle** ; toutes sont appliquées sous une forme corrigée, avec preuve (rapport 50, §2).
- **R8-A** : attribution causale et préférence de modèle contredites par le gate.
- **R8-B** : « 0,24 » n'est pas le pic (0,333) ; le remède était déjà publié et ta charge l'aurait dupliqué ; l'axe p₀ est faux sur ProteuS et contredit `rem:flooding`.
- **R8-D** : réintroduisait l'affirmation non restreinte que S2ter-B restreint, et visait une référence `sec:coverage` inexistante.
- **R8-E** : « less well than the family-specific pair » est faux, les deux prédicats coïncident sur les 3 960 cellules.
- **I5** : S9-F est appliqué sous la forme S2ter-B ; aucune de tes deux branches.

## 2. Une invalidation empirique fermée, à confirmer

Je ne présente pas une autre lecture de R-8 : je te présente une **invalidation mesurée, fermée, qui appelle ta confirmation**.

**Le modèle segmenté de R-8 n'est préféré par aucun critère qui pénalise son paramètre supplémentaire** (`s13_gate.json :: tau_segmented.post_hoc`).
- F(1,15) = 0,85, **p = 0,37**, test anti-conservateur puisque la rupture est cherchée sur la grille.
- AIC −93,19 (un morceau) contre −92,18 (deux morceaux).
- BIC −91,41 contre −89,51.

**Le « plancher » qui le motivait n'existe pas** dans les données.
- Les six médianes 31, 31, 29,5, 29, 29, 29 baissent de 6,5 % là où une loi en −2 prédit 6,1 %.
- Leur pente MCO vaut −2,58.

**L'inclusion de −2 dans l'intervalle de flanc est un produit de l'incertitude de la rupture.** Rupture fixée à son estimation, l'intervalle vaut [−1,948 ; −1,714] et exclut −2.

**Conséquences déjà appliquées** (rapport 50, §3).
- `rem:exponent` ne porte plus aucune affirmation de plancher. Le verdict « not established » est conservé, avec son vrai motif : la grille ne départage pas les deux modèles.
- R7-C et R7-D sont retirées.
- S13-G est restreint : sa prémisse de famille d'échelle est contredite par les médianes Kaplan–Meier du manuscrit (5,32× → 3,10×).
- « constant factor » est qualifié dans `sec:hydra`.
- Un erratum sur le pré-enregistrement R-8 déclare que « améliore » n'y était pas défini.

**Ce que je te demande : confirmer l'invalidation**, ou désigner la mesure commitée qui la contredirait. Ce n'est pas une question d'interprétation. Si elle tient, les numéraux cités par `rem:exponent` sont tous au gate et le texte peut être figé tel quel.

## 3. Relectures demandées (bloquantes pour le figement)

1. **`rem:exponent`** réécrite (rapport 50, §3.1).
2. **`sec:hydra`** : le facteur constant qualifié, R7-C retirée ; **`res:bell`** : R7-D retirée ; S13-G restreint.
3. **Le paragraphe INSECTS** et **« Two predicates rather than one »** (T1 « assumer », motif corrigé : la scission est la sortie par défaut de la règle, pas un gain d'accord).
4. **`rem:predicate_scope`**, placée avant le paragraphe S8-6 pour ne déplacer aucun payload appliqué.
5. **Le résumé.** Compteur A 223 mots, compteur B 225 (le résumé commité en faisait 251 au compteur B, au-dessus de la limite). Cadrage « fault detection on an endogenous residual » restitué en phrase 1. Les retraits, uniquement des numéraux, deux abréviations non définies (ARMA–GARCH, BAF) et de la compression syntaxique, sont listés au §4 du rapport.

## 4. Décisions de périmètre

**4.1 Table 8.** La Table 7 (ex-« Table II ») passe de 4,48 pt à 7,21 pt, re-composée depuis les artefacts commités, cellules inchangées. La **Table 8 (`tab:family_order`) reste délibérément à 5,8 pt**. Son bloc est la charge S2ter-I, verrouillée par `tests/test_S2ter_predicate.py` (REPLACE verbatim avec adaptation une-colonne déclarée, rapprochement ligne à ligne avec `family_table_latex()`) ; la re-composer exige d'amender cette adaptation déclarée. **Question formelle : mandates-tu une re-composition de la Table 8 analogue à celle de la Table 7 pour le stream suivant ?**

**4.2 H10.** Deux décisions t'appartiennent avant le lancement (rapport 50, §8).
- **L'artefact public.** `origin` contient `docs/` ; il faut définir l'export de soumission (sans `docs/prompts`, `docs/reports`, `docs/theory`, `docs/editorial`, `docs/plans`, ni `CLAUDE.md`).
- **Le protocole d'isolation.** Un export hors dépôt, cinq sous-agents à profil lancés depuis cet export ; l'isolation reste une consigne, pas une garantie technique. Confirme ou prescris.

## 5. Forme attendue

Confirmation ou réfutation du §2 avec les fichiers à l'appui ; relectures du §3 en blocs SEARCH/REPLACE ou validation en l'état ; réponses aux §4.1 et §4.2 ; puis l'ordre de figement et de lancement de H10. Tout chiffre nouveau entre d'abord dans un artefact commité.
