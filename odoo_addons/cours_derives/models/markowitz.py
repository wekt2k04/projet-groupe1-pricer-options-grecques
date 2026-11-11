import math
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CoursMarkowitz(models.Model):
    _name = 'cours.markowitz'
    _description = 'Portefeuille de deux actifs (Markowitz)'

    name = fields.Char(string='Nom', required=True)
    mu_A = fields.Float(string='E(R_A)', default=0.12, digits=(6, 4))
    sigma_A = fields.Float(string='σ_A', default=0.20, digits=(6, 4))
    mu_B = fields.Float(string='E(R_B)', default=0.06, digits=(6, 4))
    sigma_B = fields.Float(string='σ_B', default=0.10, digits=(6, 4))
    rho = fields.Float(string='Corrélation ρ', default=0.5, digits=(6, 4))
    w_A = fields.Float(string='Poids w_A', default=0.6, digits=(6, 4))
    mu_p = fields.Float(string='E(R_p)', compute='_compute_portfolio', store=True, digits=(6, 4))
    variance_p = fields.Float(string='Variance σ_p²', compute='_compute_portfolio', store=True, digits=(8, 6))
    sigma_p = fields.Float(string='Risque σ_p', compute='_compute_portfolio', store=True, digits=(6, 4))
    sigma_avg = fields.Float(string='Moyenne pondérée des risques', compute='_compute_portfolio', store=True,
                             digits=(6, 4))
    diversification_gain = fields.Float(string='Gain de diversification', compute='_compute_portfolio',
                                        store=True, digits=(6, 4),
                                        help='Moyenne pondérée des risques - risque du portefeuille')
    w_min = fields.Float(string='Poids de variance minimale w_A*', compute='_compute_min_var', store=True,
                         digits=(6, 4))
    sigma_min = fields.Float(string='σ_p minimal (sans vente à découvert)', compute='_compute_min_var',
                             store=True, digits=(6, 4))
    mu_min = fields.Float(string='E(R_p) au minimum de variance', compute='_compute_min_var', store=True,
                          digits=(6, 4))
    short_needed = fields.Boolean(string='Vente à découvert nécessaire', compute='_compute_min_var', store=True)

    @api.constrains('rho', 'sigma_A', 'sigma_B', 'w_A')
    def _check_params(self):
        for rec in self:
            if not -1.0 <= rec.rho <= 1.0:
                raise ValidationError("La corrélation ρ doit être comprise entre -1 et 1.")
            if rec.sigma_A < 0 or rec.sigma_B < 0:
                raise ValidationError("Les risques σ doivent être positifs.")
            if not 0.0 <= rec.w_A <= 1.0:
                raise ValidationError("Le poids w_A doit être compris entre 0 et 1 (pas de vente à découvert).")

    @staticmethod
    def _sigma(w, sA, sB, rho):
        var = w * w * sA * sA + (1 - w) ** 2 * sB * sB + 2 * w * (1 - w) * rho * sA * sB
        return math.sqrt(max(var, 0.0))

    @api.depends('mu_A', 'mu_B', 'sigma_A', 'sigma_B', 'rho', 'w_A')
    def _compute_portfolio(self):
        for rec in self:
            w = rec.w_A
            rec.mu_p = w * rec.mu_A + (1 - w) * rec.mu_B
            rec.sigma_p = self._sigma(w, rec.sigma_A, rec.sigma_B, rec.rho)
            rec.variance_p = rec.sigma_p ** 2
            rec.sigma_avg = w * rec.sigma_A + (1 - w) * rec.sigma_B
            rec.diversification_gain = rec.sigma_avg - rec.sigma_p

    @api.depends('mu_A', 'mu_B', 'sigma_A', 'sigma_B', 'rho')
    def _compute_min_var(self):
        for rec in self:
            den = rec.sigma_A ** 2 + rec.sigma_B ** 2 - 2 * rec.rho * rec.sigma_A * rec.sigma_B
            w = (rec.sigma_B ** 2 - rec.rho * rec.sigma_A * rec.sigma_B) / den if den else 0.0
            rec.short_needed = not 0.0 <= w <= 1.0
            rec.w_min = min(max(w, 0.0), 1.0)          # sans vente à découvert : on borne à [0, 1]
            rec.sigma_min = self._sigma(rec.w_min, rec.sigma_A, rec.sigma_B, rec.rho)
            rec.mu_min = rec.w_min * rec.mu_A + (1 - rec.w_min) * rec.mu_B
