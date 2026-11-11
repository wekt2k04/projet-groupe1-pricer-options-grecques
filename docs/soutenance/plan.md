# Soutenance — 15 minutes avec démonstration en direct

## Déroulé

| Minutes | Partie | Qui | Support |
|---|---|---|---|
| 0 – 1 | Le projet, son rôle de socle pour les groupes 4, 5, 6, 7, 9 | Zineb | diapositive 1 |
| 1 – 4 | Black-Scholes, Grecques, parité ; conventions d'unités | Wilfried | formules, cas de référence 10,4506 |
| 4 – 6 | Python : données AAPL, σ historique, trois preuves que le calcul est juste | Wilfried | notebook 02, `pytest` en direct |
| 6 – 10 | **Démo Odoo** : créer une option → « Calculer » → Grecques → « Courbe Delta(S) » | Hiba | Odoo en direct |
| 10 – 12 | IA : V0 contre V1, références, tableau des résultats, « Prédire la volatilité » dans Odoo | Assia | tableau RMSE / QLIKE, Odoo |
| 12 – 13 | Tests et qualité : 34 tests pytest, 13 tests Odoo | Fatima-ezzahraa | sorties des tests |
| 13 – 15 | Gantt prévu contre réalisé, rotation, limites, conclusion | Zineb | Gantt réalisé |

## Démonstration : script exact

1. `docker compose up -d` lancé **avant** la soutenance, navigateur ouvert sur l'option de référence.
2. Créer : S0 = 100, K = 100, T = 1, r = 0,05, σ = 0,20, call → **Calculer** → prix 10,4506, Delta 0,6368.
3. **Courbe Delta(S)** → graphique en S, valeur 0,6368 à 100 %.
4. Relier la série de prix AAPL → **Prédire la volatilité** → σ historique et σ prédite, deux prix côte à côte.

**Plan B** si la démo échoue : base préparée avec une option call, une option put et une option à T proche de 0 ; vidéo d'écran du parcours complet ; captures dans les diapositives.

## Questions à préparer (chacun répond sans notes)

Les 10 questions de `docs/COMPRENDRE.md` §9, plus :
- Pourquoi garder les noms de champs du TP 0 (`S0`, `K`) plutôt que ceux du guide (`spot`, `strike`) ?
- Pourquoi une table de points pour tracer Delta(S) dans Odoo ?
- Comment le LSTM entraîné en Python tourne-t-il dans Odoo sans TensorFlow ?
- Pourquoi la cible du guide favorise-t-elle la persistance, et qu'avez-vous changé ?
- Votre LSTM bat-il GARCH ? Sinon, pourquoi le présenter ?
- Pourquoi T sur 365 jours et σ sur 252 ?

## Livrables à rendre

- Rapport final assemblé (`docs/rapport/`, voir `00_LISEZMOI.md`) avec le Gantt réalisé.
- Code zippé, après fusion de toutes les PR : `git archive --format=zip -o projet-groupe1-final.zip HEAD` ; vérifier que `pytest` passe dans une copie dézippée.
- Diapositives (environ 10), construites à partir des sections du rapport.
