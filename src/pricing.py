"""Black-Scholes : prix et Grecques d'une option européenne sans dividende.

Fonctions financières pures, sans dépendance Odoo (annexe A du guide).
Conventions communes : voir CONVENTIONS.md
    T en années, sigma annualisée en décimal, r en taux continu.

SciPy est facultatif : sans lui (conteneur Odoo standard), la loi normale
est calculée avec math.erf, avec la même précision.
"""
import math

import numpy as np

try:
    from scipy.special import ndtr as _ndtr
except ImportError:  # conteneur Odoo : pas de SciPy
    _ndtr = None
    _erf = np.vectorize(math.erf, otypes=[float])

_SQRT2 = math.sqrt(2.0)
_SQRT2PI = math.sqrt(2.0 * math.pi)
JOURS_PAR_AN = 365.0   # theta_per_day : jours calendaires


def _out(x):
    """Renvoie un float pour un scalaire, un tableau sinon."""
    x = np.asarray(x)
    return float(x) if x.ndim == 0 else x


def N(x):
    """Fonction de répartition de la loi normale centrée réduite."""
    x = np.asarray(x, dtype=float)
    res = _ndtr(x) if _ndtr is not None else 0.5 * (1.0 + _erf(x / _SQRT2))
    return _out(res)


def phi(x):
    """Densité de la loi normale centrée réduite."""
    x = np.asarray(x, dtype=float)
    return _out(np.exp(-0.5 * x * x) / _SQRT2PI)


def _prepare(S, K, T, r, sigma, kind):
    if kind not in ("call", "put"):
        raise ValueError("kind doit valoir 'call' ou 'put'")
    S, K, T, r, sigma = (np.asarray(v, dtype=float) for v in (S, K, T, r, sigma))
    if np.any(S <= 0) or np.any(K <= 0):
        raise ValueError("S et K doivent être strictement positifs")
    if np.any(T < 0) or np.any(sigma < 0):
        raise ValueError("T et sigma doivent être positifs ou nuls")
    return S, K, T, r, sigma


def _d1_d2(S, K, T, r, sigma):
    sqrt_t = np.sqrt(T)
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt_t)
    return d1, d1 - sigma * sqrt_t


def bs_price(S, K, T, r, sigma, kind="call"):
    """Prix Black-Scholes. Si T = 0 ou sigma = 0, renvoie la valeur
    intrinsèque actualisée au forward (limite du modèle)."""
    S, K, T, r, sigma = _prepare(S, K, T, r, sigma, kind)
    disc = K * np.exp(-r * T)
    with np.errstate(divide="ignore", invalid="ignore"):
        d1, d2 = _d1_d2(S, K, T, r, sigma)
        if kind == "call":
            price = S * N(d1) - disc * N(d2)
            limit = np.maximum(S - disc, 0.0)
        else:
            price = disc * N(-d2) - S * N(-d1)
            limit = np.maximum(disc - S, 0.0)
    return _out(np.where((T <= 0) | (sigma <= 0), limit, price))


def greeks(S, K, T, r, sigma, kind="call", theta_per_day=False, vega_per_pct=False):
    """Grecques {delta, gamma, vega, theta, rho}.

    Par défaut : formules et unités du guide (theta par an, vega pour une
    variation de sigma de 1,00, rho pour une variation de r de 1,00).
    theta_per_day=True : theta divisé par 365 ; vega_per_pct=True : vega
    pour 1 point de volatilité (divisé par 100).
    Si T = 0 ou sigma = 0 : limites déterministes (delta en escalier,
    gamma = vega = 0), sans division par zéro.
    """
    S, K, T, r, sigma = _prepare(S, K, T, r, sigma, kind)
    disc = K * np.exp(-r * T)
    call = kind == "call"
    with np.errstate(divide="ignore", invalid="ignore"):
        d1, d2 = _d1_d2(S, K, T, r, sigma)
        pdf = phi(d1)
        sqrt_t = np.sqrt(T)
        delta = N(d1) if call else N(d1) - 1
        gamma = pdf / (S * sigma * sqrt_t)
        vega = S * pdf * sqrt_t
        if call:
            theta = -S * pdf * sigma / (2 * sqrt_t) - r * disc * N(d2)
            rho = T * disc * N(d2)
        else:
            theta = -S * pdf * sigma / (2 * sqrt_t) + r * disc * N(-d2)
            rho = -T * disc * N(-d2)

    # Cas dégénérés (T = 0 ou sigma = 0) : option déterministe
    degenerate = (T <= 0) | (sigma <= 0)
    itm = (S > disc) if call else (S < disc)
    sign = 1.0 if call else -1.0
    delta = np.where(degenerate, np.where(itm, sign, 0.0), delta)
    gamma = np.where(degenerate, 0.0, gamma)
    vega = np.where(degenerate, 0.0, vega)
    theta = np.where(degenerate, np.where(itm, -sign * r * disc, 0.0), theta)
    rho = np.where(degenerate, np.where(itm, sign * T * disc, 0.0), rho)

    if theta_per_day:
        theta = theta / JOURS_PAR_AN
    if vega_per_pct:
        vega = vega / 100.0
    return {"delta": _out(delta), "gamma": _out(gamma), "vega": _out(vega),
            "theta": _out(theta), "rho": _out(rho)}


def put_call_parity_gap(C, P, S, K, T, r):
    """Écart à la parité call-put : (C - P) - (S - K e^{-rT}). Nul sans arbitrage."""
    return (np.asarray(C, float) - np.asarray(P, float)
            - (np.asarray(S, float) - np.asarray(K, float) * np.exp(-np.asarray(r, float) * np.asarray(T, float))))
