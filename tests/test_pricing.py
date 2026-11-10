"""Tests pytest du pricer Black-Scholes (Phase 2 du guide)."""
import numpy as np
import pytest
from scipy.stats import norm

from data import (historical_volatility, log_returns, rolling_realized_vol,
                  simulate_gbm_prices)
from pricing import N, bs_price, greeks, phi, put_call_parity_gap

RNG = np.random.default_rng(42)
GRID = [(s, k, t, r, v) for s in (80.0, 100.0, 125.0) for k in (90.0, 100.0, 110.0)
        for t in (0.25, 1.0, 2.0) for r in (0.0, 0.03, 0.08) for v in (0.1, 0.25, 0.6)]


def guide_reference(S, K, T, r, sigma, kind="call"):
    """Code du guide (scipy), recopié tel quel : référence indépendante."""
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    pdf = norm.pdf(d1)
    if kind == "call":
        price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    delta = norm.cdf(d1) if kind == "call" else norm.cdf(d1) - 1
    theta = -S * pdf * sigma / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2)
    if kind == "put":
        theta = -S * pdf * sigma / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2)
    rho = (K * T * np.exp(-r * T) * norm.cdf(d2) if kind == "call"
           else -K * T * np.exp(-r * T) * norm.cdf(-d2))
    return price, {"delta": delta, "gamma": pdf / (S * sigma * np.sqrt(T)),
                   "vega": S * pdf * np.sqrt(T), "theta": theta, "rho": rho}


def test_valeur_connue():
    # BS(S=100, K=100, T=1, r=5 %, sigma=20 %) : call 10,4506 ; put 5,5735
    assert bs_price(100, 100, 1, 0.05, 0.20, "call") == pytest.approx(10.4506, abs=1e-4)
    assert bs_price(100, 100, 1, 0.05, 0.20, "put") == pytest.approx(5.5735, abs=1e-4)


@pytest.mark.parametrize("kind", ["call", "put"])
def test_identique_au_code_du_guide(kind):
    for S, K, T, r, v in GRID:
        p_ref, g_ref = guide_reference(S, K, T, r, v, kind)
        assert bs_price(S, K, T, r, v, kind) == pytest.approx(p_ref, rel=1e-12, abs=1e-12)
        g = greeks(S, K, T, r, v, kind)
        for nom in g_ref:
            assert g[nom] == pytest.approx(g_ref[nom], rel=1e-10, abs=1e-12), nom


def test_parite_call_put():
    for S, K, T, r, v in GRID:
        c, p = bs_price(S, K, T, r, v, "call"), bs_price(S, K, T, r, v, "put")
        assert put_call_parity_gap(c, p, S, K, T, r) == pytest.approx(0.0, abs=1e-10)


@pytest.mark.parametrize("kind", ["call", "put"])
def test_grecques_par_differences_finies(kind):
    S, K, T, r, v = 100.0, 105.0, 0.75, 0.04, 0.30
    g = greeks(S, K, T, r, v, kind)
    h = 1e-4
    f = lambda s=S, t=T, rr=r, vv=v: bs_price(s, K, t, rr, vv, kind)
    assert (f(s=S + h) - f(s=S - h)) / (2 * h) == pytest.approx(g["delta"], abs=1e-7)
    assert (f(s=S + h) - 2 * f() + f(s=S - h)) / h ** 2 == pytest.approx(g["gamma"], abs=1e-5)
    assert (f(vv=v + h) - f(vv=v - h)) / (2 * h) == pytest.approx(g["vega"], abs=1e-6)
    assert -(f(t=T + h) - f(t=T - h)) / (2 * h) == pytest.approx(g["theta"], abs=1e-6)
    assert (f(rr=r + h) - f(rr=r - h)) / (2 * h) == pytest.approx(g["rho"], abs=1e-6)


@pytest.mark.parametrize("kind", ["call", "put"])
def test_equation_de_black_scholes(kind):
    """Theta + 1/2 sigma^2 S^2 Gamma + r S Delta - r V = 0 (EDP de Black-Scholes)."""
    for S, K, T, r, v in GRID:
        g = greeks(S, K, T, r, v, kind)
        V = bs_price(S, K, T, r, v, kind)
        residu = g["theta"] + 0.5 * v ** 2 * S ** 2 * g["gamma"] + r * S * g["delta"] - r * V
        assert residu == pytest.approx(0.0, abs=1e-9)


