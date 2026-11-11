# Mini-compte rendu S5 — Groupe 1 (à reporter dans le modèle du professeur)

Présentation : 10 minutes, par Zineb (cheffe de projet).

## Réalisé

- [ ] Bouton Odoo « Prédire la volatilité » : série de prix → σ historique et σ prévue par le LSTM → deux prix Black-Scholes côte à côte (capture `docs/captures/s5_prediction.png`)
- [ ] Historique des prévisions dans Odoo (`cours.vol.prediction`, menu « Prévisions LSTM »)
- [ ] Inférence du LSTM en NumPy dans Odoo, sans TensorFlow, modèle monté dans le conteneur
- [ ] Tests : 34 tests pytest, 13 tests Odoo (dont intégration bouton → IA → prix)
- [ ] Rotation des rôles effective ; Gantt réalisé mis à jour

## Décisions

1. Le prix « σ prédite » est présenté comme une seconde estimation, pas comme un meilleur prix (écart d'horizon : 5 jours contre la maturité de l'option).

## Difficultés et questions

- (à compléter en fin de semaine)

## Prévu pour la S6

- Module finalisé (gel des fonctionnalités) ; rapport rédigé à 80 % avec le Gantt.
