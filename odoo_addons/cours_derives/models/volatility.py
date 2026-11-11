import math
from odoo import api, fields, models


class CoursVolatility(models.Model):
    _name = 'cours.volatility'
    _description = 'Estimation de la volatilité'

    name = fields.Char(string='Actif', required=True)
    prices = fields.Text(string='Prix historiques (séparés par des virgules ou des espaces)')
    ewma_lambda = fields.Float(string='λ (EWMA)', default=0.94, digits=(4, 2))
    nb_returns = fields.Integer(string='Nombre de rendements', compute='_compute_vol', store=True)
    vol_hist = fields.Float(string='Volatilité historique (par période)', compute='_compute_vol', store=True,
                            digits=(8, 6))
    vol_ewma = fields.Float(string='Volatilité EWMA (par période)', compute='_compute_vol', store=True,
                            digits=(8, 6))
    vol_annual = fields.Float(string='Volatilité EWMA annualisée (252 périodes)', compute='_compute_vol',
                              store=True, digits=(8, 4))
    vol_ml = fields.Float(string='Prévision ML (scikit-learn)', digits=(8, 6),
                          help='Régression Ridge de |r_t| sur |r_{t-1}| et |r_{t-2}| ; 0 si scikit-learn est absent.')

    def _returns(self):
        self.ensure_one()
        raw = (self.prices or '').replace(',', ' ').replace(';', ' ').split()
        prices = []
        for token in raw:
            try:
                prices.append(float(token))
            except ValueError:
                continue
        return [math.log(b / a) for a, b in zip(prices, prices[1:]) if a > 0 and b > 0]

    @api.depends('prices', 'ewma_lambda')
    def _compute_vol(self):
        for rec in self:
            rets = rec._returns()
            rec.nb_returns = len(rets)
            if len(rets) < 2:
                rec.vol_hist = rec.vol_ewma = rec.vol_annual = 0.0
                continue
            mean = sum(rets) / len(rets)
            rec.vol_hist = math.sqrt(sum((x - mean) ** 2 for x in rets) / (len(rets) - 1))
            lam, var = rec.ewma_lambda, rets[0] ** 2
            for x in rets[1:]:
                var = lam * var + (1 - lam) * x * x
            rec.vol_ewma = math.sqrt(var)
            rec.vol_annual = rec.vol_ewma * math.sqrt(252)

    def action_predict_ml(self):
        """Prévision d'IA : Ridge sur les valeurs absolues retardées (scikit-learn si présent)."""
        for rec in self:
            try:
                from sklearn.linear_model import Ridge
            except ImportError:
                rec.vol_ml = 0.0
                continue
            absr = [abs(x) for x in rec._returns()]
            if len(absr) < 8:
                continue
            X = [[absr[i - 1], absr[i - 2]] for i in range(2, len(absr))]
            y = [absr[i] for i in range(2, len(absr))]
            model = Ridge(alpha=1.0).fit(X, y)
            rec.vol_ml = float(model.predict([[absr[-1], absr[-2]]])[0])
