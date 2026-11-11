# 6. Tests et qualité

| Niveau | Outil | Contenu | Résultat |
|---|---|---|---|
| Code financier | pytest (`tests/test_pricing.py`, 20 tests) | valeur de référence, différences finies, équation de Black-Scholes, parité sur 243 combinaisons, cas limites, entrées invalides, vectorisation | ⟦20 passed⟧ |
| Données | pytest (`tests/test_data.py`, 5 tests) | source yfinance, repli CSV, erreur explicite, volatilités, sans réseau | ⟦5 passed⟧ |
| IA | pytest (`tests/test_ml.py`, 9 tests) | cible sans fuite, découpage chronologique, références, métriques, LSTM NumPy identique à Keras, export | ⟦9 passed⟧ |
| Odoo | `TransactionCase` (13 tests) | Grecques de référence call et put, parité, recalcul, contrainte, Delta du portefeuille, courbe Delta(S), bouton de prévision | ⟦sortie de la commande de test⟧ |

Commandes : `pytest` à la racine ; `docker compose run --rm web odoo -d groupe1 -u cours_derives --test-tags /cours_derives --stop-after-init`.
Discipline : toute modification passe par une branche et une pull request relue par un autre membre ; un test doit pouvoir échouer : le vérifier une fois en cassant volontairement une formule, comme le demande le TP ⟦résultat⟧.
