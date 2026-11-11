"""Groupe 1, Projet 1 : extension de cours.option (Grecques de Black-Scholes, prix avec σ prédite).

Le calcul financier vit dans src/pricing.py (testé par pytest) ; Odoo l'importe grâce à
PYTHONPATH=/mnt/finance_src (docker-compose.yml). Unités : CONVENTIONS.md.
"""
from odoo import api, fields, models
from odoo.exceptions import UserError

try:
    from pricing import bs_price, greeks
except ImportError:  # module pricing absent du conteneur : les Grecques restent à 0, le bouton explique
    bs_price = greeks = None

GRECQUES = ("delta", "gamma", "vega", "theta", "rho")


class CoursOptionGreeks(models.Model):
    _inherit = "cours.option"

    greeks_delta = fields.Float("Delta", compute="_compute_greeks", store=True, digits=(16, 6))
    greeks_gamma = fields.Float("Gamma", compute="_compute_greeks", store=True, digits=(16, 6))
    greeks_vega = fields.Float("Vega (pour 1,00 de σ)", compute="_compute_greeks", store=True, digits=(16, 6))
    greeks_theta = fields.Float("Theta (par an)", compute="_compute_greeks", store=True, digits=(16, 6))
    greeks_rho = fields.Float("Rho (pour 1,00 de r)", compute="_compute_greeks", store=True, digits=(16, 6))
    sigma_lstm = fields.Float("Volatilité prédite (LSTM)", digits=(6, 4),
                              help="Volatilité annualisée prévue par le LSTM ; vide tant qu'aucune prévision n'est faite.")
    bs_price_lstm = fields.Float("Prix avec σ prédite", compute="_compute_greeks", store=True, digits=(16, 4))

    @api.depends("type", "S0", "K", "T", "r", "sigma", "sigma_lstm")
    def _compute_greeks(self):
        for rec in self:
            valeurs, prix_lstm = dict.fromkeys(GRECQUES, 0.0), 0.0
            if greeks is not None:
                try:
                    valeurs = {k: float(v) for k, v in greeks(rec.S0, rec.K, rec.T, rec.r, rec.sigma, rec.type).items()}
                    if rec.sigma_lstm > 0:
                        prix_lstm = float(bs_price(rec.S0, rec.K, rec.T, rec.r, rec.sigma_lstm, rec.type))
                except ValueError:  # entrée invalide : jamais d'exception dans un champ calculé
                    pass
            for k in GRECQUES:
                rec[f"greeks_{k}"] = valeurs[k]
            rec.bs_price_lstm = prix_lstm

    def action_calculer(self):
        if greeks is None:
            raise UserError("Module « pricing » introuvable : vérifier PYTHONPATH=/mnt/finance_src dans docker-compose.yml.")
        self._compute_bs()
        self._compute_greeks()
        return True


class CoursPortfolioGreeks(models.Model):
    _inherit = "cours.portfolio"

    delta_total = fields.Float("Delta du portefeuille", compute="_compute_delta_total", store=True, digits=(16, 6),
                               help="Somme des Delta des options, signée selon la position et multipliée par la quantité.")

    @api.depends("option_ids.greeks_delta", "option_ids.position", "option_ids.quantity")
    def _compute_delta_total(self):
        for rec in self:
            rec.delta_total = sum((1.0 if o.position == "long" else -1.0) * o.quantity * o.greeks_delta
                                  for o in rec.option_ids)
