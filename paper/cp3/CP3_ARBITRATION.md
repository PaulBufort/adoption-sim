# CP3 — Arbitrage de la revue indépendante (S3.3)

**Date :** 2026-08-03 · **Candidat revu :** commit `5346724` (S3.2) ·
**Reviewer :** passe indépendante Opus (lecture seule, verdict *weak accept*,
tous les chiffres décisifs recalculés depuis les CSV appariés — zéro écart).
**Arbitre :** scientifique. **Implémentation :** S3.3. Entrée canonique :
`docs/decisions.md` **D23** ; corrigenda D19(b) et D22(a) ;
`RESULTS_VERIFIED.md` v3.

**Invariants S3.3 :** aucune simulation, aucune graine nouvelle ; tout calcul
additionnel dérive des CSV appariés déjà versionnés ; `final_rate` reste le
seul endpoint confirmatoire ; les contrastes cumulatifs restent descriptifs
(IC ponctuels non corrigés) ; 4 pages exactes ; figure papier inchangée
bit-à-bit ; audit étendu 35 → 42 claims ; 119 tests verts.

---

## 1. Table de décision point par point

| # | Point Opus | Décision | Justification / implémentation |
|---|---|---|---|
| S1.1 | « shared between-organization variance (9–16 pp) drops out » est faux (corr. médiane +0.18 ; −0.09 au headline, où l'appariement élargit l'IC de 4 %) | **ACCEPTÉ** | Erreur scientifique. L'appariement garantit le contrôle de la confusion (organisations et tirages identiques), pas un gain d'efficience. Manuscrit reformulé (« confound-free at the organization level, with no efficiency gain over independent sampling assumed ») ; corrélations post-hoc consignées dans D19(b) et PAS dans le papier ; « (9–16 pp) » supprimé. |
| S1.2 | « ignition 62 %/42 % » : coupe ≥ 10 % post hoc, à l'intérieur du mode bas | **ACCEPTÉ, AMENDÉ** | Erreur scientifique, rétractée (D22(a)). MAIS le seuil de remplacement 20 % proposé par Opus est refusé — également post hoc. Le papier ne cite plus que la forme bimodale elle-même : médianes des modes 9 %/85 %, aucun tirage entre 21 % et 82 % (split par plus grand écart, descriptif, `eucore.modes`). `eucore.ignition_share` supprimé de numbers.json. |
| S2.1 | Le croisement est annoncé dans la métrique qui le fait arriver le plus tôt ; à (1, .25) le contraste cumulatif est −1.8 [−5.4, +1.8], dans la bande | **ACCEPTÉ** | Le papier dit désormais : croisement endpoint-dependent ; terminal renversé à (1,.25) (−5.3, confirmatoire), cumulatif encore incertain (−1.8 [−5.4, +1.8], secondaire descriptif), négatif seulement à ρ=.40 (−7.4 [−10.7, −4.1]) ; renversement terminal à .25 dû principalement à la rétention différentielle (0.99 vs 0.86). Aucune nouvelle famille confirmatoire. |
| S2.2 | Abstract : 14+23≠40 ; les 23 équivalences sont structurellement dégénérées | **ACCEPTÉ EN PARTIE** | Abstract complet : « 14 of 40 cells (23 saturated or starved cells equivalent within ±2 pp, 3 uncertain, no cluster win of ≥2 pp) ». Le dénominateur « 14 of ~17 » d'Opus est REJETÉ (catégorisation post hoc). |
| S2.3 | « cluster seeding wins nowhere » trop fort ; « trois avantages cluster fiables » | **AMENDÉ** | Corps : « no cell shows a practically relevant cluster win (≥2 pp) — the largest cluster edge, 0.8 pp in the starved corner, sits inside the band ». L'affirmation d'Opus « trois fiables » est elle-même FAUSSE après Holm : un seul contraste sub-1 pp est Holm-significatif (θ̄=0.35, budget 1 %, −0.76 pp, p_holm<10⁻⁴ ; les deux autres : 0.17, 0.97). Consigné dans `regime_map.largest_cluster_edge`. |
| R1 | Ajouter random−cluster à p_innov=0 (+21.4 [14.9, 27.9]) au papier | **REJETÉ** | Panel indépendant n=12/bras (Welch) — la politique de source D19 (amendement 2) interdit de citer le panel indépendant pour un contraste entre stratégies semées. Conservé dans `REVIEWER_RATIONALE.md` v3 comme réponse orale exploratoire, étiquetée comme telle. |
| R2 | Ajouter le plafond volontaires ≈ 86 % | **REJETÉ** | Requis par aucune claim ; ajouterait un chiffre hors chaîne d'audit. Réponse orale dans RATIONALE v3. |
| R3 | Chronologie : « pre-specified before execution » lit trop fort | **ACCEPTÉ** | Manuscrit : « pre-specified in a version-controlled decision log — after exploratory n=12 panels, before the confirmatory run ». Aucune prétention de préspécification antérieure à toute exploration. |

## 2. Diff scientifique du manuscrit (avant → après)

