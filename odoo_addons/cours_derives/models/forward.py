import math
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CoursForward(models.Model):
    _name = 'cours.forward'
    _description = 'Contrat forward'

    name = fields.Char(string='Référence', required=True)
    portfolio_id = fields.Many2one('cours.portfolio', string='Portefeuille', ondelete='set null')
    S0 = fields.Float(string='Prix spot S0', default=100.0)
    r = fields.Float(string='Taux sans risque r (continu)', default=0.05, digits=(6, 4))
    T = fields.Float(string='Maturité T (années)', default=1.0)
    F0 = fields.Float(string='Prix forward F0', compute='_compute_F0', store=True,
                      help='F0 = S0 * exp(r*T) (non-arbitrage, actif sans revenu)')
    market_price = fields.Float(string='Prix forward coté')
    arbitrage_gain = fields.Float(string="Gain d'arbitrage", compute='_compute_arbitrage', store=True)
    arbitrage_signal = fields.Selection(
        [('none', 'Aucun'), ('sell_forward', 'Vendre le forward, acheter le sous-jacent'),
         ('buy_forward', 'Acheter le forward, vendre le sous-jacent à découvert')],
        string="Stratégie d'arbitrage", compute='_compute_arbitrage', store=True)
    St = fields.Float(string='Prix spot à la date t')
    t = fields.Float(string='Temps écoulé t (années)')
    Vt = fields.Float(string="Valeur pour l'acheteur Vt", compute='_compute_Vt', store=True,
                      help='Vt = St - F0 * exp(-r*(T-t))')

    @api.constrains('S0', 'T', 't')
    def _check_params(self):
        for rec in self:
            if rec.S0 <= 0 or rec.T <= 0:
                raise ValidationError("Le prix spot S0 et la maturité T doivent être strictement positifs.")
            if rec.t < 0 or rec.t > rec.T:
                raise ValidationError("Le temps écoulé t doit vérifier 0 <= t <= T.")

    @api.depends('S0', 'r', 'T')
    def _compute_F0(self):
        for rec in self:
            rec.F0 = rec.S0 * math.exp(rec.r * rec.T)

    @api.depends('F0', 'market_price')
    def _compute_arbitrage(self):
        for rec in self:
            if not rec.market_price:
                rec.arbitrage_signal, rec.arbitrage_gain = 'none', 0.0
            elif rec.market_price > rec.F0 + 1e-9:
                rec.arbitrage_signal, rec.arbitrage_gain = 'sell_forward', rec.market_price - rec.F0
            elif rec.market_price < rec.F0 - 1e-9:
                rec.arbitrage_signal, rec.arbitrage_gain = 'buy_forward', rec.F0 - rec.market_price
            else:
                rec.arbitrage_signal, rec.arbitrage_gain = 'none', 0.0

    @api.depends('St', 'F0', 'r', 'T', 't')
    def _compute_Vt(self):
        for rec in self:
            rec.Vt = rec.St - rec.F0 * math.exp(-rec.r * (rec.T - rec.t)) if rec.St else 0.0
