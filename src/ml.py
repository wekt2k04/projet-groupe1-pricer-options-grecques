"""Prévision de la volatilité (Groupe 1, Projet 1) : jeux de données, références, métriques, LSTM.

Conventions : rendements log journaliers ; volatilités annualisées (× √252), en décimal.
L'entraînement (Keras) se fait hors d'Odoo, dans notebooks/03_ia.ipynb. L'inférence
(`lstm_forward`, `predict_vol`) n'utilise que NumPy, pour tourner dans l'image Odoo.
"""
import json

import numpy as np

JOURS = 252
FENETRE = 30      # longueur de la séquence d'entrée (guide : 30 derniers jours)
HORIZON = 5       # variante V1 : volatilité réalisée des 5 jours suivants


# ---------- jeux de données ----------
def make_dataset_v0(returns, window=FENETRE, vol_window=5):
    """Variante du guide : X = 30 dernières volatilités réalisées (5 j), y = celle du lendemain.

    Limite connue : y(t+1) et X(t) partagent 4 rendements sur 5, la persistance est très forte.
    """
    from data import rolling_realized_vol   # import local : data.py exige pandas, absent de l'image Odoo
    v = rolling_realized_vol(returns, vol_window).dropna().to_numpy()
    X = np.stack([v[i:i + window] for i in range(len(v) - window)])
    return X[..., None], v[window:]


def make_dataset_v1(returns, window=FENETRE, horizon=HORIZON):
    """Variante rigoureuse : X = 30 derniers rendements, y = volatilité annualisée des `horizon` jours SUIVANTS."""
    r = np.asarray(returns, dtype=float)
    n = len(r) - window - horizon + 1
    X = np.stack([r[i:i + window] for i in range(n)])
    y = np.array([r[i + window:i + window + horizon].std(ddof=1) * np.sqrt(JOURS) for i in range(n)])
    return X[..., None], y


def chrono_split(n, train=0.70, val=0.15):
    """Bornes (a, b) d'un découpage chronologique : train [:a], validation [a:b], test [b:]. Jamais aléatoire."""
    return int(n * train), int(n * (train + val))


# ---------- normalisation (paramètres appris sur le train seul) ----------
def fit_minmax(x):
    return float(np.min(x)), float(np.max(x))


def scale(x, lo, hi):
    return (np.asarray(x, dtype=float) - lo) / (hi - lo)


def unscale(z, lo, hi):
    return np.asarray(z, dtype=float) * (hi - lo) + lo


# ---------- références ----------
def persistence_v1(X, horizon=HORIZON):
    """Prévision « demain comme aujourd'hui » : volatilité réalisée des `horizon` derniers rendements de la fenêtre."""
    return X[:, -horizon:, 0].std(axis=1, ddof=1) * np.sqrt(JOURS)


def ewma_v1(X, lam=0.94):
    """EWMA RiskMetrics sur chaque fenêtre : σ²_t = λ·σ²_{t−1} + (1 − λ)·r²_{t−1}, initialisée sur la fenêtre."""
    r = X[:, :, 0]
    s2 = r.var(axis=1, ddof=1)
    for t in range(r.shape[1]):
        s2 = lam * s2 + (1 - lam) * r[:, t] ** 2
    return np.sqrt(s2 * JOURS)


def garch_v1(X, omega, alpha, beta, horizon=HORIZON):
    """GARCH(1,1) à paramètres fixés (estimés sur le train) : variance filtrée sur la fenêtre,
    puis moyenne des prévisions à 1..horizon jours, annualisée. Rendements en décimal."""
    r = X[:, :, 0]
    s2 = np.full(r.shape[0], omega / (1 - alpha - beta))
    for t in range(r.shape[1]):
        s2 = omega + alpha * r[:, t] ** 2 + beta * s2
    lr = omega / (1 - alpha - beta)
    k = np.arange(horizon)
    prev = lr + np.outer(s2 - lr, (alpha + beta) ** k)
    return np.sqrt(prev.mean(axis=1) * JOURS)


# ---------- métriques ----------
def rmse(y, yhat):
    return float(np.sqrt(np.mean((np.asarray(y) - np.asarray(yhat)) ** 2)))


def qlike(y, yhat):
    """QLIKE sur les variances : moyenne de y²/ŷ² − ln(y²/ŷ²) − 1 ; vaut 0 pour une prévision parfaite."""
    q = (np.asarray(y) / np.asarray(yhat)) ** 2
    return float(np.mean(q - np.log(q) - 1))


# ---------- LSTM : inférence en NumPy (mêmes équations que Keras) ----------
def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def lstm_forward(X, W, U, b, Wd, bd):
    """Une couche LSTM (portes i, f, c, o, ordre Keras) puis une couche dense : X (n, T, d) → (n,)."""
    n, u = X.shape[0], U.shape[0]
    h, c = np.zeros((n, u)), np.zeros((n, u))
    for t in range(X.shape[1]):
        z = X[:, t, :] @ W + h @ U + b
        i, f, g, o = _sigmoid(z[:, :u]), _sigmoid(z[:, u:2 * u]), np.tanh(z[:, 2 * u:3 * u]), _sigmoid(z[:, 3 * u:])
        c = f * c + i * g
        h = o * np.tanh(c)
    return (h @ Wd + bd).ravel()


def save_model(path, weights, meta):
    """Enregistre les poids (W, U, b, Wd, bd) et les métadonnées (normalisation, variante, source)."""
    np.savez(path, **weights, meta=json.dumps(meta))


def load_model(path):
    z = np.load(path)
    return {k: z[k] for k in ("W", "U", "b", "Wd", "bd")}, json.loads(str(z["meta"]))


def predict_vol(returns, path):
    """Volatilité annualisée prévue pour les `horizon` jours suivants (variante V1) à partir des derniers rendements."""
    w, meta = load_model(path)
    r = np.asarray(returns, dtype=float)[-meta["window"]:]
    if len(r) < meta["window"]:
        raise ValueError(f"Il faut au moins {meta['window']} rendements, reçu {len(r)}.")
    z = lstm_forward(scale(r, *meta["x_scale"])[None, :, None], w["W"], w["U"], w["b"], w["Wd"], w["bd"])
    return float(unscale(z, *meta["y_scale"])[0])
