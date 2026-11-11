# Mini-compte rendu S2 — Groupe 1 (à reporter dans le modèle du professeur)

Présentation : 10 minutes, par Assia (quant / data).

## Réalisé

- [ ] Notebook `01_donnees` : AAPL sur 2 ans (yfinance, repli CSV versionné), rendements log, σ historique annualisée, volatilité glissante sur 5 jours
- [ ] Notebook `02_modele_python` : formules de Black-Scholes et des 5 Grecques écrites et expliquées ; cas de référence (call 10,4506, put 5,5735, Delta 0,6368)
- [ ] Validation : différences finies (écart relatif < 1e-4), parité call-put sur 72 combinaisons (écart < 1e-10), 25 tests pytest verts
- [ ] Graphiques : Delta(S) et Gamma(S), prix selon σ et T (`docs/figures/`)
- [ ] Données sur 10 ans prêtes pour le LSTM ; capture d'Odoo installé
- [ ] Gantt réalisé mis à jour

## Décisions

1. σ historique = écart-type des rendements log × √252 ; T en années sur 365 jours.
2. Le taux sans risque du cas AAPL sera sourcé (bon du Trésor à 3 mois) avant le rapport.

## Difficultés et questions

- (à compléter en fin de semaine)

## Prévu pour la S3

- Extension de `cours.option` dans Odoo : Grecques calculées et stockées, bouton « Calculer », première capture.
- Tests Odoo (`TransactionCase`) ; fonctions de données du LSTM.
