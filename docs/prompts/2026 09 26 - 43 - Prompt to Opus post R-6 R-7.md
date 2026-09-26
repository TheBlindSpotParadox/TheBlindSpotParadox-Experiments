[Saturday, September 26, 2026]

# PROMPT POST R-6/R-7 · G1–G3 EXÉCUTÉS · R-7 NE DISCRIMINE PAS · DEUX ARBITRAGES ATTENDUS SUR L'EXPOSANT

---

## 1. État des lieux

La tête de ton plan du « 2026 09 26 - 40 » est exécutée : **G1, G2, G3**, plus **G7, G8, G9 et G10** pliés dans la même passe de recalcul (mêmes artefacts, un seul passage). Commit `88330a8`, poussé sur `origin/main`, arbre propre. 188/188 tests, S13 relancé deux fois avec reproduction SHA-256 exacte, v65 recompilée sous Tectonic (61 pages A4, nouveau contenu vérifié dans la couche texte du PDF). Le reste du plan n'a pas été touché : les sept payloads S2-ter, l'arbitrage INSECTS, T1 et la pré-review restent ouverts, dans ton ordre.

Deux rapports sont dans ta mémoire de projet. Ils portent tout le détail — chiffres, tableaux, motifs — et je ne le répète pas ici :

- **`2026 09 26 - 41 - R-7 pre-registration refit HAT.md`** — le pré-enregistrement, écrit **avant** tout calcul, conformément à ta charge G3 : données (`R6_hat_instrumented.parquet`, grille identique à S6), censure déclarée (2/1 800 sur le domaine valide), estimateur en parité stricte avec le refit ARF (médiane par amplitude sur graines non censurées, `linregress` log-log, bootstrap sur graines à graine distincte), **tes deux lectures du §4**, et la règle de décision : toute issue autre que les deux branches ⇒ refit déclaré non discriminant, aucune lecture écrite comme un résultat.
- **`2026 09 26 - 42 - R-6 R-7 execution response to Opus.md`** — la réponse d'exécution. R-6 : fenêtre convergée 1 000 pas, décomptes d'événements, intervalles régénérés, S13-H appliquée avec les chiffres mesurés (tes 46 événements confirmés au chiffre exact ; à Δe = 0,4944 l'avantage devient détectable, aux deux points extrêmes l'égalité devient un résultat). R-7 : **aucune de tes deux branches ne se réalise** — CI HAT [−3,26 ; −2,83], qui exclut −2 **et** le CI ARF — donc non discriminant selon la règle pré-enregistrée. La cause, et c'est la découverte du tour : la médiane HAT n'est pas une loi de puissance sur le domaine valide, elle sature sur un **plancher structurel ~50 pas** ; la courbe ARF est **elle aussi** saturée (~29) ; et la revendication publiée « exclut −2 à 4,8 erreurs types » s'avère **sensible au point de coupure** — sur le flanc non saturé, l'exposant ARF (−1,99 à −2,11 selon la coupure) est compatible avec la borne de Hoeffding.

Le traitement du manuscrit a été **différé à ta prescription** : la phrase de ta charge S13-G (« The single-tree refit on the valid domain discriminates between a per-member and an ensemble origin ») est réfutée par notre propre artefact et ne peut pas rester, mais la révision éventuelle de « exclut −2 » renverse une affirmation qui a traversé S13 et ta revue, sur la base d'un diagnostic post-hoc — l'écrire sans arbitrage reproduirait le schéma « deux nombres, pas d'arbitrage ».

## 2. Ce que j'attends de toi

**1. L'arbitrage sur `rem:exponent` — la charge exacte.** Les trois traitements possibles sont exposés au §6 du rapport 42. Tranche :

- la phrase « discriminates » tombe dans tous les cas — **prescris le texte de remplacement** (bloc SEARCH/REPLACE comme d'habitude) ;
- « exclut −2 à 4,8 erreurs types » : conservée telle quelle, révisée avec la sensibilité au point de coupure publiée, ou rétrogradée en question ouverte avec le plancher nommé ? Si le plancher entre au manuscrit, le **critère de coupure du flanc non saturé doit être pré-enregistré** — le tableau du §4 du rapport 42 donne trois coupures cohérentes entre elles, mais le choix d'une coupure est un degré de liberté que le manuscrit ne peut pas cacher ;
- deux lacunes déclarées au §9 du rapport 42 conditionnent, à mon sens, toute entrée du plancher au manuscrit : le mécanisme exact du ~50 est **déduit des données, pas lu dans le source de River** (fenêtre minimale d'ADWIN ou période de grâce — à vérifier avant d'écrire « structural »), et les CI du flanc sont des **erreurs types de régression, pas des bootstrap sur graines**. Dis si ces deux vérifications doivent précéder la charge.

**2. Le retentissement du R-7 sur le reste de ton plan.** L'issue non discriminante et le plancher changent-ils autre chose — la formulation de S1, le cadrage « over the full grid » de `sec:hydra`, la lecture de l'effet Hydra comme facteur (le plancher d'ensemble ~29 sous le plancher d'arbre unique ~50 en est, factuellement, la démonstration la plus propre — cf. §4 du rapport 42) ? Si oui, prescris.

**3. La confirmation du chemin critique restant.** G4 (sept payloads S2-ter), G5 (INSECTS dans `sec:limitations`), G6 (T1 — arbitrage de ma part attendu), G11, G12, G13 en dernier sur le document figé. Confirme l'ordre ou réajuste-le à la lumière de ce tour.

## 3. Forme attendue

Charges numérotées avec blocs SEARCH/REPLACE pour toute mutation du `.tex`, priorités, et l'ordre d'exécution — comme pour S13 et S13-bis. Les chiffres du rapport 42 §4 (fits de flanc) ne sont **pas committés** (scratchpad, post-hoc) : toute charge qui les utilise doit d'abord les faire entrer dans le pipeline sous un critère pré-enregistré.
