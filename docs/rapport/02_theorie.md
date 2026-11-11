# 2. Fondements théoriques

## 2.1 Le modèle de Black-Scholes

Hypothèses : prix du sous-jacent log-normal, volatilité `σ` et taux `r` constants, pas de dividendes ni de frais, vente à découvert autorisée, marché continu sans arbitrage, option européenne. Sous ces hypothèses, une option se réplique par un portefeuille d'actions et d'actif sans risque ; son prix est le coût de cette réplication et vérifie l'équation aux dérivées partielles `∂V/∂t + ½σ²S²·∂²V/∂S² + rS·∂V/∂S − rV = 0`.

`d1 = [ln(S/K) + (r + σ²/2)T] / (σ√T)`, `d2 = d1 − σ√T`
Call `C = S·N(d1) − K·e^(−rT)·N(d2)` ; Put `P = K·e^(−rT)·N(−d2) − S·N(−d1)`.

`N(d2)` est la probabilité, sous la mesure risque-neutre, que le call soit exercé ; `N(d1)` est son Delta.

## 2.2 Les Grecques

| Grecque | Définition | Formule (call) | Cas de référence |
|---|---|---|---|
| Delta | ∂V/∂S | `N(d1)` | 0,6368 |
| Gamma | ∂²V/∂S² | `φ(d1)/(Sσ√T)` | 0,0188 |
| Vega | ∂V/∂σ | `S·φ(d1)·√T` | 37,524 |
| Theta | −∂V/∂T (par an) | `−Sφ(d1)σ/(2√T) − rK·e^(−rT)·N(d2)` | −6,414 |
| Rho | ∂V/∂r | `K·T·e^(−rT)·N(d2)` | 53,2325 |

Cas de référence : S = K = 100, T = 1, r = 5 %, σ = 20 % ; call 10,4506, put 5,5735. Le Delta est la quantité d'actions qui couvre l'option ; le Gamma mesure la vitesse à laquelle cette couverture se périme.

## 2.3 La parité call-put

`C − P = S − K·e^(−rT)`. Acheter un call et vendre un put de même strike et même échéance reproduit une action financée par un emprunt de `K·e^(−rT)` ; les deux positions doivent coûter la même chose, sinon un arbitrage existe. La parité sert à la fois de relation de prix et de test du code.

## 2.4 Conventions

`T` en années (jours calendaires / 365), `r` taux continu, `σ` annualisée (√252 jours de bourse), tous en décimal ; Theta par an, Vega pour 1,00 de σ, Rho pour 1,00 de r. Le décalage 365 / 252 est assumé : la maturité se compte en temps calendaire, la volatilité ne se mesure que les jours de cotation.