| Zone | Avant (S3.2) | Après (S3.3) |
|---|---|---|
| Abstract, carte | « winning 14 of 40 cells … and losing none (23 cells equivalent within ±2 pp) » | « winning 14 of 40 cells … (23 saturated or starved cells equivalent within ±2 pp, 3 uncertain, no cluster win of ≥2 pp) » |
| Abstract, decay | « the advantage shrinks and reverses » | « the **terminal-adoption** advantage shrinks and reverses » |
| §2 appariement | « paired differences from which the shared between-organization variance component (9–16 pp) drops out » | « within-organization paired differences — confound-free at the organization level, with no efficiency gain over independent sampling assumed » |
| §2 chronologie | « pre-specified … before execution » | « pre-specified … after exploratory n=12 panels, before the confirmatory run » |
| §3 carte | « **cluster seeding wins nowhere** » | « no cell shows a practically relevant cluster win (≥2 pp) — the largest cluster edge, 0.8 pp in the starved corner, sits inside the band » |
| §3 decay | « Cumulative reach clarifies the pattern: … 29.0 % (vs. 72 %) … retention 0.99 vs 0.86 » | « It is also endpoint-dependent: … terminal reversed, cumulative still uncertain (−1.8 pp [−5.4, +1.8]; **clearly** negative only at ρ=0.40: −7.4 pp [−10.7, −4.1]) — driven mainly by differential retention, 0.99 vs 0.86 … 29.0 % vs 72 % » |
| §3 Eu-core | « a bimodal ignition lottery: random ignites in 62 % of draws, cluster in 42 % » | « bimodal: draws end low (median 9 %) or high (median 85 %), none between 21 % and 82 % » |
| §4 | « (D1–D22) » | « (D1–D23) » |
| Layout | figure \textwidth ; vspace bib −14pt | figure 0.92\textwidth ; display-skips 5/3 pt ; emergencystretch 2 pt ; vspace bib −18 pt (4 pages exactes, 0 overfull) |

Nouvelles valeurs publiées (toutes recalculées des CSV versionnés, auditées) :
cumulatif (1, .25) **−1.8 pp [−5.4, +1.8]** (p=0.31) ; cumulatif (1, .40)
**−7.4 pp [−10.7, −4.1]** ; plus grand avantage cluster **0.8 pp** (θ̄=0.35,
1 %, classé équivalent, seul Holm-significatif) ; modes Eu-core **9 %/85 %**,
intervalle vide **]21 %, 82 %[** (gap 61.9 pp).

## 3. Modifications hors manuscrit

- `paper/extract_numbers.py` : + `decay.cumulative_contrasts`,
  + `regime_map.largest_cluster_edge`, `eucore.ignition_share` →
  `eucore.modes` (split par plus grand écart, descriptif).
- `paper/audit_numbers.py` : 35 → **42 claims** ; claim « eucore ignition »
  retirée ; garde-fou : si une cellule win_y apparaît un jour, la claim
  « no cluster win » devient introuvable et l'audit échoue.
- `docs/decisions.md` : D19(b), D22(a) (textes originaux conservés), **D23**
  (cette table), ligne D23 dans l'index.
- `RESULTS_VERIFIED.md` : section **v3** en tête ; marqueur de rétractation
  sur la puce v2 « ignition 62/42 ».
- `CLAUDE.md` : bloc key-numbers aligné (42 claims, retenue vs variance,
  modes Eu-core, cumulatifs).
- `docs/limitations.md` #21 : « bimodal ignition-lottery » → « bimodal
  outcome regime » + rappel « aucun taux d'ignition cité » (21 entrées,
  inchangé).
- `paper/REVIEWER_RATIONALE.md` : bloc v3 (réponses orales, dont p_innov=0
  étiqueté panel indépendant non citable).
- `paper/cp1/CP1_ARBITRATION.md` : deux encarts corrigendum (appariement,
  Eu-core) — texte historique intact.
- `experiments/cp1_analysis.py` : titre `fig_eucore` « bimodal ignition
  lottery » → « bimodal outcomes » ; régénération vérifiée par hash —
  **seul `fig_eucore.png` change**, `exp1_crossover.png` (figure papier),
  les 3 autres figures CP1 et `cp1_tables.json` sont bit-identiques.

## 3b. Micro-passe de cohérence (2026-08-03, post-arbitrage, feu vert humain)

Trois résidus corrigés, aucune conclusion modifiée :

1. « negative only at ρ=0.40 » (ambigu — le contraste moyen est déjà −1.8 à
   ρ=0.25) → « **clearly** negative only at ρ=0.40 » dans `main.tex` ; même
   levée d'ambiguïté dans RESULTS_VERIFIED v3 et RATIONALE v3 (« pointwise
   CI excluding zero only at ρ=0.40 »).
2. `docs/limitations.md` #16 aligné sur D23 : sans decay, dominance dans la
   **bande d'allumage testée** ; 14 / 23 (saturation-famine) / 3 ; aucun
   avantage cluster ≥ 2 pp, le plus grand = 0.8 pp dans la bande ; daté CP3
   2026-08-03. (Toujours 21 entrées.)
3. RESULTS_VERIFIED v3 : l'en-tête ne dit plus « every figure PNG
   bit-identical » — CSV et nombres appariés inchangés, figure papier
   bit-identique, `fig_eucore.png` régénérée (titre corrigé, mêmes données).

## 4. Vérification S3.3 (à re-exécuter avant commit)

- [x] `python paper/extract_numbers.py` idempotent ; `audit_numbers.py` → 42/42.
- [x] PDF : 4 pages (pypdf, jamais mdls), 0 overfull, figure entière.
- [x] Régénération CP1 : hashes identiques sauf fig_eucore.png (voulu).
- [x] pytest : 119 verts.
- [ ] Revue humaine du diff puis commit atomique S3.3 (règle CLAUDE.md :
      changement de claim scientifique ⇒ validation explicite avant commit).
