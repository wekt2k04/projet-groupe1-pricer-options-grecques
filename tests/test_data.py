"""Tests de src/data.py, sans réseau : yfinance est remplacé par un faux module."""
import sys
import types

import numpy as np
import pandas as pd
import pytest

from data import (historical_volatility, load_prices, load_prices_info, log_returns,
                  rolling_realized_vol)


def _faux_yfinance(monkeypatch, download):
    mod = types.ModuleType("yfinance")
    mod.download = download
    monkeypatch.setitem(sys.modules, "yfinance", mod)


def _panne(*args, **kwargs):
    raise ConnectionError("Yahoo injoignable")


@pytest.fixture
def csv_repli(tmp_path):
    chemin = tmp_path / "aapl_2y_fallback.csv"
    pd.DataFrame({"Date": pd.bdate_range("2025-01-01", periods=5),
                  "Close": [100.0, 101.0, 99.5, 102.0, 103.0]}).to_csv(chemin, index=False)
    return chemin


def test_source_yfinance_quand_le_telechargement_reussit(monkeypatch):
    idx = pd.bdate_range("2025-01-01", periods=3)
    _faux_yfinance(monkeypatch, lambda *a, **k: pd.DataFrame({"Close": [1.0, 2.0, 3.0]}, index=idx))
    prix, source = load_prices_info("AAPL", "2y")
    assert source == "yfinance"
    assert list(prix) == [1.0, 2.0, 3.0]


def test_repli_csv_quand_yfinance_echoue(monkeypatch, csv_repli):
    _faux_yfinance(monkeypatch, _panne)
    prix, source = load_prices_info("AAPL", "2y", csv_fallback=csv_repli)
    assert source == "csv"
    assert len(prix) == 5
    assert isinstance(prix.index, pd.DatetimeIndex)


def test_erreur_explicite_sans_csv_de_repli(monkeypatch):
    _faux_yfinance(monkeypatch, _panne)
    with pytest.raises(RuntimeError, match="aucun CSV de repli"):
        load_prices_info("AAPL", "2y")


def test_load_prices_garde_son_contrat(monkeypatch, csv_repli):
    _faux_yfinance(monkeypatch, _panne)
    pd.testing.assert_series_equal(load_prices("AAPL", "2y", csv_repli),
                                   load_prices_info("AAPL", "2y", csv_repli)[0])


def test_rendements_et_volatilites():
    prix = pd.Series(100.0 * np.exp(0.01 * np.arange(10)), index=pd.bdate_range("2025-01-01", periods=10))
    r = log_returns(prix)
    assert len(r) == 9 and np.allclose(r, 0.01)                  # croissance régulière : rendement constant
    assert historical_volatility(r) == pytest.approx(0.0, abs=1e-12)
    vol5 = rolling_realized_vol(r, window=5)
    assert vol5.isna().sum() == 4                                # il faut 5 rendements pour la première valeur
