"""Groupe 1, Projet 1 : le bouton Odoo déclenche le LSTM (S5).

L'option est reliée à une série de prix (cours.volatility du TP 0). Le bouton calcule la volatilité historique
annualisée de la série (→ sigma, donc bs_price) et la volatilité prévue par le LSTM (→ sigma_lstm, donc
bs_price_lstm) : les deux prix s'affichent côte à côte. Inférence en NumPy (src/ml.py), sans TensorFlow.
"""
import os
import re

import numpy as np

from odoo import fields, models
from odoo.exceptions import UserError

try:
    from ml import load_model, predict_vol
except ImportError:  # module ml absent du conteneur : le bouton explique quoi vérifier
    load_model = predict_vol = None

CHEMIN_MODELE = os.environ.get("LSTM_MODEL_PATH", "/mnt/finance_models/lstm_vol.npz")
JOURS = 252


class CoursVolPrediction(models.Model):
    _name = "cours.vol.prediction"
    _description = "Prévision de volatilité par le LSTM"
    _order = "date_prevision desc, id desc"

    name = fields.Char("Référence", required=True)
    volatility_id = fields.Many2one("cours.volatility", string="Série de prix", ondelete="set null")
    date_prevision = fields.Date("Date", default=fields.Date.context_today)
    horizon_jours = fields.Integer("Horizon (jours de bourse)")
    vol_historique = fields.Float("Volatilité historique annualisée", digits=(6, 4))
    vol_predite = fields.Float("Volatilité prévue (LSTM)", digits=(6, 4))
    modele = fields.Char("Modèle")


class CoursOptionPrediction(models.Model):
    _inherit = "cours.option"

    volatility_id = fields.Many2one("cours.volatility", string="Série de prix (volatilité)",
                                    help="Série de prix du sous-jacent ; au moins 31 prix pour le LSTM.")
    prediction_id = fields.Many2one("cours.vol.prediction", string="Dernière prévision", readonly=True)

    def action_predire_vol(self):
        if predict_vol is None:
            raise UserError("Module « ml » introuvable : vérifier PYTHONPATH=/mnt/finance_src dans docker-compose.yml.")
        for rec in self:
            if not rec.volatility_id:
                raise UserError("Choisir d'abord une série de prix (champ « Série de prix »).")
            try:
                prix = np.array([float(x) for x in re.split(r"[,;\s]+", (rec.volatility_id.prices or "").strip()) if x])
            except ValueError:
                raise UserError("La série de prix contient une valeur non numérique.")
            if len(prix) < 31 or (prix <= 0).any():
                raise UserError("Il faut au moins 31 prix strictement positifs pour prévoir la volatilité.")
            rendements = np.diff(np.log(prix))
            try:
                vol_lstm = predict_vol(rendements, CHEMIN_MODELE)
                meta = load_model(CHEMIN_MODELE)[1]
            except (OSError, ValueError) as err:
                raise UserError(f"Prévision impossible ({CHEMIN_MODELE}) : {err}")
            vol_hist = float(rendements.std(ddof=1) * np.sqrt(JOURS))
            prevision = self.env["cours.vol.prediction"].create({
                "name": f"{rec.volatility_id.name} — {fields.Date.context_today(self)}",
                "volatility_id": rec.volatility_id.id, "horizon_jours": meta.get("horizon", 0),
                "vol_historique": vol_hist, "vol_predite": vol_lstm, "modele": f"LSTM {meta.get('variante', '')}"})
            rec.write({"sigma": vol_hist, "sigma_lstm": vol_lstm, "prediction_id": prevision.id})
        return True
