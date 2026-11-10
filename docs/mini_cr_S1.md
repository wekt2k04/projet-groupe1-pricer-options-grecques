# Mini-compte rendu S1 — Groupe 1 (à reporter dans le modèle du professeur)

Séance du 11 novembre 2026. Cocher ce qui est réellement fait avant de présenter.

## Réalisé

- [ ] Dépôt GitHub créé, les 5 membres invités (`docs/`, `src/`, `tests/` en place)
- [ ] Docker installé, Odoo 17 lancé, capture de la page Applications avec le mode développeur
- [ ] Source des données choisie : yfinance, ticker AAPL, 2 ans de cours ajustés ; repli CSV documenté
- [ ] Fiche de lecture théorique rendue (`docs/fiche_lecture.pdf`)
- [ ] Schéma de base de données (`docs/schema_bdd.png`) : extension de `cours.option`
- [ ] Gantt prévisionnel déposé (`docs/gantt_previsionnel.png`, source `gantt_source.xlsx`)
- [ ] Pricer Black-Scholes et Grecques écrits, 25 tests pytest verts (20 pricer, 5 données) (en avance sur la S2)

## Décisions à présenter

1. Conventions d'unités communes (`CONVENTIONS.md`) : `T` en années, `r` continu, `sigma` annualisée en décimal.
2. `cours.option` du TP n'a ni `spot`, ni `maturite`, ni `taux`, ni `volatilite` : on les ajoute par `_inherit`.
3. Le code financier reste hors d'Odoo (`src/pricing.py`) et se repose sur `math.erf` si SciPy est absent.

## Difficultés et questions

- Noms de champs de `cours.option` à aligner avec les groupes 4 et 7.
- Séance de la S2 : confirmer la date (le 18 novembre est férié au Maroc).

## Prévu pour la S2

Notebooks `01_donnees` et `02_modele_python` (prix et Grecques sur AAPL, graphiques Delta et Gamma en fonction du spot), validation par différences finies, Gantt mis à jour.
