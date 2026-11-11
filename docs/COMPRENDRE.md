# Projet 1 — Pricer d'Options & Grecques : ce qu'il faut comprendre

Document du Groupe 1. Il ne remplace pas le guide du professeur : il dit, pour notre sujet seulement, ce que chacun doit savoir expliquer à l'oral. Tous les chiffres viennent de notre code (`src/pricing.py`, 20 tests du pricer, verts). Pour la matière dans son ensemble (dérivés, binomial, portefeuille, CAPM, Odoo), lire d'abord [`MATIERE.md`](MATIERE.md). Cas de référence utilisé partout : **S = 100, K = 100, T = 1 an, r = 5 %, σ = 20 %**.

## 1. Notre projet en une chaîne

```
(S, K, T, r, σ) ──► bs_price ──► prix du call / du put
        │
        └────────► greeks ────► Delta, Gamma, Vega, Theta, Rho
                        │
          champs calculés Odoo (extension de cours.option) + bouton « Calculer »
                        │
 LSTM : prédit la volatilité de demain ──► on compare le prix avec σ historique et avec σ prédite
```

Notre sujet est le projet « socle » : les groupes 4, 5, 6, 7 et 9 appellent `bs_price` et `greeks`. Notre signature est donc un contrat : `bs_price(S, K, T, r, sigma, kind)` et `greeks(...)` qui renvoie `{delta, gamma, vega, theta, rho}`. On ne la change pas sans prévenir les autres groupes, et les conventions d'unités sont fixées dans `CONVENTIONS.md`.

## 2. Les cinq paramètres, et les erreurs qu'ils provoquent

| Paramètre | Sens | Unité imposée | Erreur classique |
|---|---|---|---|
| `S` | prix du sous-jacent **aujourd'hui** | devise | confondre avec `S_T`, le prix à l'échéance utilisé pour le payoff du TP |
| `K` | prix d'exercice | devise | l'appeler `strike` dans un module et `K` dans l'autre |
| `T` | durée restante | **années** (jours calendaires / 365) | passer 30 au lieu de 30/365 |
| `r` | taux sans risque | **continu**, décimal (0,05) | passer 5 ; utiliser un taux annuel simple |
| `sigma` | volatilité | **annualisée**, décimal (0,20) | passer 20 ; utiliser une volatilité journalière |

Un seul de ces oublis fausse le prix sans lever d'erreur : c'est la première chose à vérifier quand un résultat paraît bizarre.

## 3. La formule de Black-Scholes, lue pas à pas

```
d1 = [ ln(S/K) + (r + σ²/2)·T ] / (σ·√T)        d2 = d1 − σ·√T
Call = S·N(d1) − K·e^(−rT)·N(d2)
Put  = K·e^(−rT)·N(−d2) − S·N(−d1)
```

`N` est la fonction de répartition de la loi normale centrée réduite. Quatre idées à retenir.

**Le rendement espéré de l'action n'apparaît pas.** Le prix est celui d'un portefeuille qui réplique l'option en ajustant la quantité d'actions détenue. Comme la réplication supprime le risque, le prix ne dépend ni de l'optimisme des investisseurs ni de leur aversion au risque. On peut donc calculer comme si tout actif rapportait `r` (probabilité « risque-neutre »). Seule la volatilité σ compte, et c'est pourquoi tout le projet tourne autour d'elle.

**`N(d2)` est la probabilité, sous cette mesure risque-neutre, que le call finisse dans la monnaie.** Pour notre cas : `N(d2) = 0,5596`. Le terme `K·e^(−rT)·N(d2)` se lit « ce que l'on paie, actualisé, pondéré par la probabilité de payer ».

**`N(d1)` n'est pas une probabilité d'exercice : c'est le Delta du call** (0,6368). Confondre `N(d1)` et `N(d2)` est l'erreur la plus fréquente à l'oral.

**La parité call-put** découle de l'absence d'arbitrage : `C − P = S − K·e^(−rT)`. Dans notre cas : 10,4506 − 5,5735 = 4,8771 = 100 − 95,1229. Elle sert à valider le code et à déduire le put du call.

