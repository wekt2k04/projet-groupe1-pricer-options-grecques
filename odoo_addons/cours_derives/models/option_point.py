"""Groupe 1, Projet 1 : courbe Delta(S) d'une option, tracée par la vue graphique d'Odoo.

Une vue graphique Odoo agrège des enregistrements : elle ne trace pas une fonction. Le bouton crée donc
21 points (spot de 50 % à 150 % du strike) dans cours.option.point, que la vue graphique relie.
"""
import numpy as np

from odoo import fields, models

from .option_greeks import greeks

POURCENTAGES = list(range(50, 151, 5))


class CoursOptionPoint(models.Model):
    _name = "cours.option.point"
    _description = "Point de la courbe Delta(S) d'une option"
    _order = "option_id, moneyness_pct"

    option_id = fields.Many2one("cours.option", string="Option", required=True, ondelete="cascade", index=True)
    moneyness_pct = fields.Integer("Spot en % du strike")
    spot = fields.Float("Spot S", digits=(16, 4))
    delta = fields.Float("Delta", digits=(16, 6), group_operator="avg")
    gamma = fields.Float("Gamma", digits=(16, 6), group_operator="avg")


class CoursOptionDeltaCurve(models.Model):
    _inherit = "cours.option"

    point_ids = fields.One2many("cours.option.point", "option_id", string="Courbe Delta(S)")

    def _generer_points(self):
        if greeks is None:
            return
        for rec in self:
            rec.point_ids.unlink()
            spots = np.array([rec.K * p / 100.0 for p in POURCENTAGES])
            try:
                g = greeks(spots, rec.K, rec.T, rec.r, rec.sigma, rec.type)
            except ValueError:
                continue
            self.env["cours.option.point"].create([
                {"option_id": rec.id, "moneyness_pct": p, "spot": float(s), "delta": float(d), "gamma": float(gm)}
                for p, s, d, gm in zip(POURCENTAGES, spots, g["delta"], g["gamma"])])

    def action_calculer(self):
        resultat = super().action_calculer()
        self._generer_points()
        return resultat

    def action_voir_delta(self):
        self.ensure_one()
        self._generer_points()
        return {
            "type": "ir.actions.act_window",
            "name": f"Delta(S) — {self.name}",
            "res_model": "cours.option.point",
            "view_mode": "graph,tree",
            "domain": [("option_id", "=", self.id)],
        }
