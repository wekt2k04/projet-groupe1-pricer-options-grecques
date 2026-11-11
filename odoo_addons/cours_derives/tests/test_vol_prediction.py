"""Tests Odoo du bouton « Prédire la volatilité » (Groupe 1, Projet 1, S5)."""
import os

import numpy as np

from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged

from ..models.vol_prediction import CHEMIN_MODELE


@tagged("post_install", "-at_install")
class TestVolPrediction(TransactionCase):

    def _option(self, n_prix):
        prix = 100 * np.exp(np.cumsum(np.random.default_rng(42).normal(0, 0.01, n_prix)))
        serie = self.env["cours.volatility"].create({"name": "AAPL test", "prices": ", ".join(f"{p:.4f}" for p in prix)})
        return self.env["cours.option"].create(dict(name="Test IA", type="call", S0=100.0, K=100.0, T=1.0, r=0.05,
                                                    sigma=0.20, volatility_id=serie.id))

    def test_sans_serie_de_prix(self):
        o = self.env["cours.option"].create(dict(name="Sans série", S0=100.0, K=100.0, T=1.0, r=0.05, sigma=0.2))
        with self.assertRaises(UserError):
            o.action_predire_vol()

    def test_serie_trop_courte(self):
        with self.assertRaises(UserError):
            self._option(20).action_predire_vol()

    def test_prevision_et_prix_cote_a_cote(self):
        if not os.path.exists(CHEMIN_MODELE):
            self.skipTest(f"modèle absent : {CHEMIN_MODELE}")
        o = self._option(80)
        o.action_predire_vol()
        self.assertGreater(o.sigma_lstm, 0.0)
        self.assertTrue(o.prediction_id)
        self.assertAlmostEqual(o.prediction_id.vol_predite, o.sigma_lstm, places=6)
        self.assertGreater(o.bs_price_lstm, 0.0)          # prix avec σ prédite, à côté de bs_price (σ historique)
