# Note de vérification des sources — Stream S5

Session de vérification : 2026-09-06. Méthode : consultation en ligne des
documentations officielles et des notices d'éditeur. Aucune citation sur
mémoire.

Statuts : **V** vérifié en session · **P** partiellement vérifié · **X** non
vérifié, interdit de citation.

## T2 — Réglementation

| Source                                              | Statut         | Constat                                                                                                                                                                                                                                                                                                                                                                  |
| --------------------------------------------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| EU AI Act, Art. 72 (post-market monitoring)         | **V**          | Texte confirmé sur le domaine officiel `ai-act-service-desk.ec.europa.eu`. Obligation d'un système de surveillance post-commercialisation documenté, collecte active de données de performance sur toute la durée de vie, plan intégré à la documentation technique (Annexe IV).                                                                                         |
| EU AI Act, Art. 15(4) (feedback loops)              | **V**          | Les systèmes à haut risque qui continuent d'apprendre après mise sur le marché doivent être conçus pour éliminer ou réduire le risque de sorties biaisées influençant les entrées futures (« feedback loops »), avec mesures d'atténuation. **C'est le levier le plus fort du stream** : le régulateur nomme lui-même la boucle fermée comme un danger.                  |
| Référence de l'instrument                           | **V**          | Regulation (EU) 2024/1689, version officielle du 13 juin 2024, `OJ:L_202401689`.                                                                                                                                                                                                                                                                                         |
| **Réserve Art. 72 / Art. 15**                       | **P**          | Le portail officiel affiche un avertissement : ces dispositions ont été **amendées par le Digital Omnibus on AI** et le texte affiché n'est pas encore à jour. Citer l'article par son numéro et son objet reste correct ; **ne pas citer de libellé littéral**. Revérifier avant soumission finale.                                                                     |
| L'acte d'exécution (modèle de plan de surveillance) | **P**          | Échéance légale : 2 février 2026. Adoption effective non vérifiée. Ne pas affirmer qu'il existe.                                                                                                                                                                                                                                                                         |
| SR 11-7 (Federal Reserve / OCC, 2011)               | **X — ABROGÉ** | **Abrogé le 17 avril 2026.** Remplacé par Fed SR 26-2 et OCC Bulletin 2026-13 (« Revised Guidance on Model Risk Management »), qui rescindent aussi OCC 2011-12, OCC 2021-19, OCC 1997-24 et FDIC FIL-22-2017. **Citer SR 11-7 comme exigence courante serait une faute factuelle.**                                                                                     |
| Fed SR 26-2 / OCC Bulletin 2026-13                  | **V**          | Cadre fondé sur des principes, proportionné au profil de risque. Les disciplines sont conservées : inventaire, tiering, validation indépendante avec *effective challenge*, **surveillance continue**, gouvernance. **Réserve** : l'IA générative et agentique est explicitement hors périmètre — sans effet sur notre argument, qui porte sur un classifieur tabulaire. |

## T2 — Outillage MLOps

| Source                              | Statut | Constat                                                                                                                                                                                                                                                                                                                                                                              |
| ----------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| NannyML — estimation de performance | **V**  | Documentation officielle. CBPE (classification, via scores de confiance) et DLE (régression, via modèle de perte secondaire). Vocabulaire employé : *the monitored model* — la séparation moniteur/modèle est dans la terminologie de l'outil. **Réserve exploitable** : CBPE suppose l'absence de dérive de concept, donc l'estimateur dégrade sous la dérive même qu'il surveille. |
| Google Vertex AI Model Monitoring   | **V**  | Documentation officielle. Détection de *skew* et de *drift* sur les features d'un endpoint déployé, requêtes journalisées en BigQuery, `monitor_interval` planifié indépendamment du modèle.                                                                                                                                                                                         |
| AWS SageMaker Model Monitor         | **P**  | Documentation officielle : data quality, model quality (fusion prédictions/labels), bias drift, feature attribution drift, alertes CloudWatch. **Réserve** : fermé aux nouveaux clients au 30/07/2026, pas de nouvelles fonctionnalités. Citer comme témoin de la pratique établie, jamais comme état de l'art courant.                                                              |
| Evidently                           | **V**  | Bibliothèque open source, presets de dérive, intégration pipeline/CI, tests pass/fail.                                                                                                                                                                                                                                                                                               |
| Azure ML data drift                 | **X**  | Non vérifié en session. Le mécanisme a par ailleurs connu une refonte entre v1 et v2 de l'API. Ne pas citer.                                                                                                                                                                                                                                                                         |
| Arize                               | **X**  | Non vérifié en session. Ne pas citer.                                                                                                                                                                                                                                                                                                                                                |
| Fiddler                             | **X**  | Non vérifié en session. Ne pas citer.                                                                                                                                                                                                                                                                                                                                                |

## T3 — Détection de défauts

