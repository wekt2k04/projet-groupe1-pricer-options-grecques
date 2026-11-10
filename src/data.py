"""Données de marché : téléchargement, repli CSV, simulation, volatilité.

Source principale : yfinance (cours de clôture ajusté).
Repli : fichier CSV exporté (colonnes Date, Close) ; à documenter dans le
rapport si utilisé. Simulation GBM pour travailler hors ligne.
"""
import numpy as np
import pandas as pd

JOURS_BOURSE = 252   # annualisation de la volatilité historique


def load_prices_info(ticker="AAPL", period="2y", csv_fallback=None):
    """Cours de clôture ajusté et source effective : (pd.Series indexée par date, "yfinance" | "csv").

    Essaie yfinance ; en cas d'échec (réseau, symbole, série vide), lit csv_fallback
    (colonnes Date, Close). Les notebooks affichent la source pour que personne ne
    prenne un CSV de repli pour un téléchargement du jour (CLAUDE.md §9, S2-03).
    """
    try:
        import yfinance as yf
        px = yf.download(ticker, period=period, auto_adjust=True, progress=False)["Close"]
        px = px.squeeze().dropna()
        if len(px) > 0:
            return px, "yfinance"
    except Exception:
        pass
    if csv_fallback is None:
        raise RuntimeError(f"Téléchargement de {ticker} impossible et aucun CSV de repli fourni")
    df = pd.read_csv(csv_fallback, parse_dates=["Date"], index_col="Date")
    return df["Close"].dropna(), "csv"


def load_prices(ticker="AAPL", period="2y", csv_fallback=None):
    """Cours de clôture ajusté (pd.Series indexée par date).

    Essaie yfinance ; en cas d'échec (réseau, symbole), lit csv_fallback.
    Contrat inchangé depuis la S1 ; pour connaître la source, utiliser load_prices_info.
    """
    return load_prices_info(ticker, period, csv_fallback)[0]


def simulate_gbm_prices(S0=100.0, mu=0.05, sigma=0.20, n=504, seed=42):
    """Trajectoire GBM journalière (n jours de bourse, graine fixée)."""
    rng = np.random.default_rng(seed)
    dt = 1.0 / JOURS_BOURSE
    z = rng.standard_normal(n)
    log_ret = (mu - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * z
    idx = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=n + 1)
    return pd.Series(S0 * np.exp(np.concatenate([[0.0], np.cumsum(log_ret)])), index=idx, name="Close")


def log_returns(prices):
    """r_t = ln(S_t / S_{t-1})."""
    return np.log(prices / prices.shift(1)).dropna()


def historical_volatility(returns, trading_days=JOURS_BOURSE):
    """Volatilité historique annualisée : écart-type(r_t) * sqrt(252), en décimal."""
    return float(returns.std(ddof=1) * np.sqrt(trading_days))


def rolling_realized_vol(returns, window=5, trading_days=JOURS_BOURSE):
    """Volatilité réalisée glissante annualisée (fenêtre de `window` jours)."""
    return returns.rolling(window).std(ddof=1) * np.sqrt(trading_days)