## 4. Les cinq Grecques

Une Grecque est la dérivée du prix par rapport à un paramètre : elle répond à « de combien le prix bouge-t-il si ce paramètre bouge d'une unité ? ».

| Grecque | Dérivée | Call | Put | Ce qu'elle dit | Unité par défaut |
|---|---|---|---|---|---|
| Delta | ∂V/∂S | 0,6368 | −0,3632 | +1 € sur le spot ⇒ +0,64 € sur le call ; nombre d'actions pour couvrir une option vendue | sans unité |
| Gamma | ∂²V/∂S² | 0,0188 | 0,0188 | vitesse à laquelle le Delta change : une couverture se dérègle d'autant plus vite que le Gamma est grand | par € |
| Vega | ∂V/∂σ | 37,52 | 37,52 | gain si σ monte de 1,00 (soit 100 points) ; **0,3752 par point de volatilité** | par unité de σ |
| Theta | ∂V/∂t | −6,41 | −1,66 | perte de valeur due au seul passage du temps ; **−0,0176 € par jour** pour le call | par an |
| Rho | ∂V/∂r | 53,23 | −41,89 | effet d'une hausse de r de 1,00 (100 points) | par unité de r |

Cinq relations à savoir justifier :

1. `Delta_call − Delta_put = 1`, car `C − P = S − K·e^(−rT)` a une dérivée égale à 1 en S.
2. Gamma et Vega sont **identiques** pour le call et le put : le terme `S − K·e^(−rT)` de la parité est linéaire en S et ne dépend pas de σ, donc il disparaît aux dérivées secondes et au Vega.
3. Le Gamma est maximal quand l'option est à la monnaie et proche de l'échéance : c'est là que couvrir coûte le plus cher.
4. Le Theta du call est presque toujours négatif (l'option perd de la valeur temps). Exception : un put européen très dans la monnaie peut avoir un Theta positif quand `r > 0`.
5. Les trois Grecques Delta, Gamma, Theta sont liées par l'équation de Black-Scholes : `Theta + ½σ²S²·Gamma + r·S·Delta − r·V = 0`. Nos tests vérifient cette égalité à 1e-9 près.

## 5. Trois preuves que notre code est juste

Le jury peut demander « comment savez-vous que vos Grecques sont exactes ? ». Les trois réponses sont dans `tests/test_pricing.py`.

1. **Parité call-put** sur 243 combinaisons de paramètres.
2. **Différences finies** : `(V(S+h) − V(S−h)) / 2h` doit retrouver le Delta analytique, et de même pour Gamma, Vega, Theta, Rho. C'est la validation demandée par le guide.
3. **Équation de Black-Scholes** (relation 5 ci-dessus), indépendante des deux autres.

Un test supplémentaire compare notre code au code du guide recopié tel quel : mêmes résultats à 1e-12 près.

## 6. Le code, fichier par fichier

| Fichier | Contenu | Choix à pouvoir justifier |
|---|---|---|
| `src/pricing.py` | `N`, `phi`, `bs_price`, `greeks`, `put_call_parity_gap` | formules du guide, **sans SciPy obligatoire** : l'image Odoo standard n'en contient vraisemblablement pas, donc repli sur `math.erf` (même précision, vérifiée à 1e-15) |
| `src/pricing.py` | cas `T = 0` ou `σ = 0` | le guide signale la division par zéro dans `d1` ; on renvoie la valeur intrinsèque (prix) et les limites déterministes (Grecques) au lieu de planter, car un champ calculé Odoo qui lève une exception fait planter le formulaire |
| `src/pricing.py` | `theta_per_day`, `vega_per_pct` | unités alternatives sans casser le contrat par défaut |
| `src/data.py` | téléchargement yfinance, repli CSV, simulation GBM, rendements, volatilité historique | graine fixée (`default_rng(42)`) pour des résultats reproductibles |
| `tests/test_pricing.py` | 20 tests pytest | voir §5 |
| `tests/test_data.py` | 5 tests sans réseau (yfinance remplacé par un faux module) | source des données, repli CSV |

Volatilité historique : `σ = écart-type(r_t) × √252`, avec `r_t = ln(S_t/S_{t−1})`. On annualise avec 252 jours de bourse, alors que `T` se compte en jours calendaires / 365 : ce décalage est un choix assumé, écrit dans `CONVENTIONS.md`.

## 7. Odoo : ce qu'il faut comprendre avant de coder (S3 à S5)

**Ce que contient déjà `cours.option` (notre TP 0, dans `odoo_addons/cours_derives`)** : champs saisis `type`, `position`, `quantity`, `S0` (prix d'aujourd'hui), `S_T` (prix à l'échéance), `K`, `premium`, `r`, `T`, `sigma` ; champs calculés `payoff`, `profit`, `break_even`, `moneyness` (à partir de `S_T`) et `bs_price` (à partir de `S0`, put par parité). Toutes les entrées de Black-Scholes existent donc : nous ajoutons seulement les Grecques, `sigma_lstm` et `bs_price_lstm`, avec `_inherit = 'cours.option'`, sans toucher au modèle d'origine. Le guide les appelle `spot`, `strike`, `maturite`, `taux`, `volatilite` : on garde les noms du TP 0 pour éviter les doublons.

**Un champ calculé** (`compute=`, `store=True`, `@api.depends`) se recalcule dès qu'un champ listé dans `depends` change, et reste stocké en base : c'est ce qui permet de trier, filtrer et regrouper. Oublier un champ dans `@api.depends` donne un résultat périmé sans message d'erreur.

**La vue graphique d'Odoo ne trace pas une fonction.** Elle regroupe des enregistrements et agrège une mesure. Pour « Delta en fonction du spot » il faut soit un modèle de points (un enregistrement par spot, créés par le bouton), soit une image matplotlib encodée en base64 dans un champ binaire ou HTML. Décision à prendre en S3.

**Le conteneur Odoo n'a pas nos bibliothèques.** D'où `pricing.py` sans SciPy. Pour le LSTM, TensorFlow ne sera pas dans l'image : on entraîne hors Odoo, et Odoo ne fait que de l'inférence via un modèle exporté ou un petit service. Décision à prendre en S4.

**Noms de champs (décision S1)** : on garde ceux de notre module (`type`, `S0`, `K`, `T`, `r`, `sigma`), voir `CONVENTIONS.md`. Les groupes 4 et 7 étendent aussi `cours.option` : on leur communique ce choix.

## 8. Le LSTM de volatilité : ce que le guide ne dit pas

**Ce que demande le guide** : prédire la volatilité de demain à partir des 30 derniers jours (LSTM, Keras). Cible = volatilité réalisée glissante sur 5 jours ; fenêtres de 30 valeurs ; normalisation apprise sur le train ; découpage chronologique 70 / 15 / 15, sans mélange.

**Le piège central.** La volatilité glissante sur 5 jours au jour t+1 partage 4 de ses 5 rendements avec celle du jour t. Une règle triviale, « demain = aujourd'hui » (la persistance), obtient donc un R² élevé par construction, et le LSTM apprend surtout à recopier son entrée. Sans précaution, on affichera un bon score qui ne prouve rien. Avec deux ans de cotations, il reste environ 330 séquences d'entraînement : c'est peu pour un LSTM.

**Ce que nous proposons** : historique de 10 ans plutôt que 1 à 2 ; cible tournée vers l'avenir et sans chevauchement (volatilité réalisée sur les 5 jours suivants) ; trois références à battre (persistance, EWMA RiskMetrics avec λ = 0,94, GARCH(1,1) via `arch`) ; mesures RMSE et QLIKE. Si le LSTM perd, on le dit et on l'explique : c'est un résultat défendable, un R² flatteur obtenu par construction ne l'est pas.

**Lien IA ↔ pricing.** Black-Scholes veut la volatilité moyenne sur toute la durée de vie de l'option ; le LSTM prédit celle du lendemain. Injecter une prévision à 1 jour dans le prix d'une option à 1 an est incohérent : on agrège la prévision sur la maturité, ou on limite la démonstration aux échéances courtes, puis Odoo affiche côte à côte « prix avec σ historique » et « prix avec σ prédite ».

**Variante « volatilité implicite future » du guide** : non réalisable avec yfinance, qui ne donne qu'une photographie de la chaîne d'options du jour, sans historique de volatilité implicite. À signaler dans le rapport plutôt que de la contourner.

## 9. Questions de soutenance probables

| Question | Réponse courte |
|---|---|
| Pourquoi le rendement espéré n'apparaît-il pas ? | La réplication supprime le risque ; le prix est le même pour tous les investisseurs, on évalue sous la mesure risque-neutre. |
| Que représente `N(d2)` ? | La probabilité risque-neutre que le call finisse dans la monnaie. `N(d1)` est le Delta. |
| Delta = 0,64 veut-il dire 64 % de chances d'être exercé ? | Non : le Delta est le nombre d'actions pour se couvrir ; la probabilité d'exercice est `N(d2)` = 56 %. |
| Pourquoi Gamma et Vega sont-ils égaux pour call et put ? | Par la parité : `C − P = S − K·e^(−rT)` est linéaire en S et indépendant de σ. |
| Que se passe-t-il si `T = 0` ou `σ = 0` ? | Le prix devient la valeur intrinsèque (actualisée) ; Gamma et Vega valent 0 ; aucune division par zéro. |
| Comment validez-vous les Grecques ? | Différences finies, parité, équation de Black-Scholes, comparaison au code du guide (§5). |
| Pourquoi 252 jours pour σ et 365 pour T ? | Les rendements sont observés les jours de bourse ; les échéances se comptent en jours calendaires. Choix documenté dans `CONVENTIONS.md`. |
| Votre LSTM bat-il la persistance ? | On présente persistance, EWMA et GARCH comme références, avec RMSE et QLIKE ; la réponse est dans le tableau de résultats, quelle qu'elle soit. |
| Quelles sont les limites de Black-Scholes ? | σ constante (alors que le smile montre le contraire), pas de sauts, pas de dividendes, taux constant, option européenne, marché sans frottements. |
| Pourquoi σ historique ≠ σ implicite ? | La première regarde le passé ; la seconde est déduite du prix de marché et regarde l'avenir (projet 7). |

## 10. Parcours S1 → S7 : ce que chacun doit maîtriser

À savoir expliquer par **chaque membre, quel que soit son rôle** : §3, §4 et §5. Le reste se répartit.

| Semaine | Livrable du guide | À comprendre pour le défendre |
|---|---|---|
| S1 | dépôt, Docker, source des données, fiche de lecture, schéma de base, Gantt prévisionnel | §1, §2, quels champs manquent à `cours.option` (§7) |
| S2 | prototype Python, notebook | §3, §4, §5 : lire `pricing.py` ligne à ligne |
| S3 | extension Odoo | §7 : champs calculés, `@api.depends`, nommage |
| S4 | vues et IA entraînée, rotation des rôles | §7 (vue graphique), §8 (cible, références) |
| S5 | intégration : le bouton Odoo déclenche le calcul et l'IA | §8 (lien IA ↔ pricing), cas limites |
| S6 | tests, rapport à 80 % | §5, §9 |
| S7 | soutenance : rapport, code zippé, démonstration de 15 minutes | tout le document |

Répartition proposée pour **5 membres** (le guide ne définit des rôles que pour 3 et 4) : chef de projet ; quant / data Python ; développeur Odoo ; ingénieur IA ; qualité et intégration (pytest, Docker, pont IA → Odoo). À la rotation de la S4, la personne qui tenait l'IA passe développeur Odoo, pour brancher elle-même son modèle derrière le bouton. À valider en groupe.
