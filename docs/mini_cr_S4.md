# Mini-compte rendu S4 (mi-parcours) — Groupe 1 (à reporter dans le modèle du professeur)

Présentation : 10 minutes, par Hiba (ingénieure IA).

## Réalisé

- [ ] Vues Odoo : formulaire (Paramètres, Résultats / Grecques, boutons « Calculer » et « Courbe Delta(S) »), liste avec Grecques, graphique Delta(S) (captures `docs/captures/s4_*.png`)
- [ ] LSTM entraîné sur 10 ans d'AAPL, variantes V0 (guide) et V1 (sans chevauchement), découpage chronologique 70 / 15 / 15
- [ ] Comparaison sur le test avec persistance, EWMA et GARCH(1,1) : tableau RMSE / QLIKE (`docs/figures/resultats_ia.csv`)
- [ ] Modèle exporté pour Odoo (`models/lstm_vol.npz`), inférence NumPy identique à Keras
- [ ] Gantt réalisé (`docs/gantt_realise.png`) ; rotation des rôles annoncée

## Décisions

1. Le modèle présenté est la variante V1 ; V0 est gardée pour montrer pourquoi la cible du guide favorise la persistance.
2. Le résultat est présenté tel quel, même si une référence simple fait mieux.

## Difficultés et questions

- (à compléter en fin de semaine)

## Prévu pour la S5 (après rotation)

- Bouton Odoo « Prédire la volatilité » : LSTM → `sigma_lstm` → prix avec σ prédite à côté du prix avec σ historique ; tests d'intégration.
