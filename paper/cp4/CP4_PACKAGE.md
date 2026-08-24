# CP4 — Paquet de soumission CN2026 (S4)

**Date :** 2026-08-03 · **Candidat scientifique :** `1e4f59b` (S3.4, validé
CP3 « clear accept ») · **HEAD S4 :** `19ab3ea` + ce paquet · **Décision
recommandée : GO** (validation humaine finale requise avant toute action
externe). Aucun push, aucun tag, aucune soumission CMT effectués.

Vérification d'identité : `git diff 1e4f59b..19ab3ea` est **vide** sur
`experiments/results/*`, `paper/numbers.json`, `paper/main.tex`,
`paper/main.pdf`, `figures/*.png`, `paper/cp1/*.json` — les commits S4 sont
purement documentaires.

---

## 1. Changements S4 dans le dépôt (avec justification)

| Commit | Contenu | Justification |
|---|---|---|
| `907bb06` S4.1 | Notebook 01 : section « regime map » remplacée par une note de supersession (D18/D23, lecture confirmatoire 14/23/3, plus grand avantage cluster 0.8 pp) ; cellule de code n=12 supprimée ; footer corrigé (D1–D23, 21 entrées de limitations) avec sortie vidée honnêtement (non ré-exécuté) ; `make_all.py` n'attend plus `exp1_regime.png` | Empêcher toute confusion exploratoire n=12 ↔ confirmatoire n=50 ; le pipeline suivi ne peut plus régénérer d'artefact périmé |
| `19ab3ea` S4.2 | README : 67→119 tests (×2), D18–D23 ajoutés à la ligne de ratification ; `exp1.py` : deux commentaires PROVISIONAL → RATIFIED (D18/D19, CP1) + docstring `run_regime_map` actualisée ; `exp3.py` : le corollaire « cannot reorder » est annoté RETRACTED (D17(a)) ; `docs/decisions.md` : deux renvois inline *[⚠ … see D19(b)]* sur les formulations historiques (trace intacte) ; `paper/README.md` : provenance (politique D19, 42 claims, audit) et checklist CMT actualisées | Mentions actives périmées ; renvoi inline D19(b) demandé au mandat S4 |
| S4.3 (ce commit) | `paper/cp4/` (ce paquet) ; `.gitignore` + `submission/` | Livraison ; `submission/` est ignoré car il ne contient que des copies dérivées octet-à-octet et du matériel de collage CMT, dont la provenance est fixée par SHA-256 ici |

**Artefacts non suivis supprimés (autorisation explicite S4)** — hashes au
moment de la suppression :

```
fdc94f3b1e93bb1f4d1944452e4500c3918b0fdc3ccf605754fae8d81bbc85bb  experiments/results/exp1_regime_headline.csv
cfc801390cb9bed3bc9528e30e675a605a5d5f7b148a0cfa23a0907096fc0738  experiments/results/exp1_regime_headline.meta.json
26c1a960075a5ee24b8a1a1bbaaa07c128c494b6a3d17f9b40f6c78c2470a68f  figures/exp1_regime.png
```

Vérification préalable : après S4.1, plus aucun fichier suivi ne lit ces
artefacts (les deux seuls « hits » grep restants sont les notes expliquant la
suppression). Aucun autre fichier supprimé.

---

## 2. Rapport de reproduction clean-room

**Verdict : REPRODUCTION PARFAITE — 15/15 artefacts scientifiques
bit-identiques, 0 divergence.**

- **Commit reproduit :** `19ab3ea` (artefacts scientifiques bit-identiques à
  `1e4f59b`, cf. supra), clone `git clone file://… && git checkout 19ab3ea`
  dans un répertoire temporaire hors du worktree canonique.
- **Environnement :** macOS 15 (Darwin 25.5.0), Python **3.13.13**
  (python.org), venv frais ; `pip install -r requirements-dev.txt -c
  constraints.txt` (28 s) → numpy **2.4.6**, networkx **3.6.1**, matplotlib
  **3.10.9** — identiques aux sidecars de provenance. Moteur LaTeX :
  tectonic (binaire système, cache local).
