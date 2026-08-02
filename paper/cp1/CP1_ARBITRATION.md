# Paquet d'arbitrage CP1 — CN2026 (S2 exécuté)

**Statut : PROVISOIRE — document d'arbitrage, pas un contenu du papier.**
Rédigé le 2026-08-02 après l'exécution unique du pipeline apparié (S2), branche
`cn2026-upgrade`, code au commit `4d7a9fe` (+ colonnes `run_job` CP1-held dans
le worktree). Lecture ~45 min. Ce document est autonome : toutes les décisions
demandées peuvent se prendre sans ouvrir le code. Figures : `paper/cp1/*.png` ;
chiffres machine-dérivés : `paper/cp1/cp1_tables.json` et
`paper/cp1/predictor_validation.json` (§7 pour reproduire).

**Décisions attendues (§5–§6) : choisir la route (A/B/C) et le titre ; ratifier
ou amender D17(a) et D18–D22 ; trancher trois questions narratives.**

---

## 1. Résumé exécutif

Le protocole apparié (mêmes organisations, mêmes tirages d'agents entre
stratégies — D19) divise les incertitudes par ~3 et change deux conclusions :

1. **Sans decay, la dispersion domine partout où quelque chose se joue.**
   Contraste headline apparié random − cluster : **+39.7 pp, IC95
   [+35.4, +43.9]** (n=50 paires). Sur la carte des régimes (40 cellules,
   Holm 2 familles, bande ±2 pp) : **14 victoires dispersion** (+4 à +43 pp),
   **23 équivalences prouvées** (saturation et famine), 3 incertaines,
   **0 victoire cluster** — les 2 cellules pro-cluster du n=12 ont disparu
   sous la correction.
2. **Sous decay, il y a un vrai croisement — l'ancienne conclusion « parité »
   est contredite.** L'avantage dispersion fond avec ρ, traverse zéro vers
   ρ≈0.2 (r=1.0), et **s'inverse significativement** : −5.3 pp
   [−9.0, −1.5] à (r=1.0, ρ=0.25) — les paramètres du vieux run « parité » —
   et −11.4 pp [−14.8, −8.0] à ρ=0.40. Mécanisme visible : cluster est
   insensible au decay (32.4 → 29.3 %), random s'effondre (72 → 18 %).
3. **Robustesse : le signe + tient partout** (8 variantes d'organisation,
   +14.7 à +48.3 pp).
4. **eu-core (topologie réelle, D22) : signe répliqué** — +13.5 pp
   [+1.0, +26.0], p=0.034 — dans un régime loterie bimodale (§3.5).
5. **Prédicteur D21 : verdict `no_go`** par les portes pré-déclarées
   (AUC V1 0.642 < 0.70), malgré un V2 parfait (14/14 signes). Le détail est
   lui-même informatif : AUC 0.996 sur cluster, 0.59–0.69 sur les stratégies
   dispersées (§3.6).

