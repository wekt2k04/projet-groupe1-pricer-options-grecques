# Mini-compte rendu S3 — Groupe 1 (à reporter dans le modèle du professeur)

Présentation : 10 minutes, par Fatima-ezzahraa (développeuse Odoo).

## Réalisé

- [ ] `cours.option` étendu par `_inherit` : 5 Grecques calculées et stockées, `sigma_lstm`, `bs_price_lstm` ; bouton « Calculer »
- [ ] `cours.portfolio` étendu : Delta du portefeuille (signé selon la position)
- [ ] Capture d'écran : option de référence, prix 10,4506 et Delta 0,6368 (`docs/captures/s3_grecques.png`)
- [ ] Tests Odoo (`TransactionCase`) : valeurs de référence call et put, parité, recalcul, entrée invalide, Delta du portefeuille
- [ ] IA : jeux de données V0 (guide) et V1 (sans chevauchement), références persistance / EWMA / GARCH, métriques RMSE et QLIKE ; 33 tests pytest

## Décisions

1. Le calcul financier reste dans `src/pricing.py`, importé par Odoo : une seule source de vérité.
2. Inférence du LSTM en NumPy dans Odoo (pas de TensorFlow dans l'image), vérifiée identique à Keras par un test.

## Difficultés et questions

- (à compléter en fin de semaine)

## Prévu pour la S4

- Vues complètes et graphique Delta(S) ; LSTM entraîné et comparé aux références ; rotation des rôles ; Gantt réalisé.
