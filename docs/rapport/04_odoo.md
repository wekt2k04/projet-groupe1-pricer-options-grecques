# 4. Intégration dans Odoo 17

## 4.1 Architecture

Odoo 17 et PostgreSQL 15 tournent sous Docker. L'image Odoo du groupe ajoute NumPy (`Dockerfile.odoo`). Le dossier `src/` est monté dans le conteneur et ajouté au `PYTHONPATH` : Odoo importe `pricing` et `ml` sans recopier le code, si bien que les tests pytest garantissent aussi les calculs faits dans Odoo.

## 4.2 Extension de `cours.option` (`_inherit`)

Le modèle du TP 0 contient déjà les entrées (`S0`, `K`, `T`, `r`, `sigma`, `type`) et `bs_price` ; on garde ses noms. L'extension ajoute les cinq Grecques en champs calculés stockés (`@api.depends` sur les entrées, `store=True` pour trier, grouper et tracer), `sigma_lstm` et `bs_price_lstm`. `cours.portfolio` gagne un Delta total, signé selon la position. Un champ calculé ne lève jamais d'exception : une entrée invalide donne 0, et la contrainte du TP 0 refuse `S0 ≤ 0`.

## 4.3 Vues et boutons

Formulaire avec groupes « Résultats » et « Résultats / Grecques » et trois boutons : « Calculer », « Courbe Delta(S) », « Prédire la volatilité » ; liste avec les Grecques. La vue graphique d'Odoo agrège des enregistrements et ne trace pas une fonction : le bouton crée donc 21 points (`cours.option.point`, spot de 50 % à 150 % du strike) que la vue relie. Captures : ⟦docs/captures/s3_grecques.png, s4_*.png⟧.

## 4.4 Le bouton déclenche l'IA

L'option est reliée à une série de prix (`cours.volatility`). « Prédire la volatilité » calcule la σ historique (→ prix Black-Scholes) et la σ prévue par le LSTM (→ prix avec σ prédite), affichés côte à côte, et enregistre la prévision dans `cours.vol.prediction`. L'inférence se fait en NumPy à partir du fichier de poids `models/lstm_vol.npz` : l'image Odoo n'a pas besoin de TensorFlow. Capture : ⟦docs/captures/s5_prediction.png⟧.