**Ma recommandation (§5) : Route A affinée** — le trade-off portée/rétention
du titre actuel devient enfin *démontré*, sous la forme précise d'un
**croisement** quantifié en (ρ, r), avec l'asymétrie honnête : la dispersion
perd tout sous decay fort, la concentration ne gagne presque rien — elle
survit (~30 % quoi qu'il arrive). Route C (« le decay comprime sans effacer »)
est **contredite** par les données. Route B pure est affaiblie (dire « cluster
ne gagne que là où les campagnes échouent » serait faux sous decay fort).

---

## 2. Ce qui a changé méthodologiquement (pourquoi ces chiffres priment)

- **Appariement (D19)** : chaque réplicat = une organisation fraîche (D14
  intact) évaluée sous *toutes* les stratégies avec les mêmes tirages
  θ/willing/able. Les contrastes sont des différences appariées ; la variance
  inter-organisations (sd 9–16 pp) disparaît des IC. Vérifié bit-exact par
  tests (graphes et tirages identiques dans un bloc).
- **Familles pré-déclarées AVANT exécution** (commits `9c8391a` → `d36cece`) :
  carte = 40 cellules, decay = 7 contrastes uniques random−cluster sur
  **final_rate** (24 bras exécutés) ; Holm par famille (différence ET
  équivalence TOST) ; bande pratique ±2 pp ; 3 classes
  victoire / équivalence / incertain. `cumulative_rate` / `retention_rate` :
  secondaires descriptives.
- **Graines figées avant toute exécution** ; exécution **unique** ; re-run de
  contrôle du headline **bit-identique**. Aucune relance, aucun choix
  post-résultats.
- **Politique de citation (D19)** : le papier citera exclusivement les runs
  appariés pour les stratégies semées ; le panel indépendant committé reste la
  source de broadcast (5.5 % ± 3.4, n=50) et une contre-vérification. Les deux
  échantillons d'organisations sont disjoints : de petits écarts de moyennes
  (~2 pp) sont attendus et ne sont pas des anomalies.

---

## 3. Résultats

### 3.1 Headline apparié (θ̄=0.30, budget 5 %, κ=20, decay off ; n=50 paires)

| stratégie | portée moyenne | sd |
|---|---|---|
| champions (top-degré) | **75.9 %** | 8.2 |
| random | **72.0 %** | 9.2 |
| one_per_team (couverture, D20) | 70.6 % | 10.4 |
| cluster | **32.4 %** | 11.0 |
| broadcast (panel indépendant committé) | 5.5 % | 3.4 |

Contrastes appariés (IC 95 %) :

| contraste | Δ (pp) | IC95 | p |
|---|---|---|---|
| **random − cluster** | **+39.7** | [+35.4, +43.9] | 5e-24 |
| champions − random | +3.9 | [+0.6, +7.1] | 0.020 |
| one_per_team − random | −1.4 | [−5.1, +2.2] | 0.44 |

Lectures :
- `one_per_team ≈ random` : c'est la **branche 2 pré-déclarée de D20** — la
  garantie de couverture n'ajoute rien, le spread Poisson de random couvre
  déjà efficacement (~84 équipes touchées sur 249 à 5 %). Une phrase du
  papier : « cohérent avec le mécanisme de couverture, dont random s'acquitte
  déjà ».
- `champions > random` devient significatif en apparié (+3.9, p=0.02) — ce
  contraste est **descriptif** (hors familles corrigées). Question narrative
  Q2 en §5.

### 3.2 Carte des régimes (Fig. `fig_regime_3class.png` — candidate Fig. 2a du papier)

40 cellules θ̄ × budget, n=50 paires/cellule, Holm 2 familles, bande ±2 pp :

- **14 victoires dispersion**, toutes `exceeds_band` sauf les +3/+4 pp de
  bordure : la bande diagonale d'allumage (θ̄ 0.25→0.45 quand le budget monte
  1→15 %), maximum **+42.6 pp [39.1, 46.0] au point headline gelé**.
- **23 équivalences prouvées** (TOST corrigé) : tout θ̄ ≤ 0.20 (saturation au
  plafond willing) et le coin affamé — « la stratégie est indifférente ici »
  est désormais une affirmation positive, pas une absence de preuve.
- **3 incertaines** (bordures de bande).
- **0 victoire cluster.** Les deux cellules pro-cluster du n=12 (−1.2 et
  −0.6 pp, non corrigées) ne survivent ni à n=50 ni à Holm ni à la bande :
  l'une est désormais équivalence prouvée, l'autre incertaine.

### 3.3 Decay (Fig. `fig_decay_family.png` — candidate Fig. 2b)

Famille pré-déclarée (7 contrastes uniques, endpoint **final_rate**, horizon
100 pas, convergence 98–100 % à points fixes ~30–45 pas — l'écart avec
l'ancien horizon 80 n'explique rien) :

| (r, ρ) | Δ random−cluster (pp) | IC95 | classe | random | cluster |
|---|---|---|---|---|---|
| ρ = 0 | **+39.6** | [+35.4, +43.9] | victoire-dispersion | 72.0 % | 32.4 % |
| (0.5, 0.10) | +13.9 | [+9.6, +18.3] | victoire-dispersion | 46.2 % | 32.3 % |
| (0.5, 0.25) | −0.3 | [−4.1, +3.5] | incertain | 31.8 % | 32.1 % |
| (0.5, 0.40) | **−7.7** | [−11.5, −3.9] | victoire-cluster | 24.2 % | 31.9 % |
| (1.0, 0.10) | +8.4 | [+4.2, +12.7] | victoire-dispersion | 39.9 % | 31.5 % |
| (1.0, 0.25) | **−5.3** | [−9.0, −1.5] | victoire-cluster | 25.4 % | 30.7 % |
| (1.0, 0.40) | **−11.4** | [−14.8, −8.0] | victoire-cluster | 17.9 % | 29.3 % |

Toutes les victoires dépassent la bande ±2 pp (`exceeds_band`). Le self-check
pré-déclaré (bras ρ=0 bit-identiques entre r=0.5 et r=1.0) passe.

