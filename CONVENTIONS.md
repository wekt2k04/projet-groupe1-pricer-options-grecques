# Conventions communes (Projet 1 — `bs_price` et `greeks`)

Notre pricer est réutilisé par les groupes 4, 5, 6, 7 et 9. Ces conventions sont celles de `src/pricing.py` ; toute modification se discute avec eux avant d'être poussée.

| Élément | Convention |
|---|---|
| Option | européenne, sans dividende ; `kind` vaut `"call"` ou `"put"` |
| `S`, `K` | strictement positifs, même devise |
| `T` | **années**, jours calendaires / 365 (ex. 30 jours = 30/365) ; `T = 0` autorisé |
| `r` | taux sans risque **continu**, décimal (5 % → 0.05) |
| `sigma` | volatilité **annualisée**, décimal (20 % → 0.20) ; `sigma = 0` autorisé |
| Volatilité historique | `std(r_t, ddof=1) × √252`, `r_t = ln(S_t / S_{t-1})` |
| Theta | **par an** par défaut ; `theta_per_day=True` divise par 365 |
| Vega | pour une variation de `sigma` de **1,00** par défaut ; `vega_per_pct=True` divise par 100 |
| Rho | pour une variation de `r` de **1,00** |
| Retour de `greeks` | dictionnaire `{"delta", "gamma", "vega", "theta", "rho"}` |
| Entrées invalides | `ValueError` (`S ≤ 0`, `K ≤ 0`, `T < 0`, `sigma < 0`, `kind` inconnu) |
| Tableaux | `bs_price` et `greeks` acceptent des scalaires et des tableaux NumPy |
| Graine aléatoire | `numpy.random.default_rng(42)` |
| Découpage de séries | toujours chronologique, jamais aléatoire ; normalisation apprise sur le train seul |

## Champs Odoo de `cours.option` (décision S1 du 11/11/2026, à communiquer aux groupes 4 et 7)

Notre module `cours_derives` (TP 0, dans `odoo_addons/`) contient déjà les entrées de Black-Scholes. **On garde ses noms** : pas de doublon `spot`/`S0` ni `strike`/`K`. Le guide écrit `spot`, `strike`, `maturite`, `taux`, `volatilite` ; l'énoncé du TP `option_type` : ce sont les mêmes grandeurs.

| Champ | Contenu | Unité | Origine |
|---|---|---|---|
| `type` | `'call'` ou `'put'` | — | TP 0 |
| `S0` | prix du sous-jacent **aujourd'hui** (sert au prix) | devise | TP 0 |
| `S_T` | prix à l'échéance (sert seulement au payoff) | devise | TP 0 |
| `K` | prix d'exercice | devise | TP 0 |
| `T` | durée restante | années | TP 0 |
| `r` | taux sans risque continu | décimal | TP 0 |
| `sigma` | volatilité annualisée | décimal | TP 0 |
| `bs_price` | prix Black-Scholes (put par parité) | devise | TP 0 |
| `greeks_delta`, `greeks_gamma`, `greeks_vega`, `greeks_theta`, `greeks_rho` | Grecques, calculées et stockées | unités ci-dessus | groupe 1 |
| `sigma_lstm`, `bs_price_lstm` | volatilité prédite et prix correspondant | décimal, devise | groupe 1 |