| Source                                       | Statut                | Constat                                                                                                                                                                                                                                                                                                                                                                                                   |
| -------------------------------------------- | --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Chen & Patton (1999)                         | **V**                 | *Robust Model-Based Fault Diagnosis for Dynamic Systems*, Kluwer Academic Publishers, Boston. ISBN 0-7923-8411-3.                                                                                                                                                                                                                                                                                         |
| Gertler (1998)                               | **V**                 | *Fault Detection and Diagnosis in Engineering Systems*, Marcel Dekker, New York.                                                                                                                                                                                                                                                                                                                          |
| Isermann (2006)                              | **V — titre corrigé** | Le sous-titre exact est *An Introduction from Fault Detection to Fault **Tolerance*** (le prompt S5 annonçait « to Fault Diagnosis »). Springer.                                                                                                                                                                                                                                                          |
| Blanke, Kinnaert, Lunze, Staroswiecki (2006) | **V**                 | *Diagnosis and Fault-Tolerant Control*, 2e éd., Springer. Ajout non demandé, retenu : couvre explicitement le diagnostic sous commande.                                                                                                                                                                                                                                                                   |
| Masquage de défaut en boucle fermée          | **V**                 | Établi par plusieurs sources indépendantes : la compensation par le régulateur réduit la sensibilité du résidu au défaut ; les méthodes FDI développées en boucle ouverte ne sont pas adaptées à la boucle fermée ; travaux récents traitant explicitement du *closed-loop fault masking* par des correcteurs adaptatifs. **Le recadrage T3 est soutenu par la littérature, pas seulement par analogie.** |
| **Limite déclarée**                          | —                     | Aucune source ne traite d'un correcteur à événements discrets non paramétrique. Le manuscrit revendique une **analogie de topologie**, pas un isomorphisme, et l'écrit.                                                                                                                                                                                                                                   |

## T4 / T5 — Théorie du changement de point

| Source                                     | Statut | Constat                                                                                                                                                                                       |
| ------------------------------------------ | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Lorden (1971)                              | **V**  | Déjà au bib v64, DOI correct.                                                                                                                                                                 |
| Moustakides (1986)                         | **V**  | Déjà au bib v64, DOI correct.                                                                                                                                                                 |
| Lai (1995)                                 | **V**  | JRSS-B 57(4), 613–644, DOI `10.1111/j.2517-6161.1995.tb02052.x`. Certaines sources indiquent 613–658 (discussion incluse) ; l'article propre est 613–644.                                     |
| Tartakovsky, Nikiforov & Basseville (2014) | **V**  | Déjà au bib v64.                                                                                                                                                                              |
| Nikiforov (2012)                           | **V**  | Déjà au bib v64 : *Sequential detection of transient signals*, IEEE TIT 58(12), 7351–7364. **Fournit exactement le critère T5** : probabilité de non-détection au pire cas sur fenêtre finie. |
| Tartakovsky (2023)                         | **V**  | Déjà au bib v64 : détection séquentielle asymptotiquement optimale de changements transitoires.                                                                                               |

## T6 — Détecteurs sur l'espace des entrées

| Source                           | Statut | Constat                                                                                                                                                                  |
| -------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| HDDDM — Ditzler & Polikar (2011) | **V**  | IEEE CIDUE, 41–48.                                                                                                                                                       |
| PCA-CD — Qahtan et al. (2015)    | **V**  | KDD '15, 935–944, DOI `10.1145/2783258.2783359`.                                                                                                                         |
| MD3 — Sethi & Kantardzic (2017)  | **V**  | Expert Systems with Applications 82, 77–99. Version antérieure : Procedia CS 53 (2015), 103–112. La version journal est retenue.                                         |
| D3 — Gözüaçık et al. (2019)      | **V**  | CIKM '19, 2365–2368, DOI `10.1145/3357384.3358144`.                                                                                                                      |
| Gemaque et al. (2020)            | **V**  | WIREs DMKD 10(6), e1381.                                                                                                                                                 |
| Hu, Kantardzic & Sethi (2020)    | **V**  | WIREs DMKD 10(2), e1327.                                                                                                                                                 |
| Lukats et al. (2025)             | **V**  | **Déjà au bib v64** mais cité comme benchmark homoscédastique. C'est un *benchmark and survey of fully unsupervised concept drift detectors* : à repositionner en §II-E. |

## Synthèse

Sources citables : 23. Sources écartées : 3 (Azure, Arize, Fiddler).
Corrections factuelles : 2 (abrogation SR 11-7, sous-titre Isermann).
Réserves à revérifier avant soumission : 3 (Digital Omnibus, acte d'exécution
Art. 72, statut commercial SageMaker Model Monitor).
## Péremption des réserves (M7)

Les statuts **P** ci-dessus portent des réserves dont la validité est datée. La session de
vérification est du **2026-09-06** ; le registre n'avait aucune date de péremption, et les trois
réserves étaient calées sur un calendrier de soumission conférence abandonné par l'action A9.

`expires_on` n'est **pas** une propriété de la source : c'est une cadence de re-vérification. La
date ne prédit pas que l'information devienne fausse ce jour-là, elle force à rouvrir le dossier.
`tests/test_manuscript_integrity.py::test_source_reservations_have_not_expired` échoue au-delà.

| source | expires_on | motif de la réserve |
|---|---|---|
| EU AI Act, Art. 72 et Art. 15(4) — libellé | 2027-03-06 | Dispositions amendées par le Digital Omnibus on AI ; le portail officiel affiche un texte non à jour. Citer par numéro et objet reste correct, jamais le libellé littéral. |
| EU AI Act, Art. 72 — acte d'exécution | 2027-03-06 | Échéance légale au 2 février 2026, adoption effective non vérifiée. Ne pas affirmer qu'il existe. |
| AWS SageMaker Model Monitor — statut commercial | 2027-03-06 | Fermé aux nouveaux clients au 30/07/2026, pas de nouvelles fonctionnalités. Témoin de la pratique établie, jamais état de l'art courant. |

Horizon de six mois à compter de la session de vérification. À la péremption : rouvrir chaque
ligne, revérifier en session, puis repousser la date ou déclasser la source en **X**.
