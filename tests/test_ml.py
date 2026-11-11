"""Tests de src/ml.py : jeux de données sans fuite, références, métriques, LSTM NumPy identique à Keras."""
import numpy as np
import pandas as pd
import pytest

from ml import (chrono_split, ewma_v1, fit_minmax, garch_v1, lstm_forward, make_dataset_v0, make_dataset_v1,
                persistence_v1, qlike, rmse, scale, unscale)

RNG = np.random.default_rng(42)
R = pd.Series(RNG.normal(0, 0.01, 300), index=pd.bdate_range("2024-01-01", periods=300))


def test_v1_cible_strictement_future():
    X, y = make_dataset_v1(R, window=30, horizon=5)
    i = 17
    assert np.allclose(X[i, :, 0], R.iloc[i:i + 30])
    assert y[i] == pytest.approx(R.iloc[i + 30:i + 35].std(ddof=1) * np.sqrt(252))
    assert len(y) == 300 - 30 - 5 + 1


def test_v0_formes():
    X, y = make_dataset_v0(R, window=30)
    assert X.shape == (len(y), 30, 1) and np.isfinite(X).all()


def test_decoupage_chronologique():
    a, b = chrono_split(100)
    assert (a, b) == (70, 85)


def test_normalisation_aller_retour():
    lo, hi = fit_minmax([1.0, 3.0])
    assert unscale(scale([2.0], lo, hi), lo, hi)[0] == pytest.approx(2.0)


def test_references_volatilite_constante():
    X = np.full((4, 30, 1), 0.01)
    X[:, ::2, 0] = -0.01                         # |r| = 1 % chaque jour
    assert np.allclose(ewma_v1(X), 0.01 * np.sqrt(252), rtol=0.05)
    assert np.allclose(garch_v1(X, omega=1e-4, alpha=0.0, beta=0.0), np.sqrt(1e-4 * 252))   # α = β = 0 : variance = ω
    assert persistence_v1(X).shape == (4,)


def test_metriques():
    y = np.array([0.2, 0.3])
    assert rmse(y, y) == 0 and qlike(y, y) == pytest.approx(0.0)
    assert qlike(y, 2 * y) > 0


def test_lstm_numpy_cas_scalaire():
    W, U, b = np.zeros((1, 4)), np.zeros((1, 4)), np.array([0.0, 0.0, 1.0, 0.0])
    out = lstm_forward(np.ones((1, 1, 1)), W, U, b, np.ones((1, 1)), np.zeros(1))
    assert out[0] == pytest.approx(0.5 * np.tanh(0.5 * np.tanh(1.0)))


def test_lstm_numpy_identique_a_keras():
    tf = pytest.importorskip("tensorflow")
    tf.keras.utils.set_random_seed(0)
    m = tf.keras.Sequential([tf.keras.Input((30, 1)), tf.keras.layers.LSTM(8), tf.keras.layers.Dense(1)])
    X = RNG.normal(size=(5, 30, 1)).astype("float32")
    W, U, b = m.layers[0].get_weights()
    Wd, bd = m.layers[1].get_weights()
    assert np.allclose(lstm_forward(X, W, U, b, Wd, bd), m.predict(X, verbose=0).ravel(), atol=1e-5)


def test_export_et_prevision_aller_retour(tmp_path):
    from ml import load_model, predict_vol, save_model, scale, unscale
    rng = np.random.default_rng(1)
    w = dict(W=rng.normal(size=(1, 16)), U=rng.normal(size=(4, 16)), b=rng.normal(size=16), Wd=rng.normal(size=(4, 1)), bd=rng.normal(size=1))
    meta = {"variante": "V1", "window": 30, "horizon": 5, "x_scale": [-0.05, 0.05], "y_scale": [0.05, 0.6]}
    chemin = tmp_path / "m.npz"
    save_model(chemin, w, meta)
    assert load_model(chemin)[1] == meta
    r = rng.normal(0, 0.01, 50)
    attendu = unscale(lstm_forward(scale(r[-30:], -0.05, 0.05)[None, :, None], **w), 0.05, 0.6)[0]
    assert predict_vol(r, chemin) == pytest.approx(attendu)
    with pytest.raises(ValueError):
        predict_vol(r[:10], chemin)
