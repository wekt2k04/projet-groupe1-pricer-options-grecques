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

## Champs Odoo de l'extension de `cours.option` (à confirmer avec les groupes 4 et 7)

Le cours utilise `type`, le TP `option_type`, le guide `type`, `strike`, `maturite`, `taux`, `volatilite`. Nom retenu pour l'instant : celui du guide. À figer après lecture du module `cours_derives` du groupe.

| Champ | Contenu | Unité |
|---|---|---|
| `spot` | prix du sous-jacent aujourd'hui (≠ `S_T` du TP) | devise |
| `strike` | prix d'exercice (équivalent du `K` du TP) | devise |
| `maturite` | durée restante | années |
| `taux` | taux sans risque continu | décimal |
| `volatilite` | volatilité annualisée | décimal |
| `greeks_delta`, `greeks_gamma`, `greeks_vega`, `greeks_theta`, `greeks_rho` | Grecques, calculées et stockées | unités ci-dessus |
