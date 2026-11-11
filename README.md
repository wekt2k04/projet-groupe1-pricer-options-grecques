# Groupe 1 — Projet 1 : Pricer d'Options & Grecques

Module *Finance des Marchés et ERP* — ENSA Safi, cycle ingénieur Informatique Décisionnelle et IA, 2026-2027.

Nous construisons un outil qui valorise une option européenne avec Black-Scholes, calcule ses cinq Grecques, les expose dans Odoo en étendant `cours.option` (module `cours_derives` du TP 0), et utilise un LSTM pour prédire la volatilité du lendemain. C'est le projet « socle » : les groupes 4, 5, 6, 7 et 9 réutilisent notre `bs_price` et `greeks`.

**À lire en premier : [`docs/MATIERE.md`](docs/MATIERE.md)** — la matière dans son ensemble (dérivés, binomial, Black-Scholes, volatilité, portefeuille, CAPM, Odoo, IA, carte des 10 projets) ; **puis [`docs/COMPRENDRE.md`](docs/COMPRENDRE.md)** — ce que chaque membre doit savoir expliquer sur notre projet, avec les chiffres de référence et les questions de soutenance probables. Les unités communes sont dans [`CONVENTIONS.md`](CONVENTIONS.md).

**Membre du groupe : ta feuille de route est [`CLAUDE.md`](CLAUDE.md) §14** (installation, règles notées, ton rôle, ta prochaine tâche, façon de contribuer) ; le plan étape par étape est au §9.

## Démarrage rapide

```bash
python -m venv .venv && source .venv/bin/activate      # Windows : .venv\Scripts\activate
pip install numpy scipy pandas matplotlib pytest yfinance   # S1 ; le reste de requirements.txt arrive en S3
pytest                                                  # 25 tests, tous verts
docker compose up -d --build                            # Odoo 17 (+ numpy) sur http://localhost:8069
docker compose run --rm web odoo -d groupe1 -i cours_derives --stop-after-init   # crée la base et installe le TP 0
```

```python
from pricing import bs_price, greeks      # depuis src/ (pytest.ini règle le chemin)
bs_price(100, 100, 1, 0.05, 0.20, "call")   # 10.4506
greeks(100, 100, 1, 0.05, 0.20, "call")     # delta 0.6368, gamma 0.0188, vega 37.52, theta -6.41, rho 53.23
```

## Arborescence

| Dossier / fichier | Contenu |
|---|---|
| `src/pricing.py` | Black-Scholes, Grecques, parité call-put (sans Odoo, SciPy facultatif) |
| `src/data.py` | cours yfinance, repli CSV, simulation GBM, volatilité historique |
| `tests/` | tests pytest : parité, différences finies, équation de Black-Scholes, cas limites ; données sans réseau |
| `notebooks/` | `01_donnees`, `02_modele_python`, `03_ia` (S2 à S4) |
| `odoo_addons/cours_derives/` | module réel du TP 0 (déposé en S1, installé dans la base `groupe1`), étendu en S3 |
| `docs/membres/` | une fiche par membre : c'est le premier commit de chacun (voir `docs/membres/README.md`) |
| `docs/` | `MATIERE.md` (la matière), `COMPRENDRE.md` (le projet), fiche de lecture, Gantt prévisionnel et réalisé, schéma de base de données, mini-comptes rendus, rapport |
| `tools/` | scripts qui régénèrent la fiche de lecture, le Gantt et le schéma de base de données |
| `CLAUDE.md` | fichier de pilotage : état d'avancement, décisions, plan étape par étape (§9), guide du membre (§14), règles des sessions Claude (§11) |
| `docker-compose.yml`, `Dockerfile.odoo` | Odoo 17 (+ numpy, pour importer `src/pricing.py`) + PostgreSQL 15 |

## Discipline Git

Un commit par semaine et par membre au minimum, avec le prénom dans le message : `[Prénom] verbe + objet`, par exemple `[Wilfried] Ajout des tests de parité call-put`. Une branche courte par fonctionnalité, une pull request relue par un autre membre avant fusion.

## Équipe et rôles

| Membre (filière) | GitHub | Rôle S1 à S4 | Rôle S5 à S7 (après rotation) |
|---|---|---|---|
| TSETSE Komla Edem Wilfried (IDIA3) | `wekt2k04` | Chef de projet / finance | Quant / data |
| SADOUR Assia (IDIA3) | `as7ia` | Quant / data | Ingénieur IA |
| EL ANKOUD Fatima-ezzahraa (GINF3) | `fatimaezzahraaelankoud` | Développeuse Odoo | Qualité et intégration |
| BOULHAIL Hiba (IDIA3) | `Hiba-2004` | Ingénieure IA | Développeuse Odoo (branche son modèle derrière le bouton) |
| ELAMRANI Zineb (GINF3) | `elamrani-zineb` | Qualité et intégration | Cheffe de projet (rapport) |

Répartition **proposée, à valider en séance** ; chaque membre confirme sa ligne par son premier commit (`docs/membres/`). Rotation obligatoire à la fin de la S4 (guide, §3.1).

## Avancement

| Semaine | Livrable attendu | État |
|---|---|---|
| S1 | dépôt, Docker, source des données, fiche de lecture, schéma de base, Gantt prévisionnel | fait ; reste : invitations et premier commit de chaque membre |
| S2 | prototype Python, tests, notebook | à faire |
| S3 | extension Odoo de `cours.option` | à faire |
| S4 | vues Odoo, LSTM entraîné, rotation des rôles, Gantt mis à jour | à faire |
| S5 | le bouton Odoo déclenche le calcul et l'IA ; tests | à faire |
| S6 | module finalisé, rapport à 80 % | à faire |
| S7 | rapport final avec Gantt, code zippé, soutenance de 15 minutes | à faire |