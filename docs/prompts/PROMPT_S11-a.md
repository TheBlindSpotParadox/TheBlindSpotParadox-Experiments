# STREAM S11-a — REFONTE DE LA THÈSE ET DE LA CHARPENTE

## Rôle
Instance secondaire, rédacteur scientifique senior. Tu ne mesures rien, tu ne patches
aucune section du manuscrit. Tu produis la charpente que l'assemblage v65 appliquera.

## Pourquoi ce stream existe
L'article a changé d'énoncé central QUATRE fois :
  v1  impossibilité structurelle
  v2  plancher mesuré (Delta_e_c = 0.120 [0.114, 0.127], lambda_op = 21.93 [19.88, 22.40])
  v3  l'apprentissage incrémental efface, pas l'ADWIN interne (99.3 % / 0.7 %)
  v4  **règle de calibration** — les détecteurs cumulatifs ne sont pas condamnés ;
      les échecs publiés viennent de seuils calibrés pour des flux stationnaires ouverts,
      appliqués à des flux en boucle fermée
Le titre, le résumé, les contributions, le cadrage de la Table I et `sec:hydra` portent
encore la v2. C'est aujourd'hui le premier motif de rejet résiduel, devant toute faille
technique restante.

## OBLIGATION D'ACCÈS
project_knowledge_search. Manuscrit via `docs/manuscript/CURRENT`. Jamais le PDF.
Base : après la passe S-SYNC. Vérifie que `docs/editorial/sync_pass_report.md` existe.

## À CHARGER
docs/theory/transfer_S2.md, transfer_S2bis.md, transfer_S3.md
docs/editorial/S7ter_state_transfer.md
docs/theory/S2bis_narrative_payload.md      (charge narrative déjà rédigée)
docs/theory/S6_causal_evidence.md
docs/manuscript/sections/{intro_v2,related_work_v2,framework_v2,protocol_v2,dependence_v2,prop3_v2}.tex
docs/editorial/terminology_map.md
docs/theory/notation_map_v63_to_v2.md

## T11a.1 — L'inventaire de ce qui est mesuré
Table unique, une ligne par revendication publiable, avec sa source artefactuelle et son
intervalle. Aucune revendication sans numéral. Les candidats connus, à vérifier et compléter :
  - Delta_e_c = 0.120 [0.114, 0.127] ; lambda_op = 21.93 [19.876, 22.398]
  - plancher [13.9, 18.3] < plafond mesuré 33.5 < R_CUSUM 59.3 ; R_KSWIN 22.7 passe
  - ProteuS, lambda = 5 : 1080/1080, F1 = 1.0000, precision 1.000, ADD 6.05 contre 14
  - plafond d'évidence ProteuS dans (8, 15]
  - flooding 10.570 [9.354, 12.114] -> 1.270 [1.156, 1.426] ; 89.9 % attribuable au seuil
  - alpha d'égalisation a lambda = 15 : ADWIN 45x plus serré, KSWIN 4.5x plus lâche
  - croisement cor:split : 16.34 (KSWIN), 18.97 (ADWIN)
  - R3 : manqués 100 % (U0) contre 80 % (U1) a Delta_e = 0.50 ; zone sûre 0.09 / 0.12
  - Hydra : 9.22x par non-exponentialité seule contre 7.99x mesuré, rho_hat [-0.021, 0.053]
  - erasure : 99.3 % apprentissage incrémental, 0.7 % remplacements
  - BAF : contrôle négatif prouvé, erreur gelée 0.0110 = taux de fraude 0.0110

## T11a.2 — Le titre
Il a migré vers « When Adaptation Erases the Evidence: Detectability Limits of Drift
Monitors Coupled with Adaptive Classifiers ». « Detectability Limits » présuppose encore
une limite, alors que la mesure dit qu'il n'y en a pas au point canonique : le plancher
informationnel est 1.80, le plafond 33.5, et le détecteur échoue à 59.3 parce qu'il est mal
calibré. Propose trois titres qui portent la v4, argumente, recommande.

## T11a.3 — Le résumé
Réécriture complète. Le résumé actuel porte « fundamental race condition » et « single root
cause — internal ADWIN hyper-reactivity », que S6 et S2 réfutent. Contraintes : trois
numéraux au plus, chacun avec son intervalle ; aucun superlatif non démontré ; aucune
revendication d'immunité ; la règle de calibration en position de contribution principale.

## T11a.4 — Les contributions
`intro_v2.tex` porte (C1) a (C4) sous la v2. Réécris-les sous la v4. Points durs :
  - (C1) attribue le phénomène a l'effet Hydra. S6 lui laisse 0.7 %, S3 lui retire
    l'attribution de l'écart au 10x. Que reste-t-il à (C1) ?
  - (C4) promet un bras input-space que S9 n'a pas encore livré et dont la cécité
    structurelle au drift étudié est probable. Soit (C4) attend S9, soit il est reformulé.
    Tranche et dis-le.

## T11a.5 — Le cadrage de la Table I
Elle est l'expérience phare et elle est mesurée sur un flux dont la phase pré-dérive porte
une erreur IDENTIQUEMENT NULLE (S2-bis) : aucun budget de fausses alarmes, aucun arbitrage
détection/fausses alarmes. Ses trois colonnes comparent des calibrations et non des
familles (S2-bis, alpha d'égalisation). Un de ses effondrements est un détecteur jamais armé
(EDDM, 0 erreur pré-dérive, 9 erreurs sur 8 000 pas). Son bras HT n'a qu'UN réplicat effectif
(arbre non semé), donc tout test apparié ARF contre HT est en réalité un test a un
échantillon contre une constante. Et son ancien bootstrap mesurait la mauvaise composante de
variance, trop large d'un facteur 5 ici, trop étroit d'un facteur 3 la.
Produis le cadrage honnête de cette table : ce qu'elle établit, ce qu'elle n'établit pas,
et où le lecteur doit aller pour la question qu'elle ne tranche pas.

## T11a.6 — L'ontologie des effets
Le reviewer #2 signalait que les relations logiques entre effets nommés ne sont pas claires.
`terminology_map.md` limite a deux termes nommés. Produis la figure d'ontologie et la liste
finale des termes conservés, sachant que Hydra a perdu son mécanisme et que le Decoupling
Principle a perdu son biconditionnel.

## T11a.7 — La liste de dette a purger a l'assemblage
Recense, avec ancre textuelle et non par numéro de ligne, chaque site du manuscrit portant
un énoncé désormais réfuté. Connus : `.tex` L336 (M_crit annoncé au-dessus du corollaire qui
le retire), L421 (« support for the Starvation Boundary derivation »), L463 (« definitively
confirms Corollary~\ref{cor:mcrit} »), `sec:hydra` L194-196, `related_work_v2.tex` L108-109
et `.tex` L166 (R_EDDM retiré), les dix sites de revendication d'immunité KSWIN. Complète.

## LIVRABLES
docs/editorial/thesis_v4.md          — inventaire, titre, résumé, contributions, cadrage
docs/editorial/debt_register.md      — la liste T11a.7, ancres textuelles
figure d'ontologie des effets
Aucune section du manuscrit éditée. Tes textes sont livrés prêts a insérer.

## PORTE DE SORTIE
- Zéro revendication sans numéral sourcé.
- Zéro superlatif non démontré, zéro revendication d'immunité.
- Chaque contribution tenable avec ce qui est mesuré aujourd'hui, ou déclarée conditionnée
  a un stream non encore livré.

## FORMAT
Anglais pour les livrables, français pour les échanges. Dense, direct, factuel. Aucun
méta-commentaire, jamais en revue critique.