def test_relations_call_put():
    S, K, T, r, v = 100.0, 95.0, 1.0, 0.03, 0.2
    gc, gp = greeks(S, K, T, r, v, "call"), greeks(S, K, T, r, v, "put")
    assert gc["delta"] - gp["delta"] == pytest.approx(1.0, abs=1e-12)
    assert gc["gamma"] == pytest.approx(gp["gamma"], abs=1e-14)
    assert gc["vega"] == pytest.approx(gp["vega"], abs=1e-12)


def test_bornes_et_limites():
    assert 0.0 < greeks(100, 100, 1, 0.05, 0.2, "call")["delta"] < 1.0
    # très dans la monnaie / très en dehors
    # S = 500 : N(d1) et N(d2) valent 1 à 1e-15 près ; S = 20 : les deux valent 0
    assert bs_price(500, 100, 1, 0.05, 0.2, "call") == pytest.approx(500 - 100 * np.exp(-0.05), abs=1e-6)
    assert bs_price(20, 100, 1, 0.05, 0.2, "call") == pytest.approx(0.0, abs=1e-6)


def test_cas_degeneres_sans_division_par_zero():
    # T = 0 : valeur intrinsèque
    assert bs_price(110, 100, 0.0, 0.05, 0.2, "call") == pytest.approx(10.0)
    assert bs_price(90, 100, 0.0, 0.05, 0.2, "put") == pytest.approx(10.0)
    assert bs_price(90, 100, 0.0, 0.05, 0.2, "call") == 0.0
    # sigma = 0 : valeur intrinsèque actualisée au forward
    assert bs_price(100, 100, 1.0, 0.05, 0.0, "call") == pytest.approx(100 - 100 * np.exp(-0.05))
    for kind in ("call", "put"):
        for T, v in ((0.0, 0.2), (1.0, 0.0), (0.0, 0.0)):
            g = greeks(110, 100, T, 0.05, v, kind)
            assert all(np.isfinite(x) for x in g.values())
            assert g["gamma"] == 0.0 and g["vega"] == 0.0
    assert greeks(110, 100, 0.0, 0.05, 0.2, "call")["delta"] == 1.0
    assert greeks(90, 100, 0.0, 0.05, 0.2, "call")["delta"] == 0.0
    assert greeks(90, 100, 0.0, 0.05, 0.2, "put")["delta"] == -1.0


@pytest.mark.parametrize("args", [(0, 100, 1, .05, .2), (100, -1, 1, .05, .2),
                                  (100, 100, -1, .05, .2), (100, 100, 1, .05, -.2)])
def test_entrees_invalides(args):
    with pytest.raises(ValueError):
        bs_price(*args)
    with pytest.raises(ValueError):
        greeks(*args)


def test_type_invalide():
    with pytest.raises(ValueError):
        bs_price(100, 100, 1, 0.05, 0.2, "straddle")


def test_vectorisation_coherente_avec_le_scalaire():
    S = np.linspace(60, 140, 9)
    prix, g = bs_price(S, 100, 1, 0.05, 0.2), greeks(S, 100, 1, 0.05, 0.2)
    assert prix.shape == (9,) and g["delta"].shape == (9,)
    for i, s in enumerate(S):
        assert prix[i] == pytest.approx(bs_price(s, 100, 1, 0.05, 0.2))
        assert g["delta"][i] == pytest.approx(greeks(s, 100, 1, 0.05, 0.2)["delta"])
    assert isinstance(bs_price(100, 100, 1, 0.05, 0.2), float)


def test_unites_theta_par_jour_vega_par_point():
    base = greeks(100, 100, 1, 0.05, 0.2)
    alt = greeks(100, 100, 1, 0.05, 0.2, theta_per_day=True, vega_per_pct=True)
    assert alt["theta"] == pytest.approx(base["theta"] / 365.0)
    assert alt["vega"] == pytest.approx(base["vega"] / 100.0)


def test_loi_normale_sans_scipy_equivalente():
    x = np.linspace(-6, 6, 241)
    assert N(x) == pytest.approx(norm.cdf(x), abs=1e-15)
    assert phi(x) == pytest.approx(norm.pdf(x), abs=1e-15)
    # repli math.erf utilisé dans le conteneur Odoo
    import math
    erf_cdf = np.array([0.5 * (1 + math.erf(v / math.sqrt(2))) for v in x])
    assert erf_cdf == pytest.approx(norm.cdf(x), abs=1e-15)


def test_donnees_volatilite_historique():
    px = simulate_gbm_prices(S0=100, sigma=0.25, n=5000, seed=42)
    r = log_returns(px)
    assert len(r) == len(px) - 1
    assert historical_volatility(r) == pytest.approx(0.25, rel=0.05)
    rv = rolling_realized_vol(r, window=5)
    assert rv.isna().sum() == 4 and (rv.dropna() >= 0).all()
