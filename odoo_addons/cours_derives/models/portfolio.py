from odoo import api, fields, models


class CoursPortfolio(models.Model):
    _name = 'cours.portfolio'
    _description = 'Portefeuille de produits dérivés'

    name = fields.Char(string='Nom', required=True)
    forward_ids = fields.One2many('cours.forward', 'portfolio_id', string='Forwards')
    option_ids = fields.One2many('cours.option', 'portfolio_id', string='Options')
    total_forward_value = fields.Float(string='Valeur des forwards', compute='_compute_totals', store=True)
    total_option_profit = fields.Float(string='Profit net des options', compute='_compute_totals', store=True)
    total_value = fields.Float(string='Valeur totale du portefeuille', compute='_compute_totals', store=True)
    total_payoff = fields.Float(string="Payoff total à l'échéance", compute='_compute_totals', store=True)
    nb_calls = fields.Integer(string='Nombre de calls', compute='_compute_totals', store=True)
    nb_puts = fields.Integer(string='Nombre de puts', compute='_compute_totals', store=True)
    pct_calls = fields.Float(string='Part des calls (%)', compute='_compute_totals', store=True)

    @api.depends('forward_ids.Vt', 'option_ids.profit', 'option_ids.payoff', 'option_ids.quantity',
                 'option_ids.position', 'option_ids.type')
    def _compute_totals(self):
        for rec in self:
            rec.total_forward_value = sum(rec.forward_ids.mapped('Vt'))
            rec.total_option_profit = sum(rec.option_ids.mapped('profit'))
            rec.total_value = rec.total_forward_value + rec.total_option_profit
            rec.total_payoff = sum((1.0 if o.position == 'long' else -1.0) * o.payoff * o.quantity
                                   for o in rec.option_ids)
            rec.nb_calls = len(rec.option_ids.filtered(lambda o: o.type == 'call'))
            rec.nb_puts = len(rec.option_ids.filtered(lambda o: o.type == 'put'))
            total = rec.nb_calls + rec.nb_puts
            rec.pct_calls = 100.0 * rec.nb_calls / total if total else 0.0
