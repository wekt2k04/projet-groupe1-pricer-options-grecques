import math
from odoo import api, fields, models
from odoo.exceptions import ValidationError


def _norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


class CoursOption(models.Model):
    _name = 'cours.option'
    _description = 'Option vanille européenne'

    name = fields.Char(string='Référence', required=True)
    portfolio_id = fields.Many2one('cours.portfolio', string='Portefeuille', ondelete='set null')
    type = fields.Selection([('call', 'Call'), ('put', 'Put')], string='Type', required=True, default='call')
    position = fields.Selection([('long', 'Acheteur'), ('short', 'Vendeur')], string='Position',
                                required=True, default='long')
    quantity = fields.Float(string='Quantité', default=1.0)
    S0 = fields.Float(string='Prix spot S0', default=100.0)
    S_T = fields.Float(string="Prix du sous-jacent à l'échéance", default=100.0)
    K = fields.Float(string='Strike K', default=100.0)
    premium = fields.Float(string='Prime')
    r = fields.Float(string='Taux sans risque r', default=0.05, digits=(6, 4))
    T = fields.Float(string='Maturité T (années)', default=1.0)
    sigma = fields.Float(string='Volatilité σ', default=0.2, digits=(6, 4))
    payoff = fields.Float(string='Payoff (acheteur)', compute='_compute_payoff', store=True,
                          help='Call : max(S_T - K, 0) ; Put : max(K - S_T, 0)')
    profit = fields.Float(string='Profit net de la position', compute='_compute_payoff', store=True,
                          help='Acheteur : payoff - prime ; vendeur : prime - payoff ; multiplié par la quantité')
    break_even = fields.Float(string='Seuil de rentabilité', compute='_compute_payoff', store=True,
                              help='Call : K + prime ; Put : K - prime')
    moneyness = fields.Selection([('itm', 'Dans la monnaie'), ('atm', 'À la monnaie'), ('otm', 'Hors de la monnaie')],
                                 string='Statut', compute='_compute_payoff', store=True)
    bs_price = fields.Float(string='Prix Black-Scholes', compute='_compute_bs', store=True)

    @api.constrains('K', 'S0', 'T', 'sigma')
    def _check_params(self):
        for rec in self:
            if rec.K <= 0 or rec.S0 <= 0 or rec.T <= 0 or rec.sigma < 0:
                raise ValidationError("S0, K et T doivent être > 0 et σ >= 0.")

    @api.depends('type', 'position', 'quantity', 'S_T', 'K', 'premium')
    def _compute_payoff(self):
        for rec in self:
            if rec.type == 'call':
                rec.payoff = max(rec.S_T - rec.K, 0.0)
                rec.break_even = rec.K + rec.premium
            else:
                rec.payoff = max(rec.K - rec.S_T, 0.0)
                rec.break_even = rec.K - rec.premium
            sign = 1.0 if rec.position == 'long' else -1.0
            rec.profit = sign * (rec.payoff - rec.premium) * rec.quantity
            if abs(rec.S_T - rec.K) < 1e-9:
                rec.moneyness = 'atm'
            elif (rec.type == 'call') == (rec.S_T > rec.K):
                rec.moneyness = 'itm'
            else:
                rec.moneyness = 'otm'

    @api.depends('type', 'S0', 'K', 'r', 'T', 'sigma')
    def _compute_bs(self):
        for rec in self:
            if rec.S0 <= 0 or rec.K <= 0 or rec.T <= 0:
                rec.bs_price = 0.0
                continue
            disc = rec.K * math.exp(-rec.r * rec.T)
            if rec.sigma <= 0:
                call = max(rec.S0 - disc, 0.0)
            else:
                d1 = (math.log(rec.S0 / rec.K) + (rec.r + 0.5 * rec.sigma ** 2) * rec.T) / (rec.sigma * math.sqrt(rec.T))
                d2 = d1 - rec.sigma * math.sqrt(rec.T)
                call = rec.S0 * _norm_cdf(d1) - disc * _norm_cdf(d2)
            # le put se déduit du call par la parité : C - P = S0 - K.exp(-rT)
            rec.bs_price = call if rec.type == 'call' else call - rec.S0 + disc
