"""Tests Odoo de l'extension Grecques (Groupe 1, Projet 1).

Lancement : docker compose run --rm web odoo -d groupe1 -u cours_derives --test-tags /cours_derives --stop-after-init
Valeurs de référence : CONVENTIONS.md (S = K = 100, T = 1, r = 5 %, σ = 20 %).
"""
import math

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestOptionGreeks(TransactionCase):

    def _option(self, **vals):
        base = dict(name="Test BS", type="call", S0=100.0, K=100.0, T=1.0, r=0.05, sigma=0.20)
        base.update(vals)
        return self.env["cours.option"].create(base)

    def test_call_valeurs_de_reference(self):
        o = self._option()
        self.assertAlmostEqual(o.bs_price, 10.4506, places=3)
        self.assertAlmostEqual(o.greeks_delta, 0.6368, places=3)
        self.assertAlmostEqual(o.greeks_gamma, 0.0188, places=3)
        self.assertAlmostEqual(o.greeks_vega, 37.524, places=2)
        self.assertAlmostEqual(o.greeks_theta, -6.414, places=2)
        self.assertAlmostEqual(o.greeks_rho, 53.2325, places=3)

    def test_put_valeurs_de_reference(self):
        o = self._option(type="put")
        self.assertAlmostEqual(o.bs_price, 5.5735, places=3)
        self.assertAlmostEqual(o.greeks_delta, -0.3632, places=3)
        self.assertAlmostEqual(o.greeks_theta, -1.6579, places=2)
        self.assertAlmostEqual(o.greeks_rho, -41.8905, places=3)

    def test_parite_call_put(self):
        c, p = self._option(), self._option(type="put")
        self.assertAlmostEqual(c.bs_price - p.bs_price, 100.0 - 100.0 * math.exp(-0.05), places=6)

    def test_recalcul_quand_le_spot_change(self):
        o = self._option()
        delta_avant = o.greeks_delta
        o.S0 = 120.0
        self.assertGreater(o.greeks_delta, delta_avant)

    def test_prix_avec_sigma_predite(self):
        o = self._option()
        self.assertEqual(o.bs_price_lstm, 0.0)          # pas de prévision : pas de prix LSTM
        o.sigma_lstm = 0.20
        self.assertAlmostEqual(o.bs_price_lstm, o.bs_price, places=6)

    def test_bouton_calculer(self):
        self.assertTrue(self._option().action_calculer())

    def test_entree_invalide_refusee(self):
        with self.assertRaises(ValidationError):
            self._option(S0=0.0)

    def test_delta_du_portefeuille(self):
        pf = self.env["cours.portfolio"].create({"name": "PF test"})
        self._option(portfolio_id=pf.id, position="long", quantity=2.0)
        self._option(portfolio_id=pf.id, type="put", position="short", quantity=1.0)
        self.assertAlmostEqual(pf.delta_total, 2 * 0.6368 + 0.3632, places=3)

    def test_courbe_delta(self):
        o = self._option()
        o.action_calculer()
        self.assertEqual(len(o.point_ids), 21)
        a_la_monnaie = o.point_ids.filtered(lambda p: p.moneyness_pct == 100)
        self.assertAlmostEqual(a_la_monnaie.delta, 0.6368, places=3)
        deltas = o.point_ids.sorted("moneyness_pct").mapped("delta")
        self.assertEqual(deltas, sorted(deltas))          # Delta du call croissant avec le spot

    def test_action_voir_delta(self):
        action = self._option().action_voir_delta()
        self.assertEqual(action["res_model"], "cours.option.point")
