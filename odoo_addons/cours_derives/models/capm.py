from odoo import api, fields, models


class CoursCapm(models.Model):
    _name = 'cours.capm'
    _description = 'Modèle CAPM'

    name = fields.Char(string='Actif', required=True)
    rf = fields.Float(string='Taux sans risque Rf', default=0.03, digits=(6, 4))
    rm = fields.Float(string='Rentabilité attendue du marché E(Rm)', default=0.08, digits=(6, 4))
    beta = fields.Float(string='Bêta β', default=1.0, digits=(6, 4))
    cov_im = fields.Float(string='Cov(Ri, Rm)', digits=(8, 6))
    var_m = fields.Float(string='Var(Rm)', digits=(8, 6))
    expected = fields.Float(string='E(R) selon le CAPM', compute='_compute_capm', store=True, digits=(6, 4))
    observed = fields.Float(string='Rentabilité attendue offerte', digits=(6, 4))
    alpha = fields.Float(string='Alpha', compute='_compute_capm', store=True, digits=(6, 4))
    verdict = fields.Selection([('under', 'Sous-évalué'), ('fair', 'Correctement évalué'), ('over', 'Surévalué')],
                               string='Verdict', compute='_compute_capm', store=True)

    def action_estimate_beta(self):
        """β = Cov(Ri, Rm) / Var(Rm)"""
        for rec in self:
            if rec.var_m:
                rec.beta = rec.cov_im / rec.var_m

    @api.depends('rf', 'rm', 'beta', 'observed')
    def _compute_capm(self):
        for rec in self:
            rec.expected = rec.rf + rec.beta * (rec.rm - rec.rf)
            rec.alpha = rec.observed - rec.expected if rec.observed else 0.0
            if not rec.observed or abs(rec.alpha) < 1e-9:
                rec.verdict = 'fair'
            else:
                rec.verdict = 'under' if rec.alpha > 0 else 'over'