- **Entrées externes :** les deux fichiers SNAP non suivis
  (`data/raw/email-Eu-core.txt.gz`, `…-department-labels.txt.gz`) ont été
  **copiés** du worktree canonique (réseau non utilisé), hashes identiques
  vérifiés — `4b47acdb…` / `e5abe5b4…`. `experiments/fetch_eucore.py` reste
  la voie documentée.
- **Déviation d'outillage consignée :** un driver fichier `clean_driver.py`
  a été écrit dans le clone (non suivi) parce que le lancement par
  stdin/heredoc fait boucler les workers multiprocessing spawn — incident
  documenté au CP1 §7 ; le driver n'introduit **aucun** choix (scénarios et
  graines gelés inchangés). La comparaison sémantique du PDF a utilisé pypdf
  depuis le venv canonique (outil d'analyse, lecture seule).

**Commandes réellement utilisées et durées :**

```
git clone file://<canonique> repo && git checkout 19ab3ea        2.1 s
python3.13 -m venv .venv-clean                                    2.0 s
pip install -r requirements-dev.txt -c constraints.txt           28.4 s
python -m pytest -q                                →  119 passed  9.9 s
python clean_driver.py            (6 744 simulations)           139.8 s
   exp1_strategies 250 rows 5.3 s · exp1_pinnov 144 rows 3.1 s
   paired_headline 200 rows 4.6 s · paired_regime 4 000 rows 76.4 s
   paired_decay 1 200 rows 26.0 s · robustness 800 rows 23.9 s
   exp4_eucore 150 rows 0.5 s
python experiments/validate_predictor.py                         49.1 s
python experiments/cp1_analysis.py                                2.7 s
python paper/extract_numbers.py                                   0.8 s
python paper/audit_numbers.py     → audit OK — 42 claims          0.4 s
tectonic main.tex                 → 0 erreur, 0 overfull          2.3 s
                                            TOTAL mur ≈ 4 min
```

**Manifeste — classe A (bit-identiques REQUIS) : 15/15 IDENTIQUES**

```
c181af01272828aafc919b751dfaf039fca45fe82670030c2f1a25ddad6eb36c  exp1_paired_headline.csv
d468d629bcefcb2dc1a02a9310e110bbfbba7c8c4287ab504d41d48cdd5ae007  exp1_regime_paired_headline.csv
2a2e741568cc18cdd9beac17068966cd4b8dd0a28621bb8f726386e799112123  exp1_decay_paired_headline.csv
4b0d7be1157596c59efab07d6c59bb90016fc13e56cff946ebc7c8a513594d34  exp1_robustness_headline.csv
3937aa7853831ce98ba0090ba20adc3426eec4fdd39f7376df33531f91b74d38  exp4_eucore.csv
8baa2de7570a2e1db7572f84a5b090a413cfa91136f60becaa9288b330cb4d61  exp1_strategies_headline.csv
6ba86178bf9748d179c4b13213444354e46a8d6165c36e9728e648ccc24cf8ee  exp1_pinnov_headline.csv
63c9602c01962d58f4894c8e97ab33c09c6ee67a5ca14de05fcb23bb87e5dfea  paper/numbers.json
c5af07dc6aa555c3353103089f8a3e9ec2b0bc11db402b68cf58b95421bc6b0d  figures/exp1_crossover.png
c241b0328236cbac3257b72724b1c91dea1a191bf432a81571661bb5fa694f61  paper/cp1/cp1_tables.json
43301d26a78c11d63ac6d3413ce36bd36bfa216d0665293523b8137fc29beaa6  paper/cp1/predictor_validation.json
3d18f843cdb49812fdd5c667914731bbbb17671275882b8b5308916332b8485e  paper/cp1/fig_regime_3class.png
15bd15cbe4b8a97cc20446b0d51f4cbf6833d2cb9d3b07695c450ae1b6636b95  paper/cp1/fig_decay_family.png
7298e6e1269277fb2564607a7f8f73654cff108e2c7d1a5db2c210cfd138ffd8  paper/cp1/fig_robustness.png
abc59e26b463a2f7ced9178ac906ae8b31b47accc060421dcb54f62b35a05255  paper/cp1/fig_eucore.png
```

**Classe B (variation de métadonnées tolérée) :** les 7 sidecars
`.meta.json` (seuls champs modifiés : `generated_utc`, `git_commit` —
vérifié par diff champ à champ) et `paper/main.pdf` (métadonnées de build).
**Comparaison sémantique du PDF reconstruit :** 4 pages ; texte des 4 pages
**strictement identique** ; image de figure embarquée **bit-identique**
(sha256 du flux) ; jeux de polices identiques ; taille identique
(218 513 octets). Aucune différence, même bénigne, au-delà des champs listés.

---

## 3. QA du PDF de soumission — PASS/FAIL

| Critère CN2026 | Verdict | Preuve |
|---|---|---|
| Extended abstract ≤ 4 pages | **PASS** | 4 pages exactes (pypdf) |
| Format Springer LLNCS | **PASS** | `llncs.cls` + `splncs03.bst` officiels, 612×792 pt |
| Single-blind : auteur conservé | **PASS** | Nom, affiliation, email en page 1 |
| Titre/nom/affiliation/email/ORCID cohérents | **PASS** | « Paul Bufort · Independent Researcher · ORCID 0009-0000-6080-1887 · paulbufort@paulbufort.com » |
| Aucune référence cassée | **PASS** | 0 « ?? » ; build sans warning de référence |
| 12 références présentes et citées | **PASS** | 12 entrées bib = 12 clés \cite ; [1]–[12] tous retrouvés dans le texte rendu |
| Polices incorporées | **PASS** | 10/10 avec FontFile (sous-ensembles) |
| Texte sélectionnable | **PASS** | 11 440 caractères extraits |
| Annotations / pièces jointes / JS / OpenAction | **PASS** | 0 / non / non / non |
| Métadonnées indésirables | **PASS** | /Info = Creator tectonic, Producer xdvipdfmx, date — rien d'autre |
| Figure lisible à l'impression | **PASS** | PNG 2401 px pour ~11.2 cm ⇒ ≈ 545 dpi ; contrôle visuel des 3 panneaux |
| Aucune coupure/superposition/overfull | **PASS** | 0 overfull ; rendu visuel des 4 pages contrôlé |
| Distinction topologie réelle / attributs synthétiques | **PASS** | Abstract + §3 + stamp figure |

**Fichier de livraison :** `submission/Bufort_CN2026_Extended_Abstract.pdf`
— copie octet-à-octet de `paper/main.pdf` (vérifiée par `cmp`).

```
SHA-256  16f28ca641fa8a6f20ce7360397b17ba4882074b9bb2cf4554f60fb27394e5a8
```

### Addendum 2026-08-23 — reconstruction après changement d'adresse de contact

`paper/main.tex` et `paper/main.pdf` ont été régénérés pour remplacer
l'adresse de contact de l'auteur par `paulbufort@paulbufort.com`. Le hash
ci-dessus reste le registre de la livraison CP4 (`19ab3ea`) et n'est pas
modifié.

- Nouveau `paper/main.pdf` : SHA-256
  `0c29888468bdfc8998118db849f5fd6392414d29100ebfef26b4e597fe58427f`
- L'équivalence octet-à-octet entre `paper/main.pdf` et
  `submission/Bufort_CN2026_Extended_Abstract.pdf` établie au CP4 **ne vaut
  plus** — elle avait déjà cessé de valoir au CP4 même, le fichier de
  livraison provenant depuis le 2026-08-13 de `Draft1_CN2026_v27.tex`.
- Fichier de soumission régénéré le 2026-08-23 depuis `Draft1_CN2026_v27.tex`
  (adresse seule ; SHA-256 `2a98f069…1192`), puis **re-typographié le
  2026-08-24 sur le gabarit LLNCS officiel de la conférence**
  (`Draft1_CN2026_v29_llncs.tex`, 24 resserrages de forme validés par
  l'auteur — aucun chiffre ni caveat modifié) : SHA-256
  `04c47d9642f950754cde7e29ac93d574efcd2dbfbe3b9b14add3cd378526dd2d`.
  QA v29 : 4 pages, 0 « ?? », 25/25 polices, caveats D19(b)/D20/D21/D22(a)
  vérifiés présents. Détail et historique des hashes dans
  `submission/CMT_METADATA.txt`.
- Diff sémantique ancien → nouveau PDF : **2 tokens** (ancienne adresse
  retirée, nouvelle ajoutée). Aucune autre différence de texte.
- QA rejouée : 4 pages · 0 « ?? » · 30/30 polices avec FontFile ·
  `audit_numbers.py` OK (42 claims).


---

## 4. Métadonnées CMT (préparées, PAS soumises)

- **Console :** https://cmt3.research.microsoft.com/COMPLEXNETWORKS2026
- **Échéance : 2026-09-02, 23:59 AoE** — cible de dépôt 2026-08-30/31.
- **Type :** Extended Abstract.
- **Titre :** Disperse to ignite, concentrate to endure: a decay-driven
  crossover in modular complex contagions
- **Auteur :** Paul Bufort — Independent Researcher —
  paulbufort@paulbufort.com — ORCID 0009-0000-6080-1887
- **Abstract (texte brut) :** voir `submission/CMT_METADATA.txt` (dérivé
  fidèlement du résumé du papier, jamais le texte complet).
- **Mots-clés (5) :** complex contagion; threshold models; seeding
  strategies; organizational networks; agent-based simulation
- **Domaines (recommandation conceptuelle, à faire correspondre aux libellés
  réels affichés par CMT — ne rien inventer ; en cas de doute, capture
  d'écran au moment de la saisie) :** primaire = diffusion/spreading &
  dynamique sur réseaux ; secondaires = réseaux sociaux/organisationnels ·
  modèles multi-agents/simulation · structure de communautés/modularité ·
  interventions sur réseaux (si un tel libellé existe).
- **Fichier à téléverser :** `Bufort_CN2026_Extended_Abstract.pdf`
  (SHA-256 ci-dessus).

**Champs exigeant une décision ou saisie humaine dans CMT :** création/login
du compte ; correspondance finale des domaines (libellés réels) ; cases de
consentement/conditions ; déclarations de conflits ; clic final « Submit ».
Rappel déontologique déjà arbitré : publication scientifique non rémunérée =
zone verte (art. 14 §5, mémo du 2026-06-19).

---

## 5. Checklist de soumission

- [x] Candidat scientifique gelé (`1e4f59b`, CP3 clear accept)
- [x] Hygiène dépôt (S4.1–S4.2) ; artefacts n=12 supprimés
- [x] Clean-room : 119 tests · 6 744 sims · audit 42/42 · 15/15 bit-identiques
- [x] QA PDF : 13/13 PASS
- [x] Copie de livraison + SHA-256
- [x] Métadonnées CMT prêtes (domaines à confirmer sur libellés réels)
- [ ] **Validation humaine du paquet CP4** ← vous êtes ici
- [ ] Push (autorisation séparée)
- [ ] Saisie CMT + Submit (humain, avec les libellés réels de domaines)
- [ ] Visibilité du dépôt : publique **à la publication** seulement (D-repo)

## 6. Recommandation

**GO.** Reproduction clean-room parfaite, QA de soumission entièrement
verte, chaîne de traçabilité (extract → numbers → audit → CI) intacte de
bout en bout. Aucune décision scientifique ouverte ; les seuls actes
restants sont humains et externes (validation CP4, push, saisie CMT).