**Secondaires descriptives** (pré-déclarées secondaires — aucun claim corrigé) :
à (1.0, 0.25), portée **cumulative** random 29.0 % vs cluster 30.9 % ;
rétention (terminal/cumulatif) random 0.86 vs cluster 0.99. Lecture mécanique
importante : le decay ne « ronge » pas une cascade dispersée déjà déployée —
il **l'empêche de croître** (cumulatif 29 % vs 72 % sans decay). Le ratio de
rétention ~0.99 de cluster s'applique à une base de ~31 % : à présenter
toujours à côté des niveaux absolus (piège limitations #16).

### 3.4 Robustesse (Fig. `fig_robustness.png`)

ΔR apparié (random − cluster) au point headline, un facteur à la fois :

| variante | Δ (pp) | IC95 |
|---|---|---|
| N = 500 | +14.7 | [+9.8, +19.7] |
| N = 2000 (référence) | +40.9 | [+37.7, +44.1] |
| N = 8000 | +48.3 | [+46.5, +50.1] |
| équipes de 5 | +32.1 | [+28.4, +35.8] |
| équipes de 12 | +40.7 | [+37.7, +43.8] |
| silo 0.50 | +32.7 | [+25.4, +40.0] |
| silo 0.70 | +47.9 | [+44.1, +51.7] |
| silo 0.95 | +36.0 | [+32.9, +39.0] |

Signe stable partout ; l'amplitude croît avec la taille de l'organisation
(petites orgs : moins d'équipes → la concentration coûte relativement moins).

### 3.5 email-Eu-core (Fig. `fig_eucore.png` ; D22 — topologie réelle, attributs synthétiques)

Réplication **sur topologie réelle avec comportements synthétiques** — pas une
validation empirique (D22, limitations #11). 986 nœuds, 42 départements
ground-truth SNAP (jamais Louvain), symétrisation par union, 50 tirages
d'attributs appariés (CRN par tirage).

| stratégie | moyenne | sd | tirages > 10 % |
|---|---|---|---|
| champions | 84.4 % | 1.3 | 100 % |
| random | 37.0 % | 35.9 | 62 % |
| cluster | 23.5 % | 29.2 | 42 % |

**random − cluster apparié : +13.5 pp [+1.0, +26.0], p=0.034.** Le signe du
contraste central se réplique. Le régime est différent du synthétique : la
topologie (dense, hubs marqués) rend l'issue **bimodale** — chaque tirage
finit à ~9 % ou ~83 %, et random s'allume plus souvent (62 % vs 42 %).
champions y sature (hubs → allumage quasi certain). Niveau de revendication
autorisé : *le signe et le mécanisme se répliquent sur une topologie réelle
modulaire ; les magnitudes ne sont pas comparables (régime d'allumage
différent)*. Engagement D22 tenu : résultat rapporté tel quel.

### 3.6 Prédicteur local D21 — verdict réel : **no_go**

Portes appliquées telles qu'écrites (`paper/cp1/predictor_validation.json`) :

- **V1 = 0.642** (< 0.70) : AUC poolée sur 12 789 unités équipe×réplicat×
  stratégie ensemencées, reconstruites bit-exactement depuis les triples de
  graines. Taux d'allumage observé des équipes ensemencées : **90.7 %** — dans
  une organisation qui atteint ~70 %, presque toutes les équipes ensemencées
  finissent allumées, ce que le modèle d'équipe isolée ne prédit pas.
- Par stratégie (descriptif) : cluster **0.996**, champions 0.694, random
  0.631, one_per_team 0.591.
- **V2 = 1.000** : 14/14 cellules décisives de la carte, signe prédit correct,
  0 erreur opposée (au point headline : +1.5 pp prédit localement vs +42.6
  observé).
- **Verdict `no_go`** (la bande partial exige AUC ≥ 0.70).

Lecture honnête : ~90 % de la portée et ~98 % des équipes allumées de random
sont **non expliquées par le prédicteur local** (deux dénominateurs distincts,
calibration officielle graine 20260802). Le contraste des AUC (0.996 sur
cluster vs ~0.6 en dispersion) est *cohérent avec* le mécanisme — l'allumage
de cluster est local et prédictible, celui de la dispersion ne l'est pas —
sans que le prédicteur démontre le canal du résidu. Conséquence papier
(variante no-go pré-déclarée en D21) : le mécanisme méso reste **mesuré**
(désormais dérivable des CSVs via `seeded_teams`), le prédicteur est nommé
« pré-enregistré, échec de sa porte de validation (AUC 0.64 < 0.80) ; modèle
à deux niveaux = travail futur ». Le V2 parfait peut être mentionné comme
observation descriptive, clairement subordonnée au verdict.

---

## 4. ⚠ Écarts avec les chiffres cités (obligation d'honnêteté)

À intégrer dans RESULTS_VERIFIED v2 au commit post-arbitrage :

| ancien (cité) | nouveau (apparié) | statut |
|---|---|---|
| « Parité sous decay : cluster−random +0.9 pp [−8, +10], n=12 ; pas de renversement sans ρ≈0.40 » (RESULTS_VERIFIED, limitations #16, CLAUDE.md) | à (r=1.0, ρ=0.25) : **renversement modeste significatif** −5.3 pp [−9.0, −1.5] ; croisement vers ρ≈0.2 | **CONTREDIT** — l'ancien design (n=12, non apparié, IC ±9 pp) ne pouvait pas le voir. Pas un artefact d'horizon (points fixes ~30–45 pas) |
| Carte n=12 : dispersion 17 cellules, **cluster 2 cellules** (−1.2, −0.6 pp) | dispersion 14 victoires, **cluster 0** ; 23 équivalences prouvées | Les cellules pro-cluster ne survivent pas à n=50 + Holm + bande (attendu, R10) |
| random 69.5 / champions 73.4 / cluster 31.9 / l-m 61.6 (panel indépendant) | random 72.0 / champions 75.9 / cluster 32.4 (échantillon apparié, orgs disjointes) | Écarts ~2 pp = bruit d'échantillonnage attendu ; les deux jeux coexistent (D19 : le papier cite l'apparié) |
| « champions ≈ random » (IC chevauchants) | champions − random +3.9 pp [+0.6, +7.1] apparié (descriptif) | Précision nouvelle ; décision narrative Q2 |

---

## 5. Routes, titre, niveau de revendication

### Route A — « trade-off portée/rétention », version croisement (RECOMMANDÉE)

*Histoire* : disperser gagne l'allumage par dizaines de points ; concentrer est
insensible au decay et prend le dessus — par quelques points — dès que la
rechute est forte (croisement à ρ≈0.2–0.3 selon r).

- **Forces** : les trois familles pré-déclarées la soutiennent (carte, decay,
  robustesse) ; le titre-cadre actuel (« a reach–retention trade-off ») devient
  *enfin étayé* — ironie utile : la revue externe doutait du trade-off, le
  protocole apparié le démontre sous une forme plus précise ; l'asymétrie
  (random s'effondre / cluster survit à ~30 %) est un mécanisme mémorable ;
  compatible avec eu-core et le no-go prédicteur.
- **Faiblesses / garde-fous** : l'inversion est modeste (max −11.4 pp) et ne
  vient pas d'un gain de cluster mais de l'effondrement de random — ne jamais
  écrire « cluster gagne beaucoup sous decay » ; ρ et r sont stipulés (la
  grille 2×3 le désamorce en partie).
- **Titres possibles** :
  (i) conserver « Seeding complex contagions in modular organizations: a
  reach–retention trade-off » ;
  (ii) plus précis : « Disperse to ignite, concentrate to endure: a decay
  crossover for seeding complex contagions in modular organizations ».

### Route B — « la dispersion domine la zone d'allumage »

- **Forces** : la carte est sans appel (0 victoire cluster, 23 équivalences).
- **Faiblesses** : ignorer le croisement decay serait une omission ; « cluster
  ne gagne que là où les campagnes sont condamnées » est désormais **faux**
  sous decay fort (cluster y atteint ~30 %, pas un échec). Route B n'est
  soutenable que restreinte au monde sans decay — plus faible que A.

### Route C — « le decay comprime sans effacer l'avantage »

- **CONTREDITE par les données** : le decay efface (ρ≈0.25, r=0.5) puis
  inverse (3 cellules sur 7, `exceeds_band`). À écarter.

### Niveau de revendication autorisé (phrases prêtes, IC à l'appui)

1. « At the frozen headline point, dispersed seeding beats clustered seeding
   by **+39.7 pp (95 % CI [35.4, 43.9]**, n=50 paired organizations). »
2. « Across a θ̄ × budget map, dispersion wins 14 of 40 cells (up to +43 pp),
   the two strategies are provably equivalent (±2 pp, Holm-TOST) in 23, and
   clustering wins none. »
3. « Under reinforcement-dependent decay the advantage crosses zero near
   ρ≈0.2 and reverses — **−5.3 pp [−9.0, −1.5]** at (r=1.0, ρ=0.25), −11.4 pp
   at ρ=0.40 : clustering is almost decay-insensitive (32→29 %) while
   dispersed adoption collapses (72→18 %). »
4. « The sign replicates on a real modular topology (email-Eu-core, synthetic
   agents) : +13.5 pp [+1.0, +26.0] paired. »
5. Mécanisme : mesuré (méso) ; « a pre-registered local ignition predictor
   failed its validation gate (AUC 0.64 < 0.80) — consistent with, but not
   demonstrating, inter-team spillover as the dominant channel. »

### Questions narratives à trancher (avec la route)

- **Q1** : inclure la phrase eu-core dans l'abstract (recommandé : oui, une
  phrase, framing D22 strict) ?
- **Q2** : mentionner champions > random (+3.9 pp apparié, descriptif) ?
  Recommandation : une subordonnée au plus (« degree targeting adds a further
  ~4 pp »), sans en faire une histoire — hors familles corrigées.
- **Q3** : le no-go prédicteur — une phrase de transparence (recommandé) ou
  silence (déconseillé : le pré-enregistrement est un atout d'honnêteté) ?

---

## 6. Décisions à ratifier / amender à CP1

| décision | contenu | mon avis |
|---|---|---|
| D17(a) corrigendum | le corollaire « un v global ne peut pas réordonner » est faux (la carte le montre) ; l'équivalence exacte θ/v reste | ratifier l'amendement |
| D18 (carte) | upgrade apparié n=50, Holm 2 familles, 3 classes ; anciens vs nouveaux comptes documentés | ratifier |
| D19 (protocole apparié + politique de citation + famille decay) | tel qu'exécuté | ratifier |
| D20 (one_per_team) | résultat : branche 2 (≈ random) | ratifier avec cette lecture |
| D21 (prédicteur) | verdict **no_go** par les portes ; variante de texte no-go | ratifier le verdict tel quel |
| D22 (eu-core) | signe répliqué, régime bimodal, engagement de rapport tenu | ratifier |
| Bumps n=50 (pinnov/silo/pilots) | à exécuter au commit atomique post-CP1 (avec les nouvelles colonnes) | inchangé |

## 7. Provenance & audit

- **Code** : commit `4d7a9fe` (+ worktree CP1-held : colonnes
  `cumulative_rate`/`retention_rate`/`seeded_teams` de `core/sweep.py` et
  `tests/test_run_job_columns.py`, destinées au commit atomique). 119 tests
  verts avant exécution.
- **Exécution unique** (2026-08-02) : 6 350 simulations ≈ 4 min —
  `run_paired_headline` (200), `run_paired_regime` (4 000, 146 s),
  `run_paired_decay` (1 200, 44 s), `run_robustness` (800, 43 s),
  `exp4 run_eucore` (150, 1 s). Graines : master 20260610 (exp1),
  (20260610, 4) (exp4), figées avant exécution.
- **Contrôle bit-stabilité** : re-run de `run_paired_headline` → CSV
  **bit-identique** (cmp).
- **CSVs** (untracked jusqu'au commit atomique) :
  `experiments/results/exp1_paired_headline.csv`,
  `exp1_regime_paired_headline.csv`, `exp1_decay_paired_headline.csv`,
  `exp1_robustness_headline.csv`, `exp4_eucore.csv` — chacun avec sidecar
  `.meta.json` (design, axes appariés complets, replicates_used, provenance
  du graphe pour exp4).
- **Analyses** : `experiments/cp1_analysis.py` (ré-analyse pure, aucune
  simulation) → `paper/cp1/cp1_tables.json` + 4 figures ;
  `experiments/validate_predictor.py` → `paper/cp1/predictor_validation.json`
  (graines V2 (20260802, 2), n_draws=800). Reproduire :
  `python experiments/cp1_analysis.py && python experiments/validate_predictor.py`.
- **Incident technique (sans impact scientifique)** : le premier lancement du
  pipeline via un heredoc stdin a fait boucler les workers `spawn` de
  multiprocessing (le module `__main__` doit venir d'un fichier) ; tâche tuée,
  aucun CSV partiel écrit, relance depuis un fichier de driver. Documenté ici.
- **Panel indépendant** (broadcast 5.5 % ± 3.4) : CSV committé
  `exp1_strategies_headline.csv`, inchangé.

## 8. Hors périmètre de ce paquet (attend l'arbitrage)

Réécriture du papier (S3), choix Route/titre, ratifications, commit atomique
(colonnes + bumps n=50 + câblage notebook 04 + CSVs + RESULTS_VERIFIED v2),
mise à jour limitations #16, REVIEWER_RATIONALE. Rien de tout cela n'a été
commencé, conformément au mandat.
