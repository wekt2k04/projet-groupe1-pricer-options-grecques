# 3. Données et implémentation Python

## 3.1 Données

Source : cours de clôture ajustés d'AAPL par `yfinance`, 2 ans pour le pricer et 10 ans pour l'IA, avec des CSV de repli versionnés (`data/*_fallback.csv`) pour que tout reste exécutable sans réseau. Rendements `r_t = ln(S_t/S_{t−1})` ; volatilité historique annualisée `σ = écart-type(r_t) × √252`.
Résultats (notebook `01_donnees`, source ⟦yfinance / csv⟧, période ⟦date début → date fin⟧) : ⟦n⟧ observations, σ historique = ⟦σ⟧. Figures : `docs/figures/fig_01_prix.png`, `fig_02_vol_realisee_5j.png`.

## 3.2 Le module `src/pricing.py`

`bs_price(S, K, T, r, sigma, kind)` et `greeks(...)`, qui renvoie `{delta, gamma, vega, theta, rho}`, acceptent des scalaires ou des tableaux NumPy. La loi normale utilise SciPy si présent, sinon `math.erf`, ce qui permet l'import dans l'image Odoo. Les cas limites (`T = 0`, `σ = 0`) renvoient la valeur intrinsèque et des Grecques déterministes au lieu d'une erreur ; les entrées invalides (`S ≤ 0`, `K ≤ 0`, `T < 0`, `σ < 0`) lèvent `ValueError`.

## 3.3 Trois preuves que le calcul est juste

| Vérification | Méthode | Résultat |
|---|---|---|
| Valeur de référence | comparaison au cours | call 10,4506, put 5,5735 |
| Différences finies | `(V(x+h) − V(x−h))/2h` pour chaque Grecque | écart relatif < 1e-6 |
| Équation de Black-Scholes | `Θ + ½σ²S²Γ + rSΔ − rV = 0` | vérifiée sur une grille |
| Parité call-put | `C − P − (S − K·e^(−rT))` | < 1e-10 sur 72 et 243 combinaisons |

## 3.4 Cas AAPL

À la monnaie, 30 jours, σ historique, taux sans risque ⟦taux et source⟧ : call ⟦prix⟧, put ⟦prix⟧, Delta ⟦Δ⟧ (notebook `02_modele_python`). Figures : `fig_03_delta_gamma.png`, `fig_04_sensibilites.png`.
