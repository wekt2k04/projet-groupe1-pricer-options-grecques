# Mini-compte rendu S1 — Groupe 1 (à reporter dans le modèle du professeur)

Séance du 11 novembre 2026. Présentation : 10 minutes, par le chef de projet (rotation du présentateur à chaque séance).

## Réalisé

- [x] Dépôt GitHub créé, avec la structure de l'annexe A du guide (`docs/`, `src/`, `tests/`, `notebooks/`, `odoo_addons/`)
- [ ] Les 4 autres membres invités, avec un premier commit de chacun (`docs/membres/`) : en cours
- [x] Docker : Odoo 17 + PostgreSQL 15 (`docker compose up -d --build`). Le module du TP 0 `cours_derives` est déposé dans `odoo_addons/` et installé sans erreur dans la base `groupe1`. L'image Odoo contient numpy, donc le module peut importer `src/pricing.py` (vérifié dans le conteneur : 10,4506)
- [x] Source des données : yfinance, ticker AAPL, 2 ans de cours ajustés ; repli CSV documenté (`src/data.py`)
- [x] Fiche de lecture rendue (`docs/fiche_lecture.pdf`, 2 pages). Elle contient les formules, les Grecques, la volatilité et le LSTM, le lien avec le TP 0, l'algorithme Python et les hypothèses de marché
- [x] Schéma de base de données (`docs/schema_bdd.png`, `tools/build_schema.py`) : extension de `cours.option` et de `cours.portfolio`, avec deux modèles nouveaux pour la volatilité
- [x] Gantt prévisionnel déposé (`docs/gantt_previsionnel.png`, source `docs/gantt_source.xlsx`). Il contient les responsables, les durées, un mini-compte rendu chaque semaine, la fiche, la rotation en S4, le rapport à 80 % en S6 et la soutenance
- [x] En avance sur la S2 : pricer Black-Scholes et Grecques, avec 25 tests pytest verts (20 pour le pricer, 5 pour les données)

## Décisions à présenter

1. Conventions d'unités communes (`CONVENTIONS.md`) : `T` en années, `r` continu, `sigma` annualisée, tous en décimal.
2. **Noms de champs** : on garde ceux de notre module du TP 0 (`type`, `S0`, `K`, `T`, `r`, `sigma`, `bs_price` existent déjà). On ajoute seulement les Grecques, `sigma_lstm` et `bs_price_lstm` par `_inherit`. Pas de `spot` ni de `strike`, qui feraient doublon.
3. Le code financier reste hors d'Odoo (`src/pricing.py`, testé par pytest) et Odoo l'importe. L'IA est entraînée hors d'Odoo ; Odoo ne fait que l'inférence.
4. Rôles proposés et rotation en fin de S4 : voir le README (à valider en séance).

## Difficultés et questions

- Noms de champs à communiquer aux groupes 4 et 7, qui étendent aussi `cours.option`.
- Séance de la S2 : confirmer la date (le 18 novembre est férié au Maroc).
- Question au professeur : le guide ne définit des rôles que pour 3 ou 4 membres ; nous en avons 5.

## Prévu pour la S2

- Notebooks `01_donnees` et `02_modele_python` : prix et Grecques sur AAPL, graphiques de Delta et de Gamma en fonction du spot, validation par différences finies.
- Premier commit de chaque membre.
- Gantt mis à jour.
